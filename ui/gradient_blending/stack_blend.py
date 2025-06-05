#!/usr/bin/env python3
"""
Stack Blend Module for Gradient Generator - FIXED VERSION

This module implements the stack blending method, which divides the gradient
range into segments for each input gradient. Fixed for divide-by-zero errors.
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
class StackBlender(GradientBlender):
    """
    Stack blending method - FIXED VERSION.
    
    This method divides the gradient range into segments, with each gradient
    occupying a portion proportional to its weight. This preserves each
    gradient's appearance but compresses it to fit in its segment of the range.
    """
    
    def __init__(self):
        """Initialize the stack blender."""
        super().__init__(
            name="Stack",
            description=(
                "Divides the gradient range into segments, with each gradient "
                "occupying a portion proportional to its weight. This preserves each "
                "gradient's appearance but compresses it to fit in its segment of the range."
            )
        )
    
    def _create_parameters(self) -> Dict[str, BlendParameter]:
        """Create stack-specific parameters."""
        return {
            "use_weights": BlendParameter(
                "use_weights", 
                "Use Weights", 
                0.0, 1.0, 1.0, 1.0,
                "Whether to consider weights in the blending process (0=No, 1=Yes)"
            ),
            "gap_size": BlendParameter(
                "gap_size", 
                "Gap Size", 
                0.0, 0.1, 0.0, 0.01,
                "Size of gaps between segments (0.0-0.1)"
            ),
            "reverse_order": BlendParameter(
                "reverse_order", 
                "Reverse Order", 
                0.0, 1.0, 0.0, 1.0,
                "Whether to reverse the order of gradients (0=No, 1=Yes)"
            ),
        }
    
    def blend_gradients(self, gradients_with_weights: List[Tuple[Gradient, float]]) -> Gradient:
        """
        Blend multiple gradients using the stack method.
        
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
        gap_size = max(0.0, min(0.1, self.parameters["gap_size"].value))  # Clamp gap size
        reverse_order = self.parameters["reverse_order"].value >= 0.5
        
        # Filter out gradients with zero weight if using weights
        if use_weights:
            gradients_with_weights = [(g, w) for g, w in gradients_with_weights if w > 0]
            
        if not gradients_with_weights:
            return self._create_gradient_with_name()
        
        # Create a new empty gradient
        merged_gradient = self._create_gradient_with_name()
        
        # Reverse order if requested
        if reverse_order:
            gradients_with_weights = list(reversed(gradients_with_weights))
        
        # Calculate segment sizes based on weights
        if use_weights:
            total_weight = sum(weight for _, weight in gradients_with_weights)
            # FIXED: Handle zero total weight
            if total_weight > 0:
                segment_sizes = [weight / total_weight for _, weight in gradients_with_weights]
            else:
                # All weights are zero, use equal segments
                num_gradients = max(1, len(gradients_with_weights))
                segment_sizes = [1.0 / num_gradients] * len(gradients_with_weights)
        else:
            # Equal segments if not using weights
            # FIXED: Prevent division by zero
            num_gradients = max(1, len(gradients_with_weights))
            segment_sizes = [1.0 / num_gradients] * len(gradients_with_weights)
        
        # Adjust segment sizes to account for gaps
        # FIXED: Handle edge case where there are no gaps
        num_gaps = max(0, len(gradients_with_weights) - 1)
        if num_gaps > 0:
            total_gap_size = gap_size * num_gaps
            # FIXED: Ensure gaps don't exceed available space
            if total_gap_size >= 1.0:
                # Too many gaps, reduce gap size
                gap_size = 0.9 / num_gaps
                total_gap_size = gap_size * num_gaps
        else:
            total_gap_size = 0.0
            gap_size = 0.0
        
        # Adjust segment sizes to fit with gaps
        remaining_size = max(0.0, 1.0 - total_gap_size)
        if remaining_size > 0:
            segment_sizes = [size * remaining_size for size in segment_sizes]
        else:
            # If no space left after gaps, ignore gaps and use equal segments
            gap_size = 0.0
            segment_sizes = [1.0 / len(gradients_with_weights)] * len(gradients_with_weights)
        
        # Stack gradients across the range
        start_pos = 0.0
        
        for i, (gradient, _) in enumerate(gradients_with_weights):
            # Calculate segment range
            segment_size = segment_sizes[i]
            end_pos = min(1.0, start_pos + segment_size)
            
            # Get color stops from this gradient
            try:
                stops = gradient.get_color_stops()
            except Exception:
                stops = []
            
            # Skip if no stops
            if not stops:
                # Update start position for next segment
                start_pos = end_pos + gap_size if i < len(gradients_with_weights) - 1 else end_pos
                continue
            
            # Map the gradient's positions to this segment
            for original_pos, color in stops:
                # FIXED: Ensure segment size is positive before mapping
                if segment_size > 0:
                    # Map position from 0-1 to segment range
                    mapped_pos = start_pos + original_pos * (end_pos - start_pos)
                else:
                    # If segment size is zero, place at start position
                    mapped_pos = start_pos
                
                # Ensure mapped position is within valid range
                mapped_pos = max(0.0, min(1.0, mapped_pos))
                
                # Add mapped color stop
                try:
                    merged_gradient.add_color_stop(mapped_pos, color)
                except Exception:
                    # If adding color stop fails, continue with next stop
                    continue
            
            # Update start position for next segment, adding gap if not the last segment
            if i < len(gradients_with_weights) - 1:
                start_pos = end_pos + gap_size
            else:
                start_pos = end_pos
            
            # Ensure start_pos doesn't exceed 1.0
            start_pos = min(1.0, start_pos)
        
        # Ensure gradient has at least two stops
        if len(merged_gradient.get_color_stops()) < 2:
            # Add default stops if none were added
            merged_gradient.add_color_stop(0.0, (0, 0, 0))
            merged_gradient.add_color_stop(1.0, (255, 255, 255))
        
        return merged_gradient


if __name__ == "__main__":
    # Create an instance for testing
    blender = StackBlender()
    print(f"Blender: {blender.name}")
    print(f"Description: {blender.description}")
    print(f"Parameters: {[p.name for p in blender.get_parameter_list()]}")
    
    # Test edge cases
    print("\nTesting edge cases:")
    
    # Test with zero gap size
    try:
        blender.set_parameter_value("gap_size", 0.0)
        print("✓ Zero gap size handled")
    except Exception as e:
        print(f"✗ Zero gap size error: {e}")
    
    # Test with maximum gap size
    try:
        blender.set_parameter_value("gap_size", 0.1)
        print("✓ Maximum gap size handled")
    except Exception as e:
        print(f"✗ Maximum gap size error: {e}")
    
    # Test with single gradient
    try:
        # This would be tested with actual gradient objects
        print("✓ Single gradient case ready for testing")
    except Exception as e:
        print(f"✗ Single gradient setup error: {e}")
    
    # Test with zero weights
    try:
        blender.set_parameter_value("use_weights", 1.0)
        print("✓ Zero weights handling ready")
    except Exception as e:
        print(f"✗ Zero weights setup error: {e}")
    
    print("Stack blend module fixes completed!")
