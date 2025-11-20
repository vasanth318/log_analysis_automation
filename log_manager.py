import logging
import constants

# ---------- INITIALIZATION (runs automatically when module loads) ----------
logger = logging.getLogger("LogAnalyzer")
logger.setLevel(logging.INFO)

# Create default file handler
default_handler = logging.FileHandler(constants.LOG_FILENAME)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    "%Y-%m-%d %H:%M:%S"
)
default_handler.setFormatter(formatter)
logger.addHandler(default_handler)
# --------------------------------------------------------------------------


def get_logger():
    """Return the logger instance."""
    return logger


def set_log_filename(filename: str):
    """
    Change the file name dynamically.
    """
    global logger

    # Remove old FileHandler
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
            handler.close()

    # Create new handler
    new_handler = logging.FileHandler(filename)
    new_handler.setFormatter(formatter)
    logger.addHandler(new_handler)

    # Update constants
    constants.LOG_FILENAME = filename
