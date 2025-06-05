#!/usr/bin/env python3
"""
Gradient History Manager Module for Undo/Redo Functionality

This module provides history management for gradient changes in the animated preview.
"""
import copy
import time
from typing import List, Optional, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal


class GradientState:
    """Represents a single gradient state in history."""
    
    def __init__(self, gradient_data: Dict[str, Any], timestamp: float = None):
        """
        Initialize a gradient state.
        
        Args:
            gradient_data: Serialized gradient data
            timestamp: When this state was created (default: current time)
        """
        self.gradient_data = copy.deepcopy(gradient_data)
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.description = self._generate_description()
    
    def _generate_description(self) -> str:
        """Generate a human-readable description of this state."""
        try:
            stops_count = len(self.gradient_data.get('color_stops', []))
            name = self.gradient_data.get('name', 'Unnamed')
            return f"{name} ({stops_count} stops)"
        except:
            return "Gradient State"
    
    def get_data(self) -> Dict[str, Any]:
        """Get a deep copy of the gradient data."""
        return copy.deepcopy(self.gradient_data)


class GradientHistoryManager(QObject):
    """Manages undo/redo history for gradient changes."""
    
    # Signals
    history_changed = pyqtSignal()  # Emitted when history state changes
    undo_available = pyqtSignal(bool)  # Emitted when undo availability changes
    redo_available = pyqtSignal(bool)  # Emitted when redo availability changes
    
    def __init__(self, max_history_size: int = 50):
        """
        Initialize the history manager.
        
        Args:
            max_history_size: Maximum number of states to keep in history
        """
        super().__init__()
        
        self.max_history_size = max_history_size
        self.history: List[GradientState] = []
        self.current_index = -1  # Index of current state in history
        self.is_enabled = True
        
        # State tracking
        self.last_save_time = 0
        self.min_save_interval = 0.5  # Minimum seconds between automatic saves
    
    def serialize_gradient(self, gradient) -> Dict[str, Any]:
        """
        Serialize a gradient to a dictionary.
        
        Args:
            gradient: Gradient object to serialize
            
        Returns:
            Dictionary containing gradient data
        """
        try:
            return {
                "color_stops": gradient.get_color_stops(),
                "name": gradient.get_name(),
                "author": gradient.get_author(),
                "description": gradient.get_description(),
                "ugr_category": gradient.get_ugr_category(),
                "combine_gradients": gradient.get_combine_gradients(),
                "seamless_blend": gradient.get_seamless_blend(),
                "blend_region": gradient.get_blend_region()
            }
        except Exception as e:
            print(f"Error serializing gradient: {e}")
            return {}
    
    def deserialize_gradient(self, gradient, data: Dict[str, Any]):
        """
        Deserialize gradient data back to a gradient object.
        
        Args:
            gradient: Gradient object to update
            data: Dictionary containing gradient data
        """
        try:
            # Clear existing stops
            gradient._color_stops = []
            
            # Restore color stops
            for position, color in data.get("color_stops", []):
                gradient.add_color_stop(position, color)
            
            # Restore metadata
            gradient.set_name(data.get("name", ""))
            gradient.set_author(data.get("author", ""))
            gradient.set_description(data.get("description", ""))
            gradient.set_ugr_category(data.get("ugr_category", "Custom"))
            gradient.set_combine_gradients(data.get("combine_gradients", False))
            gradient.set_seamless_blend(data.get("seamless_blend", False))
            gradient.set_blend_region(data.get("blend_region", 0.1))
            
        except Exception as e:
            print(f"Error deserializing gradient: {e}")
    
    def save_state(self, gradient, force: bool = False, description: str = None):
        """
        Save the current gradient state to history.
        
        Args:
            gradient: Current gradient to save
            force: Force save even if within minimum interval
            description: Optional description for this state
        """
        if not self.is_enabled:
            return
        
        current_time = time.time()
        
        # Check minimum save interval unless forced
        if not force and (current_time - self.last_save_time) < self.min_save_interval:
            return
        
        try:
            # Serialize current gradient
            gradient_data = self.serialize_gradient(gradient)
            
            # Don't save if data is empty or invalid
            if not gradient_data or not gradient_data.get("color_stops"):
                return
            
            # Check if this state is different from the current one
            if self.current_index >= 0 and self.current_index < len(self.history):
                current_state = self.history[self.current_index]
                if self._states_equal(gradient_data, current_state.gradient_data):
                    return  # No change, don't save duplicate state
            
            # Create new state
            new_state = GradientState(gradient_data, current_time)
            if description:
                new_state.description = description
            
            # Remove any history after current index (we're creating a new branch)
            if self.current_index < len(self.history) - 1:
                self.history = self.history[:self.current_index + 1]
            
            # Add new state
            self.history.append(new_state)
            self.current_index = len(self.history) - 1
            
            # Limit history size
            if len(self.history) > self.max_history_size:
                self.history = self.history[-self.max_history_size:]
                self.current_index = len(self.history) - 1
            
            self.last_save_time = current_time
            
            # Emit signals
            self._emit_availability_signals()
            self.history_changed.emit()
            
        except Exception as e:
            print(f"Error saving gradient state: {e}")
    
    def undo(self, gradient) -> bool:
        """
        Undo to the previous state.
        
        Args:
            gradient: Gradient object to update
            
        Returns:
            True if undo was successful, False otherwise
        """
        if not self.can_undo():
            return False
        
        try:
            # Move to previous state
            self.current_index -= 1
            
            # Apply the state
            state = self.history[self.current_index]
            self.deserialize_gradient(gradient, state.gradient_data)
            
            # Emit signals
            self._emit_availability_signals()
            self.history_changed.emit()
            
            return True
            
        except Exception as e:
            print(f"Error during undo: {e}")
            return False
    
    def redo(self, gradient) -> bool:
        """
        Redo to the next state.
        
        Args:
            gradient: Gradient object to update
            
        Returns:
            True if redo was successful, False otherwise
        """
        if not self.can_redo():
            return False
        
        try:
            # Move to next state
            self.current_index += 1
            
            # Apply the state
            state = self.history[self.current_index]
            self.deserialize_gradient(gradient, state.gradient_data)
            
            # Emit signals
            self._emit_availability_signals()
            self.history_changed.emit()
            
            return True
            
        except Exception as e:
            print(f"Error during redo: {e}")
            return False
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self.is_enabled and self.current_index > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self.is_enabled and self.current_index < len(self.history) - 1
    
    def clear_history(self):
        """Clear all history."""
        self.history.clear()
        self.current_index = -1
        self._emit_availability_signals()
        self.history_changed.emit()
    
    def set_enabled(self, enabled: bool):
        """Enable or disable history tracking."""
        self.is_enabled = enabled
        self._emit_availability_signals()
    
    def get_current_state_description(self) -> str:
        """Get description of current state."""
        if self.current_index >= 0 and self.current_index < len(self.history):
            return self.history[self.current_index].description
        return "No state"
    
    def get_history_info(self) -> Dict[str, Any]:
        """Get information about the current history state."""
        return {
            "total_states": len(self.history),
            "current_index": self.current_index,
            "can_undo": self.can_undo(),
            "can_redo": self.can_redo(),
            "current_description": self.get_current_state_description(),
            "is_enabled": self.is_enabled
        }
    
    def _states_equal(self, state1: Dict[str, Any], state2: Dict[str, Any]) -> bool:
        """
        Compare two gradient states for equality.
        
        Args:
            state1: First state to compare
            state2: Second state to compare
            
        Returns:
            True if states are equal, False otherwise
        """
        try:
            # Compare color stops
            stops1 = state1.get("color_stops", [])
            stops2 = state2.get("color_stops", [])
            
            if len(stops1) != len(stops2):
                return False
            
            for (pos1, color1), (pos2, color2) in zip(stops1, stops2):
                if abs(pos1 - pos2) > 0.001 or color1 != color2:
                    return False
            
            # Compare other properties that affect the gradient
            properties = ["seamless_blend", "blend_region"]
            for prop in properties:
                if state1.get(prop) != state2.get(prop):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _emit_availability_signals(self):
        """Emit signals about undo/redo availability."""
        self.undo_available.emit(self.can_undo())
        self.redo_available.emit(self.can_redo())
