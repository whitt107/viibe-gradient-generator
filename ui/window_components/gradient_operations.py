#!/usr/bin/env python3
"""
Gradient Operations Module for Gradient Generator - Updated to Remove Dialog Popups

This module handles all gradient-related operations including creation, 
modification, and list management with streamlined user experience.
"""
from PyQt5.QtWidgets import QMessageBox, QInputDialog

from ..image_to_gradient import ImageToGradientDialog
from ..random_gradient_dialog import RandomGradientDialog


class GradientOperations:
    """Handles gradient operations for the gradient generator."""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def new_gradient(self):
        """Create a new gradient."""
        if self._confirm_new_gradient():
            self.main_window.current_gradient.reset()
            self.main_window._update_ui_for_gradient()
            self.main_window.statusBar().showMessage("New gradient created")
    
    def create_from_image(self):
        """Create a gradient from an image."""
        if self._confirm_new_gradient():
            dialog = ImageToGradientDialog(self.main_window)
            dialog.gradient_created.connect(self.apply_generated_gradient)
            dialog.exec_()
    
    def create_random_gradient(self):
        """Create a random gradient."""
        if self._confirm_new_gradient():
            dialog = RandomGradientDialog(self.main_window)
            dialog.gradient_generated.connect(self.apply_generated_gradient)
            dialog.exec_()
    
    def apply_generated_gradient(self, gradient):
        """Apply a generated gradient."""
        if gradient:
            self._copy_gradient_data(gradient, self.main_window.current_gradient)
            self.main_window._update_ui_for_gradient()
            self.main_window.statusBar().showMessage(f"Gradient created: {gradient.get_name()}")
    
    def add_to_gradient_list(self):
        """Add current gradient to the list with auto-generated name (no dialog popup)."""
        gradient_copy = self.main_window.current_gradient.clone()
        
        # Auto-generate name without dialog popup
        name = gradient_copy.get_name()
        if not name or name in ["New Gradient", "Unnamed Gradient", ""]:
            # Get next available counter number
            existing_names = [grad_name for _, grad_name in self.main_window.gradient_list_panel.gradients]
            counter = 1
            while f"Gradient {counter:02d}" in existing_names:
                counter += 1
            name = f"Gradient {counter:02d}"
        
        gradient_copy.set_name(name)
        self.main_window.gradient_list_panel.add_gradient(gradient_copy, name)
        self.main_window.statusBar().showMessage(f"Added to list: {name}")
    
    def create_batch_gradients(self):
        """Open batch gradient creation dialog."""
        try:
            # Import here to avoid circular imports
            from ..batch_operations import BatchOperationsDialog
            
            dialog = BatchOperationsDialog(self.main_window.current_gradient, self.main_window)
            dialog.gradients_generated.connect(self.on_batch_gradients_generated)
            dialog.exec_()
        except ImportError as e:
            QMessageBox.critical(
                self.main_window, "Import Error", 
                f"Failed to import batch operations: {str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self.main_window, "Error", 
                f"Failed to open batch operations: {str(e)}"
            )
    
    def on_gradient_selected_from_list(self, gradient):
        """Handle gradient selection from the list panel."""
        if gradient and self._confirm_switch_gradient():
            self._copy_gradient_data(gradient, self.main_window.current_gradient)
            self.main_window.update_ui_for_new_gradient()
            self.main_window.statusBar().showMessage(f"Loaded gradient: {gradient.get_name()}")
    
    def on_batch_gradients_generated(self, gradients):
        """Handle batch generated gradients."""
        for gradient, name in gradients:
            self.main_window.gradient_list_panel.add_gradient(gradient, name)
        
        if gradients:
            self.main_window.gradient_list_panel.set_current_index(
                len(self.main_window.gradient_list_panel.gradients) - len(gradients)
            )
            self.main_window.statusBar().showMessage(f"Generated {len(gradients)} gradients")
    
    def _confirm_new_gradient(self):
        """Confirm creating a new gradient if current has unsaved changes."""
        if not self.main_window.current_gradient.is_empty():
            reply = QMessageBox.question(
                self.main_window, "New Gradient",
                "Create a new gradient? Any unsaved changes will be lost.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            return reply == QMessageBox.Yes
        return True
    
    def _confirm_switch_gradient(self):
        """Confirm switching gradients if current has unsaved changes."""
        if not self.main_window.current_gradient.is_empty():
            reply = QMessageBox.question(
                self.main_window, "Switch Gradient",
                "Switch to selected gradient? Any unsaved changes to the current gradient will be lost.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            return reply == QMessageBox.Yes
        return True
    
    def _copy_gradient_data(self, source, target):
        """
        Copy gradient data from source to target.
        Performs a complete deep copy of all properties.
        
        Args:
            source: Source gradient
            target: Target gradient
        """
        try:
            # Start with a clean slate by clearing color stops
            target._color_stops = []
            
            # Copy each color stop individually to ensure deep copy
            for stop in source.get_color_stop_objects():
                # Create a new color stop with the same values (deep copy)
                target.add_color_stop(stop.position, stop.color)
            
            # ======= Metadata properties =======
            # Copy basic metadata
            target.set_name(source.get_name())
            target.set_author(source.get_author())
            target.set_description(source.get_description())
            
            # Copy JWildfire specific metadata
            target.set_ugr_category(source.get_ugr_category())
            target.set_combine_gradients(source.get_combine_gradients())
            
            # ======= Seamless blending properties =======
            target.set_seamless_blend(source.get_seamless_blend())
            target.set_blend_region(source.get_blend_region())
            
            # ======= Additional properties =======
            # Handle any additional properties added to the Gradient class
            # Get attribute lists to find all properties
            source_attrs = dir(source)
            target_attrs = dir(target)
            
            # Look for getter/setter method pairs that might indicate properties
            for attr in source_attrs:
                # Look for getter methods that start with "get_"
                if attr.startswith("get_") and attr not in [
                    "get_name", "get_author", "get_description", 
                    "get_ugr_category", "get_combine_gradients",
                    "get_seamless_blend", "get_blend_region",
                    "get_color_stops", "get_color_stop_objects",
                    "get_interpolated_color", "get_sample_colors",
                    "get_preset"
                ]:
                    # Check if corresponding setter exists
                    setter = "set_" + attr[4:]
                    if setter in source_attrs and setter in target_attrs:
                        try:
                            # Get value from source
                            getter_method = getattr(source, attr)
                            value = getter_method()
                            
                            # Set value in target
                            setter_method = getattr(target, setter)
                            setter_method(value)
                        except Exception as e:
                            print(f"Warning: Could not copy property {attr[4:]}: {e}")
            
        except Exception as e:
            # Log the error but don't crash the application
            print(f"Error copying gradient data: {e}")
            # If possible, show the error to the user
            QMessageBox.warning(
                self.main_window, 
                "Gradient Copy Error",
                f"Some gradient properties might not have been copied correctly: {str(e)}"
            )