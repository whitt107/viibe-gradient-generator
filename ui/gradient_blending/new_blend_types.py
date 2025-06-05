#!/usr/bin/env python3
"""
Updated New Gradient Blend Types for Gradient Generator

This file contains implementations of 5 blending methods with even distribution removed
from Crystal and Chromatic blenders while preserving their mathematical behavior:

1. Waveform Blender - Wave interference patterns (unchanged)
2. Crystal Blender - Crystalline facet patterns (updated to use original positions)
3. Layer Blender - Photoshop-style blend modes (unchanged) 
4. Chromatic Blender - Color channel separation (updated to use original positions)
5. Memory Blender - Echo/trailing effects (unchanged)

These integrate with the existing blend_core infrastructure.
"""

from typing import List, Tuple, Dict
import math
import random

try:
    from .blend_core import GradientBlender, BlendParameter, BlendRegistry
    from ..core.gradient import Gradient
    from ..core.color_utils import rgb_to_hsv, hsv_to_rgb, blend_colors
except ImportError:
    try:
        from gradient_generator.ui.gradient_blending.blend_core import GradientBlender, BlendParameter, BlendRegistry
        from gradient_generator.core.gradient import Gradient
        from gradient_generator.core.color_utils import rgb_to_hsv, hsv_to_rgb, blend_colors
    except ImportError:
        from blend_core import GradientBlender, BlendParameter, BlendRegistry
        from core.gradient import Gradient
        from core.color_utils import rgb_to_hsv, hsv_to_rgb, blend_colors


@BlendRegistry.register
class WaveformBlender(GradientBlender):
    """
    Waveform blending - Creates wave-like interference patterns between gradients.
    
    This method simulates how sound waves or light waves interfere with each other,
    creating constructive and destructive interference patterns that blend gradients
    in wave-like formations.
    """
    
    def __init__(self):
        super().__init__(
            name="Waveform",
            description=(
                "Creates wave-like interference patterns between gradients, simulating "
                "constructive and destructive interference effects like sound or light waves."
            )
        )
    
    def _create_parameters(self) -> Dict[str, BlendParameter]:
        """Create waveform-specific parameters."""
        return {
            "wave_type": BlendParameter(
                "wave_type", "Wave Type", 
                0.0, 3.0, 0.0, 1.0,
                "Wave function: 0=Sine, 1=Square, 2=Triangle, 3=Sawtooth"
            ),
            "frequency_ratio": BlendParameter(
                "frequency_ratio", "Frequency Ratio", 
                0.5, 4.0, 1.0, 0.1,
                "Frequency relationship between gradients"
            ),
            "phase_shift": BlendParameter(
                "phase_shift", "Phase Shift", 
                0.0, 360.0, 0.0, 1.0,
                "Phase shift between waves in degrees"
            ),
            "interference": BlendParameter(
                "interference", "Interference Strength", 
                0.0, 1.0, 0.7, 0.05,
                "Strength of wave interference effects"
            ),
            "amplitude": BlendParameter(
                "amplitude", "Wave Amplitude", 
                0.1, 2.0, 1.0, 0.1,
                "Amplitude of the wave patterns"
            )
        }
    
    def blend_gradients(self, gradients_with_weights: List[Tuple[Gradient, float]]) -> Gradient:
        """Blend gradients using wave interference patterns."""
        if not gradients_with_weights:
            return self._create_gradient_with_name()
            
        if len(gradients_with_weights) == 1:
            result = gradients_with_weights[0][0].clone()
            result.set_name(f"Merged Gradient ({self.name})")
            return result
        
        # Get parameter values
        wave_type = int(self.parameters["wave_type"].value)
        frequency_ratio = self.parameters["frequency_ratio"].value
        phase_shift = math.radians(self.parameters["phase_shift"].value)
        interference = self.parameters["interference"].value
        amplitude = self.parameters["amplitude"].value
        
        # Create result gradient
        result = self._create_gradient_with_name()
        
        # Get all unique positions from all gradients - preserves original behavior
        unique_positions = set()
        
        # Add any explicit stops from input gradients
        for gradient, _ in gradients_with_weights:
            stops = gradient.get_color_stops()
            for pos, _ in stops:
                unique_positions.add(pos)
        
        # Sort positions
        sorted_positions = sorted(unique_positions)
        
        # Generate wave interference pattern at existing gradient positions
        for position in sorted_positions:
            # Calculate wave values for each gradient
            wave_sum = 0.0
            colors = []
            
            for j, (gradient, weight) in enumerate(gradients_with_weights):
                # Calculate wave function for this gradient
                frequency = 1.0 + j * frequency_ratio
                phase = j * phase_shift
                wave_position = position * frequency * 2 * math.pi + phase
                
                # Apply selected wave function
                if wave_type == 0:  # Sine
                    wave_value = math.sin(wave_position)
                elif wave_type == 1:  # Square
                    wave_value = 1.0 if math.sin(wave_position) >= 0 else -1.0
                elif wave_type == 2:  # Triangle
                    wave_value = (2.0 / math.pi) * math.asin(math.sin(wave_position))
                else:  # Sawtooth
                    wave_value = 2.0 * (wave_position / (2 * math.pi) - math.floor(wave_position / (2 * math.pi) + 0.5))
                
                # Scale by amplitude and weight
                wave_value *= amplitude * weight
                wave_sum += abs(wave_value)
                
                # Get color from gradient
                color = gradient.get_interpolated_color(position)
                colors.append((color, wave_value))
            
            # Blend colors based on wave interference
            if wave_sum > 0:
                r_sum = g_sum = b_sum = 0.0
                weight_sum = 0.0
                
                for (r, g, b), wave_val in colors:
                    # Use interference to modulate contribution
                    contribution = (1.0 + wave_val * interference) / 2.0
                    contribution = max(0.0, min(1.0, contribution))
                    
                    r_sum += r * contribution
                    g_sum += g * contribution  
                    b_sum += b * contribution
                    weight_sum += contribution
                
                if weight_sum > 0:
                    blended_color = (
                        int(r_sum / weight_sum),
                        int(g_sum / weight_sum),
                        int(b_sum / weight_sum)
                    )
                else:
                    blended_color = colors[0][0]
            else:
                blended_color = colors[0][0]
            
            result.add_color_stop(position, blended_color)
        
        result.set_name("Waveform Blend")
        return result


