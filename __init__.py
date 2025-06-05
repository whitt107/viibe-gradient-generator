"""
JWildfire Gradient Generator

A Python application for creating and editing gradients compatible with JWildfire.
Supports MAP and UGR file formats.
"""

# Version and metadata
__version__ = "1.0.0"
__author__ = "Gradient Generator Team"
__license__ = "MIT"

# Import core modules
from .core import Gradient
from .core.color_utils import rgb_to_hsv, hsv_to_rgb
from .core.image_analyzer import ImageAnalyzer, create_gradient_from_image_path

# Import UI modules
from .ui import MainWindow

# Import export modules
from .export import ImageExporter, save_map_format, save_ugr_format

# Import utility modules
from .utils import Config, get_logger
