#!/usr/bin/env python3
"""
Interleave Blend Module for Gradient Generator

This module implements the interleave blending method, which preserves 
the original positions of color stops from all input gradients.
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
class InterleaveBlender(GradientBlender):
    """
    Interleave blending method.
    
    This method preserves all color stops from all gradients, keeping their
    original positions. If multiple stops have the same position, the highest
    weighted gradient's color is used (if weights are enabled).
    """
    
    def __init__(self):
        """Initialize the interleave blender."""
        super().__init__(
            name="Interleave",
            description=(
                "Preserves all color stops from all gradients, keeping their "
                "original positions. If multiple stops have the same position, the highest "
                "weighted gradient's color is used (if weights are enabled)."
            )
        )
    
    def _create_parameters(self) -> Dict[str, BlendParameter]:
        """Create interleave-specific parameters."""
        return {
            "use_weights": BlendParameter(
                "use_weights", 
                "Use Weights", 
                0.0, 1.0, 1.0, 1.0,
                "Whether to consider weights in the merging process (0=No, 1=Yes)"
            ),
            "tolerance": BlendParameter(
                "tolerance", 
                "Position Tolerance", 
                0.0, 0.1, 0.001, 0.001,
                "Positions within this distance are considered the same (0.0-0.1)"
            ),
            "preserve_all": BlendParameter(
                "preserve_all", 
                "Preserve All Stops", 
                0.0, 1.0, 0.0, 1.0,
                "Whether to preserve all stops at the same position (0=No, 1=Yes)"
            ),
            "min_spacing": BlendParameter(
                "min_spacing",
                "Minimum Spacing",
                0.0, 0.1, 0.005, 0.001,
                "Minimum distance between color stops to prevent solid lines (0.0-0.1)"
            ),
        }
    
    def blend_gradients(self, gradients_with_weights: List[Tuple[Gradient, float]]) -> Gradient:
        """
        Blend multiple gradients using the interleave method.
        
        Args:
            gradients_with_weights: List of (gradient, weight) tuples
            
        Returns:
            Blended gradient
        """
        if not gradients_with_weights:
            return self._create_gradient_with_name()
            
        if len(gradients_with_weights) == 1:
            # Return a clone of the single gradient
            result = gradients_with_weights[0][0].clone()
            result.set_name(f"Merged Gradient ({self.name})")
            return result
        
        # Get parameter values
        use_weights = self.parameters["use_weights"].value >= 0.5
        tolerance = self.parameters["tolerance"].value
        preserve_all = self.parameters["preserve_all"].value >= 0.5
        min_spacing = self.parameters["min_spacing"].value
        
        # Create a new empty gradient
        merged_gradient = self._create_gradient_with_name()
        
        # Collect all color stops from all gradients
        all_stops = []
        
        for gradient, weight in gradients_with_weights:
            # Skip gradients with zero weight if using weights
            if use_weights and weight <= 0:
                continue
                
            # Get color stops
            stops = gradient.get_color_stops()
            
            # Add weight information
            weighted_stops = [(pos, color, weight if use_weights else 1.0) for pos, color in stops]
            all_stops.extend(weighted_stops)
        
        # Sort by position
        all_stops.sort(key=lambda s: s[0])
        
        # Group stops by position (within tolerance)
        grouped_stops = []
        current_group = []
        current_pos = -1
        
        for pos, color, weight in all_stops:
            if current_pos < 0 or abs(pos - current_pos) <= tolerance:
                current_group.append((pos, color, weight))
                current_pos = pos
            else:
                if current_group:
                    grouped_stops.append(current_group)
                current_group = [(pos, color, weight)]
                current_pos = pos
        
        if current_group:
            grouped_stops.append(current_group)
        
        # Process each position group
        processed_stops = []
        
        for group in grouped_stops:
            # Average the position
            avg_pos = sum(pos for pos, _, _ in group) / len(group)
            
            if preserve_all:
                # Add all colors (interleaved) with slight position offsets
                for i, (_, color, _) in enumerate(group):
                    # Slightly offset the position to preserve all colors
                    offset_pos = avg_pos + (i * tolerance)
                    processed_stops.append((min(offset_pos, 1.0), color))
            else:
                # Take the color with the highest weight
                if use_weights:
                    # Find the color with the highest weight
                    max_weight_color = max(group, key=lambda s: s[2])[1]
                    processed_stops.append((avg_pos, max_weight_color))
                else:
                    # Without weights, just take the last color at this position
                    processed_stops.append((avg_pos, group[-1][1]))
        
        # Apply minimum spacing if needed
        if min_spacing > 0.0 and len(processed_stops) > 1:
            # Sort by position again to ensure proper ordering
            processed_stops.sort(key=lambda s: s[0])
            
            # Apply minimum spacing
            adjusted_stops = [processed_stops[0]]  # Start with the first stop
            
            for i in range(1, len(processed_stops)):
                prev_pos = adjusted_stops[-1][0]
                current_pos, color = processed_stops[i]
                
                # Check if too close to previous stop
                if current_pos - prev_pos < min_spacing:
                    # Adjust position to maintain minimum spacing
                    new_pos = min(prev_pos + min_spacing, 1.0)
                    adjusted_stops.append((new_pos, color))
                else:
                    adjusted_stops.append((current_pos, color))
            
            # Use the adjusted stops
            processed_stops = adjusted_stops
        
        # Add all stops to the gradient
        for pos, color in processed_stops:
            merged_gradient.add_color_stop(pos, color)
        
        return merged_gradient


if __name__ == "__main__":
    # Create an instance for testing
    blender = InterleaveBlender()
    print(f"Blender: {blender.name}")
    print(f"Description: {blender.description}")
    print(f"Parameters: {[p.name for p in blender.get_parameter_list()]}")