@BlendRegistry.register
class CrystalBlender(GradientBlender):
    """
    Crystal blending - Creates crystalline facet patterns.
    
    Simulates light refraction through crystal structures, creating
    faceted patterns with internal reflections and refractions.
    """
    
    def __init__(self):
        super().__init__(
            name="Crystal",
            description=(
                "Creates crystalline facet patterns that simulate light refraction "
                "through crystal structures with internal reflections."
            )
        )
    
    def _create_parameters(self) -> Dict[str, BlendParameter]:
        """Create crystal-specific parameters."""
        return {
            "facet_size": BlendParameter(
                "facet_size", "Facet Size", 
                0.01, 0.2, 0.05, 0.01,
                "Size of individual crystal facets"
            ),
            "refraction_index": BlendParameter(
                "refraction_index", "Refraction Index", 
                1.0, 2.5, 1.5, 0.1,
                "Crystal refraction index (affects light bending)"
            ),
            "clarity": BlendParameter(
                "clarity", "Crystal Clarity", 
                0.0, 1.0, 0.8, 0.05,
                "Crystal clarity (affects color mixing)"
            ),
            "symmetry": BlendParameter(
                "symmetry", "Crystal Symmetry", 
                3.0, 8.0, 6.0, 1.0,
                "Crystal symmetry (number of faces)"
            ),
            "internal_reflection": BlendParameter(
                "internal_reflection", "Internal Reflection", 
                0.0, 1.0, 0.6, 0.05,
                "Amount of internal reflection within crystal"
            )
        }
    
    def blend_gradients(self, gradients_with_weights: List[Tuple[Gradient, float]]) -> Gradient:
        """Blend gradients using crystal refraction simulation."""
        if not gradients_with_weights:
            return self._create_gradient_with_name()
            
        if len(gradients_with_weights) == 1:
            result = gradients_with_weights[0][0].clone()
            result.set_name(f"Merged Gradient ({self.name})")
            return result
        
        # Get parameter values
        facet_size = self.parameters["facet_size"].value
        refraction_index = self.parameters["refraction_index"].value
        clarity = self.parameters["clarity"].value
        symmetry = int(self.parameters["symmetry"].value)
        internal_reflection = self.parameters["internal_reflection"].value
        
        # Create result gradient
        result = self._create_gradient_with_name()
        
        # Get all unique positions from all gradients - NO MORE UNIFORM SAMPLING
        unique_positions = set()
        
        # Add positions from input gradients
        for gradient, _ in gradients_with_weights:
            stops = gradient.get_color_stops()
            for pos, _ in stops:
                unique_positions.add(pos)
        
        # Sort positions
        sorted_positions = sorted(unique_positions)
        
        # Generate crystal facet pattern at original gradient positions
        for position in sorted_positions:
            # Determine which facet this position belongs to
            facet_index = int(position / facet_size) % symmetry
            facet_position = (position % facet_size) / facet_size
            
            # Calculate refraction based on facet angle
            facet_angle = facet_index * 2 * math.pi / symmetry
            normal_angle = facet_angle + math.pi / 2
            
            # Snell's law simulation (simplified)
            incident_angle = facet_position * math.pi / 4  # Varies across facet
            refracted_angle = math.asin(math.sin(incident_angle) / refraction_index)
            
            # Calculate refracted sampling positions for each gradient
            colors = []
            for j, (gradient, weight) in enumerate(gradients_with_weights):
                # Different gradients simulate different "rays" through crystal
                ray_offset = j * 0.1 / len(gradients_with_weights)
                
                # Apply refraction offset
                refraction_offset = math.sin(refracted_angle + facet_angle) * facet_size
                sample_pos = position + refraction_offset + ray_offset
                
                # Handle internal reflections
                if internal_reflection > 0:
                    reflection_count = int(internal_reflection * 3)
                    for _ in range(reflection_count):
                        if sample_pos < 0 or sample_pos > 1:
                            sample_pos = 1.0 - abs(sample_pos % 1.0)  # Reflect at boundaries
                
                # Clamp to valid range
                sample_pos = max(0.0, min(1.0, sample_pos))
                
                color = gradient.get_interpolated_color(sample_pos)
                colors.append((color, weight))
            
            # Blend colors based on crystal clarity and weights
            if colors:
                if clarity > 0.9:
                    # High clarity - sharp facets, pick dominant color
                    max_weight = max(weight for _, weight in colors)
                    dominant_colors = [(color, weight) for color, weight in colors if weight == max_weight]
                    blended_color = dominant_colors[0][0]
                else:
                    # Lower clarity - blend colors
                    r_sum = g_sum = b_sum = 0.0
                    weight_sum = 0.0
                    
                    for (r, g, b), weight in colors:
                        # Apply clarity factor
                        effective_weight = weight * (clarity + (1 - clarity) * 0.5)
                        r_sum += r * effective_weight
                        g_sum += g * effective_weight
                        b_sum += b * effective_weight
                        weight_sum += effective_weight
                    
                    if weight_sum > 0:
                        blended_color = (
                            int(r_sum / weight_sum),
                            int(g_sum / weight_sum),
                            int(b_sum / weight_sum)
                        )
                    else:
                        blended_color = colors[0][0]
            else:
                blended_color = (128, 128, 128)  # Gray fallback
            
            result.add_color_stop(position, blended_color)
        
        result.set_name("Crystal Blend")
        return result


