#!/usr/bin/env python3
"""
Gradient Blending Integration Module for Gradient Generator

This module provides integration utilities for adding gradient blending
functionality to the main application.

Updated to import only the available blend types (removed harmony, procedural, gravity)
and added fractal blend.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox

try:
    from .gradient_blending_ui import GradientBlendingWidget
except ImportError:
    try:
        from gradient_generator.ui.gradient_blending.gradient_blending_ui import GradientBlendingWidget
    except ImportError:
        # Define a stub class for error handling
        class GradientBlendingWidget:
            def __init__(self, *args, **kwargs):
                raise ImportError("GradientBlendingWidget could not be imported")

# Import blenders to register them with the registry
try:
    from . import interleave_blend, mix_blend, crossfade_blend, stack_blend
    from . import new_blend_types  # Contains: waveform, crystal, layer, chromatic, memory
    from . import fractal_blend    # Contains: fractal
except ImportError:
    try:
        from gradient_generator.ui.gradient_blending import (
            interleave_blend, mix_blend, crossfade_blend, stack_blend,
            new_blend_types, fractal_blend
        )
    except ImportError:
        print("Warning: Could not import blending methods. Functionality will be limited.")


def integrate_blending(control_panel):
    """
    Integrates gradient blending functionality into the control panel.
    
    Args:
        control_panel: ControlPanel instance to integrate with
        
    Returns:
        True if integration was successful, False otherwise
    """
    try:
        # Create container widget for the blending UI
        container = QWidget()
        
        # Create a layout for the container
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for better appearance
        
        # Create the blending widget
        blending_widget = GradientBlendingWidget(control_panel.gradient_model)
        
        # Add the blending widget to the layout
        layout.addWidget(blending_widget)
        
        # Connect the blended gradient signal
        blending_widget.gradient_blended.connect(
            lambda gradient: on_gradient_blended(control_panel, gradient)
        )
        
        # Add the container widget to the tab widget, but prevent auto-expansion
        # Store the current index to restore it after adding the tab
        current_index = control_panel.tabs.currentIndex()
        control_panel.tabs.addTab(container, "Blend")
        control_panel.tabs.setCurrentIndex(current_index)  # Restore original tab
        
        # Store a reference to prevent garbage collection
        control_panel.blending_container = container
        control_panel.blending_widget = blending_widget
        
        # Modify the add_gradient_to_list method to prevent tab expansion
        original_add_method = blending_widget.add_gradient_to_list
        
        def wrapped_add_gradient(gradient, name, weight):
            # Get the current tab index
            current_tab = control_panel.tabs.currentIndex()
            
            # Call the original method
            result = original_add_method(gradient, name, weight)
            
            # Restore the tab index if it changed
            if control_panel.tabs.currentIndex() != current_tab:
                control_panel.tabs.setCurrentIndex(current_tab)
                
            return result
        
        # Replace the original method with our wrapped version
        blending_widget.add_gradient_to_list = wrapped_add_gradient
        
        # Also modify add_current_gradient and add_from_gradient_list methods
        original_add_current = blending_widget.add_current_gradient
        
        def wrapped_add_current_gradient():
            # Get the current tab index
            current_tab = control_panel.tabs.currentIndex()
            
            # Call the original method
            result = original_add_current()
            
            # Restore the tab index if it changed
            if control_panel.tabs.currentIndex() != current_tab:
                control_panel.tabs.setCurrentIndex(current_tab)
                
            return result
        
        # Replace the original method
        blending_widget.add_current_gradient = wrapped_add_current_gradient
        
        # Wrap add_from_gradient_list method
        original_add_from_list = blending_widget.add_from_gradient_list
        
        def wrapped_add_from_gradient_list():
            # Get the current tab index
            current_tab = control_panel.tabs.currentIndex()
            
            # Call the original method
            result = original_add_from_list()
            
            # Restore the tab index if it changed
            if control_panel.tabs.currentIndex() != current_tab:
                control_panel.tabs.setCurrentIndex(current_tab)
                
            return result
        
        # Replace the original method
        blending_widget.add_from_gradient_list = wrapped_add_from_gradient_list
        
        # Wrap add_selected_from_gradient_list method (if it exists)
        if hasattr(blending_widget, 'add_selected_from_gradient_list'):
            original_add_selected = blending_widget.add_selected_from_gradient_list
            
            def wrapped_add_selected_from_gradient_list():
                # Get the current tab index
                current_tab = control_panel.tabs.currentIndex()
                
                # Call the original method
                result = original_add_selected()
                
                # Restore the tab index if it changed
                if control_panel.tabs.currentIndex() != current_tab:
                    control_panel.tabs.setCurrentIndex(current_tab)
                    
                return result
            
            # Replace the original method
            blending_widget.add_selected_from_gradient_list = wrapped_add_selected_from_gradient_list
        
        return True
    except Exception as e:
        print(f"Error integrating gradient blending: {e}")
        return False


def on_gradient_blended(control_panel, gradient):
    """
    Handle a gradient blended by the blending widget.
    
    Args:
        control_panel: ControlPanel instance
        gradient: Blended gradient
    """
    try:
        # Copy the gradient to the main gradient model
        main_gradient = control_panel.gradient_model
        
        # Clear existing stops
        main_gradient._color_stops = []
        
        # Copy color stops
        for stop in gradient.get_color_stop_objects():
            main_gradient.add_color_stop(stop.position, stop.color)
        
        # Copy metadata
        main_gradient.set_name(gradient.get_name())
        main_gradient.set_description(gradient.get_description())
        
        # Emit signal that gradient has been updated
        control_panel.gradient_updated.emit()
        
    except Exception as e:
        print(f"Error applying blended gradient: {e}")


def add_blending_tab(control_panel):
    """
    Manually add the blending tab to an existing control panel.
    
    Args:
        control_panel: ControlPanel instance
        
    Returns:
        True if successful, False otherwise
    """
    return integrate_blending(control_panel)


def get_available_blend_types():
    """
    Get a list of available blend types after the module changes.
    
    Returns:
        List of available blend type names
    """
    try:
        from .blend_core import BlendRegistry
        return BlendRegistry.get_blender_names()
    except ImportError:
        return []


def verify_blend_types():
    """
    Verify which blend types are actually registered and available.
    
    Returns:
        Dictionary with status of each blend type
    """
    try:
        from .blend_core import BlendRegistry
        
        expected_types = [
            'interleave', 'mix', 'crossfade', 'stack',
            'waveform', 'crystal', 'layer', 'chromatic', 'memory', 'fractal'
        ]
        
        removed_types = ['harmony', 'procedural', 'gravity']
        
        registered = BlendRegistry.get_blender_names()
        
        status = {
            'available': registered,
            'expected': expected_types,
            'removed': removed_types,
            'missing': [t for t in expected_types if t not in registered],
            'unexpected': [t for t in registered if t not in expected_types and t not in removed_types]
        }
        
        return status
    except ImportError:
        return {'error': 'BlendRegistry not available'}


if __name__ == "__main__":
    print("Gradient Blending Integration module")
    print("=" * 50)
    
    # Verify blend types
    status = verify_blend_types()
    
    if 'error' in status:
        print(f"Error: {status['error']}")
    else:
        print(f"Available blend types: {', '.join(status['available'])}")
        print(f"Expected: {len(status['expected'])}")
        print(f"Actually available: {len(status['available'])}")
        
        if status['missing']:
            print(f"Missing: {', '.join(status['missing'])}")
        
        if status['unexpected']:
            print(f"Unexpected: {', '.join(status['unexpected'])}")
        
        print(f"Removed (as requested): {', '.join(status['removed'])}")
    
    print("\nThis module should be imported by the main application.")