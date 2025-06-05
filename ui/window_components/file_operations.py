#!/usr/bin/env python3
"""
File Operations Module for Gradient Generator

This module handles all file-related operations including saving and exporting gradients.
"""
import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog

from ...export.image_exporter import ImageExporter
from ...export.file_formats import save_map_format, save_ugr_format


class FileOperations:
    """Handles file operations for the gradient generator."""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def save_map(self):
        """Save gradient in MAP format."""
        self._save_gradient_file("MAP Files (*.map);;All Files (*)", 
                               save_map_format, "MAP")
    
    def save_ugr(self):
        """Save gradient in UGR format."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window, "Save UGR File", "", "UGR Files (*.ugr);;All Files (*)"
        )
        
        if file_path:
            try:
                gradient_name = self._get_gradient_name_for_save()
                if gradient_name:
                    save_ugr_format(self.main_window.current_gradient, file_path, gradient_name)
                    self.main_window.statusBar().showMessage(
                        f"Saved as UGR: {os.path.basename(file_path)}"
                    )
            except Exception as e:
                QMessageBox.critical(
                    self.main_window, "Error", 
                    f"Failed to save UGR file: {str(e)}"
                )
    
    def export_image(self):
        """Export gradient as image."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window, "Export Image", "", 
            "PNG Images (*.png);;JPEG Images (*.jpg);;All Files (*)"
        )
        
        if file_path:
            try:
                exporter = ImageExporter()
                exporter.export(self.main_window.current_gradient, file_path)
                self.main_window.statusBar().showMessage(
                    f"Exported image: {os.path.basename(file_path)}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self.main_window, "Error", 
                    f"Failed to export image: {str(e)}"
                )
    
    def _save_gradient_file(self, filter_str, save_function, format_name):
        """Generic method for saving gradient files."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window, f"Save {format_name} File", "", filter_str
        )
        
        if file_path:
            try:
                save_function(self.main_window.current_gradient, file_path)
                self.main_window.statusBar().showMessage(
                    f"Saved as {format_name}: {os.path.basename(file_path)}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self.main_window, "Error", 
                    f"Failed to save {format_name} file: {str(e)}"
                )
    
    def _get_gradient_name_for_save(self):
        """Get gradient name for saving, prompting if necessary."""
        gradient_name = self.main_window.current_gradient.get_name()
        if not gradient_name or gradient_name == "New Gradient":
            gradient_name, ok = QInputDialog.getText(
                self.main_window, "Gradient Name", "Enter gradient name:"
            )
            if not ok or not gradient_name:
                return None
        return gradient_name
