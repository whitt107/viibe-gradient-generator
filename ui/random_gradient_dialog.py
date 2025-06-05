#!/usr/bin/env python3
"""
Random Gradient Dialog for VIIBE Gradient Generator

This module provides a dialog for generating random gradients with various
color schemes and configurations.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QGroupBox, QRadioButton, QSpinBox, 
                           QFormLayout, QCheckBox, QButtonGroup,
                           QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QLinearGradient, QColor

# Import RandomGradientGenerator with fallback options
try:
    from .random_gradient import RandomGradientGenerator
except ImportError:
    try:
        from gradient_generator.ui.random_gradient import RandomGradientGenerator
    except ImportError:
        # Mock interface for when imports fail
        class RandomGradientGenerator:
            MAX_COLOR_STOPS = 64
            DEFAULT_STOPS = 10
            
            @staticmethod
            def generate_random_gradient(*args, **kwargs):
                pass


class GradientPreviewLabel(QLabel):
    """Simple preview widget for displaying gradients."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gradient = None
        self.setMinimumSize(300, 120)
        self.setStyleSheet("border: 1px solid #555;")
        
    def set_gradient(self, gradient):
        """Set the gradient to display."""
        self.gradient = gradient
        self.update()
        
    def paintEvent(self, event):
        """Override paintEvent to draw the gradient."""
        super().paintEvent(event)
        
        if not self.gradient:
            return
            
        # Get widget dimensions
        w = self.width()
        h = self.height()
        
        # Create a painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create a linear gradient
        qgradient = QLinearGradient(0, 0, w, 0)
        
        # Add color stops
        for position, color in self.gradient.get_color_stops():
            qgradient.setColorAt(position, QColor(*color))
        
        # Draw gradient
        painter.fillRect(0, 0, w, h, qgradient)
        
        # Draw border
        painter.setPen(Qt.darkGray)
        painter.drawRect(0, 0, w-1, h-1)
        painter.end()


