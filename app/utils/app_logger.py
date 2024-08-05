#InventoryHDataHub/app/utils/app_logger.py
import logging
from logging.handlers import RotatingFileHandler
import os

class AppLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.configure_logger()

    def configure_logger(self):
        # Set the log level to INFO
        self.logger.setLevel(logging.INFO)

        # File handler with rotation
        log_directory = os.getenv('LOG_DIR', '/var/log/IDHLogs')
        try:
            if not os.path.exists(log_directory):
                os.makedirs(log_directory, exist_ok=True)  # Safe to use in concurrent environ
        except Exception as e:
            print(f"Failed to create log directory {log_directory}: {e}")
             # Fallback to a directory that you are sure the application can write to
            log_directory = '/tmp'

        # Attempt to set up a file handler
        try:
            log_file_path = os.path.join(log_directory, 'inventory_data_hub.log')
            file_handler = RotatingFileHandler(log_file_path, maxBytes=10485760, backupCount=5)
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            
            print(f"Failed to set up file handler for {log_file_path}: {e}")
            # Consider what to do if the log file can't be created - perhaps fall back to console logging only
        # Console handler for additional output in the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger
