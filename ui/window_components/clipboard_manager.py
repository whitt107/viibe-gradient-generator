#!/usr/bin/env python3
"""
Clipboard Manager Module for Gradient Generator

This module handles clipboard operations for copying and pasting gradients.
"""
import json
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QMimeData

from .gradient_serializer import GradientSerializer


class ClipboardManager:
    """Manages clipboard operations for gradients."""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.serializer = GradientSerializer()
    
    def copy_gradient(self):
        """Copy current gradient to clipboard."""
        try:
            gradient_data = self.serializer.serialize_gradient(
                self.main_window.current_gradient
            )
            gradient_json = json.dumps(gradient_data)
            
            clipboard = QApplication.clipboard()
            mime_data = QMimeData()
            mime_data.setText(gradient_json)
            mime_data.setData("application/x-gradient", gradient_json.encode())
            clipboard.setMimeData(mime_data)
            
            self.main_window.statusBar().showMessage("Gradient copied to clipboard")
        except Exception as e:
            QMessageBox.critical(
                self.main_window, "Error", 
                f"Failed to copy gradient: {str(e)}"
            )
    
    def paste_gradient(self):
        """Paste gradient from clipboard."""
        try:
            gradient_data = self._get_gradient_from_clipboard()
            
            if gradient_data:
                gradient = self.serializer.deserialize_gradient(gradient_data)
                self.main_window.gradient_operations.apply_generated_gradient(gradient)
                self.main_window.statusBar().showMessage("Gradient pasted from clipboard")
            else:
                QMessageBox.warning(
                    self.main_window, "No Data", 
                    "No gradient data found in clipboard."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self.main_window, "Error", 
                f"Failed to paste gradient: {str(e)}"
            )
    
    def _get_gradient_from_clipboard(self):
        """Get gradient data from clipboard."""
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        # Try to get gradient data from custom MIME type
        if mime_data.hasFormat("application/x-gradient"):
            gradient_json = str(mime_data.data("application/x-gradient"), 'utf-8')
            return json.loads(gradient_json)
        # Fall back to text
        elif mime_data.hasText():
            text = mime_data.text()
            try:
                return json.loads(text)
            except:
                return None
        
        return None
