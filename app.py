"""
Main application entry point for PDF Tools website
"""
from app_factory import create_app

# Create application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)