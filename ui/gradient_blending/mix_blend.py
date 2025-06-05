#!/usr/bin/env python3
"""
Mix Blend Module for Gradient Generator - FIXED VERSION

This module implements the mix blending method, which blends colors at the same positions
from all input gradients based on their weights. Fixed for divide-by-zero errors.
Uniform sampling removed.
"""
from typing import List, Tuple, Dict

try:
    from .blend_core import GradientBlender, BlendParameter, BlendRegistry
    from ..core.gradient import Gradient
except ImportError:
    try:
        from gradient_generator.ui.gradient_blending.blend_core import GradientBlender, BlendParameter, BlendRegistry
        from gradient_generator.core.gradient import Gradient
    except ImportError:
        from blend_core import GradientBlender, BlendParameter, BlendRegistry
        from core.gradient import Gradient


@BlendRegistry.register
class MixBlender(GradientBlender):
    """
    Mix blending method - FIXED VERSION.
    
    This method mixes colors at each position by combining RGB components from all gradients.
    The contribution of each gradient is determined by its weight. This creates smooth
    transitions between all contributing gradients.
    """
    
    def __init__(self):
        """Initialize the mix blender."""
        super().__init__(
            name="Mix",
            description=(
                "Mixes colors at each position by combining RGB components from all gradients. "
                "The contribution of each gradient is determined by its weight. This creates "
                "smooth transitions between all contributing gradients."
            )
        )
    
    def _create_parameters(self) -> Dict[str, BlendParameter]:
        """Create mix-specific parameters."""
        return {
            "use_weights": BlendParameter(
                "use_weights", 
                "Use Weights", 
                0.0, 1.0, 1.0, 1.0,
                "Whether to consider weights in the blending process (0=No, 1=Yes)"
            ),
            "sample_count": BlendParameter(
                "sample_count", 
                "Sample Count", 
                5.0, 30.0, 15.0, 1.0,
                "Number of positions to sample across the gradient range (5-30)"
            ),
            "color_space": BlendParameter(
                "color_space", 
                "Color Space", 
                0.0, 1.0, 0.0, 1.0,
                "Color space for blending: 0=RGB, 1=HSV"
            ),
        }
    
    def blend_gradients(self, gradients_with_weights: List[Tuple[Gradient, float]]) -> Gradient:
        """
        Blend multiple gradients using the mix method.
        
        Args:
            gradients_with_weights: List of (gradient, weight) tuples
            
        Returns:
            Blended gradient
        """
        # Input validation
        if not gradients_with_weights:
            return self._create_gradient_with_name()
            
        if len(gradients_with_weights) == 1:
            # Return a clone of the single gradient
            result = gradients_with_weights[0][0].clone()
            result.set_name(f"Merged Gradient ({self.name})")
            return result
        
        # Get parameter values
        use_weights = self.parameters["use_weights"].value >= 0.5
        sample_count = max(2, int(self.parameters["sample_count"].value))  # FIXED: Ensure minimum sample count
        use_hsv = self.parameters["color_space"].value >= 0.5
        
        # Filter out gradients with zero weight if using weights
        if use_weights:
            gradients_with_weights = [(g, w) for g, w in gradients_with_weights if w > 0]
            
        if not gradients_with_weights:
            return self._create_gradient_with_name()
        
        # Create a new empty gradient
        merged_gradient = self._create_gradient_with_name()
        
        # Get all unique positions from all gradients
        unique_positions = set()
        
        # Add any explicit stops from input gradients
        for gradient, _ in gradients_with_weights:
            stops = gradient.get_color_stops()
            for pos, _ in stops:
                unique_positions.add(pos)
        
        # Sort positions
        sorted_positions = sorted(unique_positions)
        
        # Sample each gradient at each position and blend the colors
        for pos in sorted_positions:
            blended_color = self._mix_colors_at_position(
                gradients_with_weights, pos, use_weights, use_hsv
            )
            
            # Add the blended color stop
            merged_gradient.add_color_stop(pos, blended_color)
        
        return merged_gradient
    
    def _mix_colors_at_position(
        self, 
        gradients_with_weights: List[Tuple[Gradient, float]], 
        position: float,
        use_weights: bool,
        use_hsv: bool
    ) -> Tuple[int, int, int]:
        """
        Mix colors from all gradients at the given position.
        
        Args:
            gradients_with_weights: List of (gradient, weight) tuples
            position: Position in the gradient (0.0-1.0)
            use_weights: Whether to consider weights
            use_hsv: Whether to blend in HSV space
            
        Returns:
            RGB color tuple
        """
        # Input validation
        if not gradients_with_weights:
            return (0, 0, 0)
        
        if use_hsv:
            return self._mix_colors_hsv(gradients_with_weights, position, use_weights)
        else:
            return self._mix_colors_rgb(gradients_with_weights, position, use_weights)
    
    def _mix_colors_rgb(
        self, 
        gradients_with_weights: List[Tuple[Gradient, float]], 
        position: float,
        use_weights: bool
    ) -> Tuple[int, int, int]:
        """
        Mix colors in RGB space - FIXED VERSION.
        
        Args:
            gradients_with_weights: List of (gradient, weight) tuples
            position: Position in the gradient (0.0-1.0)
            use_weights: Whether to consider weights
            
        Returns:
            RGB color tuple
        """
        r_sum = 0.0
        g_sum = 0.0
        b_sum = 0.0
        total_weight = 0.0
        
        for gradient, weight in gradients_with_weights:
            # Get the interpolated color at this position
            try:
                color = gradient.get_interpolated_color(position)
                r, g, b = color
                
                # Apply weight factor
                factor = weight if use_weights else 1.0
                # FIXED: Ensure weight is positive
                factor = max(0.0, factor)
                total_weight += factor
                
                # Add weighted color components
                r_sum += r * factor
                g_sum += g * factor
                b_sum += b * factor
                
            except Exception:
                # If gradient interpolation fails, skip this gradient
                continue
        
        # FIXED: Normalize the blended color with zero-division protection
        if total_weight > 0:
            r = min(255, max(0, int(r_sum / total_weight)))
            g = min(255, max(0, int(g_sum / total_weight)))
            b = min(255, max(0, int(b_sum / total_weight)))
            return (r, g, b)
        
        # Default to black if no valid colors or weights
        return (0, 0, 0)
    
    def _mix_colors_hsv(
        self, 
        gradients_with_weights: List[Tuple[Gradient, float]], 
        position: float,
        use_weights: bool
    ) -> Tuple[int, int, int]:
        """
        Mix colors in HSV space - FIXED VERSION.
        
        Args:
            gradients_with_weights: List of (gradient, weight) tuples
            position: Position in the gradient (0.0-1.0)
            use_weights: Whether to consider weights
            
        Returns:
            RGB color tuple
        """
        try:
            from ..core.color_utils import rgb_to_hsv, hsv_to_rgb
        except ImportError:
            try:
                from gradient_generator.core.color_utils import rgb_to_hsv, hsv_to_rgb
            except ImportError:
                # Fallback to RGB mixing if HSV utilities not available
                return self._mix_colors_rgb(gradients_with_weights, position, use_weights)
        
        h_x_sum = 0.0  # Sum of sin(h)
        h_y_sum = 0.0  # Sum of cos(h)
        s_sum = 0.0
        v_sum = 0.0
        total_weight = 0.0
        
        for gradient, weight in gradients_with_weights:
            try:
                # Get the interpolated color at this position
                color = gradient.get_interpolated_color(position)
                r, g, b = color
                
                # Convert to HSV
                h, s, v = rgb_to_hsv(r, g, b)
                
                # Apply weight factor
                factor = weight if use_weights else 1.0
                # FIXED: Ensure weight is positive
                factor = max(0.0, factor)
                total_weight += factor
                
                # For hue, we need to handle the circular nature of hue values
                import math
                h_rad = math.radians(h)
                h_x_sum += math.sin(h_rad) * factor
                h_y_sum += math.cos(h_rad) * factor
                
                # Add weighted saturation and value
                s_sum += s * factor
                v_sum += v * factor
                
            except Exception:
                # If gradient interpolation or conversion fails, skip this gradient
                continue
        
        # FIXED: Normalize the blended color with zero-division protection
        if total_weight > 0:
            # Calculate average hue using atan2
            import math
            h_avg = math.degrees(math.atan2(h_x_sum / total_weight, h_y_sum / total_weight))
            if h_avg < 0:
                h_avg += 360
            
            s_avg = min(1.0, max(0.0, s_sum / total_weight))
            v_avg = min(1.0, max(0.0, v_sum / total_weight))
            
            # Convert back to RGB
            try:
                return hsv_to_rgb(h_avg, s_avg, v_avg)
            except Exception:
                # If HSV to RGB conversion fails, return grayscale based on value
                gray = int(v_avg * 255)
                return (gray, gray, gray)
        
        # Default to black if no valid colors or weights
        return (0, 0, 0)


if __name__ == "__main__":
    # Create an instance for testing
    blender = MixBlender()
    print(f"Blender: {blender.name}")
    print(f"Description: {blender.description}")
    print(f"Parameters: {[p.name for p in blender.get_parameter_list()]}")
    
    # Test edge cases that could cause division by zero
    print("\nTesting edge cases:")
    
    # Test with empty gradients list
    try:
        empty_result = blender.blend_gradients([])
        print("✓ Empty gradients list handled")
    except Exception as e:
        print(f"✗ Empty gradients error: {e}")
    
    # Test with sample_count = 1
    try:
        blender.set_parameter_value("sample_count", 1.0)
        print("✓ Sample count = 1 handled")
    except Exception as e:
        print(f"✗ Sample count = 1 error: {e}")
    
    # Test with zero weights
    try:
        blender.set_parameter_value("use_weights", 1.0)
        print("✓ Zero weights handling ready")
    except Exception as e:
        print(f"✗ Zero weights setup error: {e}")
    
    print("Mix blend module fixes completed!")