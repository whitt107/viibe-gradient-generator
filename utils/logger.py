#!/usr/bin/env python3
"""
Logger Module for Gradient Generator

This module implements logging functionality for the application,
allowing consistent error reporting and debugging.
"""
import os
import logging
import datetime
import traceback


class Logger:
    """Application logger for Gradient Generator."""
    
    def __init__(self, log_level=logging.INFO, log_to_file=True):
        """
        Initialize the logger.
        
        Args:
            log_level: Logging level (default: INFO)
            log_to_file: Whether to log to file (default: True)
        """
        self.logger = logging.getLogger("GradientGenerator")
        self.logger.setLevel(log_level)
        
        # Clear any existing handlers
        self.logger.handlers = []
        
        # Create console handler
        console = logging.StreamHandler()
        console.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add formatter to console handler
        console.setFormatter(formatter)
        
        # Add console handler to logger
        self.logger.addHandler(console)
        
        # Add file handler if enabled
        if log_to_file:
            self._add_file_handler()
    
    def _add_file_handler(self):
        """Add a file handler to the logger."""
        # Create logs directory in user's home directory
        log_dir = os.path.expanduser("~/.gradient_generator/logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log file name with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"gradient_generator_{timestamp}.log")
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        
        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add formatter to file handler
        file_handler.setFormatter(formatter)
        
        # Add file handler to logger
        self.logger.addHandler(file_handler)
        
        self.logger.info(f"Log file created at: {log_file}")
    
    def debug(self, message):
        """Log a debug message."""
        self.logger.debug(message)
    
    def info(self, message):
        """Log an info message."""
        self.logger.info(message)
    
    def warning(self, message):
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message, exc_info=None):
        """
        Log an error message.
        
        Args:
            message: Error message
            exc_info: Exception information (default: None)
        """
        if exc_info:
            self.logger.error(f"{message}\n{traceback.format_exc()}")
        else:
            self.logger.error(message)
    
    def critical(self, message, exc_info=None):
        """
        Log a critical error message.
        
        Args:
            message: Critical error message
            exc_info: Exception information (default: None)
        """
        if exc_info:
            self.logger.critical(f"{message}\n{traceback.format_exc()}")
        else:
            self.logger.critical(message)
    
    def log_exception(self, message="An exception occurred"):
        """
        Log an exception with traceback.
        
        Args:
            message: Message prefix (default: "An exception occurred")
        """
        self.logger.exception(message)


# Create a global logger instance
logger = Logger()


def get_logger():
    """
    Get the logger instance.
    
    Returns:
        Logger instance
    """
    return logger


def set_log_level(level):
    """
    Set the log level for all handlers.
    
    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO)
    """
    logger.logger.setLevel(level)
    
    for handler in logger.logger.handlers:
        handler.setLevel(level)