@BlendRegistry.register
class LayerBlender(GradientBlender):
    """
    Layer blending - Photoshop-style blend modes.
    
    Provides familiar layer blending operations like multiply, screen, overlay,
    and other modes familiar to digital artists and photographers.
    """
    
    def __init__(self):
        super().__init__(
            name="Layer",
            description=(
                "Photoshop-style blend modes including multiply, screen, overlay, "
                "and other layer blending operations familiar to digital artists."
            )
        )
    
    def _create_parameters(self) -> Dict[str, BlendParameter]:
        """Create layer blend-specific parameters."""
        return {
            "blend_mode": BlendParameter(
                "blend_mode", "Blend Mode", 
                0.0, 7.0, 0.0, 1.0,
                "Photoshop-style blend modes"
            ),
            "opacity": BlendParameter(
                "opacity", "Layer Opacity", 
                0.0, 1.0, 1.0, 0.05,
                "Opacity/strength of the blend effect"
            ),
            "mask_type": BlendParameter(
                "mask_type", "Layer Mask", 
                0.0, 3.0, 0.0, 1.0,
                "Layer mask type: 0=None, 1=Linear, 2=Radial, 3=Noise"
            ),
            "mask_invert": BlendParameter(
                "mask_invert", "Invert Mask", 
                0.0, 1.0, 0.0, 1.0,
                "Invert the layer mask"
            )
        }
    
    def blend_gradients(self, gradients_with_weights: List[Tuple[Gradient, float]]) -> Gradient:
        """Blend gradients using Photoshop-style layer modes."""
        if not gradients_with_weights:
            return self._create_gradient_with_name()
            
        if len(gradients_with_weights) == 1:
            result = gradients_with_weights[0][0].clone()
            result.set_name(f"Merged Gradient ({self.name})")
            return result
        
        # Get parameter values
        blend_mode = int(self.parameters["blend_mode"].value)
        opacity = self.parameters["opacity"].value
        mask_type = int(self.parameters["mask_type"].value)
        mask_invert = self.parameters["mask_invert"].value >= 0.5
        
        # Use first gradient as base layer
        base_gradient = gradients_with_weights[0][0]
        
        # Create result gradient
        result = self._create_gradient_with_name()
        
        # Blend mode names for naming
        mode_names = ["Multiply", "Screen", "Overlay", "Soft Light", 
                     "Hard Light", "Color Dodge", "Color Burn", "Difference"]
        
        # Get all unique positions from all gradients - preserves original behavior
        unique_positions = set()
        
        # Add any explicit stops from input gradients
        for gradient, _ in gradients_with_weights:
            stops = gradient.get_color_stops()
            for pos, _ in stops:
                unique_positions.add(pos)
        
        # Sort positions
        sorted_positions = sorted(unique_positions)
        
        # Process each position
        for position in sorted_positions:
            # Get base color
            base_color = base_gradient.get_interpolated_color(position)
            result_color = base_color
            
            # Apply each additional gradient as a layer
            for gradient, weight in gradients_with_weights[1:]:
                layer_color = gradient.get_interpolated_color(position)
                
                # Calculate mask value
                mask_value = self._calculate_mask(position, mask_type, mask_invert)
                
                # Apply layer blend mode
                blended = self._apply_blend_mode(result_color, layer_color, blend_mode)
                
                # Apply opacity and mask
                final_opacity = opacity * weight * mask_value
                result_color = self._blend_with_opacity(result_color, blended, final_opacity)
            
            result.add_color_stop(position, result_color)
        
        result.set_name(f"Layer Blend - {mode_names[blend_mode]}")
        return result
    
    def _apply_blend_mode(self, base: Tuple[int, int, int], layer: Tuple[int, int, int], mode: int) -> Tuple[int, int, int]:
        """Apply Photoshop-style blend mode."""
        br, bg, bb = [c / 255.0 for c in base]   # Normalize to 0-1
        lr, lg, lb = [c / 255.0 for c in layer]  # Normalize to 0-1
        
        if mode == 0:  # Multiply
            r, g, b = br * lr, bg * lg, bb * lb
        elif mode == 1:  # Screen
            r, g, b = 1 - (1 - br) * (1 - lr), 1 - (1 - bg) * (1 - lg), 1 - (1 - bb) * (1 - lb)
        elif mode == 2:  # Overlay
            r = 2 * br * lr if br < 0.5 else 1 - 2 * (1 - br) * (1 - lr)
            g = 2 * bg * lg if bg < 0.5 else 1 - 2 * (1 - bg) * (1 - lg)
            b = 2 * bb * lb if bb < 0.5 else 1 - 2 * (1 - bb) * (1 - lb)
        elif mode == 3:  # Soft Light
            r = (1 - 2 * lr) * br**2 + 2 * lr * br if lr < 0.5 else (1 - 2 * (1 - lr)) * br * (1 - br) + 2 * (1 - lr) * br
            g = (1 - 2 * lg) * bg**2 + 2 * lg * bg if lg < 0.5 else (1 - 2 * (1 - lg)) * bg * (1 - bg) + 2 * (1 - lg) * bg
            b = (1 - 2 * lb) * bb**2 + 2 * lb * bb if lb < 0.5 else (1 - 2 * (1 - lb)) * bb * (1 - bb) + 2 * (1 - lb) * bb
        elif mode == 4:  # Hard Light
            r = 2 * br * lr if lr < 0.5 else 1 - 2 * (1 - br) * (1 - lr)
            g = 2 * bg * lg if lg < 0.5 else 1 - 2 * (1 - bg) * (1 - lg)
            b = 2 * bb * lb if lb < 0.5 else 1 - 2 * (1 - bb) * (1 - lb)
        elif mode == 5:  # Color Dodge
            r = br / (1 - lr) if lr < 1 else 1
            g = bg / (1 - lg) if lg < 1 else 1
            b = bb / (1 - lb) if lb < 1 else 1
        elif mode == 6:  # Color Burn
            r = 1 - (1 - br) / lr if lr > 0 else 0
            g = 1 - (1 - bg) / lg if lg > 0 else 0
            b = 1 - (1 - bb) / lb if lb > 0 else 0
        elif mode == 7:  # Difference
            r, g, b = abs(br - lr), abs(bg - lg), abs(bb - lb)
        else:
            r, g, b = br, bg, bb  # No blend
        
        # Clamp and convert back to 0-255
        return (
            int(max(0, min(1, r)) * 255),
            int(max(0, min(1, g)) * 255),
            int(max(0, min(1, b)) * 255)
        )
    
    def _calculate_mask(self, position: float, mask_type: int, invert: bool) -> float:
        """Calculate mask value at position."""
        if mask_type == 0:  # No mask
            mask = 1.0
        elif mask_type == 1:  # Linear
            mask = position
        elif mask_type == 2:  # Radial
            center_dist = abs(position - 0.5) * 2
            mask = 1.0 - center_dist
        elif mask_type == 3:  # Noise
            # Simple noise based on position
            noise_seed = int(position * 1000)
            random.seed(noise_seed)
            mask = random.random()
        else:
            mask = 1.0
        
        return (1.0 - mask) if invert else mask
    
    def _blend_with_opacity(self, base: Tuple[int, int, int], layer: Tuple[int, int, int], opacity: float) -> Tuple[int, int, int]:
        """Blend two colors with opacity."""
        opacity = max(0.0, min(1.0, opacity))
        
        r = int(base[0] * (1 - opacity) + layer[0] * opacity)
        g = int(base[1] * (1 - opacity) + layer[1] * opacity)
        b = int(base[2] * (1 - opacity) + layer[2] * opacity)
        
        return (r, g, b)


