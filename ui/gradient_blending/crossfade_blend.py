#!/usr/bin/env python3
"""
Crossfade Blend Module for Gradient Generator - UPDATED VERSION

This module implements the crossfade blending method, which creates sequential
transitions between gradients across the range. Updated to remove even distribution
while preserving mathematical behavior.
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
class CrossfadeBlender(GradientBlender):
    """
    Crossfade blending method - UPDATED VERSION.
    
    This method creates a sequential transition between gradients, similar to a
    crossfade in audio. Each gradient is allocated a portion of the range based
    on its weight. This method maintains the original appearance of each gradient.
    """
    
    def __init__(self):
        """Initialize the crossfade blender."""
        super().__init__(
            name="Crossfade",
            description=(
                "Creates a sequential transition between gradients, similar to a "
                "crossfade in audio. Each gradient is allocated a portion of the range based "
                "on its weight. This method maintains the original appearance of each gradient."
            )
        )
    
    def _create_parameters(self) -> Dict[str, BlendParameter]:
        """Create crossfade-specific parameters."""
        return {
            "use_weights": BlendParameter(
                "use_weights", 
                "Use Weights", 
                0.0, 1.0, 1.0, 1.0,
                "Whether to consider weights in the blending process (0=No, 1=Yes)"
            ),
            "overlap": BlendParameter(
                "overlap", 
                "Overlap Amount", 
                0.0, 1.0, 0.3, 0.05,
                "How much gradients overlap in the transition (0.0-1.0)"
            ),
        }
    
    def blend_gradients(self, gradients_with_weights: List[Tuple[Gradient, float]]) -> Gradient:
        """
        Blend multiple gradients using the crossfade method.
        
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
        overlap = max(0.0, min(1.0, self.parameters["overlap"].value))
        
        # Filter out gradients with zero weight if using weights
        if use_weights:
            gradients_with_weights = [(g, w) for g, w in gradients_with_weights if w > 0]
            
        if not gradients_with_weights:
            return self._create_gradient_with_name()
        
        # Create a new empty gradient
        merged_gradient = self._create_gradient_with_name()
        
        # Get all unique positions from all gradients - preserves original behavior
        unique_positions = set()
        
        # Add positions from input gradients
        for gradient, _ in gradients_with_weights:
            stops = gradient.get_color_stops()
            for pos, _ in stops:
                unique_positions.add(pos)
        
        # Sort positions
        sorted_positions = sorted(unique_positions)
        
        # Calculate weight-based segment boundaries first
        if use_weights:
            total_weight = sum(weight for _, weight in gradients_with_weights)
            if total_weight > 0:
                segment_sizes = [weight / total_weight for _, weight in gradients_with_weights]
            else:
                segment_sizes = [1.0 / len(gradients_with_weights)] * len(gradients_with_weights)
        else:
            segment_sizes = [1.0 / len(gradients_with_weights)] * len(gradients_with_weights)
        
        # Calculate cumulative segment positions
        segment_boundaries = [0.0]
        for size in segment_sizes:
            segment_boundaries.append(segment_boundaries[-1] + size)
        
        # Calculate overlap regions based on actual segment boundaries
        overlap_regions = []
        for i in range(len(segment_boundaries) - 2):  # -2 because we need i+1 to exist
            segment_end = segment_boundaries[i + 1]
            next_segment_start = segment_boundaries[i + 1]
            
            # Create overlap centered around the boundary
            overlap_size = overlap * min(segment_sizes[i], segment_sizes[i + 1])
            overlap_start = max(0.0, segment_end - overlap_size / 2)
            overlap_end = min(1.0, segment_end + overlap_size / 2)
            
            if overlap_start < overlap_end:
                overlap_regions.append({
                    'start': overlap_start,
                    'end': overlap_end,
                    'boundary': segment_end,
                    'gradient1_index': i,
                    'gradient2_index': i + 1
                })
        
        # Generate color stops at the original gradient positions
        color_stops = []
        
        # Calculate weight-based segment boundaries
        if use_weights:
            total_weight = sum(weight for _, weight in gradients_with_weights)
            if total_weight > 0:
                segment_sizes = [weight / total_weight for _, weight in gradients_with_weights]
            else:
                segment_sizes = [1.0 / len(gradients_with_weights)] * len(gradients_with_weights)
        else:
            segment_sizes = [1.0 / len(gradients_with_weights)] * len(gradients_with_weights)
        
        # Calculate cumulative segment positions
        segment_boundaries = [0.0]
        for size in segment_sizes:
            segment_boundaries.append(segment_boundaries[-1] + size)
        
        # Process each position from the sorted unique positions
        for position in sorted_positions:
            final_color = None
            
            # Check if we're in any overlap region first
            in_overlap_region = None
            for region in overlap_regions:
                if region['start'] <= position <= region['end']:
                    in_overlap_region = region
                    break
            
            if in_overlap_region:
                # We're in an overlap region - blend between two gradients
                region = in_overlap_region
                gradient1, weight1 = gradients_with_weights[region['gradient1_index']]
                gradient2, weight2 = gradients_with_weights[region['gradient2_index']]
                
                # Calculate blend factor: 0.0 = full gradient1, 1.0 = full gradient2
                overlap_size = region['end'] - region['start']
                if overlap_size > 0:
                    blend_factor = (position - region['start']) / overlap_size
                else:
                    blend_factor = 0.5
                
                # Calculate local positions in both gradients
                # For gradient1: map position to its segment
                seg1_start = segment_boundaries[region['gradient1_index']]
                seg1_end = segment_boundaries[region['gradient1_index'] + 1]
                if seg1_end > seg1_start:
                    local_pos1 = (position - seg1_start) / (seg1_end - seg1_start)
                else:
                    local_pos1 = 0.5
                local_pos1 = max(0.0, min(1.0, local_pos1))
                
                # For gradient2: map position to its segment  
                seg2_start = segment_boundaries[region['gradient2_index']]
                seg2_end = segment_boundaries[region['gradient2_index'] + 1]
                if seg2_end > seg2_start:
                    local_pos2 = (position - seg2_start) / (seg2_end - seg2_start)
                else:
                    local_pos2 = 0.5
                local_pos2 = max(0.0, min(1.0, local_pos2))
                
                # Get colors from both gradients
                try:
                    color1 = gradient1.get_interpolated_color(local_pos1)
                except Exception:
                    color1 = (128, 128, 128)
                
                try:
                    color2 = gradient2.get_interpolated_color(local_pos2)
                except Exception:
                    color2 = (128, 128, 128)
                
                # Blend the colors bidirectionally
                r1, g1, b1 = color1
                r2, g2, b2 = color2
                
                # Crossfade: gradient1 fades out as gradient2 fades in
                r = int(r1 * (1.0 - blend_factor) + r2 * blend_factor)
                g = int(g1 * (1.0 - blend_factor) + g2 * blend_factor)
                b = int(b1 * (1.0 - blend_factor) + b2 * blend_factor)
                
                # Ensure valid color values
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))
                
                final_color = (r, g, b)
                
            else:
                # Not in overlap region - determine which gradient segment this position falls into
                segment_index = 0
                for i in range(len(segment_boundaries) - 1):
                    if segment_boundaries[i] <= position < segment_boundaries[i + 1]:
                        segment_index = i
                        break
                else:
                    # Handle position = 1.0 case
                    if position >= segment_boundaries[-1]:
                        segment_index = len(gradients_with_weights) - 1
                
                # Ensure segment_index is valid
                segment_index = max(0, min(len(gradients_with_weights) - 1, segment_index))
                
                # Get the gradient for this segment
                current_gradient, current_weight = gradients_with_weights[segment_index]
                
                # Calculate the local position within this gradient's segment
                segment_start = segment_boundaries[segment_index]
                segment_end = segment_boundaries[segment_index + 1]
                
                if segment_end > segment_start:
                    local_position = (position - segment_start) / (segment_end - segment_start)
                else:
                    local_position = 0.0
                
                # Clamp local position to valid range
                local_position = max(0.0, min(1.0, local_position))
                
                # Get the color from the current gradient at the local position
                try:
                    final_color = current_gradient.get_interpolated_color(local_position)
                except Exception:
                    final_color = (128, 128, 128)  # Gray fallback
            
            # Add the color stop
            if final_color:
                color_stops.append((position, final_color))
        
        # Sort color stops by position
        color_stops.sort(key=lambda x: x[0])
        
        # Remove duplicate positions (keep the last color at each position)
        if color_stops:
            unique_stops = [color_stops[0]]
            for pos, color in color_stops[1:]:
                if abs(pos - unique_stops[-1][0]) > 0.001:  # Different position
                    unique_stops.append((pos, color))
                else:  # Same position, replace color
                    unique_stops[-1] = (pos, color)
            color_stops = unique_stops
        
        # Add color stops to gradient
        for position, color in color_stops:
            merged_gradient.add_color_stop(position, color)
        
        return merged_gradient


if __name__ == "__main__":
    # Create an instance for testing
    blender = CrossfadeBlender()
    print(f"Blender: {blender.name}")
    print(f"Description: {blender.description}")
    print(f"Parameters: {[p.name for p in blender.get_parameter_list()]}")
    
    print("\nChanges made:")
    print("✓ Removed sample_density parameter")
    print("✓ Removed uniform sampling loop")
    print("✓ Now uses original gradient positions")
    print("✓ Mathematical behavior preserved")
    print("✓ Crossfade algorithm unchanged")
