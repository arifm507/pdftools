"""
PDF processing routes
Handles API endpoints for PDF operations like merge, split, etc.
"""
import os
from flask import Blueprint, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from services.pdf_merger import PDFMergerService
from services.pdf_to_word import PDFToWordService
from services.image_to_pdf import ImageToPDFService
from services.pdf_compressor import PDFCompressorService
from services.pdf_splitter import PDFSplitterService
from services.word_to_pdf import WordToPDFService

# Create blueprint for PDF routes
pdf_bp = Blueprint('pdf', __name__, url_prefix='/api/pdf')

@pdf_bp.route('/merge', methods=['POST'])
def merge_pdf():
    """API endpoint for merging PDF files"""
    try:
        # Check if files were uploaded
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files[]')
        output_filename = request.form.get('output_filename', 'merged-document.pdf')
        
        # Initialize PDF merger service
        merger_service = PDFMergerService()
        
        # Merge files
        success, result = merger_service.merge_files(files, output_filename)
        
        if success:
            # Return success with download URL
            download_url = url_for(
                'pdf.download_file', 
                unique_id=result['unique_id'], 
                filename=result['filename']
            )
            
            return jsonify({
                'success': True,
                'message': result['message'],
                'download_url': download_url,
                'filename': result['filename']
            })
        else:
            return jsonify({'error': result}), 400
            
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@pdf_bp.route('/pdf-to-word', methods=['POST'])
def convert_pdf_to_word():
    """API endpoint for converting PDF to Word"""
    try:
        # Check if files were uploaded
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files[]')
        output_filename = request.form.get('output_filename', '')
        
        # Initialize PDF to Word service
        converter_service = PDFToWordService()
        
        # Convert file
        success, result = converter_service.convert_file(files, output_filename)
        
        if success:
            # Return success with download URL
            download_url = url_for(
                'pdf.download_file', 
                unique_id=result['unique_id'], 
                filename=result['filename']
            )
            
            return jsonify({
                'success': True,
                'message': result['message'],
                'download_url': download_url,
                'filename': result['filename']
            })
        else:
            return jsonify({'error': result}), 400
            
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@pdf_bp.route('/image-to-pdf', methods=['POST'])
def convert_images_to_pdf():
    """API endpoint for converting images to PDF"""
    try:
        # Check if files were uploaded
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files[]')
        output_filename = request.form.get('output_filename', '')
        margin_size = request.form.get('margin_size', 'medium')
        
        # Initialize image to PDF service
        converter_service = ImageToPDFService()
        
        # Convert images
        success, result = converter_service.convert_images_to_pdf(files, output_filename, margin_size)
        
        if success:
            # Return success with download URL
            download_url = url_for(
                'pdf.download_file', 
                unique_id=result['unique_id'], 
                filename=result['filename']
            )
            
            return jsonify({
                'success': True,
                'message': result['message'],
                'download_url': download_url,
                'filename': result['filename']
            })
        else:
            return jsonify({'error': result}), 400
            
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@pdf_bp.route('/compress', methods=['POST'])
def compress_pdf():
    """API endpoint for compressing PDF files"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        output_filename = request.form.get('output_filename', '')
        compression_level = request.form.get('compression_level', 'medium')
        
        # Initialize PDF compressor service
        compressor_service = PDFCompressorService()
        
        # Compress PDF
        success, result = compressor_service.compress_pdf(file, output_filename, compression_level)
        
        if success:
            # Return success with download URL and compression stats
            download_url = url_for(
                'pdf.download_file', 
                unique_id=result['unique_id'], 
                filename=result['filename']
            )
            
            return jsonify({
                'success': True,
                'message': result['message'],
                'download_url': download_url,
                'filename': result['filename'],
                'original_size': compressor_service.format_file_size(result['original_size']),
                'compressed_size': compressor_service.format_file_size(result['compressed_size']),
                'compression_ratio': f"{result['compression_ratio']:.1f}%",
                'size_reduction': result['original_size'] - result['compressed_size']
            })
        else:
            return jsonify({'error': result}), 400
            
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@pdf_bp.route('/split', methods=['POST'])
def split_pdf():
    """API endpoint for splitting PDF files"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        output_filename = request.form.get('output_filename', '')
        split_type = request.form.get('split_type', 'pages')
        page_ranges = request.form.getlist('page_ranges[]') if split_type == 'ranges' else None
        
        # Initialize PDF splitter service
        splitter_service = PDFSplitterService()
        
        # Split PDF
        success, result = splitter_service.split_pdf(file, split_type, page_ranges, output_filename)
        
        if success:
            # Return success with download URL
            download_url = url_for(
                'pdf.download_file', 
                unique_id=result['unique_id'], 
                filename=result['filename']
            )
            
            return jsonify({
                'success': True,
                'message': result['message'],
                'download_url': download_url,
                'filename': result['filename'],
                'split_count': result['split_count']
            })
        else:
            return jsonify({'error': result}), 400
            
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@pdf_bp.route('/word-to-pdf', methods=['POST'])
def convert_word_to_pdf():
    """API endpoint for converting Word documents to PDF"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        output_filename = request.form.get('output_filename', '')
        
        # Initialize Word to PDF service
        converter_service = WordToPDFService()
        
        # Convert Word to PDF
        success, result = converter_service.convert_word_to_pdf(file, output_filename)
        
        if success:
            # Return success with download URL
            download_url = url_for(
                'pdf.download_file', 
                unique_id=result['unique_id'], 
                filename=result['filename']
            )
            
            return jsonify({
                'success': True,
                'message': result['message'],
                'download_url': download_url,
                'filename': result['filename']
            })
        else:
            return jsonify({'error': result}), 400
            
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@pdf_bp.route('/download/<unique_id>/<filename>')
def download_file(unique_id, filename):
    """Download processed files (PDF or Word)"""
    try:
        # Security check - ensure filename is safe
        filename = secure_filename(filename)
        
        # Determine file type and appropriate service
        if filename.endswith('.docx'):
            service = PDFToWordService()
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            redirect_endpoint = 'main.pdf_to_word'
        elif filename.startswith('images-to-pdf'):
            service = ImageToPDFService()
            mimetype = 'application/pdf'
            redirect_endpoint = 'main.image_to_pdf'
        elif 'compressed' in filename:
            service = PDFCompressorService()
            mimetype = 'application/pdf'
            redirect_endpoint = 'main.compress_pdf'
        elif 'split' in filename and filename.endswith('.zip'):
            service = PDFSplitterService()
            mimetype = 'application/zip'
            redirect_endpoint = 'main.split_pdf'
        elif filename.startswith('word-to-pdf') or 'word-to-pdf' in filename:
            service = WordToPDFService()
            mimetype = 'application/pdf'
            redirect_endpoint = 'main.word_to_pdf'
        else:
            service = PDFMergerService()
            mimetype = 'application/pdf'
            redirect_endpoint = 'main.merge_pdf'
        
        # Get file path
        file_path = service.get_file_path(unique_id, filename)
        
        if not os.path.exists(file_path):
            flash('File not found or has expired.', 'error')
            return redirect(url_for(redirect_endpoint))
        
        # Schedule cleanup after download
        service.cleanup_processed_file(file_path)
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
        
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('main.pdf_to_word'))