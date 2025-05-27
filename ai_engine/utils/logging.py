import logging
import os
from datetime import datetime

DATETIME = datetime.now().strftime('%Y-%m-%d-%H%M%S')
LOG_FILE = f'saves/log/project-{DATETIME}.log'

def setup_logger(name, log_file=LOG_FILE, level=logging.DEBUG, console=True):
    """Set up a logger with both file and console output.

    Args:
        name (str): Name of the logger
        log_file (str): Path to the log file (default: LOG_FILE)
        level (int): Logging level (default: logging.DEBUG)
        console (bool): Whether to output logs to console (default: True)

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create log directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create logger instance with specified name
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicate logging
    if logger.hasHandlers():
        logger.handlers.clear()

    # Set up file handler for logging to file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    # Define log format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Set up console handler if console output is enabled
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

logger = setup_logger('Neuroplex_Logger', log_file=LOG_FILE)
