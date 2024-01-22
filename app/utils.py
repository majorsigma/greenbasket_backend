"""Logger for Taskora"""
import logging
import uuid

def generate_uuid():
    """Generates a unique id"""
    return str(uuid.uuid4())

class GBLogger:
    """Custom Logger"""
    log_format = '%(asctime)s - %(levelname)s %(message)s'
    logger = logging.getLogger(__name__)

    log_formatter = logging.Formatter(log_format)

    # Create a custom stream handler
    stream_handler = logging.StreamHandler()

    # Set the formatter for the stream handler
    stream_handler.setFormatter(log_formatter)

    # Add the stream handler to the logger
    logger.addHandler(stream_handler)

    # Set the logging level to DEBUG
    logger.setLevel(logging.DEBUG)

    # Define the color and emoji mappings for each log level
    level_colors = {
            logging.DEBUG: '\033[94m',    # Blue color
            logging.INFO: '\033[92m',     # Green color
            logging.WARNING: '\033[93m',  # Yellow color
            logging.ERROR: '\033[91m',    # Red color
            logging.CRITICAL: '\033[95m'  # Purple color
    }

    level_emojis = {
            logging.DEBUG: '🔵',
            logging.INFO: '✅',
            logging.WARNING: '⚠️',
            logging.ERROR: '❌',
            logging.CRITICAL: '💥'
        }

    def __init__(self, location = None):
        self.location = location
    @staticmethod
    def log(level, message):
        """Log message"""

        color_start = GBLogger.level_colors.get(level, '')
        color_end = '\033[0m'
        emoji = GBLogger.level_emojis.get(level, '')

        log_message = f'{color_start}{emoji} {message}{color_end}'
        GBLogger.logger.log(level, log_message)

    def log_debug(self, message):
        """Log debug message"""
        GBLogger.log(logging.DEBUG, f"<{self.location}> {message}")

    def log_error(self, message):
        """Log error message"""
        GBLogger.log(logging.ERROR, f"<{self.location}> {message}")

    def log_info(self, message):
        """Log info message"""
        GBLogger.log(logging.INFO, f"<{self.location}> {message}")