@BlendRegistry.register
class ChromaticBlender(GradientBlender):
    """
    Chromatic blending - Separates color channels and blends them independently.
    
    Creates prismatic and chromatic aberration effects by treating RGB channels
    as separate entities that can be offset and manipulated independently.
    """
    
    def __init__(self):
        super().__init__(
            name="Chromatic",
            description=(
                "Separates color channels and blends them independently, creating "
                "prismatic and chromatic aberration effects like light through a prism."
            )
        )
    
    def _create_parameters(self) -> Dict[str, BlendParameter]:
        """Create chromatic-specific parameters."""
        return {
            "red_offset": BlendParameter(
                "red_offset", "Red Channel Offset", 
                -0.1, 0.1, 0.01, 0.005,
                "Position offset for red color channel"
            ),
            "green_offset": BlendParameter(
                "green_offset", "Green Channel Offset", 
                -0.1, 0.1, 0.0, 0.005,
                "Position offset for green color channel"
            ),
            "blue_offset": BlendParameter(
                "blue_offset", "Blue Channel Offset", 
                -0.1, 0.1, -0.01, 0.005,
                "Position offset for blue color channel"
            ),
            "dispersion": BlendParameter(
                "dispersion", "Chromatic Dispersion", 
                0.0, 1.0, 0.5, 0.05,
                "Amount of chromatic dispersion effect"
            ),
            "prism_angle": BlendParameter(
                "prism_angle", "Prism Angle", 
                0.0, 45.0, 15.0, 1.0,
                "Angle of light dispersion (degrees)"
            )
        }
    
    def blend_gradients(self, gradients_with_weights: List[Tuple[Gradient, float]]) -> Gradient:
        """Blend gradients using chromatic separation."""
        if not gradients_with_weights:
            return self._create_gradient_with_name()
            
        if len(gradients_with_weights) == 1:
            # Apply chromatic effect to single gradient
            return self._apply_chromatic_effect(gradients_with_weights[0][0])
        
        # Get parameter values
        red_offset = self.parameters["red_offset"].value
        green_offset = self.parameters["green_offset"].value
        blue_offset = self.parameters["blue_offset"].value
        dispersion = self.parameters["dispersion"].value
        prism_angle = math.radians(self.parameters["prism_angle"].value)
        
        # Create result gradient
        result = self._create_gradient_with_name()
        
        # Get all unique positions from all gradients - NO MORE UNIFORM SAMPLING
        unique_positions = set()
        
        # Add positions from input gradients
        for gradient, _ in gradients_with_weights:
            stops = gradient.get_color_stops()
            for pos, _ in stops:
                unique_positions.add(pos)
        
        # Sort positions
        sorted_positions = sorted(unique_positions)
        
        # Process chromatic separation at original gradient positions
        for position in sorted_positions:
            # Calculate separate channel positions with offsets
            red_pos = position + red_offset * dispersion
            green_pos = position + green_offset * dispersion
            blue_pos = position + blue_offset * dispersion
            
            # Apply prism angle effect
            prism_factor = math.sin(position * math.pi) * math.sin(prism_angle)
            red_pos += prism_factor * 0.02
            blue_pos -= prism_factor * 0.02
            
            # Wrap positions to valid range
            red_pos = red_pos % 1.0
            green_pos = green_pos % 1.0
            blue_pos = blue_pos % 1.0
            
            # Sample each gradient at different positions for each channel
            final_r = final_g = final_b = 0
            total_weight = 0
            
            for gradient, weight in gradients_with_weights:
                # Get colors at offset positions
                red_color = gradient.get_interpolated_color(red_pos)
                green_color = gradient.get_interpolated_color(green_pos)
                blue_color = gradient.get_interpolated_color(blue_pos)
                
                # Extract individual channels
                r = red_color[0]
                g = green_color[1]
                b = blue_color[2]
                
                # Weight the contribution
                final_r += r * weight
                final_g += g * weight
                final_b += b * weight
                total_weight += weight
            
            # Normalize by total weight
            if total_weight > 0:
                final_r = int(final_r / total_weight)
                final_g = int(final_g / total_weight)
                final_b = int(final_b / total_weight)
            
            # Ensure valid color values
            final_r = max(0, min(255, final_r))
            final_g = max(0, min(255, final_g))
            final_b = max(0, min(255, final_b))
            
            result.add_color_stop(position, (final_r, final_g, final_b))
        
        result.set_name("Chromatic Blend")
        return result
    
    def _apply_chromatic_effect(self, gradient: Gradient) -> Gradient:
        """Apply chromatic aberration to a single gradient."""
        result = gradient.clone()
        result._color_stops = []
        
        # Get parameter values
        red_offset = self.parameters["red_offset"].value
        green_offset = self.parameters["green_offset"].value
        blue_offset = self.parameters["blue_offset"].value
        dispersion = self.parameters["dispersion"].value
        prism_angle = math.radians(self.parameters["prism_angle"].value)
        
        # Get original gradient positions - NO MORE UNIFORM SAMPLING
        original_stops = gradient.get_color_stops()
        
        # Apply chromatic effect at original positions
        for position, original_color in original_stops:
            # Calculate channel positions
            red_pos = (position + red_offset * dispersion) % 1.0
            green_pos = (position + green_offset * dispersion) % 1.0
            blue_pos = (position + blue_offset * dispersion) % 1.0
            
            # Apply prism effect
            prism_factor = math.sin(position * math.pi) * math.sin(prism_angle)
            red_pos = (red_pos + prism_factor * 0.02) % 1.0
            blue_pos = (blue_pos - prism_factor * 0.02) % 1.0
            
            # Sample each channel separately
            red_color = gradient.get_interpolated_color(red_pos)
            green_color = gradient.get_interpolated_color(green_pos)
            blue_color = gradient.get_interpolated_color(blue_pos)
            
            # Combine channels
            chromatic_color = (red_color[0], green_color[1], blue_color[2])
            
            result.add_color_stop(position, chromatic_color)
        
        result.set_name(f"{gradient.get_name()} (Chromatic)")
        return result


