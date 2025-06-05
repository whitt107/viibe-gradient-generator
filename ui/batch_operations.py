#!/usr/bin/env python3
"""
Batch Operations Module for Gradient Generator - Optimized for size reduction

This module provides batch operations for generating multiple gradients with variations.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QSpinBox, QComboBox, QGroupBox, QCheckBox,
                           QFormLayout, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal, QThread

from ..core.color_utils import (complementary_color, triadic_colors, 
                              analogous_colors, rotate_hue, 
                              adjust_brightness, adjust_saturation)


class BatchGenerationThread(QThread):
    """Thread for batch gradient generation."""
    
    progress = pyqtSignal(int)
    gradient_generated = pyqtSignal(object, str)
    finished = pyqtSignal()
    
    def __init__(self, base_gradient, operation, count, options):
        super().__init__()
        self.base_gradient = base_gradient
        self.operation = operation
        self.count = count
        self.options = options
    
    def run(self):
        """Run the batch generation."""
        # Map operations to methods
        operations = {
            "Hue Rotation": self._generate_hue_rotations,
            "Brightness Variation": self._generate_brightness_variations,
            "Saturation Variation": self._generate_saturation_variations,
            "Complementary": self._generate_complementary,
            "Triadic": self._generate_triadic,
            "Analogous": self._generate_analogous
        }
        
        # Use the appropriate generation method
        generate_method = operations.get(self.operation, self._generate_hue_rotations)
        generate_method()
        
        self.finished.emit()
    
    def _generate_hue_rotations(self):
        """Generate hue rotation variations."""
        for i in range(self.count):
            gradient = self.base_gradient.clone()
            name = f"{self.base_gradient.get_name()} Hue {i+1}"
            
            # Rotate hue progressively
            angle = (360 / self.count) * i
            self._apply_color_transformation(gradient, 
                                           lambda color: rotate_hue(color, angle))
            
            self._update_progress(i)
            self.gradient_generated.emit(gradient, name)
    
    def _generate_brightness_variations(self):
        """Generate brightness variations."""
        for i in range(self.count):
            gradient = self.base_gradient.clone()
            name = f"{self.base_gradient.get_name()} Brightness {i+1}"
            
            # Create brightness variations
            factor = 0.5 + (1.0 * i / max(1, self.count - 1))
            self._apply_color_transformation(gradient, 
                                           lambda color: adjust_brightness(color, factor))
            
            self._update_progress(i)
            self.gradient_generated.emit(gradient, name)
    
    def _generate_saturation_variations(self):
        """Generate saturation variations."""
        for i in range(self.count):
            gradient = self.base_gradient.clone()
            name = f"{self.base_gradient.get_name()} Saturation {i+1}"
            
            # Create saturation variations
            factor = 0.5 + (1.0 * i / max(1, self.count - 1))
            self._apply_color_transformation(gradient, 
                                           lambda color: adjust_saturation(color, factor))
            
            self._update_progress(i)
            self.gradient_generated.emit(gradient, name)
    
    def _generate_complementary(self):
        """Generate complementary variation."""
        # Original gradient
        gradient = self.base_gradient.clone()
        name = f"{self.base_gradient.get_name()} Original"
        self._update_progress(0)
        self.gradient_generated.emit(gradient, name)
        
        # Complementary gradient
        comp_gradient = self.base_gradient.clone()
        comp_name = f"{self.base_gradient.get_name()} Complementary"
        
        self._apply_color_transformation(comp_gradient, complementary_color)
        
        self._update_progress(50)
        self.gradient_generated.emit(comp_gradient, comp_name)
    
    def _generate_triadic(self):
        """Generate triadic variations."""
        # Get all triadic variations for each color
        for i in range(3):
            gradient = self.base_gradient.clone()
            name = f"{self.base_gradient.get_name()} Triadic {i+1}"
            
            def transform_color(color):
                triadic = triadic_colors(color)
                return triadic[i]
            
            self._apply_color_transformation(gradient, transform_color)
            
            self._update_progress(i * 33)
            self.gradient_generated.emit(gradient, name)
    
    def _generate_analogous(self):
        """Generate analogous variations."""
        # Get all analogous variations for each color
        for i in range(3):
            gradient = self.base_gradient.clone()
            name = f"{self.base_gradient.get_name()} Analogous {i+1}"
            
            def transform_color(color):
                analogous = analogous_colors(color)
                return analogous[i]
            
            self._apply_color_transformation(gradient, transform_color)
            
            self._update_progress(i * 33)
            self.gradient_generated.emit(gradient, name)
    
    def _apply_color_transformation(self, gradient, transform_func):
        """Apply a color transformation to each stop in the gradient."""
        new_stops = []
        
        for position, color in gradient.get_color_stops():
            new_color = transform_func(color)
            new_stops.append((position, new_color))
        
        # Clear and rebuild stops
        gradient._color_stops = []
        for position, color in new_stops:
            gradient.add_color_stop(position, color)
    
    def _update_progress(self, current_step):
        """Update the progress bar."""
        progress = int((current_step + 1) / self.count * 100)
        self.progress.emit(progress)


class BatchOperationsDialog(QDialog):
    """Dialog for batch gradient operations."""
    
    gradients_generated = pyqtSignal(list)  # List of (gradient, name) tuples
    
    def __init__(self, base_gradient, parent=None):
        super().__init__(parent)
        
        self.base_gradient = base_gradient
        self.generated_gradients = []
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Batch Gradient Operations")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Operation selection
        operation_group = QGroupBox("Operation")
        operation_layout = QFormLayout(operation_group)
        
        self.operation_combo = QComboBox()
        self.operation_combo.addItems([
            "Hue Rotation",
            "Brightness Variation",
            "Saturation Variation",
            "Complementary",
            "Triadic",
            "Analogous"
        ])
        self.operation_combo.currentTextChanged.connect(self.on_operation_changed)
        operation_layout.addRow("Type:", self.operation_combo)
        
        # Count spinner
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 50)
        self.count_spin.setValue(5)
        operation_layout.addRow("Count:", self.count_spin)
        
        layout.addWidget(operation_group)
        
        # Options group
        options_group = QGroupBox("Options")
        options_layout = QFormLayout(options_group)
        
        self.reverse_check = QCheckBox("Include reverse gradients")
        options_layout.addRow("", self.reverse_check)
        
        layout.addWidget(options_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.generate_gradients)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.generate_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Update UI based on initial operation
        self.on_operation_changed(self.operation_combo.currentText())
    
    def on_operation_changed(self, operation):
        """Handle operation type change."""
        if operation in ["Complementary", "Triadic", "Analogous"]:
            if operation == "Complementary":
                self.count_spin.setValue(2)
                self.count_spin.setMaximum(2)
            else:
                self.count_spin.setValue(3)
                self.count_spin.setMaximum(3)
            self.count_spin.setEnabled(False)
        else:
            self.count_spin.setEnabled(True)
            self.count_spin.setMaximum(50)
            self.count_spin.setValue(5)
    
    def generate_gradients(self):
        """Start the gradient generation thread."""
        self.generated_gradients = []
        
        # Disable controls during generation
        self.generate_button.setEnabled(False)
        self.operation_combo.setEnabled(False)
        self.count_spin.setEnabled(False)
        self.reverse_check.setEnabled(False)
        
        # Create and start thread
        options = {"reverse": self.reverse_check.isChecked()}
        
        self.thread = BatchGenerationThread(
            self.base_gradient,
            self.operation_combo.currentText(),
            self.count_spin.value(),
            options
        )
        
        # Connect signals
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.gradient_generated.connect(self.on_gradient_generated)
        self.thread.finished.connect(self.on_generation_finished)
        
        # Start thread
        self.thread.start()
    
    def on_gradient_generated(self, gradient, name):
        """Handle a generated gradient."""
        self.generated_gradients.append((gradient, name))
    
    def on_generation_finished(self):
        """Handle generation completion."""
        # Re-enable controls
        self.generate_button.setEnabled(True)
        self.operation_combo.setEnabled(True)
        self.count_spin.setEnabled(True)
        self.reverse_check.setEnabled(True)
        
        # Reset progress bar
        self.progress_bar.setValue(100)
        
        # Emit results
        self.gradients_generated.emit(self.generated_gradients)
        
        # Close dialog
        self.accept()