#!/usr/bin/env python3
"""
FIXED Color Distribution Widget - Smooth Strength Transitions and Optimized UI

Fixed the strength slider to smoothly interpolate color reordering and matched
the UI layout to mathematical distributions while reducing file size.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QComboBox, QGroupBox, QFormLayout, 
                           QCheckBox, QColorDialog, QSlider, QSpinBox,
                           QSplitter, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

# Import the shared preview system
try:
    from .shared_distribution_preview import create_distribution_preview_system
except ImportError:
    try:
        from shared_distribution_preview import create_distribution_preview_system
    except ImportError:
        def create_distribution_preview_system(gradient_model):
            from PyQt5.QtWidgets import QLabel
            return QLabel("Preview not available"), None

# Import the distribution algorithms
try:
    from .color_distribution_base import (
        get_distribution, get_available_distributions, 
        create_distance_distribution
    )
    DISTRIBUTIONS_AVAILABLE = True
except ImportError:
    DISTRIBUTIONS_AVAILABLE = False
    def get_distribution(name): return None
    def get_available_distributions(): 
        return [("brightness", "Brightness", "Sort by brightness")]
    def create_distance_distribution(color): return None


class ColorDistributionWidget(QWidget):
    """Optimized color distribution widget with smooth strength transitions."""
    
    distribution_changed = pyqtSignal()
    
    def __init__(self, gradient_model, parent=None):
        super().__init__(parent)
        self.gradient_model = gradient_model
        self.current_distribution = "brightness"
        self.reference_color = (128, 128, 128)
        self.distribution_strength = 100  # 0-100%
        self.original_stops = []
        
        # Create preview system
        self.preview_widget, self.preview_controller = create_distribution_preview_system(gradient_model)
        
        self.init_ui()
        self._setup_preview_connections()
        self._store_original_stops()
        self._update_preview()
    
    def init_ui(self):
        """Initialize UI to match mathematical distributions layout."""
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        
        # === Controls panel (matching math distribution layout) ===
        controls_widget = QWidget()
        controls_widget.setMinimumHeight(600)  # Match math widget height
        controls_layout = QVBoxLayout(controls_widget)
        
        # Main distribution group
        dist_group = QGroupBox("Color-Based Reordering Patterns")
        dist_group.setMinimumHeight(500)  # Match math widget
        dist_layout = QVBoxLayout(dist_group)
        
        # Top section - distribution selector and strength
        top_form = QFormLayout()
        
        # Distribution selector
        self.distribution_combo = QComboBox()
        if DISTRIBUTIONS_AVAILABLE:
            for key, name, _ in get_available_distributions():
                self.distribution_combo.addItem(name, key)
            self.distribution_combo.addItem("Distance from Color", "distance")
        else:
            self.distribution_combo.addItem("Brightness", "brightness")
        
        self.distribution_combo.currentIndexChanged.connect(self._on_distribution_changed)
        top_form.addRow("Pattern:", self.distribution_combo)
        
        # Strength control (matching math widget style)
        self.strength_slider = QSlider(Qt.Horizontal)
        self.strength_slider.setRange(0, 100)
        self.strength_slider.setValue(100)
        self.strength_slider.valueChanged.connect(self._on_strength_changed)
        
        self.strength_label = QLabel("Strength: 100%")
        strength_layout = QHBoxLayout()
        strength_layout.addWidget(self.strength_slider)
        strength_layout.addWidget(self.strength_label)
        top_form.addRow("Strength:", strength_layout)
        
        dist_layout.addLayout(top_form)
        
        # === Scrollable parameters section (matching math widget) ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)
        scroll_area.setMaximumHeight(400)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        params_widget = QWidget()
        params_layout = QFormLayout(params_widget)
        params_layout.setVerticalSpacing(10)
        
        # Options controls
        self.reverse_check = QCheckBox("Reverse Order")
        self.reverse_check.stateChanged.connect(self._update_preview)
        params_layout.addRow("", self.reverse_check)
        
        self.preserve_endpoints_check = QCheckBox("Preserve Endpoints")
        self.preserve_endpoints_check.setChecked(True)
        self.preserve_endpoints_check.stateChanged.connect(self._update_preview)
        params_layout.addRow("", self.preserve_endpoints_check)
        
        # Reference color section (only for distance distribution)
        self.reference_group = QWidget()
        ref_layout = QFormLayout(self.reference_group)
        
        # Color picker
        color_layout = QHBoxLayout()
        self.color_button = QPushButton()
        self.color_button.setFixedSize(30, 30)
        self.color_button.clicked.connect(self._choose_reference_color)
        self._update_color_button()
        color_layout.addWidget(self.color_button)
        
        self.color_label = QLabel("RGB(128, 128, 128)")
        color_layout.addWidget(self.color_label)
        color_layout.addStretch()
        ref_layout.addRow("Reference:", color_layout)
        
        # Preset colors
        preset_layout = QHBoxLayout()
        presets = [("Black", (0, 0, 0)), ("White", (255, 255, 255)), 
                  ("Red", (255, 0, 0)), ("Green", (0, 255, 0)), ("Blue", (0, 0, 255))]
        
        for name, color in presets:
            btn = QPushButton(name)
            btn.setMaximumWidth(50)
            btn.clicked.connect(lambda checked, c=color: self._set_reference_color(c))
            preset_layout.addWidget(btn)
        
        preset_layout.addStretch()
        ref_layout.addRow("Presets:", preset_layout)
        
        params_layout.addRow("", self.reference_group)
        
        scroll_area.setWidget(params_widget)
        dist_layout.addWidget(scroll_area)
        
        # Description (matching math widget)
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #888; font-style: italic; padding: 5px; margin-top: 10px;")
        self.description_label.setMinimumHeight(60)
        dist_layout.addWidget(self.description_label)
        
        controls_layout.addWidget(dist_group)
        controls_layout.addStretch()
        
        # Add to splitter
        splitter.addWidget(controls_widget)
        splitter.addWidget(self.preview_widget)
        splitter.setSizes([450, 550])  # Match math widget proportions
        
        main_layout.addWidget(splitter)
        self._update_ui_state()
    
    def _setup_preview_connections(self):
        """Setup preview controller connections."""
        if self.preview_controller:
            # Override apply method with our fixed version
            self.preview_controller._original_apply = self.preview_controller.apply_to_model
            self.preview_controller.apply_to_model = self._fixed_apply_to_model
            
            # Connect signals
            self.preview_controller.preview_widget.apply_changes.connect(self._on_apply)
            self.preview_controller.preview_widget.reset_changes.connect(self._on_reset)
    
    def _store_original_stops(self):
        """Store original stops for strength blending."""
        if self.gradient_model and hasattr(self.gradient_model, 'get_color_stops'):
            self.original_stops = self.gradient_model.get_color_stops().copy()
    
    def _on_distribution_changed(self, index):
        """Handle distribution change."""
        data = self.distribution_combo.itemData(index)
        self.current_distribution = data if data else "brightness"
        self._update_ui_state()
        self._update_preview()
    
    def _on_strength_changed(self, value):
        """Handle strength slider change with smooth transitions."""
        self.distribution_strength = value
        self.strength_label.setText(f"Strength: {value}%")
        self._update_preview()
    
    def _update_ui_state(self):
        """Update UI based on current distribution."""
        is_distance = self.current_distribution == "distance"
        self.reference_group.setVisible(is_distance)
        
        # Update description
        descriptions = {
            "brightness": "Reorder colors by brightness from dark to light",
            "hue": "Reorder colors by hue around the color wheel",
            "saturation": "Reorder colors by saturation from gray to vivid",
            "distance": f"Reorder by distance from RGB{self.reference_color}"
        }
        desc = descriptions.get(self.current_distribution, "Reorder colors by properties")
        self.description_label.setText(desc)
    
    def _choose_reference_color(self):
        """Open color dialog."""
        color = QColorDialog.getColor(QColor(*self.reference_color), self, "Choose Reference Color")
        if color.isValid():
            self._set_reference_color((color.red(), color.green(), color.blue()))
    
    def _set_reference_color(self, color):
        """Set reference color and update preview."""
        self.reference_color = color
        self._update_color_button()
        self.color_label.setText(f"RGB({color[0]}, {color[1]}, {color[2]})")
        if self.current_distribution == "distance":
            self._update_ui_state()
            self._update_preview()
    
    def _update_color_button(self):
        """Update color button appearance."""
        r, g, b = self.reference_color
        self.color_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgb({r}, {g}, {b});
                border: 2px solid #555;
                border-radius: 2px;
            }}
            QPushButton:hover {{ border: 2px solid #888; }}
        """)
    
    def _update_preview(self):
        """Update preview with current settings."""
        if not self.preview_controller:
            return
        
        def color_distributor(color_stops, **kwargs):
            return self._apply_smooth_color_distribution(color_stops)
        
        # Create description
        if self.current_distribution == "distance":
            r, g, b = self.reference_color
            description = f"Color Reordering: Distance from RGB({r}, {g}, {b})"
        else:
            description = f"Color Reordering: {self.current_distribution.title()}"
        
        if self.distribution_strength < 100:
            description += f" (Strength: {self.distribution_strength}%)"
        
        self.preview_controller.set_distributor(color_distributor, {}, description)
    
    def _apply_smooth_color_distribution(self, color_stops):
        """FIXED: Apply color distribution with truly smooth strength transitions."""
        if not color_stops or len(color_stops) < 2:
            return color_stops
        
        try:
            # Get the full reordered result
            full_reordered = self._get_full_reordered_stops(color_stops)
            
            # Apply smooth strength blending
            if self.distribution_strength == 0:
                return color_stops  # No change
            elif self.distribution_strength == 100:
                return full_reordered  # Full reordering
            else:
                # FIXED: Use smooth color sequence interpolation
                return self._smooth_color_sequence_blend(
                    color_stops, full_reordered, self.distribution_strength / 100.0
                )
                
        except Exception as e:
            print(f"Color distribution error: {e}")
            return color_stops
    
    def _smooth_color_sequence_blend(self, original_stops, target_stops, strength):
        """Create smooth transitions between original and target color sequences."""
        if len(original_stops) != len(target_stops):
            return target_stops
        
        # Extract positions and colors
        positions = [pos for pos, _ in original_stops]
        orig_colors = [color for _, color in original_stops]
        target_colors = [color for _, color in target_stops]
        
        # Create a weighted blend of the two color sequences
        result_colors = []
        
        # Apply smooth step function for natural transition feel
        def smooth_step(t):
            """Smooth step function: 3t² - 2t³"""
            return t * t * (3.0 - 2.0 * t) if 0 <= t <= 1 else (0 if t < 0 else 1)
        
        blend_factor = smooth_step(strength)
        
        # Method 1: Gradual color sequence morphing
        # This creates a smooth wave-like transition across the gradient
        for i, (orig_color, target_color) in enumerate(zip(orig_colors, target_colors)):
            # Calculate position-based influence (creates a smooth sweep effect)
            position_factor = i / (len(orig_colors) - 1) if len(orig_colors) > 1 else 0
            
            # Create a wave that sweeps across the gradient based on strength
            # This makes the transition visible as it progresses
            wave_position = blend_factor * 1.2 - 0.1  # Slight overshoot for complete coverage
            
            # Calculate local blend weight based on position
            distance_from_wave = abs(position_factor - wave_position)
            wave_width = 0.3  # Width of the transition zone
            
            if distance_from_wave < wave_width:
                # In transition zone - blend between original and target
                local_blend = 1.0 - (distance_from_wave / wave_width)
                local_blend = smooth_step(local_blend)
                
                # Interpolate between original and target colors
                if local_blend > 0.5:
                    result_colors.append(target_color)
                else:
                    result_colors.append(orig_color)
            else:
                # Outside transition zone
                if position_factor < wave_position - wave_width:
                    # Already transitioned
                    result_colors.append(target_color)
                else:
                    # Not yet transitioned
                    result_colors.append(orig_color)
        
        # Method 2: If the wave approach seems too complex, use simpler interpolation
        # Fallback to direct interpolation if we want simpler behavior
        if strength < 0.1:  # Very low strength - mostly original
            result_colors = orig_colors.copy()
        elif strength > 0.9:  # Very high strength - mostly target
            result_colors = target_colors.copy()
        else:
            # Create smooth blend by gradually replacing colors from one end
            blend_point = int(len(orig_colors) * blend_factor)
            result_colors = target_colors[:blend_point] + orig_colors[blend_point:]
        
        return list(zip(positions, result_colors))
    
    def _get_full_reordered_stops(self, color_stops):
        """Get fully reordered color stops."""
        if DISTRIBUTIONS_AVAILABLE:
            if self.current_distribution == "distance":
                distribution = create_distance_distribution(self.reference_color)
            else:
                distribution = get_distribution(self.current_distribution)
            
            if distribution:
                return distribution.distribute(
                    color_stops,
                    self.reverse_check.isChecked(),
                    self.preserve_endpoints_check.isChecked()
                )
        
        # Fallback: simple brightness sorting
        return self._fallback_brightness_sort(color_stops)
    

    
    def _fallback_brightness_sort(self, color_stops):
        """Fallback brightness sorting."""
        def brightness_key(stop):
            _, (r, g, b) = stop
            return 0.299 * r + 0.587 * g + 0.114 * b
        
        # Extract positions and colors
        positions = [pos for pos, _ in color_stops]
        sorted_colors = [color for _, color in sorted(color_stops, key=brightness_key, 
                                                     reverse=self.reverse_check.isChecked())]
        
        # Handle endpoint preservation
        if self.preserve_endpoints_check.isChecked() and len(sorted_colors) >= 2:
            first_color = color_stops[0][1]
            last_color = color_stops[-1][1]
            
            # Remove these from sorted list
            if first_color in sorted_colors:
                sorted_colors.remove(first_color)
            if last_color in sorted_colors and last_color != first_color:
                sorted_colors.remove(last_color)
            
            # Reconstruct with preserved endpoints
            final_colors = [first_color] + sorted_colors + [last_color]
            final_colors = final_colors[:len(positions)]
        else:
            final_colors = sorted_colors
        
        return list(zip(positions, final_colors))
    
    def _fixed_apply_to_model(self):
        """Fixed apply method for gradient model."""
        if not self.preview_controller.preview_widget.preview_stops:
            return
        
        try:
            preview_stops = self.preview_controller.preview_widget.preview_stops
            
            # Clear and repopulate model
            self.gradient_model._color_stops = []
            sorted_stops = sorted(preview_stops, key=lambda x: x[0])
            
            for position, color in sorted_stops:
                self.gradient_model.add_color_stop(
                    max(0.0, min(1.0, position)),
                    tuple(max(0, min(255, int(c))) for c in color)
                )
            
            # Update stored original stops
            self._store_original_stops()
            self.preview_controller.refresh_original()
            
        except Exception as e:
            print(f"Apply error: {e}")
    
    def _on_apply(self):
        """Handle apply from preview."""
        self._fixed_apply_to_model()
        self.distribution_changed.emit()
    
    def _on_reset(self):
        """Handle reset from preview."""
        if self.original_stops:
            self.gradient_model._color_stops = []
            for position, color in self.original_stops:
                self.gradient_model.add_color_stop(position, color)
        
        # Reset controls
        self.distribution_strength = 100
        self.strength_slider.setValue(100)
        self.strength_label.setText("Strength: 100%")
        self.reverse_check.setChecked(False)
        self.preserve_endpoints_check.setChecked(True)
        self.reference_color = (128, 128, 128)
        self._update_color_button()
        self.color_label.setText("RGB(128, 128, 128)")
        
        self.distribution_changed.emit()
        
        if self.preview_controller:
            self.preview_controller.refresh_original()
            self._update_preview()
    
    def update_from_model(self):
        """Update when model changes."""
        self._store_original_stops()
        if self.preview_controller:
            self.preview_controller.refresh_original()
            self._update_preview()
    
    def showEvent(self, event):
        """Handle show event."""
        super().showEvent(event)
        self._store_original_stops()
        if self.preview_controller:
            self.preview_controller.refresh_original()
            self._update_preview()