@BlendRegistry.register
class MemoryBlender(GradientBlender):
    """
    Memory blending - Uses previous position samples to influence current blending.
    
    Creates trailing, echo-like effects where the gradient "remembers" previous
    color states and incorporates them into current blending decisions.
    """
    
    def __init__(self):
        super().__init__(
            name="Memory",
            description=(
                "Uses previous position samples to influence current blending, "
                "creating trailing, echo-like effects with gradient memory."
            )
        )
    
    def _create_parameters(self) -> Dict[str, BlendParameter]:
        """Create memory-specific parameters."""
        return {
            "memory_length": BlendParameter(
                "memory_length", "Memory Length", 
                2.0, 20.0, 5.0, 1.0,
                "Number of previous samples to remember"
            ),
            "decay_rate": BlendParameter(
                "decay_rate", "Memory Decay Rate", 
                0.1, 0.9, 0.7, 0.05,
                "Rate at which memories fade (higher = faster decay)"
            ),
            "feedback": BlendParameter(
                "feedback", "Memory Feedback", 
                0.0, 1.0, 0.3, 0.05,
                "Amount of feedback from memory to current state"
            ),
            "echo_strength": BlendParameter(
                "echo_strength", "Echo Strength", 
                0.0, 1.0, 0.5, 0.05,
                "Strength of echo effects in the memory"
            ),
            "memory_mode": BlendParameter(
                "memory_mode", "Memory Mode", 
                0.0, 2.0, 0.0, 1.0,
                "Memory behavior: 0=Linear Decay, 1=Exponential, 2=Oscillating"
            )
        }
    
    def blend_gradients(self, gradients_with_weights: List[Tuple[Gradient, float]]) -> Gradient:
        """Blend gradients using memory effects."""
        if not gradients_with_weights:
            return self._create_gradient_with_name()
            
        if len(gradients_with_weights) == 1:
            result = gradients_with_weights[0][0].clone()
            result.set_name(f"Merged Gradient ({self.name})")
            return result
        
        # Get parameter values
        memory_length = int(self.parameters["memory_length"].value)
        decay_rate = self.parameters["decay_rate"].value
        feedback = self.parameters["feedback"].value
        echo_strength = self.parameters["echo_strength"].value
        memory_mode = int(self.parameters["memory_mode"].value)
        
        # Create result gradient
        result = self._create_gradient_with_name()
        
        # Initialize memory buffer
        memory_buffer = []
        
        # Get all unique positions from all gradients - preserves original behavior
        unique_positions = set()
        
        # Add any explicit stops from input gradients
        for gradient, _ in gradients_with_weights:
            stops = gradient.get_color_stops()
            for pos, _ in stops:
                unique_positions.add(pos)
        
        # Sort positions
        sorted_positions = sorted(unique_positions)
        
        # Process with memory at existing gradient positions
        for i, position in enumerate(sorted_positions):
            # Get current colors from all gradients
            current_colors = []
            for gradient, weight in gradients_with_weights:
                color = gradient.get_interpolated_color(position)
                current_colors.append((color, weight))
            
            # Blend current colors
            current_blend = self._blend_colors_weighted(current_colors)
            
            # Apply memory effects if we have memory
            if memory_buffer:
                memory_blend = self._process_memory(memory_buffer, memory_length, 
                                                  decay_rate, memory_mode, echo_strength)
                
                # Combine current with memory using feedback
                final_color = self._combine_with_memory(current_blend, memory_blend, feedback)
            else:
                final_color = current_blend
            
            # Add to memory buffer
            memory_buffer.append({
                'position': position,
                'color': final_color,
                'timestamp': i
            })
            
            # Trim memory buffer to specified length
            if len(memory_buffer) > memory_length:
                memory_buffer.pop(0)
            
            result.add_color_stop(position, final_color)
        
        result.set_name("Memory Blend")
        return result
    
    def _blend_colors_weighted(self, colors_with_weights: List[Tuple[Tuple[int, int, int], float]]) -> Tuple[int, int, int]:
        """Blend colors with weights."""
        if not colors_with_weights:
            return (0, 0, 0)
        
        r_sum = g_sum = b_sum = 0.0
        weight_sum = 0.0
        
        for (r, g, b), weight in colors_with_weights:
            r_sum += r * weight
            g_sum += g * weight
            b_sum += b * weight
            weight_sum += weight
        
        if weight_sum > 0:
            return (int(r_sum / weight_sum), int(g_sum / weight_sum), int(b_sum / weight_sum))
        else:
            return colors_with_weights[0][0]
    
    def _process_memory(self, memory_buffer: List[Dict], memory_length: int, 
                       decay_rate: float, memory_mode: int, echo_strength: float) -> Tuple[int, int, int]:
        """Process memory buffer to create memory blend."""
        if not memory_buffer:
            return (0, 0, 0)
        
        r_sum = g_sum = b_sum = 0.0
        weight_sum = 0.0
        
        # Current timestamp
        current_time = memory_buffer[-1]['timestamp']
        
        for i, memory in enumerate(memory_buffer):
            age = current_time - memory['timestamp']
            
            # Calculate memory weight based on mode
            if memory_mode == 0:  # Linear decay
                weight = max(0, 1.0 - (age / memory_length) * decay_rate)
            elif memory_mode == 1:  # Exponential decay
                weight = math.exp(-age * decay_rate)
            elif memory_mode == 2:  # Oscillating decay
                weight = math.exp(-age * decay_rate * 0.5) * (1 + math.sin(age * math.pi / 2) * 0.5)
            else:
                weight = 1.0
            
            # Apply echo strength
            if i < len(memory_buffer) - 1:  # Not the current sample
                weight *= echo_strength
            
            # Weight the color contribution
            r, g, b = memory['color']
            r_sum += r * weight
            g_sum += g * weight
            b_sum += b * weight
            weight_sum += weight
        
        if weight_sum > 0:
            return (int(r_sum / weight_sum), int(g_sum / weight_sum), int(b_sum / weight_sum))
        else:
            return memory_buffer[-1]['color']
    
    def _combine_with_memory(self, current: Tuple[int, int, int], memory: Tuple[int, int, int], 
                           feedback: float) -> Tuple[int, int, int]:
        """Combine current color with memory using feedback."""
        cr, cg, cb = current
        mr, mg, mb = memory
        
        # Blend current with memory
        r = int(cr * (1 - feedback) + mr * feedback)
        g = int(cg * (1 - feedback) + mg * feedback)
        b = int(cb * (1 - feedback) + mb * feedback)
        
        # Ensure valid color values
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        return (r, g, b)


