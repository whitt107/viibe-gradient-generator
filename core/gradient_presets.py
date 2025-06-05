#!/usr/bin/env python3
"""
Enhanced Gradient Presets Module for Gradient Generator

This module provides preset gradients with support for up to 64 color stops,
defaulting to 10 stops for basic presets.
"""
import json
import os
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .gradient import ColorStop


class GradientPresets:
    """Class for managing gradient presets with enhanced color stop support."""
    
    # Constants
    MAX_COLOR_STOPS = 64
    DEFAULT_STOPS = 10
    
    def __init__(self):
        """Initialize the presets manager."""
        # Built-in presets
        self.built_in_presets = {
            "default": self._create_default(),
            "rainbow": self._create_rainbow(),
            "sunset": self._create_sunset(),
            "fire": self._create_fire(),
            "ocean": self._create_ocean(),
            "grayscale": self._create_grayscale()
        }
        
        # Custom presets (loaded from/saved to file)
        self.custom_presets: Dict[str, List['ColorStop']] = {}
    
    def get_preset(self, preset_name: str) -> List['ColorStop']:
        """
        Get a preset gradient by name.
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            List of ColorStop objects
        """
        preset_name = preset_name.lower()
        
        # Check built-in presets first
        if preset_name in self.built_in_presets:
            return self.built_in_presets[preset_name]
        
        # Check custom presets
        if preset_name in self.custom_presets:
            return self.custom_presets[preset_name]
        
        # Default fallback
        return self._create_default()
    
    def save_preset(self, preset_name: str, color_stops: List['ColorStop']):
        """
        Save a custom preset.
        
        Args:
            preset_name: Name for the preset
            color_stops: List of ColorStop objects
        """
        # Limit to MAX_COLOR_STOPS if necessary
        if len(color_stops) > self.MAX_COLOR_STOPS:
            color_stops = color_stops[:self.MAX_COLOR_STOPS]
            
        self.custom_presets[preset_name] = color_stops.copy()
    
    def _create_color_stop(self, position: float, color: tuple) -> 'ColorStop':
        """Create a ColorStop object - imported here to avoid circular import."""
        from .gradient import ColorStop
        return ColorStop(position, color)
    
    def _create_default(self) -> List['ColorStop']:
        """Create default gradient with 10 stops from black to white."""
        stops = []
        
        # Create DEFAULT_STOPS color stops evenly distributed from black to white
        for i in range(self.DEFAULT_STOPS):
            position = i / (self.DEFAULT_STOPS - 1) if self.DEFAULT_STOPS > 1 else 0
            # Calculate color based on position (grayscale from black to white)
            value = int(255 * position)
            color = (value, value, value)
            
            stops.append(self._create_color_stop(position, color))
            
        return stops
    
    def _create_rainbow(self) -> List['ColorStop']:
        """Create enhanced rainbow gradient with more color transitions."""
        # Create a more detailed rainbow with up to 10 color stops
        return [
            self._create_color_stop(0.0, (255, 0, 0)),      # Red
            self._create_color_stop(0.125, (255, 127, 0)),  # Orange
            self._create_color_stop(0.25, (255, 255, 0)),   # Yellow
            self._create_color_stop(0.375, (127, 255, 0)),  # Chartreuse
            self._create_color_stop(0.5, (0, 255, 0)),      # Green
            self._create_color_stop(0.625, (0, 255, 127)),  # Spring green
            self._create_color_stop(0.75, (0, 127, 255)),   # Cyan
            self._create_color_stop(0.875, (0, 0, 255)),    # Blue
            self._create_color_stop(0.9375, (127, 0, 255)), # Violet
            self._create_color_stop(1.0, (255, 0, 255)),    # Magenta
        ]
    
    def _create_sunset(self) -> List['ColorStop']:
        """Create enhanced sunset gradient."""
        return [
            self._create_color_stop(0.0, (15, 10, 39)),     # Deep night blue
            self._create_color_stop(0.2, (44, 33, 100)),    # Purple
            self._create_color_stop(0.4, (130, 55, 150)),   # Pink-purple
            self._create_color_stop(0.5, (191, 64, 95)),    # Deep pink
            self._create_color_stop(0.6, (255, 93, 35)),    # Dark orange
            self._create_color_stop(0.7, (254, 192, 81)),   # Orange-yellow
            self._create_color_stop(0.8, (255, 229, 119)),  # Light yellow
            self._create_color_stop(0.9, (255, 247, 229)),  # Very light yellow
            self._create_color_stop(1.0, (200, 255, 255)),  # Light blue-white
        ]
    
    def _create_fire(self) -> List['ColorStop']:
        """Create enhanced fire gradient with more variation."""
        return [
            self._create_color_stop(0.0, (7, 5, 9)),        # Almost black
            self._create_color_stop(0.1, (31, 7, 1)),       # Very dark red
            self._create_color_stop(0.25, (80, 11, 0)),     # Dark red
            self._create_color_stop(0.4, (142, 27, 0)),     # Medium red
            self._create_color_stop(0.5, (204, 47, 0)),     # Bright red
            self._create_color_stop(0.6, (255, 91, 0)),     # Red-orange
            self._create_color_stop(0.7, (255, 135, 0)),    # Orange
            self._create_color_stop(0.8, (255, 180, 0)),    # Yellow-orange
            self._create_color_stop(0.9, (255, 220, 0)),    # Yellow
            self._create_color_stop(1.0, (255, 255, 224)),  # Light yellow
        ]
    
    def _create_ocean(self) -> List['ColorStop']:
        """Create enhanced ocean gradient with more depth levels."""
        return [
            self._create_color_stop(0.0, (0, 5, 30)),       # Abyss blue
            self._create_color_stop(0.1, (0, 10, 50)),      # Very deep blue
            self._create_color_stop(0.2, (0, 20, 80)),      # Deep blue
            self._create_color_stop(0.3, (0, 30, 100)),     # Deep blue
            self._create_color_stop(0.4, (0, 40, 120)),     # Medium deep blue
            self._create_color_stop(0.5, (0, 60, 153)),     # Medium blue
            self._create_color_stop(0.6, (0, 85, 180)),     # Blue
            self._create_color_stop(0.7, (0, 120, 200)),    # Lighter blue
            self._create_color_stop(0.8, (0, 160, 215)),    # Light blue
            self._create_color_stop(0.9, (42, 200, 232)),   # Cyan-blue
            self._create_color_stop(1.0, (110, 230, 244)),  # Very light blue
        ]
    
    def _create_grayscale(self) -> List['ColorStop']:
        """Create enhanced grayscale gradient with more steps."""
        stops = []
        
        # Create DEFAULT_STOPS color stops evenly distributed in grayscale
        for i in range(self.DEFAULT_STOPS):
            position = i / (self.DEFAULT_STOPS - 1) if self.DEFAULT_STOPS > 1 else 0
            value = int(position * 255)
            stops.append(self._create_color_stop(position, (value, value, value)))
            
        return stops
    
    def load_custom_presets(self, file_path: str):
        """
        Load custom presets from a JSON file.
        
        Args:
            file_path: Path to the presets JSON file
        """
        if not os.path.exists(file_path):
            return
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.custom_presets = {}
            for name, stops_data in data.items():
                stops = []
                for stop_data in stops_data:
                    stops.append(self._create_color_stop(
                        stop_data['position'],
                        tuple(stop_data['color'])
                    ))
                self.custom_presets[name] = stops
        except Exception as e:
            print(f"Error loading custom presets: {e}")
    
    def save_custom_presets(self, file_path: str):
        """
        Save custom presets to a JSON file.
        
        Args:
            file_path: Path where to save the presets
        """
        data = {}
        
        for name, stops in self.custom_presets.items():
            stops_data = []
            for stop in stops:
                stops_data.append({
                    'position': stop.position,
                    'color': list(stop.color)
                })
            data[name] = stops_data
        
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving custom presets: {e}")
