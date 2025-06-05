"""
Utilities Module for Gradient Generator

This module contains utility functions and classes for the gradient generator,
including configuration, logging, and application styling.
"""

from .config import Config
from .logger import get_logger, set_log_level
from .styles import apply_dark_theme, apply_widget_dark_theme, DarkTheme
from .gradient_utils import (
    hsv_to_rgb, rgb_to_hsv, generate_naturalistic_positions,
    generate_color_palette, create_naturalistic_color_stops,
    blend_rgb_colors, blend_hsv_colors, get_hue_name
)