#!/usr/bin/env python3
"""
Simplified Gradient Adjustments Module for Gradient Generator

Streamlined controls for adjusting gradient properties including brightness, 
contrast, gamma, saturation, hue shift, warmth, highlights, and shadows.
Simplified randomization with single "Randomize All" button and "Reset All" 
that restores to pre-adjustment state.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                          QLabel, QSlider, QGroupBox, QDoubleSpinBox,
                          QFormLayout, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
import random
import copy

# Import with fallback mechanism
try:
    from gradient_generator.core.color_utils import rgb_to_hsv, hsv_to_rgb
except ImportError:
    try:
        import sys, os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
        from gradient_generator.core.color_utils import rgb_to_hsv, hsv_to_rgb
    except ImportError:
        from ...core.color_utils import rgb_to_hsv, hsv_to_rgb


class GradientAdjustmentsWidget(QWidget):
    """Simplified widget for adjusting overall gradient properties."""
    
    adjustments_changed = pyqtSignal()
    
    def __init__(self, gradient_model):
        super().__init__()
        
        self.gradient_model = gradient_model
        self._original_stops = None
        self._pre_adjustment_backup = None
        
        # Adjustment properties with defaults
        self.adjustments = {
            'brightness': 1.0,
            'contrast': 1.0,
            'saturation': 1.0,
            'gamma': 1.0,
            'hue_shift': 0,
            'warmth': 0.0,
            'highlights': 0.0,
            'shadows': 0.0
        }
        
        # Update timer for performance
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.apply_adjustments)
        
        self.init_ui()
        self._store_original_stops()
        self._create_pre_adjustment_backup()
    
    def _store_original_stops(self):
        """Store the original color stops for non-destructive editing."""
        self._original_stops = self.gradient_model.get_color_stop_objects().copy()
    
    def _create_pre_adjustment_backup(self):
        """Create a backup of the gradient before any adjustments are made."""
        try:
            self._pre_adjustment_backup = {
                'color_stops': [(stop.position, stop.color) for stop in self.gradient_model.get_color_stop_objects()],
                'metadata': {
                    'name': self.gradient_model.get_name(),
                    'author': self.gradient_model.get_author(),
                    'description': self.gradient_model.get_description(),
                    'ugr_category': self.gradient_model.get_ugr_category(),
                    'combine_gradients': self.gradient_model.get_combine_gradients(),
                    'seamless_blend': self.gradient_model.get_seamless_blend(),
                    'blend_region': self.gradient_model.get_blend_region(),
                }
            }
            
            # Store additional properties if they exist
            for prop in ['progressive_blending', 'intensity_falloff', 'preview_overlay']:
                if hasattr(self.gradient_model, f'get_{prop}'):
                    try:
                        self._pre_adjustment_backup['metadata'][prop] = getattr(self.gradient_model, f'get_{prop}')()
                    except:
                        pass
                        
        except Exception as e:
            print(f"Error creating pre-adjustment backup: {e}")
            self._pre_adjustment_backup = None
    
    def _update_original_stops(self):
        """Update stored original stops (called when gradient changes externally)."""
        self._store_original_stops()
        self._create_pre_adjustment_backup()
    
    def init_ui(self):
        """Initialize the simplified UI components."""
        main_layout = QVBoxLayout(self)
        
        # Color Adjustments Group
        adjustments_group = QGroupBox("Color Adjustments")
        adjustments_layout = QVBoxLayout(adjustments_group)
        
        # Create sliders for each adjustment
        self.sliders = {}
        
        slider_configs = [
            ('brightness', 'Brightness', 0.0, 2.0, 1.0, 0.01),
            ('contrast', 'Contrast', 0.5, 2.0, 1.0, 0.01),
            ('saturation', 'Saturation', 0.0, 2.0, 1.0, 0.01),
            ('gamma', 'Gamma', 0.5, 2.0, 1.0, 0.01),
            ('hue_shift', 'Hue Shift', 0, 360, 0, 1),
            ('warmth', 'Warmth', -1.0, 1.0, 0.0, 0.01),
            ('highlights', 'Highlights', -1.0, 1.0, 0.0, 0.01),
            ('shadows', 'Shadows', -1.0, 1.0, 0.0, 0.01)
        ]
        
        for key, label, min_val, max_val, default, step in slider_configs:
            control_widget = self._create_slider_control(key, label, min_val, max_val, default, step)
            adjustments_layout.addWidget(control_widget)
        
        main_layout.addWidget(adjustments_group)
        
        # Simplified Controls Group
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Randomization amount
        amount_layout = QFormLayout()
        self.randomize_amount_spin = QDoubleSpinBox()
        self.randomize_amount_spin.setRange(0.01, 1.0)
        self.randomize_amount_spin.setSingleStep(0.01)
        self.randomize_amount_spin.setValue(0.2)  # Default randomization strength
        self.randomize_amount_spin.setDecimals(2)
        amount_layout.addRow("Randomization Strength:", self.randomize_amount_spin)
        controls_layout.addLayout(amount_layout)
        
        # Button row
        button_layout = QHBoxLayout()
        
        self.randomize_all_button = QPushButton("Randomize All")
        self.randomize_all_button.clicked.connect(self.randomize_all_adjustments)
        self.randomize_all_button.setStyleSheet("font-weight: bold; padding: 8px; background-color: #5a5a7c;")
        button_layout.addWidget(self.randomize_all_button)
        
        self.reset_all_button = QPushButton("Reset All")
        self.reset_all_button.clicked.connect(self.reset_to_pre_adjustment_state)
        self.reset_all_button.setStyleSheet("font-weight: bold; padding: 8px; background-color: #7c5a4a;")
        button_layout.addWidget(self.reset_all_button)
        
        controls_layout.addLayout(button_layout)
        
        main_layout.addWidget(controls_group)
        main_layout.addStretch()
    
    def _create_slider_control(self, key, label, min_val, max_val, default, step):
        """Create a simplified slider control."""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(5, 5, 5, 5)
        container_layout.setSpacing(5)
        
        # Label with value
        if key == 'hue_shift':
            label_text = f"{label}: {int(default)}°"
            is_int = True
        else:
            label_text = f"{label}: {default:.2f}"
            is_int = False
        
        label_widget = QLabel(label_text)
        label_widget.setMinimumWidth(120)
        container_layout.addWidget(label_widget)
        
        # Slider
        slider = QSlider(Qt.Horizontal)
        
        if is_int:
            slider.setRange(int(min_val), int(max_val))
            slider.setValue(int(default))
            slider.setSingleStep(int(step))
        else:
            # Convert to integer range for QSlider
            slider.setRange(int(min_val * 100), int(max_val * 100))
            slider.setValue(int(default * 100))
            slider.setSingleStep(int(step * 100))
        
        # Connect signals
        slider.valueChanged.connect(lambda value, k=key, lw=label_widget, is_i=is_int: 
                                   self._on_slider_changed(k, value, lw, is_i))
        slider.sliderPressed.connect(lambda: self.update_timer.stop())
        slider.sliderReleased.connect(self.apply_adjustments)
        
        container_layout.addWidget(slider)
        
        # Store references
        self.sliders[key] = {'slider': slider, 'label': label_widget}
        
        return container
    
    def _on_slider_changed(self, key, value, label_widget, is_int):
        """Handle slider value changes."""
        if is_int:
            actual_value = value
            self.adjustments[key] = actual_value
            label_widget.setText(f"{key.replace('_', ' ').title()}: {actual_value}°")
        else:
            actual_value = value / 100.0
            self.adjustments[key] = actual_value
            label_widget.setText(f"{key.replace('_', ' ').title()}: {actual_value:.2f}")
        
        # Debounce updates during dragging
        slider = self.sliders[key]['slider']
        if not slider.isSliderDown():
            self.apply_adjustments()
        else:
            self.update_timer.start(100)
    
    def randomize_all_adjustments(self):
        """Apply random adjustments to all parameters."""
        amount = self.randomize_amount_spin.value()
        
        # Reset all adjustments first
        self.reset_adjustment_values(apply_immediately=False)
        
        # Randomize all parameters
        for param in self.adjustments.keys():
            self._randomize_single_parameter(param, amount)
        
        self.apply_adjustments()
        
        # Show feedback
        try:
            main_window = self.window()
            if hasattr(main_window, 'statusBar'):
                main_window.statusBar().showMessage(f"Randomized all adjustments with strength {amount:.2f}", 3000)
        except:
            pass
    
    def _randomize_single_parameter(self, param, amount):
        """Randomize a single parameter within reasonable bounds."""
        if param == 'hue_shift':
            # Hue shift: random value across full range
            hue_shift = random.randint(0, 360)
            self.sliders[param]['slider'].setValue(hue_shift)
            
        elif param in ['brightness', 'contrast', 'saturation', 'gamma']:
            # Multiplicative factors: vary around 1.0
            base_value = 1.0
            max_variation = amount * 1.5  # Allow more variation for these
            factor = max(0.1, min(2.0, base_value + (random.random() * 2 - 1) * max_variation))
            self.sliders[param]['slider'].setValue(int(factor * 100))
            
        elif param in ['warmth', 'highlights', 'shadows']:
            # Additive factors: vary around 0.0
            max_variation = amount
            factor = max(-1.0, min(1.0, (random.random() * 2 - 1) * max_variation))
            self.sliders[param]['slider'].setValue(int(factor * 100))
    
    def apply_adjustments(self):
        """Apply all adjustments to the gradient."""
        if not self._original_stops:
            self._store_original_stops()
        
        # Clear existing stops
        self.gradient_model._color_stops = []
        
        # Apply adjustments to each original stop
        for stop in self._original_stops:
            adjusted_color = self._apply_color_adjustments(stop.color)
            self.gradient_model.add_color_stop(stop.position, adjusted_color)
        
        self.adjustments_changed.emit()
    
    def _apply_color_adjustments(self, color):
        """Apply all adjustments to a single color."""
        r, g, b = color
        
        # Convert to HSV for hue/saturation adjustments
        h, s, v = rgb_to_hsv(r, g, b)
        
        # Hue shift
        if self.adjustments['hue_shift'] != 0:
            h = (h + self.adjustments['hue_shift']) % 360
        
        # Saturation
        if self.adjustments['saturation'] != 1.0:
            s = max(0.0, min(1.0, s * self.adjustments['saturation']))
        
        # Convert back to RGB for other adjustments
        r, g, b = hsv_to_rgb(h, s, v)
        
        # Normalize to 0-1 range for calculations
        r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
        
        # Brightness
        if self.adjustments['brightness'] != 1.0:
            r_norm *= self.adjustments['brightness']
            g_norm *= self.adjustments['brightness']
            b_norm *= self.adjustments['brightness']
        
        # Contrast (pivot around 0.5)
        if self.adjustments['contrast'] != 1.0:
            r_norm = 0.5 + (r_norm - 0.5) * self.adjustments['contrast']
            g_norm = 0.5 + (g_norm - 0.5) * self.adjustments['contrast']
            b_norm = 0.5 + (b_norm - 0.5) * self.adjustments['contrast']
        
        # Gamma correction
        if self.adjustments['gamma'] != 1.0:
            gamma_factor = 1.0 / max(0.01, self.adjustments['gamma'])
            r_norm = pow(max(0.0, r_norm), gamma_factor)
            g_norm = pow(max(0.0, g_norm), gamma_factor)
            b_norm = pow(max(0.0, b_norm), gamma_factor)
        
        # Warmth adjustment (shift towards orange/blue)
        if self.adjustments['warmth'] != 0.0:
            warmth = self.adjustments['warmth']
            if warmth > 0:  # Warmer (more orange/red)
                r_norm = min(1.0, r_norm + warmth * 0.2)
                g_norm = min(1.0, g_norm + warmth * 0.1)
                b_norm = max(0.0, b_norm - warmth * 0.1)
            else:  # Cooler (more blue)
                warmth = abs(warmth)
                r_norm = max(0.0, r_norm - warmth * 0.1)
                g_norm = max(0.0, g_norm - warmth * 0.05)
                b_norm = min(1.0, b_norm + warmth * 0.2)
        
        # Highlights adjustment (affects brighter tones)
        if self.adjustments['highlights'] != 0.0:
            highlights = self.adjustments['highlights']
            # Calculate luminance to determine if pixel is in highlights
            luminance = 0.299 * r_norm + 0.587 * g_norm + 0.114 * b_norm
            if luminance > 0.6:  # Only affect highlights
                highlight_factor = (luminance - 0.6) / 0.4  # 0-1 for highlights range
                adjustment = highlights * highlight_factor * 0.3
                r_norm = max(0.0, min(1.0, r_norm + adjustment))
                g_norm = max(0.0, min(1.0, g_norm + adjustment))
                b_norm = max(0.0, min(1.0, b_norm + adjustment))
        
        # Shadows adjustment (affects darker tones)
        if self.adjustments['shadows'] != 0.0:
            shadows = self.adjustments['shadows']
            # Calculate luminance to determine if pixel is in shadows
            luminance = 0.299 * r_norm + 0.587 * g_norm + 0.114 * b_norm
            if luminance < 0.4:  # Only affect shadows
                shadow_factor = (0.4 - luminance) / 0.4  # 0-1 for shadows range
                adjustment = shadows * shadow_factor * 0.3
                r_norm = max(0.0, min(1.0, r_norm + adjustment))
                g_norm = max(0.0, min(1.0, g_norm + adjustment))
                b_norm = max(0.0, min(1.0, b_norm + adjustment))
        
        # Convert back to 0-255 range and clamp
        r = max(0, min(255, int(r_norm * 255)))
        g = max(0, min(255, int(g_norm * 255)))
        b = max(0, min(255, int(b_norm * 255)))
        
        return (r, g, b)
    
    def reset_to_pre_adjustment_state(self):
        """Reset gradient to its state before any adjustments were made."""
        if not self._pre_adjustment_backup:
            try:
                main_window = self.window()
                if hasattr(main_window, 'statusBar'):
                    main_window.statusBar().showMessage("No pre-adjustment backup available", 3000)
            except:
                pass
            return
        
        try:
            # Restore color stops
            self.gradient_model._color_stops = []
            for position, color in self._pre_adjustment_backup['color_stops']:
                self.gradient_model.add_color_stop(position, color)
            
            # Restore metadata
            metadata = self._pre_adjustment_backup['metadata']
            for prop, value in metadata.items():
                if hasattr(self.gradient_model, f'set_{prop}'):
                    try:
                        getattr(self.gradient_model, f'set_{prop}')(value)
                    except:
                        pass
            
            # Reset adjustment values
            self.reset_adjustment_values(apply_immediately=False)
            
            # Update original stops to current state
            self._store_original_stops()
            
            # Emit change signal
            self.adjustments_changed.emit()
            
            # Show feedback
            try:
                main_window = self.window()
                if hasattr(main_window, 'statusBar'):
                    main_window.statusBar().showMessage("Reset to pre-adjustment state", 3000)
            except:
                pass
                
        except Exception as e:
            print(f"Reset error: {e}")
    
    def reset_adjustment_values(self, apply_immediately=True):
        """Reset all adjustment values to default values."""
        # Block signals to prevent multiple updates
        self.blockSignals(True)
        
        # Reset all sliders
        for key, config in self.sliders.items():
            slider = config['slider']
            label = config['label']
            
            if key == 'hue_shift':
                slider.setValue(0)
                label.setText("Hue Shift: 0°")
                self.adjustments[key] = 0
            elif key in ['warmth', 'highlights', 'shadows']:
                slider.setValue(0)  # 0 * 100 = 0
                label.setText(f"{key.replace('_', ' ').title()}: 0.00")
                self.adjustments[key] = 0.0
            else:
                slider.setValue(100)  # 1.0 * 100 = 100
                label.setText(f"{key.replace('_', ' ').title()}: 1.00")
                self.adjustments[key] = 1.0
        
        # Unblock signals
        self.blockSignals(False)
        
        # Apply changes if requested
        if apply_immediately and self._original_stops:
            self.gradient_model._color_stops = []
            for stop in self._original_stops:
                self.gradient_model.add_color_stop(stop.position, stop.color)
            self.adjustments_changed.emit()
    
    def get_adjustment_values(self):
        """Get current adjustment values as a dictionary."""
        return self.adjustments.copy()
    
    def set_adjustment_values(self, values):
        """Set adjustment values from a dictionary."""
        for key, value in values.items():
            if key in self.adjustments and key in self.sliders:
                self.adjustments[key] = value
                slider = self.sliders[key]['slider']
                label = self.sliders[key]['label']
                
                if key == 'hue_shift':
                    slider.setValue(int(value))
                    label.setText(f"Hue Shift: {int(value)}°")
                else:
                    slider.setValue(int(value * 100))
                    label.setText(f"{key.replace('_', ' ').title()}: {value:.2f}")
        
        self.apply_adjustments()
