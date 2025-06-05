#!/usr/bin/env python3
"""
Theme Gradient Generator Base Module

This module provides the base class for theme-based gradient generators.
It defines the common interface and functionality for all theme generators.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Any

# Try multiple import paths to handle different execution contexts
try:
    from gradient_generator.core.gradient import Gradient, ColorStop
    from gradient_generator.core.color_utils import rgb_to_hsv, hsv_to_rgb
except ImportError:
    try:
        from core.gradient import Gradient, ColorStop
        from core.color_utils import rgb_to_hsv, hsv_to_rgb
    except ImportError:
        import sys, os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
        from gradient_generator.core.gradient import Gradient, ColorStop
        from gradient_generator.core.color_utils import rgb_to_hsv, hsv_to_rgb


class ThemeParameter:
    """Class representing an adjustable parameter for a theme generator."""
    
    def __init__(self, name: str, label: str, min_value: float, max_value: float, 
                default_value: float, step: float = 0.1, description: str = ""):
        """
        Initialize a theme parameter.
        
        Args:
            name: Parameter identifier
            label: Display name for the UI
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            default_value: Initial value
            step: Step size for adjustments
            description: Parameter description for tooltips
        """
        self.name = name
        self.label = label
        self.min_value = min_value
        self.max_value = max_value
        self.default_value = default_value
        self.value = default_value
        self.step = step
        self.description = description
    
    def set_value(self, value: float) -> None:
        """Set parameter value, clamping to valid range."""
        self.value = max(self.min_value, min(self.max_value, value))
    
    def reset(self) -> None:
        """Reset to default value."""
        self.value = self.default_value


class ThemeGradientGenerator(ABC):
    """Base class for theme-based gradient generators."""
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the theme generator.
        
        Args:
            name: Theme name
            description: Theme description
        """
        self.name = name
        self.description = description
        self.parameters = self._create_parameters()
    
    @abstractmethod
    def _create_parameters(self) -> Dict[str, ThemeParameter]:
        """
        Create theme-specific parameters.
        
        Returns:
            Dictionary of parameter name to ThemeParameter object
        """
        pass
    
    @abstractmethod
    def generate_gradient(self) -> Gradient:
        """
        Generate a gradient based on the current parameter values.
        
        Returns:
            Gradient object
        """
        pass
    
    def get_parameter(self, name: str) -> ThemeParameter:
        """Get a parameter by name."""
        return self.parameters.get(name)
    
    def set_parameter_value(self, name: str, value: float) -> None:
        """Set a parameter value."""
        if name in self.parameters:
            self.parameters[name].set_value(value)
    
    def get_parameter_value(self, name: str) -> float:
        """Get a parameter value."""
        if name in self.parameters:
            return self.parameters[name].value
        return 0.0
    
    def reset_parameters(self) -> None:
        """Reset all parameters to their default values."""
        for param in self.parameters.values():
            param.reset()
    
    def get_parameter_list(self) -> List[ThemeParameter]:
        """Get the list of all parameters."""
        return list(self.parameters.values())
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the theme.
        
        Returns:
            Dictionary with theme metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameter_count": len(self.parameters)
        }
    
    def _create_gradient_with_name(self) -> Gradient:
        """Create a gradient with theme name."""
        gradient = Gradient()
        gradient._color_stops = []  # Clear default stops
        gradient.set_name(f"{self.name} Theme Gradient")
        return gradient


# Helper functions for theme implementation

def create_color_ramp(colors: List[Tuple[int, int, int]], stop_count: int = 10) -> List[Tuple[float, Tuple[int, int, int]]]:
    """
    Create a smooth color ramp from a list of colors.
    
    Args:
        colors: List of RGB color tuples
        stop_count: Total number of color stops to generate
        
    Returns:
        List of (position, color) tuples
    """
    if not colors:
        return []
    
    if len(colors) == 1:
        return [(0.0, colors[0])]
    
    # Calculate segment size
    segment_count = len(colors) - 1
    stops_per_segment = max(1, stop_count // segment_count)
    
    # Generate color stops
    color_stops = []
    
    for i in range(segment_count):
        start_color = colors[i]
        end_color = colors[i+1]
        
        # Start position of segment
        start_pos = i / segment_count
        end_pos = (i + 1) / segment_count
        
        # Generate stops for this segment
        for j in range(stops_per_segment):
            if i == segment_count - 1 and j == stops_per_segment - 1:
                # Last segment, last stop
                position = 1.0
                color = end_color
            else:
                # Calculate position and interpolate color
                position = start_pos + (end_pos - start_pos) * j / stops_per_segment
                blend_factor = j / stops_per_segment
                
                # Interpolate RGB values
                r = int(start_color[0] * (1 - blend_factor) + end_color[0] * blend_factor)
                g = int(start_color[1] * (1 - blend_factor) + end_color[1] * blend_factor)
                b = int(start_color[2] * (1 - blend_factor) + end_color[2] * blend_factor)
                
                color = (r, g, b)
            
            color_stops.append((position, color))
    
    # Add the final color at position 1.0 if not already there
    if color_stops[-1][0] < 1.0:
        color_stops.append((1.0, colors[-1]))
    
    return color_stops


def adjust_color_brightness(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """
    Adjust brightness of a color.
    
    Args:
        color: RGB color tuple
        factor: Brightness factor (1.0 = no change)
        
    Returns:
        RGB color tuple with adjusted brightness
    """
    r, g, b = color
    h, s, v = rgb_to_hsv(r, g, b)
    v = max(0.0, min(1.0, v * factor))
    return hsv_to_rgb(h, s, v)


def adjust_color_saturation(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """
    Adjust saturation of a color.
    
    Args:
        color: RGB color tuple
        factor: Saturation factor (1.0 = no change)
        
    Returns:
        RGB color tuple with adjusted saturation
    """
    r, g, b = color
    h, s, v = rgb_to_hsv(r, g, b)
    s = max(0.0, min(1.0, s * factor))
    return hsv_to_rgb(h, s, v)


def rotate_color_hue(color: Tuple[int, int, int], degrees: float) -> Tuple[int, int, int]:
    """
    Rotate the hue of a color.
    
    Args:
        color: RGB color tuple
        degrees: Hue rotation in degrees
        
    Returns:
        RGB color tuple with rotated hue
    """
    r, g, b = color
    h, s, v = rgb_to_hsv(r, g, b)
    h = (h + degrees) % 360
    return hsv_to_rgb(h, s, v)
