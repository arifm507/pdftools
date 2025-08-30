"""
PDF compression service
Handles compressing PDF files to reduce file size while maintaining quality
"""
import os
import uuid
import PyPDF2
from PIL import Image
from werkzeug.utils import secure_filename
from config import config
import io

class PDFCompressorService:
    """Service for compressing PDF files"""
    
    def __init__(self):
        """Initialize the service with upload directory"""
        self.upload_folder = config['default'].UPLOAD_FOLDER
        self.ensure_upload_directory()
    
    def ensure_upload_directory(self):
        """Ensure upload directory exists"""
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
    
    def compress_pdf(self, file, output_filename=None, compression_level='medium'):
        """
        Compress a PDF file
        
        Args:
            file: Uploaded PDF file
            output_filename: Optional custom output filename
            compression_level: Compression level ('low', 'medium', 'high')
            
        Returns:
            tuple: (success: bool, result: dict or error_message)
        """
        try:
            # Validate file
            if not file or not file.filename:
                return False, "No file provided"
            
            if not file.filename.lower().endswith('.pdf'):
                return False, "Please select a PDF file"
            
            # Generate unique identifier and filename
            unique_id = str(uuid.uuid4())
            if not output_filename or not output_filename.strip():
                base_name = os.path.splitext(file.filename)[0]
                output_filename = f"{base_name}_compressed.pdf"
            elif not output_filename.endswith('.pdf'):
                output_filename += '.pdf'
            
            # Secure the filename
            output_filename = secure_filename(output_filename)
            
            # Save uploaded file temporarily
            temp_filename = f"temp_{unique_id}_{secure_filename(file.filename)}"
            temp_path = os.path.join(self.upload_folder, temp_filename)
            file.save(temp_path)
            
            # Get original file size
            original_size = os.path.getsize(temp_path)
            
            # Output path
            output_path = os.path.join(self.upload_folder, f"{unique_id}_{output_filename}")
            
            # Compress the PDF
            success = self._compress_pdf_file(temp_path, output_path, compression_level)
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if not success:
                return False, "Failed to compress PDF"
            
            # Get compressed file size
            compressed_size = os.path.getsize(output_path)
            
            # Calculate compression ratio
            compression_ratio = ((original_size - compressed_size) / original_size) * 100
            
            return True, {
                'message': f'PDF compressed successfully! Size reduced by {compression_ratio:.1f}%',
                'filename': output_filename,
                'unique_id': unique_id,
                'file_path': output_path,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': compression_ratio
            }
            
        except Exception as e:
            return False, f"Compression failed: {str(e)}"
    
    def _compress_pdf_file(self, input_path, output_path, compression_level):
        """
        Internal method to compress PDF file
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save compressed PDF
            compression_level: Compression level ('low', 'medium', 'high')
            
        Returns:
            bool: Success status
        """
        try:
            # Try advanced compression with reportlab and PyPDF2
            success = self._compress_with_advanced_method(input_path, output_path, compression_level)
            
            if success:
                return True
            
            # Fallback to basic compression
            return self._compress_with_basic_method(input_path, output_path)
            
        except Exception as e:
            return False
    
    def _compress_with_advanced_method(self, input_path, output_path, compression_level):
        """
        Advanced compression method using image optimization
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save compressed PDF
            compression_level: Compression level
            
        Returns:
            bool: Success status
        """
        try:
            import fitz  # PyMuPDF
            
            # Compression settings based on level
            compression_settings = {
                'low': {'quality': 90, 'dpi': 150},      # Light compression
                'medium': {'quality': 75, 'dpi': 120},   # Balanced compression
                'high': {'quality': 60, 'dpi': 100}      # Maximum compression
            }
            
            settings = compression_settings.get(compression_level, compression_settings['medium'])
            
            # Open the PDF
            doc = fitz.open(input_path)
            
            # Create new PDF
            new_doc = fitz.open()
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Get page as image with specified DPI
                mat = fitz.Matrix(settings['dpi'] / 72, settings['dpi'] / 72)
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image for compression
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # Compress image
                img_buffer = io.BytesIO()
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img.save(img_buffer, format='JPEG', quality=settings['quality'], optimize=True)
                img_buffer.seek(0)
                
                # Create new page with compressed image
                img_rect = fitz.Rect(0, 0, page.rect.width, page.rect.height)
                new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
                new_page.insert_image(img_rect, stream=img_buffer.getvalue())
            
            # Save compressed PDF
            new_doc.save(output_path, garbage=4, deflate=True, clean=True)
            new_doc.close()
            doc.close()
            
            return True
            
        except ImportError:
            # PyMuPDF not available, fall back to basic method
            return False
        except Exception as e:
            return False
    
    def _compress_with_basic_method(self, input_path, output_path):
        """
        Basic compression method using PyPDF2
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save compressed PDF
            
        Returns:
            bool: Success status
        """
        try:
            with open(input_path, 'rb') as input_file:
                reader = PyPDF2.PdfReader(input_file)
                writer = PyPDF2.PdfWriter()
                
                # Copy all pages
                for page in reader.pages:
                    # Remove annotations and form fields to reduce size
                    if '/Annots' in page:
                        del page['/Annots']
                    if '/AcroForm' in page:
                        del page['/AcroForm']
                    
                    writer.add_page(page)
                
                # Compress streams
                writer.compress_identical_objects()
                
                # Write compressed PDF
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
            
            return True
            
        except Exception as e:
            return False
    
    def get_file_path(self, unique_id, filename):
        """Get the full path for a processed file"""
        filename = secure_filename(filename)
        return os.path.join(self.upload_folder, f"{unique_id}_{filename}")
    
    def cleanup_processed_file(self, file_path):
        """Schedule cleanup of processed file after download"""
        def delayed_cleanup():
            import time
            import threading
            def cleanup():
                time.sleep(5)  # Wait 5 seconds before cleanup
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except:
                    pass  # Ignore cleanup errors
            
            thread = threading.Thread(target=cleanup)
            thread.daemon = True
            thread.start()
        
        delayed_cleanup()
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"