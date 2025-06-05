#!/usr/bin/env python3
"""
Blend Core Module for Gradient Generator - FIXED VERSION

This module provides the base classes and interfaces for gradient blending functionality,
defining a consistent API for all blending methods. Fixed for divide-by-zero errors.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Optional

# Use standardized import approach with proper exception handling
try:
    # Try relative imports first
    from ..core.gradient import Gradient, ColorStop
    from ..core.color_utils import rgb_to_hsv, hsv_to_rgb, blend_colors
except ImportError:
    try:
        # Fall back to absolute imports if relative fails
        from gradient_generator.core.gradient import Gradient, ColorStop
        from gradient_generator.core.color_utils import rgb_to_hsv, hsv_to_rgb, blend_colors
    except ImportError:
        # As a last resort, try a different relative path
        try:
            from core.gradient import Gradient, ColorStop
            from core.color_utils import rgb_to_hsv, hsv_to_rgb, blend_colors
        except ImportError:
            # Provide an informative error message
            raise ImportError(
                "Could not import required classes from gradient_generator.core. "
                "Please ensure the gradient_generator package is properly installed "
                "or that this file is in the correct location within the package."
            )


class BlendParameter:
    """Class representing an adjustable parameter for gradient blending."""
    
    def __init__(self, name: str, label: str, min_value: float, max_value: float, 
                default_value: float, step: float = 0.1, description: str = ""):
        """
        Initialize a blend parameter.
        
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


class GradientBlender(ABC):
    """Base class for gradient blending methods."""
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the gradient blender.
        
        Args:
            name: Blending method name
            description: Method description
        """
        self.name = name
        self.description = description
        self.parameters = self._create_parameters()
    
    @abstractmethod
    def _create_parameters(self) -> Dict[str, BlendParameter]:
        """
        Create blend-specific parameters.
        
        Returns:
            Dictionary of parameter name to BlendParameter object
        """
        pass
    
    @abstractmethod
    def blend_gradients(self, gradients_with_weights: List[Tuple[Gradient, float]]) -> Gradient:
        """
        Blend multiple gradients using this blending method.
        
        Args:
            gradients_with_weights: List of (gradient, weight) tuples
            
        Returns:
            Blended gradient
        """
        pass
    
    def get_parameter(self, name: str) -> Optional[BlendParameter]:
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
    
    def get_parameter_list(self) -> List[BlendParameter]:
        """Get the list of all parameters."""
        return list(self.parameters.values())
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the blending method.
        
        Returns:
            Dictionary with method metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameter_count": len(self.parameters)
        }
    
    def _create_gradient_with_name(self) -> Gradient:
        """Create a gradient with blend method name."""
        gradient = Gradient()
        gradient._color_stops = []  # Clear default stops
        gradient.set_name(f"Merged Gradient ({self.name})")
        return gradient


class BlendRegistry:
    """Registry for all available gradient blending methods."""
    
    _blenders = {}
    
    @classmethod
    def register(cls, blender_class):
        """
        Register a blender class.
        
        Args:
            blender_class: GradientBlender subclass
            
        Returns:
            The blender class (for decorator use)
        """
        instance = blender_class()
        cls._blenders[instance.name.lower()] = instance
        return blender_class
    
    @classmethod
    def get_blender(cls, name: str) -> Optional[GradientBlender]:
        """
        Get a blender by name.
        
        Args:
            name: Blender name (case insensitive)
            
        Returns:
            GradientBlender instance or None if not found
        """
        return cls._blenders.get(name.lower())
    
    @classmethod
    def get_all_blenders(cls) -> List[GradientBlender]:
        """
        Get all registered blenders.
        
        Returns:
            List of GradientBlender instances
        """
        return list(cls._blenders.values())
    
    @classmethod
    def get_blender_names(cls) -> List[str]:
        """
        Get names of all registered blenders.
        
        Returns:
            List of blender names
        """
        return list(cls._blenders.keys())


# Helper functions for gradient manipulation

def get_interpolated_color_at_position(gradient: Gradient, position: float) -> Tuple[int, int, int]:
    """
    Get the interpolated color at a position in a gradient.
    
    Args:
        gradient: Gradient object
        position: Position in the gradient (0.0-1.0)
        
    Returns:
        RGB color tuple
    """
    return gradient.get_interpolated_color(position)


def create_blended_gradient(
    name: str, 
    color_stops: List[Tuple[float, Tuple[int, int, int]]]
) -> Gradient:
    """
    Create a gradient with the given name and color stops.
    
    Args:
        name: Gradient name
        color_stops: List of (position, color) tuples
        
    Returns:
        New gradient with the given properties
    """
    gradient = Gradient()
    gradient._color_stops = []  # Clear default stops
    
    for position, color in color_stops:
        gradient.add_color_stop(position, color)
    
    gradient.set_name(name)
    return gradient


def distribute_stops_evenly(
    colors: List[Tuple[int, int, int]], 
    count: int = 10
) -> List[Tuple[float, Tuple[int, int, int]]]:
    """
    Distribute colors evenly across the gradient range.
    FIXED VERSION - handles all divide-by-zero cases
    
    Args:
        colors: List of RGB color tuples
        count: Number of stops to create (default: 10)
        
    Returns:
        List of (position, color) tuples
    """
    # Input validation
    if not colors or count <= 0:
        return []
    
    if len(colors) == 1:
        return [(0.5, colors[0])]
    
    if count == 1:
        # Single stop case - return middle color
        mid_idx = len(colors) // 2
        return [(0.5, colors[mid_idx])]
    
    if len(colors) >= count:
        # If we have more colors than stops, sample the colors
        result = []
        for i in range(count):
            # FIXED: Prevent division by zero
            if count > 1:
                idx = i * (len(colors) - 1) // (count - 1)
                position = i / (count - 1)
            else:
                idx = 0
                position = 0.5
            result.append((position, colors[idx]))
        return result
    
    # Create interpolated stops
    result = []
    # FIXED: Ensure segment_count is never zero
    segment_count = max(1, len(colors) - 1)
    
    for i in range(count):
        # FIXED: Prevent division by zero when count = 1
        if count > 1:
            position = i / (count - 1)
        else:
            position = 0.5
        
        # Find the two colors to interpolate between
        segment_size = 1.0 / segment_count
        segment_idx = min(int(position / segment_size), segment_count - 1)
        
        # Calculate the position within the segment (0.0-1.0)
        # FIXED: Prevent division by zero when segment_size = 0
        if segment_size > 0:
            segment_pos = (position - segment_idx * segment_size) / segment_size
        else:
            segment_pos = 0.0
        
        # Get the segment's colors with bounds checking
        color1 = colors[segment_idx]
        color2 = colors[min(segment_idx + 1, len(colors) - 1)]
        
        # Interpolate the color
        r = int(color1[0] * (1 - segment_pos) + color2[0] * segment_pos)
        g = int(color1[1] * (1 - segment_pos) + color2[1] * segment_pos)
        b = int(color1[2] * (1 - segment_pos) + color2[2] * segment_pos)
        
        # Ensure valid color values
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        result.append((position, (r, g, b)))
    
    return result


if __name__ == "__main__":
    # Example usage for testing
    print("Gradient Blending Core Module - FIXED VERSION")
    print("Register blending methods with @BlendRegistry.register decorator")
    
    # Test the fixed distribute_stops_evenly function
    test_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    
    print("\nTesting distribute_stops_evenly fixes:")
    
    # Test edge cases that previously caused division by zero
    try:
        result1 = distribute_stops_evenly(test_colors, 1)  # count = 1
        print(f"✓ count=1: {result1}")
        
        result2 = distribute_stops_evenly([(255, 0, 0)], 5)  # single color
        print(f"✓ single color: {result2}")
        
        result3 = distribute_stops_evenly([], 5)  # empty colors
        print(f"✓ empty colors: {result3}")
        
        result4 = distribute_stops_evenly(test_colors, 0)  # count = 0
        print(f"✓ count=0: {result4}")
        
        print("All edge cases handled successfully!")
        
    except Exception as e:
        print(f"✗ Error in edge case testing: {e}")
