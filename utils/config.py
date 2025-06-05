#!/usr/bin/env python3
"""
Configuration Module for Gradient Generator

This module handles application configuration, including user preferences,
recent files, and default settings.
"""
import os
import json
from PyQt5.QtCore import QSettings


class Config:
    """Configuration manager for the Gradient Generator application."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        # Use QSettings for cross-platform settings storage
        self.settings = QSettings("GradientGenerator", "JWildfire")
        
        # Default configuration values
        self.defaults = {
            # UI settings
            "window_width": 800,
            "window_height": 600,
            "splitter_sizes": [320, 480],
            "preview_type": "linear",
            "preview_size": 256,
            "show_color_points": True,
            
            # Export settings
            "export_format": "map",
            "export_quality": 100,
            "export_size": 512,
            "last_export_dir": "",
            
            # Default metadata
            "default_author": "",
            "default_category": "Custom",
            
            # Recent files
            "recent_files": [],
            "max_recent_files": 10,
            
            # Presets directory
            "presets_dir": ""
        }
        
        # Ensure presets directory exists
        self._ensure_presets_dir()
    
    def _ensure_presets_dir(self):
        """Ensure that the presets directory exists."""
        presets_dir = self.get("presets_dir")
        
        if not presets_dir:
            # Use default location in user's home directory
            home_dir = os.path.expanduser("~")
            presets_dir = os.path.join(home_dir, ".gradient_generator", "presets")
            self.set("presets_dir", presets_dir)
        
        # Create directory if it doesn't exist
        os.makedirs(presets_dir, exist_ok=True)
    
    def get(self, key, default=None):
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found (defaults to None)
            
        Returns:
            Configuration value or default
        """
        # Use the provided default or the default from self.defaults
        if default is None and key in self.defaults:
            default = self.defaults[key]
        
        # Get from QSettings
        value = self.settings.value(key, default)
        
        # Convert certain types based on default
        if default is not None:
            if isinstance(default, bool):
                # Convert string to bool
                if isinstance(value, str):
                    return value.lower() in ("true", "1", "yes")
                return bool(value)
            elif isinstance(default, int):
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return default
            elif isinstance(default, float):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return default
            elif isinstance(default, list):
                # Handle lists (stored as JSON)
                if isinstance(value, str):
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return default
                return value
        
        return value
    
    def set(self, key, value):
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        # Handle special types
        if isinstance(value, list):
            # Store lists as JSON
            value = json.dumps(value)
        
        # Store in QSettings
        self.settings.setValue(key, value)
        self.settings.sync()
    
    def add_recent_file(self, file_path):
        """
        Add a file to the recent files list.
        
        Args:
            file_path: Path to the file
        """
        recent_files = self.get("recent_files", [])
        max_recent = self.get("max_recent_files")
        
        # Remove if already in list
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to the beginning
        recent_files.insert(0, file_path)
        
        # Trim list to max size
        recent_files = recent_files[:max_recent]
        
        # Save updated list
        self.set("recent_files", recent_files)
    
    def clear_recent_files(self):
        """Clear the recent files list."""
        self.set("recent_files", [])
    
    def save_window_state(self, window):
        """
        Save the state of the main window.
        
        Args:
            window: Main window instance
        """
        self.set("window_geometry", window.saveGeometry())
        self.set("window_state", window.saveState())
    
    def restore_window_state(self, window):
        """
        Restore the state of the main window.
        
        Args:
            window: Main window instance
        """
        geometry = self.get("window_geometry")
        state = self.get("window_state")
        
        if geometry:
            window.restoreGeometry(geometry)
        if state:
            window.restoreState(state)
    
    def save_splitter_state(self, splitter):
        """
        Save the state of a splitter.
        
        Args:
            splitter: QSplitter instance
        """
        self.set("splitter_sizes", splitter.sizes())
    
    def restore_splitter_state(self, splitter):
        """
        Restore the state of a splitter.
        
        Args:
            splitter: QSplitter instance
        """
        sizes = self.get("splitter_sizes")
        if sizes:
            splitter.setSizes(sizes)
    
    def get_presets_dir(self):
        """
        Get the directory where gradient presets are stored.
        
        Returns:
            Path to presets directory
        """
        return self.get("presets_dir")
    
    def set_presets_dir(self, directory):
        """
        Set the directory where gradient presets are stored.
        
        Args:
            directory: Path to presets directory
        """
        self.set("presets_dir", directory)
        
        # Ensure directory exists
        os.makedirs(directory, exist_ok=True)
