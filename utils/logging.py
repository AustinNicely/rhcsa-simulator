"""
Logging configuration for RHCSA Simulator.
"""

import logging
import sys
from pathlib import Path
from config import settings


def setup_logging(log_level=None, log_file=None):
    """
    Set up logging configuration for the application.

    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (Path): Path to log file (default: from settings)

    Returns:
        logging.Logger: Configured root logger
    """
    if log_level is None:
        log_level = settings.LOG_LEVEL

    if log_file is None:
        log_file = settings.LOG_FILE

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers = []

    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler (all levels)
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            settings.LOG_FORMAT,
            datefmt=settings.LOG_DATE_FORMAT
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create log file: {e}")

    return logger


def get_logger(name):
    """
    Get a logger for a specific module.

    Args:
        name (str): Logger name (usually __name__)

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)
