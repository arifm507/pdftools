"""
Utility functions for the PDF Tools website
"""
import os
import uuid
import threading
import time
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def generate_unique_id():
    """Generate a unique identifier"""
    return str(uuid.uuid4())

def create_temp_directory(base_path, unique_id):
    """Create a temporary directory for file processing"""
    temp_dir = os.path.join(base_path, unique_id)
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def cleanup_files(file_paths, delay=0):
    """Clean up files and directories with optional delay"""
    def delayed_cleanup():
        if delay > 0:
            time.sleep(delay)
        
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        # Remove directory if empty
                        if not os.listdir(file_path):
                            os.rmdir(file_path)
            except Exception:
                # Silently ignore cleanup errors
                pass
    
    if delay > 0:
        # Run cleanup in background thread
        cleanup_thread = threading.Thread(target=delayed_cleanup)
        cleanup_thread.daemon = True
        cleanup_thread.start()
    else:
        # Run cleanup immediately
        delayed_cleanup()

def save_uploaded_files(files, temp_dir):
    """Save uploaded files to temporary directory and return file paths"""
    temp_files = []
    for i, file in enumerate(files):
        if file and file.filename:
            temp_filename = f"temp_{i}_{secure_filename(file.filename)}"
            temp_filepath = os.path.join(temp_dir, temp_filename)
            file.save(temp_filepath)
            temp_files.append(temp_filepath)
    return temp_files

def validate_pdf_files(files, min_files=2):
    """Validate uploaded files for PDF processing"""
    if not files:
        return False, "No files uploaded"
    
    valid_files = [f for f in files if f and f.filename and allowed_file(f.filename)]
    
    if len(valid_files) < min_files:
        return False, f"At least {min_files} valid PDF files are required"
    
    return True, valid_files

def secure_output_filename(filename, default_name="output.pdf"):
    """Ensure output filename is secure and has proper extension"""
    if not filename:
        filename = default_name
    
    if not filename.endswith('.pdf'):
        filename += '.pdf'
    
    return secure_filename(filename)