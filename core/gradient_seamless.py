#!/usr/bin/env python3
"""
Refactored Gradient Seamless Blending Module

Simplified seamless blending:
- Basic seamless: Replace last color stop with first color stop
- Progressive blending: Use blend region for gradual transitions
- Preview overlay: Optional visual indicators
"""
from typing import Callable, Tuple, List
from .color_utils import blend_colors


class SeamlessBlending:
    """Simplified seamless blending with basic color replacement and optional progressive features."""
    
    def __init__(self):
        self.enabled = False
        self.progressive_enabled = False
        self.blend_region = 0.1
        self.intensity_falloff = 0.7
        self.preview_overlay = True
    
    def reset(self):
        self.__init__()
    
    @property
    def blend_region(self) -> float:
        return self._blend_region
    
    @blend_region.setter
    def blend_region(self, value: float):
        self._blend_region = max(0.0, min(0.5, value))
    
    def apply_seamless_to_gradient(self, gradient_stops: List[Tuple[float, Tuple[int, int, int]]]) -> List[Tuple[float, Tuple[int, int, int]]]:
        """Apply seamless blending by replacing last color with first color."""
        if not self.enabled or not gradient_stops:
            return gradient_stops
        
        if len(gradient_stops) < 2:
            return gradient_stops
        
        # Create modified stops
        modified_stops = gradient_stops.copy()
        
        # Replace last stop color with first stop color
        last_pos = modified_stops[-1][0]
        first_color = modified_stops[0][1]
        modified_stops[-1] = (last_pos, first_color)
        
        return modified_stops
    
    def get_seamless_color(self, position: float, 
                          color_function: Callable[[float], Tuple[int, int, int]],
                          gradient_stops: List[Tuple[float, Tuple[int, int, int]]] = None) -> Tuple[int, int, int]:
        """FIXED: Get seamless color for preview with proper first/last identification."""
        position = max(0.0, min(1.0, position))
        
        if not self.enabled:
            return color_function(position)
        
        # Get base color first
        base_color = color_function(position)
        
        if not gradient_stops or len(gradient_stops) < 2:
            return base_color
        
        # Sort stops to identify true first and last
        sorted_stops = sorted(gradient_stops, key=lambda x: x[0])
        first_color = sorted_stops[0][1]
        last_color = sorted_stops[-1][1]
        last_pos = sorted_stops[-1][0]
        
        # If we're sampling at the last position, return first color for seamless effect
        if abs(position - last_pos) < 1e-6:
            return first_color
        
        # Progressive blending if enabled
        if self.progressive_enabled:
            blend_intensity = self._get_blend_intensity(position)
            if blend_intensity > 0.0:
                return self._progressive_blend_fixed(position, base_color, sorted_stops, blend_intensity)
        
        return base_color
    
    def _progressive_blend_fixed(self, position: float, base_color: Tuple[int, int, int],
                              sorted_stops: List[Tuple[float, Tuple[int, int, int]]],
                              blend_intensity: float) -> Tuple[int, int, int]:
        """FIXED: Progressive blend with proper first/last colors."""
        if not sorted_stops or len(sorted_stops) < 2:
            return base_color
        
        first_color = sorted_stops[0][1]
        last_color = sorted_stops[-1][1]
        
        # End region blending - blend towards first color
        if position > (1.0 - self._blend_region):
            return self._blend_colors(base_color, first_color, blend_intensity * self.intensity_falloff)
        
        # Start region blending - blend towards last color (but subtle)
        elif position < self._blend_region:
            return self._blend_colors(base_color, last_color, blend_intensity * self.intensity_falloff * 0.3)
        
        return base_color
    
    def _blend_colors(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Blend two RGB colors with proper clamping."""
        factor = max(0.0, min(1.0, factor))
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        
        r = max(0, min(255, int(r1 * (1 - factor) + r2 * factor)))
        g = max(0, min(255, int(g1 * (1 - factor) + g2 * factor)))
        b = max(0, min(255, int(b1 * (1 - factor) + b2 * factor)))
        
        return (r, g, b)
    def _get_blend_intensity(self, position: float) -> float:
        """Calculate blend intensity for progressive blending."""
        # End region blending
        if position > (1.0 - self._blend_region):
            return (position - (1.0 - self._blend_region)) / self._blend_region
        # Start region blending (optional wrap continuation)
        elif position < self._blend_region:
            return (self._blend_region - position) / self._blend_region * 0.3
        return 0.0
    
    def _progressive_blend(self, position: float, base_color: Tuple[int, int, int],
                          gradient_stops: List[Tuple[float, Tuple[int, int, int]]],
                          blend_intensity: float) -> Tuple[int, int, int]:
        """Apply progressive blending in the blend region."""
        if not gradient_stops or len(gradient_stops) < 2:
            return base_color
        
        stops = sorted(gradient_stops, key=lambda x: x[0])
        first_color = stops[0][1]
        last_color = stops[-1][1]
        
        # Progressive blend toward first color in the end region
        if position > (1.0 - self._blend_region):
            return blend_colors(base_color, first_color, blend_intensity * self.intensity_falloff)
        # Optional start region blending
        elif position < self._blend_region:
            return blend_colors(base_color, last_color, blend_intensity * self.intensity_falloff * 0.5)
        
        return base_color
    
    def get_blend_preview_data(self) -> dict:
        """Get data for rendering preview overlays."""
        return {
            'enabled': self.enabled,
            'progressive_enabled': self.progressive_enabled,
            'blend_region': self._blend_region,
            'preview_overlay': self.preview_overlay,
            'intensity_falloff': self.intensity_falloff
        }
    
    def set_progressive_blending(self, enabled: bool):
        self.progressive_enabled = enabled
    
    def set_intensity_falloff(self, falloff: float):
        self.intensity_falloff = max(0.0, min(1.0, falloff))
    
    def set_preview_overlay(self, enabled: bool):
        self.preview_overlay = enabled
    
    def copy(self) -> 'SeamlessBlending':
        new = SeamlessBlending()
        new.enabled = self.enabled
        new.progressive_enabled = self.progressive_enabled
        new.blend_region = self._blend_region
        new.intensity_falloff = self.intensity_falloff
        new.preview_overlay = self.preview_overlay
        return new
    
    def __repr__(self):
        return (f"SeamlessBlending(enabled={self.enabled}, progressive={self.progressive_enabled}, "
                f"blend_region={self._blend_region}, overlay={self.preview_overlay})")
