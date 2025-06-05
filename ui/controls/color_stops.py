#!/usr/bin/env python3
"""
Refactored Color Stops Editor Module for Gradient Generator

Streamlined random gradient UI with slider for color stops count and hidden seed parameter.
All features and functionality retained while saving space.
"""
import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QScrollArea, QGroupBox, QSlider,
                           QFormLayout, QMessageBox, QRadioButton,
                           QButtonGroup, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal

from .color_stop_widget import ColorStopWidget

# Import RandomGradientGenerator with fallback
try:
    from ..random_gradient import RandomGradientGenerator
except ImportError:
    class RandomGradientGenerator:
        MAX_COLOR_STOPS = 64
        DEFAULT_STOPS = 10
        
        @staticmethod
        def generate_random_gradient(**kwargs):
            from core.gradient import Gradient
            grad = Gradient()
            grad.set_name("Default Gradient")
            return grad


class ColorStopsEditor(QWidget):
    """Streamlined widget for editing color stops with refactored randomization UI."""
    
    stops_changed = pyqtSignal()
    
    MAX_COLOR_STOPS = RandomGradientGenerator.MAX_COLOR_STOPS
    DEFAULT_STOPS = RandomGradientGenerator.DEFAULT_STOPS
    
    def __init__(self, gradient_model):
        super().__init__()
        self.gradient_model = gradient_model
        self.color_stops = []
        self._internal_seed = None  # Hidden seed for reproducibility
        self.init_ui()
        self.update_from_model()
    
    def init_ui(self):
        """Initialize the streamlined UI components."""
        main_layout = QVBoxLayout(self)
        
        # Color Stops Section
        stops_group = QGroupBox("Color Stops")
        stops_layout = QVBoxLayout(stops_group)
        
        # Scrollable container
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(200)
        
        self.stops_container = QWidget()
        self.stops_layout = QVBoxLayout(self.stops_container)
        self.stops_layout.setSpacing(2)
        self.stops_layout.setContentsMargins(0, 0, 0, 0)
        self.stops_layout.addStretch()
        
        scroll_area.setWidget(self.stops_container)
        stops_layout.addWidget(scroll_area)
        
        # Counter and basic controls
        controls_layout = QVBoxLayout()
        
        self.stops_counter = QLabel(f"Color Stops: 0/{self.MAX_COLOR_STOPS}")
        controls_layout.addWidget(self.stops_counter)
        
        # Main control buttons
        button_row = QHBoxLayout()
        
        self.add_stop_button = QPushButton("Add Stop")
        self.add_stop_button.clicked.connect(self.add_color_stop)
        button_row.addWidget(self.add_stop_button)
        
        self.randomize_positions_button = QPushButton("Randomize Positions")
        self.randomize_positions_button.clicked.connect(self.randomize_positions)
        button_row.addWidget(self.randomize_positions_button)
        
        self.randomize_colors_button = QPushButton("Randomize Colors")
        self.randomize_colors_button.clicked.connect(self.randomize_colors)
        button_row.addWidget(self.randomize_colors_button)
        
        self.distribute_evenly_button = QPushButton("Distribute Evenly")
        self.distribute_evenly_button.clicked.connect(self.distribute_evenly)
        button_row.addWidget(self.distribute_evenly_button)
        
        controls_layout.addLayout(button_row)
        stops_layout.addLayout(controls_layout)
        
        # Info label
        info_label = QLabel("💡 For advanced distribution controls, use the Distribution tab")
        info_label.setStyleSheet("color: #888; font-style: italic; padding: 4px;")
        info_label.setWordWrap(True)
        stops_layout.addWidget(info_label)
        
        main_layout.addWidget(stops_group)
        
        # Streamlined Random Gradient Generator Section
        random_group = self._create_streamlined_random_ui()
        main_layout.addWidget(random_group)
        
        # Additional info
        info_label = QLabel(
            "💡 <b>Color Adjustments:</b> Modify brightness, contrast, and hue in the Adjustments tab"
        )
        info_label.setStyleSheet("color: #888; font-style: italic; padding: 8px; "
                               "background-color: #333; border-radius: 4px; margin: 5px;")
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        main_layout.addStretch()
    
    def _create_streamlined_random_ui(self):
        """Create the streamlined random gradient generator UI."""
        random_group = QGroupBox("Random Gradient Generator")
        random_layout = QVBoxLayout(random_group)
        
        # Color scheme selection with radio buttons
        self.scheme_button_group = QButtonGroup(self)
        scheme_layout = QVBoxLayout()
        
        schemes = [
            ("Random Spectrum", "Generate completely random colors across full spectrum"),
            ("Harmonious", "Generate colors with pleasing relationships"),
            ("Monochromatic", "Single hue with variations in brightness and saturation"),
            ("Analogous", "Colors adjacent on the color wheel"),
            ("Complementary", "Colors from opposite sides of the color wheel"),
            ("Triadic", "Three colors evenly spaced on the color wheel")
        ]
        
        for i, (name, tooltip) in enumerate(schemes):
            radio = QRadioButton(name)
            radio.setToolTip(tooltip)
            self.scheme_button_group.addButton(radio, i)
            scheme_layout.addWidget(radio)
        
        self.scheme_button_group.button(0).setChecked(True)
        
        # Compact form layout
        form_layout = QFormLayout()
        form_layout.addRow("Color Scheme:", scheme_layout)
        
        # CHANGED: Number of stops as slider instead of spinbox
        stops_layout = QHBoxLayout()
        self.random_stops_slider = QSlider(Qt.Horizontal)
        self.random_stops_slider.setRange(3, self.MAX_COLOR_STOPS)
        self.random_stops_slider.setValue(10)
        self.random_stops_slider.valueChanged.connect(self._update_stops_label)
        
        self.stops_value_label = QLabel("10")
        self.stops_value_label.setFixedWidth(30)
        self.stops_value_label.setAlignment(Qt.AlignCenter)
        
        stops_layout.addWidget(self.random_stops_slider)
        stops_layout.addWidget(self.stops_value_label)
        
        form_layout.addRow("Number of stops:", stops_layout)
        
        # REMOVED: Seed option completely hidden but internally managed
        random_layout.addLayout(form_layout)
        
        # Generate button with enhanced styling
        self.generate_button = QPushButton("Generate Random Gradient")
        self.generate_button.clicked.connect(self.generate_random_gradient)
        self.generate_button.setStyleSheet("""
            QPushButton {
                font-weight: bold; 
                padding: 8px; 
                background-color: #2a7a2a;
                border: 1px solid #555;
                border-radius: 4px;
                color: white;
            }
            QPushButton:hover {
                background-color: #3a8a3a;
            }
            QPushButton:pressed {
                background-color: #1a6a1a;
            }
        """)
        random_layout.addWidget(self.generate_button)
        
        # Compact status
        self.status_label = QLabel("Click 'Generate Random Gradient' to create a new random gradient")
        self.status_label.setStyleSheet("color: #888; font-style: italic; font-size: 11px;")
        self.status_label.setWordWrap(True)
        random_layout.addWidget(self.status_label)
        
        return random_group
    
    def _update_stops_label(self, value):
        """Update the stops count label when slider changes."""
        self.stops_value_label.setText(str(value))
    
    def _generate_internal_seed(self):
        """Generate a new internal seed for reproducibility."""
        self._internal_seed = random.randint(1, 999999)
        return self._internal_seed
    
    def add_color_stop(self):
        """Add a new color stop."""
        if len(self.color_stops) >= self.MAX_COLOR_STOPS:
            QMessageBox.warning(self, "Maximum Reached", 
                f"Cannot add more than {self.MAX_COLOR_STOPS} color stops.")
            return
        
        self.gradient_model.add_color_stop(0.5, (255, 255, 255))
        self.update_from_model()
        self.stops_changed.emit()
    
    def randomize_positions(self):
        """Randomize positions while keeping colors."""
        if len(self.color_stops) < 2:
            QMessageBox.information(self, "Need More Stops", 
                "Need at least 2 color stops to randomize positions.")
            return
        
        colors = [stop.color for stop in self.color_stops]
        
        # Generate random positions maintaining endpoints
        positions = [0.0]
        if len(colors) > 2:
            for _ in range(len(colors) - 2):
                positions.append(random.uniform(0.01, 0.99))
        positions.append(1.0)
        
        self._apply_new_stops(positions, colors)
    
    def randomize_colors(self):
        """Randomize colors while keeping positions."""
        if not self.color_stops:
            QMessageBox.information(self, "No Stops", "No color stops to randomize.")
            return
        
        positions = [stop.position for stop in self.color_stops]
        colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) 
                 for _ in range(len(positions))]
        
        self._apply_new_stops(positions, colors)
    
    def distribute_evenly(self):
        """Distribute color stops evenly."""
        if len(self.color_stops) < 2:
            QMessageBox.information(self, "Need More Stops", 
                "Need at least 2 color stops to distribute evenly.")
            return
        
        colors = [stop.color for stop in self.color_stops]
        num_stops = len(colors)
        
        # Calculate even positions
        if num_stops == 1:
            positions = [0.5]
        elif num_stops == 2:
            positions = [0.0, 1.0]
        else:
            positions = [i / (num_stops - 1) for i in range(num_stops)]
        
        self._apply_new_stops(positions, colors)
        
        # Show status
        try:
            main_window = self.window()
            if hasattr(main_window, 'statusBar'):
                main_window.statusBar().showMessage(
                    f"Distributed {num_stops} color stops evenly", 3000)
        except:
            pass
    
    def generate_random_gradient(self):
        """Generate a random gradient with streamlined parameters."""
        try:
            scheme_id = self.scheme_button_group.checkedId()
            num_stops = self.random_stops_slider.value()  # CHANGED: Get from slider
            
            # Generate internal seed for reproducibility (hidden from user)
            random_seed = self._generate_internal_seed()
            
            # Map scheme ID to flags
            scheme_flags = [
                {"harmonious": False},      # Random Spectrum
                {"harmonious": True},       # Harmonious  
                {"monochromatic": True},    # Monochromatic
                {"analogous": True},        # Analogous
                {"complementary": True},    # Complementary
                {"triadic": True}           # Triadic
            ]
            
            flags = scheme_flags[scheme_id] if 0 <= scheme_id < len(scheme_flags) else {}
            
            # Generate gradient
            new_gradient = RandomGradientGenerator.generate_random_gradient(
                num_stops=num_stops, random_seed=random_seed, **flags
            )
            
            if new_gradient is None:
                raise Exception("Generator returned None")
            
            # Apply to model
            self.gradient_model._color_stops = []
            for stop in new_gradient.get_color_stop_objects():
                self.gradient_model.add_color_stop(stop.position, stop.color)
            
            self.gradient_model.set_name(new_gradient.get_name())
            self.gradient_model.set_description(new_gradient.get_description())
            
            self.update_from_model()
            self.stops_changed.emit()
            
            # Update status with scheme info only (no seed shown to user)
            scheme_names = ["Random Spectrum", "Harmonious", "Monochromatic", 
                           "Analogous", "Complementary", "Triadic"]
            scheme_name = scheme_names[scheme_id] if 0 <= scheme_id < len(scheme_names) else "Unknown"
            
            status_msg = f"Generated: {scheme_name} gradient with {num_stops} random stops"
            self.status_label.setText(status_msg)
            
        except Exception as e:
            error_msg = f"Error generating random gradient: {str(e)}"
            self.status_label.setText(error_msg)
            QMessageBox.critical(self, "Error", f"Failed to generate random gradient: {str(e)}")
    
    def update_from_model(self):
        """Update UI from the gradient model."""
        # Clear existing widgets
        for widget in self.color_stops:
            self.stops_layout.removeWidget(widget)
            widget.deleteLater()
        
        self.color_stops = []
        
        # Get and sort stops by position for display
        model_stops = self.gradient_model.get_color_stops()
        sorted_stops = sorted(model_stops, key=lambda stop: stop[0])
        
        # Add widgets for each stop
        for i, (position, color) in enumerate(sorted_stops):
            self._add_stop_widget(i, position, color)
        
        self._update_ui_state()
    
    def _add_stop_widget(self, display_index, position, color):
        """Add a widget for a color stop."""
        widget = ColorStopWidget(display_index, position, color)
        
        # Connect signals using position-based handlers
        widget.color_changed.connect(lambda idx, clr: self._on_color_changed(position, clr))
        widget.position_changed.connect(lambda idx, new_pos: self._on_position_changed(position, new_pos))
        widget.delete_requested.connect(lambda idx: self._on_delete_stop(position))
        
        # Add to layout
        self.stops_layout.insertWidget(self.stops_layout.count() - 1, widget)
        self.color_stops.append(widget)
        
        self._update_ui_state()
    
    def _on_color_changed(self, original_position, color):
        """Handle color change."""
        model_index = self._find_model_index(original_position)
        if model_index >= 0:
            self.gradient_model.set_color_at_index(model_index, color)
            self.stops_changed.emit()
    
    def _on_position_changed(self, original_position, new_position):
        """Handle position change."""
        model_index = self._find_model_index(original_position)
        if model_index >= 0:
            self.gradient_model.set_position_at_index(model_index, new_position)
            # Delay update to avoid recursion
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(50, self.update_from_model)
            self.stops_changed.emit()
    
    def _on_delete_stop(self, position):
        """Handle stop deletion."""
        if len(self.color_stops) <= 1:
            QMessageBox.information(self, "Cannot Delete", 
                "Cannot delete the last color stop.")
            return
        
        model_index = self._find_model_index(position)
        if model_index >= 0:
            self.gradient_model.remove_color_stop_at_index(model_index)
            self.update_from_model()
            self.stops_changed.emit()
    
    def _find_model_index(self, target_position, tolerance=0.0001):
        """Find model index for a position."""
        model_stops = self.gradient_model.get_color_stops()
        for i, (position, _) in enumerate(model_stops):
            if abs(position - target_position) < tolerance:
                return i
        return -1
    
    def _apply_new_stops(self, positions, colors):
        """Apply new stops to the model."""
        self.gradient_model._color_stops = []
        for pos, color in zip(positions, colors):
            self.gradient_model.add_color_stop(pos, color)
        
        self.update_from_model()
        self.stops_changed.emit()
    
    def _update_ui_state(self):
        """Update UI element states."""
        count = len(self.color_stops)
        self.stops_counter.setText(f"Color Stops: {count}/{self.MAX_COLOR_STOPS}")
        
        # Update button states
        self.add_stop_button.setEnabled(count < self.MAX_COLOR_STOPS)
        self.randomize_colors_button.setEnabled(count > 0)
        self.randomize_positions_button.setEnabled(count > 1)
        self.distribute_evenly_button.setEnabled(count > 1)
    
    # Utility methods for debugging/advanced use (seed still accessible programmatically)
    def get_last_seed(self):
        """Get the last used seed for reproducibility (for advanced users/debugging)."""
        return self._internal_seed
    
    def set_manual_seed(self, seed):
        """Set a manual seed (for programmatic use, not exposed in UI)."""
        self._internal_seed = seed
    
    def regenerate_with_same_seed(self):
        """Regenerate using the same seed (useful for tweaking other parameters)."""
        if self._internal_seed is not None:
            # Temporarily store current values
            scheme_id = self.scheme_button_group.checkedId()
            num_stops = self.random_stops_slider.value()
            
            # Use the stored seed
            old_seed = self._internal_seed
            try:
                scheme_flags = [
                    {"harmonious": False}, {"harmonious": True}, {"monochromatic": True},
                    {"analogous": True}, {"complementary": True}, {"triadic": True}
                ]
                flags = scheme_flags[scheme_id] if 0 <= scheme_id < len(scheme_flags) else {}
                
                new_gradient = RandomGradientGenerator.generate_random_gradient(
                    num_stops=num_stops, random_seed=old_seed, **flags
                )
                
                if new_gradient:
                    self.gradient_model._color_stops = []
                    for stop in new_gradient.get_color_stop_objects():
                        self.gradient_model.add_color_stop(stop.position, stop.color)
                    
                    self.gradient_model.set_name(new_gradient.get_name())
                    self.gradient_model.set_description(new_gradient.get_description())
                    
                    self.update_from_model()
                    self.stops_changed.emit()
                    
                    self.status_label.setText("Regenerated with same pattern")
                    
            except Exception as e:
                self.status_label.setText(f"Regeneration failed: {str(e)}")
        else:
            self.status_label.setText("No previous pattern to regenerate")
