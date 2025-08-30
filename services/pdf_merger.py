"""
PDF Merge Service
Handles merging multiple PDF files into a single document
"""
import os
from PyPDF2 import PdfMerger
from flask import current_app
from utils import (
    generate_unique_id, create_temp_directory, 
    save_uploaded_files, cleanup_files, 
    validate_pdf_files, secure_output_filename
)

class PDFMergerService:
    """Service class for handling PDF merge operations"""
    
    def __init__(self):
        self.upload_folder = current_app.config['UPLOAD_FOLDER']
    
    def merge_files(self, files, output_filename=None):
        """
        Merge multiple PDF files into a single document
        
        Args:
            files: List of uploaded file objects
            output_filename: Optional custom filename for output
            
        Returns:
            tuple: (success, result_data_or_error_message)
        """
        try:
            # Validate files
            is_valid, result = validate_pdf_files(files, min_files=2)
            if not is_valid:
                return False, result
            
            valid_files = result
            
            # Generate unique ID and create temp directory
            unique_id = generate_unique_id()
            temp_dir = create_temp_directory(self.upload_folder, unique_id)
            
            # Save uploaded files temporarily
            temp_files = save_uploaded_files(valid_files, temp_dir)
            
            # Prepare output filename
            output_filename = secure_output_filename(
                output_filename, 
                default_name="merged-document.pdf"
            )
            
            # Merge PDFs
            success, result = self._merge_pdf_files(temp_files, temp_dir, output_filename)
            
            if success:
                # Clean up temporary files (but keep the merged file)
                cleanup_files(temp_files)
                
                return True, {
                    'unique_id': unique_id,
                    'filename': output_filename,
                    'message': 'PDF files merged successfully!'
                }
            else:
                # Clean up all files on error
                cleanup_files(temp_files + [temp_dir])
                return False, result
                
        except Exception as e:
            return False, f'An error occurred during merge: {str(e)}'
    
    def _merge_pdf_files(self, temp_files, temp_dir, output_filename):
        """
        Internal method to perform the actual PDF merge
        
        Args:
            temp_files: List of temporary file paths
            temp_dir: Temporary directory path
            output_filename: Name for the output file
            
        Returns:
            tuple: (success, result_or_error)
        """
        merger = PdfMerger()
        
        try:
            # Add each PDF to the merger
            for temp_file in temp_files:
                try:
                    merger.append(temp_file)
                except Exception as e:
                    merger.close()
                    return False, f'Error processing PDF file: {str(e)}'
            
            # Write merged PDF
            output_path = os.path.join(temp_dir, output_filename)
            merger.write(output_path)
            merger.close()
            
            return True, output_path
            
        except Exception as e:
            merger.close()
            return False, f'Error during PDF merge: {str(e)}'
    
    def get_file_path(self, unique_id, filename):
        """Get the full path to a processed file"""
        return os.path.join(self.upload_folder, unique_id, filename)
    
    def cleanup_processed_file(self, file_path, delay=None):
        """Clean up a processed file with optional delay"""
        cleanup_delay = delay or current_app.config.get('CLEANUP_DELAY', 10)
        
        temp_dir = os.path.dirname(file_path)
        cleanup_files([file_path, temp_dir], delay=cleanup_delay)