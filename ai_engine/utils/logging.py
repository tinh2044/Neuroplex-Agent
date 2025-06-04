import logging
import os
from datetime import datetime

DATETIME = datetime.now().strftime('%Y-%m-%d-%H%M%S')
LOG_FILE = f'saves/log/project-{DATETIME}.log'

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset color
    }
    
    def format(self, record):
        # Get the original formatted message
        log_message = super().format(record)
        
        # Add color based on log level
        if record.levelname in self.COLORS:
            log_message = f"{self.COLORS[record.levelname]}{log_message}{self.COLORS['RESET']}"
        
        return log_message

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

    # Set up file handler for logging to file (without colors)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Set up console handler with colors if console output is enabled
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # Use colored formatter for console output
        console_formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger

# Alternative using colorlog library (you need to install it: pip install colorlog)
def setup_logger_with_colorlog(name, log_file=LOG_FILE, level=logging.DEBUG, console=True):
    """Alternative logger setup using colorlog library"""
    try:
        import colorlog
        
        # Create log directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        # Create logger instance with specified name
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Clear existing handlers to avoid duplicate logging
        if logger.hasHandlers():
            logger.handlers.clear()

        # Set up file handler for logging to file (without colors)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Set up console handler with colors if console output is enabled
        if console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            
            # Use colorlog formatter for colored console output
            console_formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'bold_red',
                }
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        return logger
    
    except ImportError:
        print("colorlog library not found. Install it with: pip install colorlog")
        return setup_logger(name, log_file, level, console)

# Usage examples:
logger = setup_logger('Neuroplex_Logger', log_file=LOG_FILE)

# Or use the colorlog version:
# logger = setup_logger_with_colorlog('Neuroplex_Logger', log_file=LOG_FILE)

# Test the colored logging
if __name__ == "__main__":
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")