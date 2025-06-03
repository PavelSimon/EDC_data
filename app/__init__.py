from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import os
import sys # Added for stderr output in custom handler
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()

# Custom Handler Definition
class GracefulRotatingFileHandler(RotatingFileHandler):
    def rotate(self, source, dest):
        """
        Override the default rotate method to catch PermissionError on Windows
        and gracefully skip rotation if the file is locked.
        `source` is the current log file name.
        `dest` is the target rotated log file name (e.g., app.log.1).
        """
        try:
            super().rotate(source, dest)
        except PermissionError as e:
            # Check if it's the specific Windows error for file locking
            if hasattr(e, 'winerror') and e.winerror == 32:
                sys.stderr.write(f"Log rotation skipped for {source} due to lock: {e}\\n")
            else:
                raise # Re-raise other PermissionErrors

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',  # Point to templates in root directory
                static_folder='../static')       # Point to static in root directory
    
    # Configure logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Set up file handler
    file_handler = GracefulRotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    console_handler.setLevel(logging.INFO)
    
    # Configure app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('EDC Data Scraper startup')
    
    # Configure other loggers
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    logging.getLogger('werkzeug').addHandler(file_handler)
    
    # Configure SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edc_data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
