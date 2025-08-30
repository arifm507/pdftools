"""
PDF Split Service
Handles splitting PDF files into separate pages or page ranges
"""
import os
from PyPDF2 import PdfReader, PdfWriter
from flask import current_app
from utils import (
    generate_unique_id, create_temp_directory, 
    save_uploaded_files, cleanup_files, 
    validate_pdf_files, secure_output_filename
)
import zipfile

class PDFSplitterService:
    """Service class for handling PDF split operations"""
    
    def __init__(self):
        self.upload_folder = current_app.config['UPLOAD_FOLDER']
    
    def split_pdf(self, file, split_type='pages', page_ranges=None, output_filename=None):
        """
        Split PDF into separate files
        
        Args:
            file: Uploaded file object
            split_type: 'pages' (each page separate) or 'ranges' (custom ranges)
            page_ranges: List of page ranges for 'ranges' type (e.g., ['1-3', '4-6'])
            output_filename: Optional custom filename prefix for output
            
        Returns:
            tuple: (success, result_data_or_error_message)
        """
        try:
            # Validate file
            is_valid, result = validate_pdf_files([file], min_files=1)
            if not is_valid:
                return False, result
            
            valid_file = result[0]
            
            # Generate unique ID and create temp directory
            unique_id = generate_unique_id()
            temp_dir = create_temp_directory(self.upload_folder, unique_id)
            
            # Save uploaded file temporarily
            temp_files = save_uploaded_files([valid_file], temp_dir)
            input_file = temp_files[0]
            
            # Prepare output filename prefix
            if not output_filename:
                output_filename = os.path.splitext(valid_file.filename)[0]
            output_filename = secure_output_filename(output_filename, default_name="split-pdf")
            
            # Split PDF based on type
            if split_type == 'pages':
                success, result = self._split_into_pages(input_file, temp_dir, output_filename)
            elif split_type == 'ranges':
                success, result = self._split_into_ranges(input_file, temp_dir, output_filename, page_ranges)
            else:
                return False, 'Invalid split type specified'
            
            if success:
                # Create ZIP file containing all split files
                zip_filename = f"{output_filename}-split.zip"
                zip_path = os.path.join(temp_dir, zip_filename)
                
                zip_success = self._create_zip_file(result['files'], zip_path)
                
                if zip_success:
                    # Clean up individual PDF files but keep the ZIP
                    cleanup_files(temp_files + result['files'])
                    
                    return True, {
                        'unique_id': unique_id,
                        'filename': zip_filename,
                        'message': f'PDF split successfully into {result["count"]} files!',
                        'split_count': result['count']
                    }
                else:
                    cleanup_files(temp_files + result['files'] + [temp_dir])
                    return False, 'Error creating ZIP file'
            else:
                # Clean up all files on error
                cleanup_files(temp_files + [temp_dir])
                return False, result
                
        except Exception as e:
            return False, f'An error occurred during split: {str(e)}'
    
    def _split_into_pages(self, input_file, temp_dir, output_filename):
        """
        Split PDF into individual pages
        
        Args:
            input_file: Path to input PDF file
            temp_dir: Temporary directory path
            output_filename: Filename prefix for output files
            
        Returns:
            tuple: (success, result_data_or_error)
        """
        try:
            reader = PdfReader(input_file)
            total_pages = len(reader.pages)
            split_files = []
            
            for page_num in range(total_pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])
                
                # Create filename for this page
                page_filename = f"{output_filename}-page-{page_num + 1}.pdf"
                page_path = os.path.join(temp_dir, page_filename)
                
                # Write the page to file
                with open(page_path, 'wb') as output_file:
                    writer.write(output_file)
                
                split_files.append(page_path)
            
            return True, {
                'files': split_files,
                'count': total_pages
            }
            
        except Exception as e:
            return False, f'Error splitting PDF into pages: {str(e)}'
    
    def _split_into_ranges(self, input_file, temp_dir, output_filename, page_ranges):
        """
        Split PDF into specified page ranges
        
        Args:
            input_file: Path to input PDF file
            temp_dir: Temporary directory path
            output_filename: Filename prefix for output files
            page_ranges: List of page ranges (e.g., ['1-3', '4-6', '7'])
            
        Returns:
            tuple: (success, result_data_or_error)
        """
        try:
            if not page_ranges:
                return False, 'No page ranges specified'
            
            reader = PdfReader(input_file)
            total_pages = len(reader.pages)
            split_files = []
            
            for i, page_range in enumerate(page_ranges):
                writer = PdfWriter()
                
                # Parse page range
                try:
                    if '-' in page_range:
                        start, end = map(int, page_range.split('-'))
                        start = max(1, start)  # Ensure start is at least 1
                        end = min(total_pages, end)  # Ensure end doesn't exceed total pages
                        
                        if start > end:
                            return False, f'Invalid range: {page_range} (start > end)'
                        
                        # Add pages in range (convert to 0-based indexing)
                        for page_num in range(start - 1, end):
                            if page_num < total_pages:
                                writer.add_page(reader.pages[page_num])
                        
                        range_desc = f"pages-{start}-to-{end}"
                    else:
                        # Single page
                        page_num = int(page_range)
                        if page_num < 1 or page_num > total_pages:
                            return False, f'Invalid page number: {page_num} (valid range: 1-{total_pages})'
                        
                        writer.add_page(reader.pages[page_num - 1])  # Convert to 0-based indexing
                        range_desc = f"page-{page_num}"
                
                except ValueError:
                    return False, f'Invalid page range format: {page_range}'
                
                # Create filename for this range
                range_filename = f"{output_filename}-{range_desc}.pdf"
                range_path = os.path.join(temp_dir, range_filename)
                
                # Write the range to file
                with open(range_path, 'wb') as output_file:
                    writer.write(output_file)
                
                split_files.append(range_path)
            
            return True, {
                'files': split_files,
                'count': len(split_files)
            }
            
        except Exception as e:
            return False, f'Error splitting PDF into ranges: {str(e)}'
    
    def _create_zip_file(self, file_paths, zip_path):
        """
        Create a ZIP file containing all split PDF files
        
        Args:
            file_paths: List of file paths to include in ZIP
            zip_path: Path where ZIP file should be created
            
        Returns:
            bool: Success status
        """
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in file_paths:
                    filename = os.path.basename(file_path)
                    zipf.write(file_path, filename)
            
            return True
            
        except Exception as e:
            current_app.logger.error(f'Error creating ZIP file: {str(e)}')
            return False
    
    def get_file_path(self, unique_id, filename):
        """Get the full path to a processed file"""
        return os.path.join(self.upload_folder, unique_id, filename)
    
    def cleanup_processed_file(self, file_path, delay=None):
        """Clean up a processed file with optional delay"""
        cleanup_delay = delay or current_app.config.get('CLEANUP_DELAY', 10)
        
        temp_dir = os.path.dirname(file_path)
        cleanup_files([file_path, temp_dir], delay=cleanup_delay)