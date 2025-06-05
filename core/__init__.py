"""
Core Module for Gradient Generator

This module contains the core functionality for the gradient generator,
including gradient representation, color utilities, and image analysis.
"""

from .gradient import Gradient, ColorStop
from .gradient_metadata import GradientMetadata
from .gradient_seamless import SeamlessBlending
from .gradient_presets import GradientPresets
from .color_utils import (
    rgb_to_hsv, hsv_to_rgb, rgb_to_hex, hex_to_rgb, 
    blend_colors, interpolate_colors, adjust_brightness, 
    adjust_saturation, rotate_hue, complementary_color,
    triadic_colors, analogous_colors
)
from .image_analyzer import ImageAnalyzer, create_gradient_from_image_path

__all__ = [
    # Gradient classes
    'Gradient', 'ColorStop',
    'GradientMetadata', 'SeamlessBlending', 'GradientPresets',
    
    # Color utilities
    'rgb_to_hsv', 'hsv_to_rgb', 'rgb_to_hex', 'hex_to_rgb',
    'blend_colors', 'interpolate_colors', 'adjust_brightness',
    'adjust_saturation', 'rotate_hue', 'complementary_color',
    'triadic_colors', 'analogous_colors',
    
    # Image analysis
    'ImageAnalyzer', 'create_gradient_from_image_path'
]
