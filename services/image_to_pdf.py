"""
Image to PDF conversion service
Handles converting multiple image files to a single PDF document
"""
import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from config import config

class ImageToPDFService:
    """Service for converting images to PDF"""
    
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'}
    
    # Margin settings in points (72 points = 1 inch)
    MARGIN_SETTINGS = {
        'none': 0,      # No margin
        'small': 36,    # 0.5 inch
        'medium': 72,   # 1 inch
        'large': 144    # 2 inches
    }
    
    def __init__(self):
        """Initialize the service with upload directory"""
        self.upload_folder = config['default'].UPLOAD_FOLDER
        self.ensure_upload_directory()
    
    def ensure_upload_directory(self):
        """Ensure upload directory exists"""
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
    
    def is_allowed_file(self, filename):
        """Check if file extension is allowed"""
        return ('.' in filename and 
                filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS)
    
    def convert_images_to_pdf(self, files, output_filename=None, margin_size='medium'):
        """
        Convert multiple image files to a single PDF
        
        Args:
            files: List of uploaded files
            output_filename: Optional custom output filename
            margin_size: Margin size ('small', 'medium', 'large')
            
        Returns:
            tuple: (success: bool, result: dict or error_message)
        """
        try:
            # Validate files
            if not files or len(files) == 0:
                return False, "No files provided"
            
            valid_files = []
            for file in files:
                if file and file.filename and self.is_allowed_file(file.filename):
                    valid_files.append(file)
            
            if not valid_files:
                return False, "No valid image files found. Supported formats: " + ", ".join(self.ALLOWED_EXTENSIONS)
            
            # Generate unique identifier and filename
            unique_id = str(uuid.uuid4())
            if not output_filename or not output_filename.strip():
                output_filename = f"images-to-pdf-{unique_id[:8]}.pdf"
            elif not output_filename.endswith('.pdf'):
                output_filename += '.pdf'
            
            # Validate margin size
            if margin_size not in self.MARGIN_SETTINGS:
                margin_size = 'medium'  # Default to medium if invalid
            
            margin = self.MARGIN_SETTINGS[margin_size]
            
            # Secure the filename
            output_filename = secure_filename(output_filename)
            output_path = os.path.join(self.upload_folder, f"{unique_id}_{output_filename}")
            
            # Process images and convert to PDF with margins
            success = self._convert_images_with_margins(valid_files, output_path, margin, unique_id)
            
            if not success:
                return False, "Failed to process images"
            
            return True, {
                'message': f'Successfully converted {len(valid_files)} images to PDF',
                'filename': output_filename,
                'unique_id': unique_id,
                'file_path': output_path
            }
            
        except Exception as e:
            return False, f"Conversion failed: {str(e)}"
    
    def _convert_images_with_margins(self, files, output_path, margin, unique_id):
        """
        Convert images to PDF with specified margins using reportlab
        
        Args:
            files: List of uploaded files
            output_path: Path to save the PDF
            margin: Margin size in points
            unique_id: Unique identifier for temp files
            
        Returns:
            bool: Success status
        """
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.utils import ImageReader
            import io
            
            # Create PDF canvas
            c = canvas.Canvas(output_path, pagesize=A4)
            page_width, page_height = A4
            
            # Calculate available space for image
            available_width = page_width - (2 * margin)
            available_height = page_height - (2 * margin)
            
            temp_files = []
            
            for file in files:
                # Save temp file
                temp_filename = f"temp_{unique_id}_{secure_filename(file.filename)}"
                temp_path = os.path.join(self.upload_folder, temp_filename)
                file.save(temp_path)
                temp_files.append(temp_path)
                
                try:
                    # Open and process image
                    img = Image.open(temp_path)
                    
                    # Convert to RGB if necessary
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Get image dimensions
                    img_width, img_height = img.size
                    
                    if margin == 0:
                        # No margin: fill entire page
                        final_width = page_width
                        final_height = page_height
                        x_pos = 0
                        y_pos = 0
                    else:
                        # With margin: scale to fit within available space while maintaining aspect ratio
                        width_ratio = available_width / img_width
                        height_ratio = available_height / img_height
                        scale_ratio = min(width_ratio, height_ratio)
                        
                        # Calculate final dimensions
                        final_width = img_width * scale_ratio
                        final_height = img_height * scale_ratio
                        
                        # Calculate position to center image
                        x_pos = margin + (available_width - final_width) / 2
                        y_pos = margin + (available_height - final_height) / 2
                    
                    # Convert PIL image to bytes for reportlab
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG', quality=95)
                    img_byte_arr.seek(0)
                    
                    # Draw image on canvas
                    c.drawImage(ImageReader(img_byte_arr), x_pos, y_pos, 
                              width=final_width, height=final_height)
                    
                    img.close()
                    
                    # Add new page for next image (except for the last one)
                    if file != files[-1]:
                        c.showPage()
                        
                except Exception as e:
                    # Clean up on error
                    for temp_file in temp_files:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    return False
            
            # Save the PDF
            c.save()
            
            # Clean up temp files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            return True
            
        except ImportError:
            # Fallback to PIL method if reportlab is not available
            return self._convert_images_simple(files, output_path, unique_id)
        except Exception as e:
            return False
    
    def _convert_images_simple(self, files, output_path, unique_id):
        """
        Fallback method using PIL for basic conversion without margins
        
        Args:
            files: List of uploaded files
            output_path: Path to save the PDF
            unique_id: Unique identifier for temp files
            
        Returns:
            bool: Success status
        """
        try:
            images = []
            temp_files = []
            
            for file in files:
                # Save temp file
                temp_filename = f"temp_{unique_id}_{secure_filename(file.filename)}"
                temp_path = os.path.join(self.upload_folder, temp_filename)
                file.save(temp_path)
                temp_files.append(temp_path)
                
                # Open and process image
                try:
                    img = Image.open(temp_path)
                    
                    # Convert to RGB if necessary (for PNG with transparency, etc.)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    images.append(img)
                except Exception as e:
                    # Clean up on error
                    for temp_file in temp_files:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    return False
            
            if not images:
                # Clean up temp files
                for temp_file in temp_files:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                return False
            
            # Convert to PDF
            if len(images) == 1:
                images[0].save(output_path, "PDF")
            else:
                images[0].save(output_path, "PDF", save_all=True, append_images=images[1:])
            
            # Clean up temp files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            # Close images
            for img in images:
                img.close()
            
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