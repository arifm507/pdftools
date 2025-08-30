"""
Configuration settings for the PDF Tools website
"""
import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # PDF processing settings
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # File cleanup settings
    CLEANUP_DELAY = 10  # seconds to wait before cleaning up files after download
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    @staticmethod
    def init_app(app):
        """Initialize application with config"""
        # Ensure upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENV = 'production'
    
    # In production, use environment variables or fallback to base config
    SECRET_KEY = os.environ.get('SECRET_KEY') or Config.SECRET_KEY

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    UPLOAD_FOLDER = 'test_uploads'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}