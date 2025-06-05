#!/usr/bin/env python3
"""
Updated Gradient Core Module with Simplified Seamless Blending - Sorting Removed for True Randomization

Key changes:
- Removed all automatic sorting of color stops to allow true randomization
- get_interpolated_color now applies basic seamless (last = first) when enabled
- Progressive blending moved to preview-only functionality
- Streamlined seamless implementation
- Color stops maintain their original order as added
"""
import copy
import hashlib
import time
from typing import List, Tuple, Optional, Dict, Any
from .color_utils import blend_colors
from .gradient_metadata import GradientMetadata
from .gradient_seamless import SeamlessBlending
from .gradient_presets import GradientPresets


class ColorStop:
    """Represents a single color stop in a gradient."""
    
    def __init__(self, position: float, color: Tuple[int, int, int]):
        self.position = max(0.0, min(1.0, position))
        self.color = tuple(max(0, min(255, c)) for c in color)
    
    def __eq__(self, other):
        return isinstance(other, ColorStop) and self.position == other.position and self.color == other.color
    
    def __lt__(self, other):
        return self.position < other.position
    
    def __repr__(self):
        return f"ColorStop({self.position}, {self.color})"


class Gradient:
    """Enhanced gradient class with simplified seamless blending and no automatic sorting."""
    
    MAX_COLOR_STOPS = 64
    DEFAULT_STOPS = 10
    
    def __init__(self):
        self._color_stops: List[ColorStop] = []
        self._metadata = GradientMetadata()
        self._seamless = SeamlessBlending()
        self._presets = GradientPresets()
        self._initialize_default()
    
    def _initialize_default(self):
        """Set up default gradient with grayscale stops."""
        self._color_stops = []
        for i in range(self.DEFAULT_STOPS):
            position = i / (self.DEFAULT_STOPS - 1) if self.DEFAULT_STOPS > 1 else 0
            value = int(255 * position)
            self._color_stops.append(ColorStop(position, (value, value, value)))
    
    def get_interpolated_color(self, position: float) -> Tuple[int, int, int]:
        """Get interpolated color with basic seamless blending support."""
        position = max(0.0, min(1.0, position))
        
        if not self._color_stops:
            return (128, 128, 128)
        
        if len(self._color_stops) == 1:
            return self._color_stops[0].color
        
        # For seamless blending, use modified stops where last = first
        if self._seamless.enabled:
            effective_stops = self._get_seamless_stops()
        else:
            effective_stops = [(stop.position, stop.color) for stop in self._color_stops]
        
        return self._interpolate_from_stops(position, effective_stops)
    
    def get_interpolated_color_for_preview(self, position: float) -> Tuple[int, int, int]:
        """Get interpolated color for preview with FIXED seamless handling."""
        position = max(0.0, min(1.0, position))
        
        if not self._seamless.enabled:
            return self.get_interpolated_color(position)
        
        # For seamless preview, use modified stops
        if self._seamless.progressive_enabled:
            # Progressive blending preview
            return self._seamless.get_seamless_color(
                position, 
                self._get_base_color,
                self.get_color_stops()
            )
        else:
            # Basic seamless preview - use stops with last=first color
            preview_stops = self.get_seamless_preview_stops()
            return self._interpolate_from_stops(position, preview_stops)
    
    def _get_seamless_stops(self) -> List[Tuple[float, Tuple[int, int, int]]]:
        """Get color stops with seamless modification (last color = first color)."""
        stops = [(stop.position, stop.color) for stop in self._color_stops]
        
        if len(stops) >= 2:
            # Replace last color with first color
            last_pos = stops[-1][0]
            first_color = stops[0][1]
            stops[-1] = (last_pos, first_color)
        
        return stops
    
    def _get_base_color(self, position: float) -> Tuple[int, int, int]:
        """Get interpolated color without any seamless modifications."""
        position = max(0.0, min(1.0, position))
        
        if not self._color_stops:
            return (128, 128, 128)
        
        if len(self._color_stops) == 1:
            return self._color_stops[0].color
        
        effective_stops = [(stop.position, stop.color) for stop in self._color_stops]
        return self._interpolate_from_stops(position, effective_stops)
    
    def _interpolate_from_stops(self, position: float, stops: List[Tuple[float, Tuple[int, int, int]]]) -> Tuple[int, int, int]:
        """Interpolate color from a list of stops."""
        if not stops:
            return (128, 128, 128)
        
        if len(stops) == 1:
            return stops[0][1]
        
        # Find bracketing stops
        before = after = None
        for stop_pos, stop_color in stops:
            if stop_pos <= position and (before is None or stop_pos > before[0]):
                before = (stop_pos, stop_color)
            if stop_pos >= position and (after is None or stop_pos < after[0]):
                after = (stop_pos, stop_color)
        
        if before is None:
            return stops[0][1]
        if after is None:
            return stops[-1][1]
        if before[0] == after[0]:
            return before[1]
        
        blend_factor = (position - before[0]) / (after[0] - before[0])
        return blend_colors(before[1], after[1], blend_factor)
    
    def apply_seamless_permanently(self):
        """Permanently apply seamless blending by modifying the actual color stops."""
        if not self._seamless.enabled or len(self._color_stops) < 2:
            return False
        
        # Replace last stop color with first stop color
        first_color = self._color_stops[0].color
        self._color_stops[-1].color = first_color
        
        return True
    
    # Core gradient operations
    def reset(self):
        """Reset to default state."""
        self._initialize_default()
        self._metadata.reset()
        self._seamless.reset()
    
    def is_empty(self) -> bool:
        """Check if gradient is in default state."""
        if len(self._color_stops) != self.DEFAULT_STOPS:
            return False
        
        for i, stop in enumerate(self._color_stops):
            expected_pos = i / (self.DEFAULT_STOPS - 1) if self.DEFAULT_STOPS > 1 else 0
            expected_val = int(255 * expected_pos)
            expected_color = (expected_val, expected_val, expected_val)
            
            if abs(stop.position - expected_pos) > 0.001 or stop.color != expected_color:
                return False
        
        return self._metadata.is_default()
    
    # Color stop management
    def get_color_stops(self) -> List[Tuple[float, Tuple[int, int, int]]]:
        """Get color stops as tuples - maintains original order."""
        return [(stop.position, stop.color) for stop in self._color_stops]
    
    def get_color_stops_for_preview(self) -> List[Tuple[float, Tuple[int, int, int]]]:
        """Get color stops for preview - may include seamless modifications."""
        if self._seamless.enabled and not self._seamless.progressive_enabled:
            return self._get_seamless_stops()
        else:
            return self.get_color_stops()
    def get_seamless_preview_stops(self):
        """
        Get color stops modified for seamless preview display.
        This is ONLY for preview - doesn't modify the actual gradient.
        """
        if not self._seamless.enabled:
            return self.get_color_stops()
        
        current_stops = self.get_color_stops()
        if len(current_stops) < 2:
            return current_stops
        
        # Sort stops by position to find true first and last
        sorted_stops = sorted(current_stops, key=lambda x: x[0])
        
        # Identify first and last stops properly
        first_stop = sorted_stops[0]
        last_stop = sorted_stops[-1]
        
        first_pos, first_color = first_stop
        last_pos, last_color = last_stop
        
        # For preview, create modified stops where last color = first color
        preview_stops = []
        for pos, color in current_stops:
            if abs(pos - last_pos) < 1e-6:  # This is a last position stop
                preview_stops.append((pos, first_color))  # Use first color
            else:
                preview_stops.append((pos, color))  # Keep original color
        
        return preview_stops

    
    def get_color_stop_objects(self) -> List[ColorStop]:
        """Get ColorStop objects - maintains original order."""
        return self._color_stops.copy()
    
    def add_color_stop(self, position: float, color: Tuple[int, int, int]) -> bool:
        """Add new color stop - REMOVED SORTING to allow random positions."""
        if len(self._color_stops) >= self.MAX_COLOR_STOPS:
            return False
        self._color_stops.append(ColorStop(position, color))
        # NO SORTING - maintains order as added
        return True
    
    def remove_color_stop_at_index(self, index: int):
        """Remove color stop by index."""
        if 0 <= index < len(self._color_stops) and len(self._color_stops) > 1:
            self._color_stops.pop(index)
    
    def set_color_at_index(self, index: int, color: Tuple[int, int, int]):
        """Set color at index."""
        if 0 <= index < len(self._color_stops):
            self._color_stops[index].color = tuple(max(0, min(255, c)) for c in color)
    
    def set_position_at_index(self, index: int, position: float):
        """Set position at index."""
        if 0 <= index < len(self._color_stops):
            self._color_stops[index].position = max(0.0, min(1.0, position))
    
    def sort_color_stops(self):
        """Sort color stops by position - OPTIONAL method for manual sorting only."""
        self._color_stops.sort()
    
    def distribute_stops_evenly(self):
        """Distribute color stops evenly while preserving colors and order."""
        if len(self._color_stops) <= 1:
            return
        
        # Preserve the current order and colors, just redistribute positions
        colors = [stop.color for stop in self._color_stops]
        for i, color in enumerate(colors):
            position = i / (len(colors) - 1) if len(colors) > 1 else 0.5
            self._color_stops[i] = ColorStop(position, color)
    
    # Utility methods
    def get_sample_colors(self, num_samples: int = 256) -> List[Tuple[int, int, int]]:
        """Get evenly sampled colors."""
        return [self.get_interpolated_color(i / (num_samples - 1)) 
                for i in range(num_samples)]
    
    def get_sample_colors_for_preview(self, num_samples: int = 256) -> List[Tuple[int, int, int]]:
        """Get evenly sampled colors for preview (with progressive blending if enabled)."""
        return [self.get_interpolated_color_for_preview(i / (num_samples - 1)) 
                for i in range(num_samples)]
    
    def apply_preset(self, preset_name: str):
        """Apply preset gradient."""
        self._color_stops = self._presets.get_preset(preset_name)
    
    def save_as_preset(self, preset_name: str):
        """Save as preset."""
        self._presets.save_preset(preset_name, self._color_stops)
        self._metadata.name = preset_name
    
    # Metadata properties (consolidated)
    def get_name(self) -> str: return self._metadata.name
    def set_name(self, name: str): self._metadata.name = name
    def get_author(self) -> str: return self._metadata.author
    def set_author(self, author: str): self._metadata.author = author
    def get_description(self) -> str: return self._metadata.description
    def set_description(self, desc: str): self._metadata.description = desc
    def get_ugr_category(self) -> str: return self._metadata.ugr_category
    def set_ugr_category(self, cat: str): self._metadata.ugr_category = cat
    def get_combine_gradients(self) -> bool: return self._metadata.combine_gradients
    def set_combine_gradients(self, combine: bool): self._metadata.combine_gradients = combine
    
    # Seamless blending properties
    def get_seamless_blend(self) -> bool: return self._seamless.enabled
    def set_seamless_blend(self, enabled: bool): self._seamless.enabled = enabled
    def get_blend_region(self) -> float: return self._seamless.blend_region
    def set_blend_region(self, region: float): self._seamless.blend_region = region
    def get_progressive_blending(self) -> bool: return self._seamless.progressive_enabled
    def set_progressive_blending(self, enabled: bool): self._seamless.set_progressive_blending(enabled)
    def get_intensity_falloff(self) -> float: return self._seamless.intensity_falloff
    def set_intensity_falloff(self, falloff: float): self._seamless.set_intensity_falloff(falloff)
    def get_preview_overlay(self) -> bool: return self._seamless.preview_overlay
    def set_preview_overlay(self, enabled: bool): self._seamless.set_preview_overlay(enabled)
    
    # State management (streamlined)
    def get_full_state(self) -> Dict[str, Any]:
        """Get complete state for serialization."""
        return {
            "color_stops": self.get_color_stops(),
            "name": self.get_name(),
            "author": self.get_author(),
            "description": self.get_description(),
            "ugr_category": self.get_ugr_category(),
            "combine_gradients": self.get_combine_gradients(),
            "seamless_blend": self.get_seamless_blend(),
            "blend_region": self.get_blend_region(),
            "progressive_blending": self.get_progressive_blending(),
            "intensity_falloff": self.get_intensity_falloff(),
            "preview_overlay": self.get_preview_overlay()
        }
    
    def set_full_state(self, state: Dict[str, Any]):
        """Restore complete state from serialization."""
        self._color_stops = []
        for position, color in state.get("color_stops", []):
            self.add_color_stop(position, color)
        
        # Restore all properties
        for prop, value in state.items():
            if hasattr(self, f"set_{prop}"):
                getattr(self, f"set_{prop}")(value)
    
    def clone(self) -> 'Gradient':
        """Create deep copy."""
        new_gradient = Gradient()
        new_gradient._color_stops = [ColorStop(s.position, s.color) for s in self._color_stops]
        new_gradient._metadata = copy.deepcopy(self._metadata)
        new_gradient._seamless = copy.deepcopy(self._seamless)
        return new_gradient
    
    def copy_state_from(self, other_gradient):
        """Copy state from another gradient."""
        if hasattr(other_gradient, 'get_full_state'):
            self.set_full_state(other_gradient.get_full_state())
        else:
            # Legacy fallback
            self._color_stops = []
            for pos, color in other_gradient.get_color_stops():
                self.add_color_stop(pos, color)
            
            # Copy metadata safely
            for attr in ['name', 'author', 'description', 'ugr_category', 'combine_gradients']:
                if hasattr(other_gradient, f'get_{attr}'):
                    setattr(self._metadata, attr, getattr(other_gradient, f'get_{attr}')())
    
    # Analysis and validation
    def validate_state_integrity(self) -> Tuple[bool, List[str]]:
        """Validate gradient state."""
        issues = []
        
        if not self._color_stops:
            issues.append("No color stops")
        elif len(self._color_stops) > self.MAX_COLOR_STOPS:
            issues.append(f"Too many stops ({len(self._color_stops)})")
        
        for i, stop in enumerate(self._color_stops):
            if not (0.0 <= stop.position <= 1.0):
                issues.append(f"Stop {i} invalid position: {stop.position}")
            
            if not all(0 <= c <= 255 for c in stop.color):
                issues.append(f"Stop {i} invalid color: {stop.color}")
        
        if not (0.0 <= self.get_blend_region() <= 0.5):
            issues.append(f"Invalid blend region: {self.get_blend_region()}")
        
        return len(issues) == 0, issues
    
    def get_color_stats(self) -> Dict[str, Any]:
        """Get color statistics."""
        if not self._color_stops:
            return {"error": "No color stops"}
        
        colors = [stop.color for stop in self._color_stops]
        components = list(zip(*colors))
        
        return {
            "stop_count": len(colors),
            "unique_colors": len(set(colors)),
            "red_range": (min(components[0]), max(components[0])),
            "green_range": (min(components[1]), max(components[1])),
            "blue_range": (min(components[2]), max(components[2])),
            "avg_brightness": sum(0.299*r + 0.587*g + 0.114*b for r,g,b in colors) / len(colors),
            "seamless_enabled": self.get_seamless_blend(),
            "progressive_enabled": self.get_progressive_blending()
        }
    
    # Backup and recovery (streamlined)
    def create_backup_state(self) -> Dict[str, Any]:
        """Create backup with metadata."""
        return {
            "gradient_state": self.get_full_state(),
            "backup_metadata": {
                "timestamp": time.time(),
                "checksum": self._calculate_checksum(),
                "version": "2.0"
            }
        }
    
    def restore_from_backup(self, backup: Dict[str, Any]) -> bool:
        """Restore from backup."""
        try:
            self.set_full_state(backup["gradient_state"])
            return True
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
    
    def _calculate_checksum(self) -> str:
        """Calculate state checksum."""
        state_str = ""
        for stop in self._color_stops:
            state_str += f"{stop.position:.6f}:{stop.color[0]}:{stop.color[1]}:{stop.color[2]}|"
        state_str += f"seamless:{self.get_seamless_blend()}|region:{self.get_blend_region():.6f}"
        return hashlib.md5(state_str.encode()).hexdigest()[:16]
    
    # Advanced operations
    def interpolate_to_size(self, target_count: int) -> 'Gradient':
        """Create gradient with specified number of evenly distributed stops."""
        target_count = max(2, min(self.MAX_COLOR_STOPS, target_count))
        
        new_gradient = Gradient()
        new_gradient.set_name(f"{self.get_name()} (Interpolated {target_count})")
        new_gradient.copy_state_from(self)
        
        new_gradient._color_stops = []
        for i in range(target_count):
            position = i / (target_count - 1) if target_count > 1 else 0.5
            color = self.get_interpolated_color(position)
            new_gradient.add_color_stop(position, color)
        
        return new_gradient
    
    def get_dominant_colors(self, num_colors: int = 5) -> List[Tuple[Tuple[int, int, int], float]]:
        """Get dominant colors with weights."""
        samples = self.get_sample_colors(100)
        
        # Group similar colors
        color_groups = {}
        tolerance = 20
        
        for color in samples:
            found = False
            for group_color in color_groups:
                if all(abs(color[i] - group_color[i]) <= tolerance for i in range(3)):
                    color_groups[group_color] += 1
                    found = True
                    break
            if not found:
                color_groups[color] = 1
        
        # Sort by frequency and normalize
        sorted_colors = sorted(color_groups.items(), key=lambda x: x[1], reverse=True)
        total_weight = sum(weight for _, weight in sorted_colors)
        
        return [(color, weight/total_weight) for color, weight in sorted_colors[:num_colors]]