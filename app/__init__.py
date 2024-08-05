#/home/jawwad/InventoryDataHub/app/__init__
import os
import secrets
from flask import Flask,session
from datetime import timedelta
from .controllers.main_controller import main_blueprint
from .controllers.sfp_controller import sfp_blueprint
from .controllers.card_controller import card_blueprint  # Corrected impo
from .controllers.shelf_fan_controller import shelf_fan_blueprint
from .controllers.power_controller import power_blueprint
from .controllers.flash_memory_controller import flash_memory_blueprint
from .controllers.summary_controller import summary_blueprint

from .utils.cleanup_manager import CleanupManager
from .utils.app_logger import AppLogger

import tempfile

def get_or_create_secret_key():
    # Determine the base directory dynamically
    base_dir = os.path.abspath(os.path.dirname(__file__))  # Gets the directory of the current __init__.py file
    secret_key_path = os.path.join(base_dir, 'secret', 'secret.key')  # Path to the secret.key file

    if not os.path.exists(secret_key_path):
        # Generate and save the secret key if it does not exist
        secret_key = secrets.token_urlsafe(16)  # Generates a 16-byte (128-bit) key
        os.makedirs(os.path.dirname(secret_key_path), exist_ok=True)  # Ensure the directory exists
        with open(secret_key_path, 'w') as file:
            file.write(secret_key)  # Write the generated key to a file
    else:
        # Read the existing secret key
        with open(secret_key_path, 'r') as file:
            secret_key = file.read().strip()  # Read and strip any extra whitespace
    return secret_key

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = get_or_create_secret_key()  # Set the secret key from the file or newly generated
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)  # Session timeout set to 2 hours
    app.config['temp_dir'] = os.getenv('APP_TEMP_DIR', tempfile.gettempdir())
    logger=AppLogger("Flask App Logger").get_logger()
    logger.info("Creating the Flask Application")
  
    cleanup_manager = CleanupManager()  # Initialize the cleanup manager
    logger.info("Checking Session Expiry")
    
    @app.before_request
    def handle_potential_cleanup():
        
        print("This runs before every request.")
        """Attempt to clean up if the session is new, implying potential expiration of an old session."""
        if not session.get('initialized', False):
            cleanup_manager.cleanup_files()  # Cleanup logic for potentially expired sessions
            session['initialized'] = True  # Mark session as initialized
            logger.info("Session initialized and cleanup performed")

    logger.info("Registering BluePrint")
    app.register_blueprint(main_blueprint)  # Register the blueprint
    app.register_blueprint(sfp_blueprint, url_prefix='/reports')
    app.register_blueprint(card_blueprint, url_prefix='/reports')
    app.register_blueprint(shelf_fan_blueprint,url_prefix='/reports')
    app.register_blueprint(power_blueprint, url_prefix='/reports')
    app.register_blueprint(flash_memory_blueprint,url_prefix='/reports')
    app.register_blueprint(summary_blueprint,url_prefix='/reports')    
    
    logger.info("Flask app created with SECRET_KEY and main_blueprint registered.")
    print("Flask app created with SECRET_KEY and main_blueprint registered.")  # Debug statement
    return app
