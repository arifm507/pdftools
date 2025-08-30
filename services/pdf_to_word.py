"""
PDF to Word Conversion Service
Handles converting PDF files to Word (.docx) documents
"""
import os
from flask import current_app
from utils import (
    generate_unique_id, create_temp_directory, 
    save_uploaded_files, cleanup_files, 
    validate_pdf_files, secure_output_filename
)

class PDFToWordService:
    """Service class for handling PDF to Word conversion operations"""
    
    def __init__(self):
        self.upload_folder = current_app.config['UPLOAD_FOLDER']
    
    def convert_file(self, files, output_filename=None):
        """
        Convert a PDF file to Word (.docx) document
        
        Args:
            files: List of uploaded file objects (should contain only 1 PDF)
            output_filename: Optional custom filename for output
            
        Returns:
            tuple: (success, result_data_or_error_message)
        """
        try:
            # Validate files - PDF to Word needs exactly 1 file
            is_valid, result = validate_pdf_files(files, min_files=1)
            if not is_valid:
                return False, result
            
            valid_files = result
            if len(valid_files) > 1:
                return False, "Please select only one PDF file for conversion"
            
            # Generate unique ID and create temp directory
            unique_id = generate_unique_id()
            temp_dir = create_temp_directory(self.upload_folder, unique_id)
            
            # Save uploaded file temporarily
            temp_files = save_uploaded_files(valid_files, temp_dir)
            
            if not temp_files:
                return False, "Failed to save uploaded file"
            
            # Prepare output filename
            if not output_filename:
                # Get original filename and replace extension
                original_name = valid_files[0].filename
                base_name = os.path.splitext(original_name)[0] if original_name else "converted-document"
                output_filename = f"{base_name}.docx"
            
            output_filename = secure_output_filename(
                output_filename, 
                default_name="converted-document.docx"
            )
            
            # Ensure output has .docx extension
            if not output_filename.endswith('.docx'):
                output_filename = os.path.splitext(output_filename)[0] + '.docx'
            
            # Convert PDF to Word
            success, result = self._convert_pdf_to_word(temp_files[0], temp_dir, output_filename)
            
            if success:
                # Clean up temporary PDF file (but keep the Word file)
                cleanup_files(temp_files)
                
                return True, {
                    'unique_id': unique_id,
                    'filename': output_filename,
                    'message': 'PDF converted to Word successfully!'
                }
            else:
                # Clean up all files on error
                cleanup_files(temp_files + [temp_dir])
                return False, result
                
        except Exception as e:
            return False, f'An error occurred during conversion: {str(e)}'
    
    def _convert_pdf_to_word(self, pdf_file_path, temp_dir, output_filename):
        """
        Internal method to perform the actual PDF to Word conversion
        
        Args:
            pdf_file_path: Path to the PDF file
            temp_dir: Temporary directory path
            output_filename: Name for the output file
            
        Returns:
            tuple: (success, result_or_error)
        """
        try:
            # Try importing pdf2docx
            try:
                from pdf2docx import Converter
            except ImportError:
                return False, "PDF to Word conversion library is not installed. Please install pdf2docx."
            
            output_path = os.path.join(temp_dir, output_filename)
            
            # Create converter instance and convert
            converter = Converter(pdf_file_path)
            converter.convert(output_path)
            converter.close()
            
            # Verify the output file was created
            if not os.path.exists(output_path):
                return False, "Conversion failed: Output file was not created"
            
            return True, output_path
            
        except Exception as e:
            error_msg = str(e)
            if "pdf2docx" in error_msg.lower():
                return False, f"PDF to Word conversion error: {error_msg}. The PDF might be password-protected or corrupted."
            return False, f'Error during PDF to Word conversion: {error_msg}'
    
    def get_file_path(self, unique_id, filename):
        """Get the full path to a processed file"""
        return os.path.join(self.upload_folder, unique_id, filename)
    
    def cleanup_processed_file(self, file_path, delay=None):
        """Clean up a processed file with optional delay"""
        cleanup_delay = delay or current_app.config.get('CLEANUP_DELAY', 10)
        
        temp_dir = os.path.dirname(file_path)
        cleanup_files([file_path, temp_dir], delay=cleanup_delay)