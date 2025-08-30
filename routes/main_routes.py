"""
Main application routes
Handles general pages like home, tools overview, etc.
"""
from flask import Blueprint, render_template

# Create blueprint for main routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Home page"""
    return render_template('home.html')

@main_bp.route('/tools')
def tools():
    """Tools overview page"""
    return render_template('tools.html')

@main_bp.route('/merge-pdf')
def merge_pdf():
    """PDF merge page"""
    return render_template('merge_pdf.html')

@main_bp.route('/split-pdf')
def split_pdf():
    """PDF split page"""
    return render_template('split_pdf.html')

@main_bp.route('/compress-pdf')
def compress_pdf():
    """PDF compress page"""
    return render_template('compress_pdf.html')

@main_bp.route('/image-to-pdf')
def image_to_pdf():
    """Image to PDF conversion page"""
    return render_template('image_to_pdf.html')

@main_bp.route('/pdf-to-word')
def pdf_to_word():
    """PDF to Word conversion page"""
    return render_template('pdf_to_word.html')

@main_bp.route('/word-to-pdf')
def word_to_pdf():
    """Word to PDF conversion page"""
    return render_template('word_to_pdf.html')