if __name__ == "__main__":
    print("Updated New Gradient Blend Types Implementation")
    print("=" * 50)
    
    # List the blender types with updates
    updated_blenders = [
        "WaveformBlender - Wave interference patterns (unchanged - already uses original positions)",
        "CrystalBlender - Crystalline facet patterns (UPDATED - now uses original gradient positions)", 
        "LayerBlender - Photoshop-style blend modes (unchanged - already uses original positions)",
        "ChromaticBlender - Color channel separation effects (UPDATED - now uses original gradient positions)",
        "MemoryBlender - Echo/trailing memory effects (unchanged - already uses original positions)"
    ]
    
    print("Changes made:")
    for blender in updated_blenders:
        print(f"✓ {blender}")
    
    print(f"\nTotal: {len(updated_blenders)} blend types")
    
    print("\nSpecific changes to remove even distribution:")
    print("CRYSTAL BLENDER:")
    print("• Removed: num_samples = 80 and uniform sampling loop")
    print("• Added: unique_positions from all input gradients")
    print("• Result: Uses original gradient positions while preserving crystal facet mathematics")
    
    print("\nCHROMATIC BLENDER:")
    print("• Removed: num_samples = 60 and uniform sampling loop")
    print("• Added: unique_positions from all input gradients")
    print("• Updated: _apply_chromatic_effect to use original stops instead of uniform sampling")
    print("• Result: Uses original gradient positions while preserving chromatic aberration effects")
    
    print("\nMathematical behavior preserved:")
    print("• Crystal facet calculations unchanged")
    print("• Chromatic aberration algorithms unchanged")
    print("• Color blending formulas unchanged")
    print("• Only sampling strategy changed from uniform to original positions")