class RandomGradientDialog(QDialog):
    """Dialog for generating random gradients."""
    
    gradient_generated = pyqtSignal(object)  # Emitted when a gradient is generated
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Random Gradient Generator")
        self.setMinimumWidth(600)
        self.setMinimumHeight(450)
        
        # Initialize components
        self.current_gradient = None
        self.current_seed = None
        
        # Initialize UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout(self)
        
        # Create split view with controls and preview
        controls_preview_layout = QHBoxLayout()
        
        # --- Left side: Controls ---
        controls_layout = QVBoxLayout()
        
        # Scheme selection group
        scheme_group = QGroupBox("Color Scheme")
        scheme_layout = QVBoxLayout(scheme_group)
        
        self.scheme_button_group = QButtonGroup(self)
        
        # Create radio buttons for each scheme type
        scheme_options = [
            ("Random Spectrum", "Create a gradient with completely random colors"),
            ("Harmonious Colors", "Create a gradient with colors that work well together"),
            ("Monochromatic", "Create a gradient with different shades of a single color"),
            ("Analogous", "Create a gradient with colors that are adjacent on the color wheel"),
            ("Complementary", "Create a gradient with colors from opposite sides of the color wheel"),
            ("Triadic", "Create a gradient with three colors evenly spaced on the color wheel")
        ]
        
        for i, (name, tooltip) in enumerate(scheme_options):
            radio = QRadioButton(name)
            radio.setToolTip(tooltip)
            self.scheme_button_group.addButton(radio, i)
            scheme_layout.addWidget(radio)
        
        # Set Random Spectrum as default
        self.scheme_button_group.button(0).setChecked(True)
        
        # Connect signal
        self.scheme_button_group.buttonClicked.connect(self.on_scheme_changed)
        
        controls_layout.addWidget(scheme_group)
        
        # Options group
        options_group = QGroupBox("Options")
        options_layout = QFormLayout(options_group)
        
        # Number of color stops
        self.stops_spin = QSpinBox()
        self.stops_spin.setRange(5, RandomGradientGenerator.MAX_COLOR_STOPS)
        self.stops_spin.setValue(RandomGradientGenerator.DEFAULT_STOPS)
        self.stops_spin.setToolTip(f"Number of color stops to generate (5-{RandomGradientGenerator.MAX_COLOR_STOPS})")
        options_layout.addRow("Number of stops:", self.stops_spin)
        
        # Random seed
        self.seed_enabled = QCheckBox("Use specific seed")
        self.seed_enabled.setToolTip("Enable to use a specific seed for reproducible results")
        
        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(1, 1000000)
        self.seed_spin.setValue(12345)
        self.seed_spin.setEnabled(False)
        
        self.seed_enabled.stateChanged.connect(self.on_seed_changed)
        
        seed_layout = QHBoxLayout()
        seed_layout.addWidget(self.seed_enabled)
        seed_layout.addWidget(self.seed_spin)
        
        options_layout.addRow("Random Seed:", seed_layout)
        
        controls_layout.addWidget(options_group)
        controls_layout.addStretch()
        
        # --- Right side: Preview ---
        preview_layout = QVBoxLayout()
        
        # Create preview label
        preview_title = QLabel("Gradient Preview")
        preview_title.setAlignment(Qt.AlignCenter)
        preview_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        preview_layout.addWidget(preview_title)
        
        self.preview_label = GradientPreviewLabel()
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preview_layout.addWidget(self.preview_label, 1)
        
        # Status info
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #888; font-style: italic;")
        preview_layout.addWidget(self.info_label)
        
        # Add controls and preview to horizontal layout
        controls_preview_layout.addLayout(controls_layout, 1)
        controls_preview_layout.addLayout(preview_layout, 2)
        
        main_layout.addLayout(controls_preview_layout, 1)
        
        # Button row
        button_layout = QHBoxLayout()
        
        # Generate button
        self.generate_button = QPushButton("Generate New Random Gradient")
        self.generate_button.clicked.connect(self.generate_random_gradient)
        self.generate_button.setStyleSheet("font-weight: bold; padding: 8px;")
        button_layout.addWidget(self.generate_button)
        
        button_layout.addStretch()
        
        # Accept/Cancel buttons
        self.accept_button = QPushButton("Use This Gradient")
        self.accept_button.clicked.connect(self.accept)
        button_layout.addWidget(self.accept_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # Create initial gradient
        self.generate_random_gradient()
    
    def on_scheme_changed(self, button):
        """Handle scheme selection change."""
        # Generate a new gradient with the selected scheme
        self.generate_random_gradient()
    
    def on_seed_changed(self, state):
        """Handle seed checkbox state change."""
        self.seed_spin.setEnabled(state == Qt.Checked)
    
    def generate_random_gradient(self):
        """Generate a random gradient based on current settings."""
        try:
            # Get values from controls
            scheme_id = self.scheme_button_group.checkedId()
            num_stops = self.stops_spin.value()
            
            # Map scheme ID to scheme type
            scheme_types = {
                0: "random", 1: "harmonious", 2: "monochromatic",
                3: "analogous", 4: "complementary", 5: "triadic"
            }
            scheme_type = scheme_types.get(scheme_id, "random")
            
            # Determine seed
            random_seed = None
            if self.seed_enabled.isChecked():
                random_seed = self.seed_spin.value()
                self.current_seed = random_seed
            
            # Generate gradient based on options
            self.current_gradient = RandomGradientGenerator.generate_random_gradient(
                num_stops=num_stops,
                harmonious=(scheme_type == "harmonious"),
                monochromatic=(scheme_type == "monochromatic"),
                analogous=(scheme_type == "analogous"),
                complementary=(scheme_type == "complementary"),
                triadic=(scheme_type == "triadic"),
                random_seed=random_seed
            )
            
            # Update the preview
            self.preview_label.set_gradient(self.current_gradient)
            
            # Update info label
            gradient_info = f"Generated: {self.current_gradient.get_name()}"
            if self.current_seed and not self.seed_enabled.isChecked():
                gradient_info += f"\nUsed seed: {self.current_seed}"
            
            self.info_label.setText(gradient_info)
            
            # Update window title
            self.setWindowTitle(f"Random Gradient Generator - {self.current_gradient.get_name()}")
        
        except Exception as e:
            self.info_label.setText(f"Error generating gradient: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to generate random gradient: {str(e)}")
    
    def accept(self):
        """Handle dialog acceptance."""
        if self.current_gradient:
            # Emit the generated gradient
            self.gradient_generated.emit(self.current_gradient)
        
        # Close the dialog
        super().accept()


if __name__ == "__main__":
    # Test code
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Apply dark theme if available
    try:
        from gradient_generator.utils.styles import apply_dark_theme
        apply_dark_theme(app)
    except ImportError:
        pass
    
    dialog = RandomGradientDialog()
    dialog.show()
    
    sys.exit(app.exec_())