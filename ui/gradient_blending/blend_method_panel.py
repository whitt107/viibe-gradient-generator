#!/usr/bin/env python3
"""
Updated Blend Method Panel with Enhanced Parameter Controls

This version integrates the enhanced BlendParameterWidget with improved UI controls
for better user experience with gradient blending parameters.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QGroupBox, QFormLayout)
from PyQt5.QtCore import pyqtSignal

# Import the enhanced parameter widget
from .blend_parameter_widget import BlendParameterWidget


class BlendMethodPanel(QWidget):
    """Panel for a specific blend method with enhanced parameter controls."""
    
    parameters_changed = pyqtSignal()
    
    def __init__(self, blender, parent=None):
        super().__init__(parent)
        
        self.blender = blender
        self.param_widgets = {}
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components with enhanced controls."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Method description
        desc_label = QLabel(self.blender.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #aaa; font-style: italic;")
        desc_label.setFixedHeight(80)  # Slightly taller for better readability
        layout.addWidget(desc_label)
        
        # Parameters group
        param_group = QGroupBox("Parameters")
        param_layout = QFormLayout(param_group)
        param_layout.setSpacing(8)  # Better spacing between parameters
        
        # Add enhanced parameter controls
        for param in self.blender.get_parameter_list():
            # Use the enhanced BlendParameterWidget
            widget = BlendParameterWidget(param)
            widget.parameter_changed.connect(self.on_parameter_changed)
            
            # Add the widget to the form layout
            param_layout.addRow(widget)
            self.param_widgets[param.name] = widget
        
        layout.addWidget(param_group)
        layout.addStretch()
    
    def on_parameter_changed(self, param_name, value):
        """Handle parameter change from enhanced controls."""
        # Update the parameter in the blender
        self.blender.set_parameter_value(param_name, value)
        
        # Emit signal to update preview
        self.parameters_changed.emit()
    
    def update_from_blender(self):
        """Update enhanced controls from the blender parameters."""
        for name, widget in self.param_widgets.items():
            param = self.blender.get_parameter(name)
            if param:
                widget.update_value(param.value)
    
    def get_parameter_summary(self):
        """Get a summary of current parameter values for display."""
        summary = []
        for param in self.blender.get_parameter_list():
            if param.name == "blend_mode":
                # Special handling for blend modes
                mode_names = [
                    "Multiply", "Screen", "Overlay", "Soft Light",
                    "Hard Light", "Color Dodge", "Color Burn", "Difference"
                ]
                mode_index = int(param.value)
                if 0 <= mode_index < len(mode_names):
                    summary.append(f"{param.label}: {mode_names[mode_index]}")
                else:
                    summary.append(f"{param.label}: {param.value}")
            elif param.name in ["use_weights", "preserve_all", "mask_invert", "reverse_order"]:
                # Binary parameters
                value_str = "Yes" if param.value >= 0.5 else "No"
                summary.append(f"{param.label}: {value_str}")
            elif param.name in ["phase_shift", "prism_angle"]:
                # Angle parameters
                summary.append(f"{param.label}: {param.value:.0f}°")
            elif param.name in ["sample_density", "sample_count", "memory_length"]:
                # Integer parameters
                summary.append(f"{param.label}: {int(param.value)}")
            else:
                # Float parameters
                summary.append(f"{param.label}: {param.value:.2f}")
        
        return summary
            