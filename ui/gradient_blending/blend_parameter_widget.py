#!/usr/bin/env python3
"""
Enhanced Blend Parameter Widget with Improved UI Controls

This version provides better UI controls:
- Checkboxes for binary parameters
- Sliders for continuous parameters
- Descriptive labels for blend modes
"""
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, QComboBox, QSlider, 
                           QCheckBox, QVBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal


class BlendParameterWidget(QWidget):
    """Enhanced widget for adjusting a single blend parameter with improved controls."""
    
    parameter_changed = pyqtSignal(str, float)  # Parameter name, new value
    
    def __init__(self, param, parent=None):
        super().__init__(parent)
        
        self.param = param
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components with enhanced controls."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Parameter label
        self.label = QLabel(f"{self.param.label}:")
        self.label.setMinimumWidth(120)
        layout.addWidget(self.label)
        
        # Create appropriate control based on parameter type and name
        if self._is_binary_parameter():
            self._create_checkbox_control(layout)
        elif self._is_blend_mode_parameter():
            self._create_blend_mode_control(layout)
        elif self._is_slider_parameter():
            self._create_slider_control(layout)
        elif self.param.step >= 1.0:
            self._create_discrete_control(layout)
        else:
            self._create_default_slider_control(layout)
        
        # Set tooltip
        self.setToolTip(self.param.description)
    
    def _is_binary_parameter(self):
        """Check if this is a binary (0/1) parameter that should be a checkbox."""
        binary_params = [
            "use_weights", "preserve_all", "mask_invert", "reverse_order"
        ]
        return (self.param.name in binary_params or 
                (self.param.min_value == 0.0 and self.param.max_value == 1.0 and 
                 self.param.step == 1.0))
    
    def _is_blend_mode_parameter(self):
        """Check if this is a blend mode parameter."""
        return self.param.name == "blend_mode"
    
    def _is_slider_parameter(self):
        """Check if this parameter should specifically be a slider."""
        slider_params = ["sample_density", "phase_shift", "prism_angle", "sample_count"]
        return self.param.name in slider_params
    
    def _create_checkbox_control(self, layout):
        """Create a checkbox control for binary parameters."""
        self.control = QCheckBox()
        self.control.setChecked(self.param.value >= 0.5)
        self.control.stateChanged.connect(self._on_checkbox_changed)
        layout.addWidget(self.control)
    
    def _create_blend_mode_control(self, layout):
        """Create a combo box with descriptive blend mode names."""
        self.control = QComboBox()
        
        # Photoshop-style blend mode descriptions
        blend_modes = [
            "Multiply (Darken)",
            "Screen (Lighten)", 
            "Overlay (Contrast)",
            "Soft Light (Subtle)",
            "Hard Light (Strong)",
            "Color Dodge (Brighten)",
            "Color Burn (Darken)",
            "Difference (Invert)"
        ]
        
        self.control.addItems(blend_modes)
        
        # Set current value
        index = int(self.param.value)
        if 0 <= index < len(blend_modes):
            self.control.setCurrentIndex(index)
        
        self.control.currentIndexChanged.connect(self._on_combo_changed)
        layout.addWidget(self.control)
    
    def _create_slider_control(self, layout):
        """Create a slider control for specific parameters."""
        slider_layout = QVBoxLayout()
        
        # Slider
        self.control = QSlider(Qt.Horizontal)
        
        # Configure slider based on parameter
        if self.param.name in ["sample_density", "sample_count"]:
            # Integer slider for sample counts
            self.control.setRange(int(self.param.min_value), int(self.param.max_value))
            self.control.setValue(int(self.param.value))
            self.control.setSingleStep(1)
        else:
            # Float slider for angles and other continuous values
            min_val_int = int(self.param.min_value * 10)
            max_val_int = int(self.param.max_value * 10)
            val_int = int(self.param.value * 10)
            
            self.control.setRange(min_val_int, max_val_int)
            self.control.setValue(val_int)
            self.control.setSingleStep(1)
        
        # Value label
        self._update_slider_label()
        slider_layout.addWidget(self.control)
        slider_layout.addWidget(self.value_label)
        
        self.control.valueChanged.connect(self._on_slider_changed)
        layout.addLayout(slider_layout)
    
    def _create_discrete_control(self, layout):
        """Create discrete parameter control (combo box)."""
        self.control = QComboBox()
        
        # Parse description for options or create numeric values
        if ":" in self.param.description:
            options_str = self.param.description.split(":", 1)[1]
            options = [opt.strip() for opt in options_str.split(",")]
            self.control.addItems(options)
            
            index = int(self.param.value)
            if 0 <= index < len(options):
                self.control.setCurrentIndex(index)
        else:
            for i in range(int(self.param.min_value), int(self.param.max_value) + 1):
                self.control.addItem(str(i))
            
            self.control.setCurrentIndex(int(self.param.value - self.param.min_value))
        
        self.control.currentIndexChanged.connect(self._on_combo_changed)
        layout.addWidget(self.control)
    
    def _create_default_slider_control(self, layout):
        """Create default slider control for continuous parameters."""
        # Convert to integer range for slider
        min_val_int = int(self.param.min_value * 100)
        max_val_int = int(self.param.max_value * 100)
        val_int = int(self.param.value * 100)
        step_int = max(1, int(self.param.step * 100))
        
        self.control = QSlider(Qt.Horizontal)
        self.control.setRange(min_val_int, max_val_int)
        self.control.setValue(val_int)
        self.control.setSingleStep(step_int)
        
        # Add value label
        self.value_label = QLabel(f"{self.param.value:.2f}")
        self.value_label.setFixedWidth(50)
        layout.addWidget(self.value_label)
        
        self.control.valueChanged.connect(self._on_default_slider_changed)
        layout.addWidget(self.control)
    
    def _update_slider_label(self):
        """Update slider value label."""
        if self.param.name in ["sample_density", "sample_count"]:
            self.value_label = QLabel(f"{int(self.param.value)}")
        elif self.param.name == "phase_shift":
            self.value_label = QLabel(f"{self.param.value:.0f}°")
        elif self.param.name == "prism_angle":
            self.value_label = QLabel(f"{self.param.value:.1f}°")
        else:
            self.value_label = QLabel(f"{self.param.value:.2f}")
        
        self.value_label.setFixedWidth(50)
    
    def _on_checkbox_changed(self, state):
        """Handle checkbox state change."""
        value = 1.0 if state == Qt.Checked else 0.0
        self.parameter_changed.emit(self.param.name, value)
    
    def _on_slider_changed(self, value_int):
        """Handle slider value change for specific parameters."""
        if self.param.name in ["sample_density", "sample_count"]:
            # Integer value
            value = float(value_int)
            self.value_label.setText(f"{int(value)}")
        else:
            # Float value divided by 10
            value = value_int / 10.0
            if self.param.name == "phase_shift":
                self.value_label.setText(f"{value:.0f}°")
            elif self.param.name == "prism_angle":
                self.value_label.setText(f"{value:.1f}°")
            else:
                self.value_label.setText(f"{value:.2f}")
        
        self.parameter_changed.emit(self.param.name, value)
    
    def _on_default_slider_changed(self, value_int):
        """Handle default slider value change."""
        value = value_int / 100.0
        self.value_label.setText(f"{value:.2f}")
        self.parameter_changed.emit(self.param.name, value)
    
    def _on_combo_changed(self, index):
        """Handle combo box selection change."""
        value = float(index)
        if self.param.name == "blend_mode":
            # For blend mode, the index directly maps to the mode number
            value = float(index)
        else:
            # For other discrete parameters, add min_value offset
            value = float(index + self.param.min_value)
        
        self.parameter_changed.emit(self.param.name, value)
    
    def update_value(self, value):
        """Update the control to reflect a new parameter value."""
        if isinstance(self.control, QCheckBox):
            self.control.setChecked(value >= 0.5)
        elif isinstance(self.control, QSlider):
            if self.param.name in ["sample_density", "sample_count"]:
                self.control.setValue(int(value))
                self.value_label.setText(f"{int(value)}")
            elif hasattr(self, 'value_label'):
                if self.param.name in ["phase_shift", "prism_angle"]:
                    self.control.setValue(int(value * 10))
                    if self.param.name == "phase_shift":
                        self.value_label.setText(f"{value:.0f}°")
                    else:
                        self.value_label.setText(f"{value:.1f}°")
                else:
                    self.control.setValue(int(value * 100))
                    self.value_label.setText(f"{value:.2f}")
        elif isinstance(self.control, QComboBox):
            if self.param.name == "blend_mode":
                index = int(value)
            else:
                index = int(value - self.param.min_value)
            
            if 0 <= index < self.control.count():
                self.control.setCurrentIndex(index)