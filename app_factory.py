"""
Application factory for creating Flask app instances
"""
import os
from flask import Flask
from config import config

def create_app(config_name=None):
    """
    Create and configure Flask application instance
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Register blueprints
    from routes.main_routes import main_bp
    from routes.pdf_routes import pdf_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(pdf_bp)
    
    return app