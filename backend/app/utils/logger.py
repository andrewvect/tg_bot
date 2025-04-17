import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from app.core.config import settings

# ANSI color codes
COLORS = {
    "DEBUG": "\033[94m",  # Blue
    "INFO": "\033[92m",  # Green
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",  # Red
    "CRITICAL": "\033[95m",  # Magenta
    "RESET": "\033[0m",  # Reset color
}


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        # Save original levelname
        orig_levelname = record.levelname
        # Add color to the levelname
        record.levelname = (
            f"{COLORS.get(record.levelname, '')}{record.levelname}{COLORS['RESET']}"
        )
        # Format the message
        result = super().format(record)
        # Restore original levelname
        record.levelname = orig_levelname
        return result


def setup_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create formatter
    formatter = ColoredFormatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Add formatter to handler
    console_handler.setFormatter(formatter)

    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(console_handler)

        # Add file logging in production environment
        if settings.ENVIRONMENT == "production":
            # Create logs directory if it doesn't exist
            log_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs"
            )
            os.makedirs(log_dir, exist_ok=True)

            # Set up rotating file handler (100MB max size)
            log_file = os.path.join(log_dir, f"{name}.log")
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=100 * 1024 * 1024,  # 100MB
                backupCount=5,  # Keep 5 backup files
                encoding="utf-8",
            )
            file_handler.setLevel(max(logging.INFO, level))

            # Create plain formatter for file (without colors)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)

            # Add file handler to logger
            logger.addHandler(file_handler)

    return logger


# Create default logger instance
logger = setup_logger("default")
