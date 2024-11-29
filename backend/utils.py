import os
import logging
from datetime import datetime

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'json'}

# Setup logging configuration
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def validate_file_type(filename):
    """
    Validates if the file has an allowed extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_time():
    """
    Returns the current time as a formatted string.
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def log_event(message):
    """
    Logs a custom event message to app.log.
    """
    logging.info(message)

def log_upload(filename):
    """
    Logs a file upload event with the filename.
    """
    log_event(f'File uploaded: {filename}')

def handle_file_upload(file, upload_folder='uploads'):
    """
    Saves the uploaded file to the specified upload folder.
    Ensures the folder exists before saving.
    """
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)  # Create the folder if it doesn't exist
    
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)
    return file_path

def log_error(error_message):
    """
    Logs an error message to app.log.
    """
    logging.error(error_message)

