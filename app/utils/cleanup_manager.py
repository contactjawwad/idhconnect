import os
import logging
import tempfile
class CleanupManager:
    def __init__(self):
        # Fetch the directory from environment variable or use the system default temporary directory
        self.directory = os.getenv('APP_TEMP_DIR', tempfile.gettempdir())

    def cleanup_files(self):
        """Remove Excel and CSV files in the specified directory."""
        extensions = ['.csv', '.xls', '.xlsx']  # Targeted file extensions
        for filename in os.listdir(self.directory):
            file_path = os.path.join(self.directory, filename)
            if any(file_path.endswith(ext) for ext in extensions):
                try:
                    if os.path.isfile(file_path):  # Ensure it's a file, not a directory
                        os.remove(file_path)
                        logging.info(f"Deleted file {file_path}")
                except Exception as e:
                    logging.error(f"Failed to delete {file_path}. Reason: {e}")
