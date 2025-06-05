#!/usr/bin/env python3
"""
Session Manager Module for Gradient Generator

This module handles saving and loading gradient sessions.
"""
import os
import json
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from .gradient_serializer import GradientSerializer


class SessionManager:
    """Manages saving and loading gradient sessions."""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.serializer = GradientSerializer()
    
    def save_session(self):
        """Save the current session including all gradients in the list."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window, "Save Session", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                session_data = self._create_session_data()
                with open(file_path, 'w') as f:
                    json.dump(session_data, f, indent=2)
                
                self.main_window.statusBar().showMessage(
                    f"Session saved: {os.path.basename(file_path)}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self.main_window, "Error", 
                    f"Failed to save session: {str(e)}"
                )
    
    def load_session(self):
        """Load a saved session."""
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window, "Load Session", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    session_data = json.load(f)
                
                self._load_session_data(session_data)
                self.main_window.statusBar().showMessage(
                    f"Session loaded: {os.path.basename(file_path)}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self.main_window, "Error", 
                    f"Failed to load session: {str(e)}"
                )
    
    def _create_session_data(self):
        """Create session data for saving."""
        session_data = {
            "current_gradient": self.serializer.serialize_gradient(
                self.main_window.current_gradient
            ),
            "gradient_list": []
        }
        
        for gradient, name in self.main_window.gradient_list_panel.gradients:
            session_data["gradient_list"].append({
                "name": name,
                "gradient": self.serializer.serialize_gradient(gradient)
            })
        
        return session_data
    
    def _load_session_data(self, session_data):
        """Load session data."""
        # Clear current list
        self.main_window.gradient_list_panel.clear_all_gradients()
        
        # Load gradients
        for item in session_data.get("gradient_list", []):
            gradient = self.serializer.deserialize_gradient(item["gradient"])
            self.main_window.gradient_list_panel.add_gradient(gradient, item["name"])
        
        # Load current gradient if present
        if "current_gradient" in session_data:
            current = self.serializer.deserialize_gradient(session_data["current_gradient"])
            self.main_window.gradient_operations.apply_generated_gradient(current)
