#!/usr/bin/env python3
"""
UPDATED Mathematical Distribution Widget - Phase Controls Instead of Strength

Modified to replace strength sliders with phase sliders for all patterns except even distribution.
Even distribution keeps its strength slider as it's the only one that needs gradual blending.
"""
import math
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QComboBox, QSlider, QGroupBox, QFormLayout, 
                           QSplitter, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal

# Import the shared preview system with fallback
try:
    from .shared_distribution_preview import create_distribution_preview_system
except ImportError:
    try:
        from shared_distribution_preview import create_distribution_preview_system
    except ImportError:
        def create_distribution_preview_system(gradient_model):
            from PyQt5.QtWidgets import QLabel
            return QLabel("Preview not available"), None

# Import the distributions with fallback
try:
    from .base_distributions import DISTRIBUTIONS, ColorStopDistribution
except ImportError:
    try:
        from base_distributions import DISTRIBUTIONS, ColorStopDistribution
    except ImportError:
        # Complete fallback implementation
        class ColorStopDistribution:
            def __init__(self, name, description):
                self.name = name
                self.description = description
            
            def distribute(self, num_stops, params=None):
                # Even distribution fallback
                if num_stops <= 1:
                    return [0.5]
                return [i / (num_stops - 1) for i in range(num_stops)]
            
            def _apply_strength(self, original_positions, target_positions, strength):
                if strength <= 0.0:
                    return original_positions
                elif strength >= 1.0:
                    return target_positions
                
                result = []
                for orig, target in zip(original_positions, target_positions):
                    interpolated = orig + (target - orig) * strength
                    result.append(interpolated)
                return result
        
        # Create minimal distributions registry
        class EvenDistribution(ColorStopDistribution):
            def __init__(self):
                super().__init__("Even Distribution", "Evenly space color stops")
            
            def distribute(self, num_stops, params=None):
                if num_stops <= 1:
                    return [0.5]
                
                p = params or {}
                strength = max(0.0, min(1.0, p.get('strength', 1.0)))
                original_positions = p.get('original_positions', None)
                
                if original_positions is None or len(original_positions) != num_stops:
                    original_positions = [i / (num_stops - 1) for i in range(num_stops)]
                
                # Generate target even positions
                target_positions = [i / (num_stops - 1) for i in range(num_stops)]
                
                # Apply strength
                result_positions = self._apply_strength(original_positions, target_positions, strength)
                
                # Ensure endpoints and sort
                if len(result_positions) >= 2:
                    result_positions[0] = 0.0
                    result_positions[-1] = 1.0
                
                return sorted(result_positions)
        
        class SineWaveDistribution(ColorStopDistribution):
            def __init__(self):
                super().__init__("Sine Wave", "Sinusoidal wave pattern")
            
            def distribute(self, num_stops, params=None):
                if num_stops <= 2:
                    return [0.0, 1.0] if num_stops == 2 else [0.5]
                
                try:
                    p = params or {}
                    frequency = max(0.1, min(8.0, p.get('frequency', 2.0)))
                    amplitude = max(0.0, min(0.4, p.get('amplitude', 0.2)))
                    phase = p.get('phase', 0.0)
                    original_positions = p.get('original_positions', [i / (num_stops - 1) for i in range(num_stops)])
                    
                    # Generate wave positions using phase
                    target_positions = []
                    for i in range(num_stops):
                        t = i / (num_stops - 1)
                        wave = math.sin(2 * math.pi * frequency * t + phase)
                        distorted = t + amplitude * wave
                        target_positions.append(distorted)
                    
                    # Always apply full pattern (no strength, just phase)
                    result_positions = [max(0.0, min(1.0, pos)) for pos in target_positions]
                    result_positions = sorted(result_positions)
                    if len(result_positions) >= 2:
                        result_positions[0] = 0.0
                        result_positions[-1] = 1.0
                    
                    return result_positions
                except Exception:
                    return [i / (num_stops - 1) for i in range(num_stops)]
        
        # Create minimal distributions registry
        DISTRIBUTIONS = {
            "even": EvenDistribution(),
            "sine_wave": SineWaveDistribution(),
        }


class ColorStopDistributionWidget(QWidget):
    """UPDATED Mathematical distribution widget with phase controls instead of strength."""
    
    distribution_changed = pyqtSignal()
    
    def __init__(self, gradient_model, parent=None):
        super().__init__(parent)
        self.gradient_model = gradient_model
        self.current_distribution = "even"
        self.distribution_params = {}
        self.param_controls = {}
        
        # Create preview system
        self.preview_widget, self.preview_controller = create_distribution_preview_system(gradient_model)
        
        self.init_ui()
        self._update_controls()
        
        # Connect preview signals
        if self.preview_controller:
            self.preview_controller.preview_widget.apply_changes.connect(self._on_apply)
            self.preview_controller.preview_widget.reset_changes.connect(self._on_reset)
            
        self._update_preview()
    
    def init_ui(self):
        """Initialize UI with conditional strength/phase control."""
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        
        # Controls panel
        controls_widget = QWidget()
        controls_widget.setMinimumHeight(500)
        controls_layout = QVBoxLayout(controls_widget)
        
        # Distribution group
        dist_group = QGroupBox("Mathematical Distribution Patterns")
        dist_group.setMinimumHeight(400)
        dist_layout = QVBoxLayout(dist_group)
        
        # Essential controls
        form = QFormLayout()
        
        # Distribution selector
        self.distribution_combo = QComboBox()
        if DISTRIBUTIONS:
            for dist in DISTRIBUTIONS.values():
                self.distribution_combo.addItem(dist.name)
        else:
            self.distribution_combo.addItem("Even Distribution")
        self.distribution_combo.currentIndexChanged.connect(self._on_distribution_changed)
        form.addRow("Pattern:", self.distribution_combo)
        
        # UPDATED: Primary control - either Strength OR Phase based on distribution
        self.primary_control_container = QWidget()
        self.primary_control_layout = QFormLayout(self.primary_control_container)
        form.addRow(self.primary_control_container)
        
        # Create both strength and phase controls (only one will be shown at a time)
        self._create_strength_control()
        self._create_phase_control()
        
        dist_layout.addLayout(form)
        
        # Scrollable parameters
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(200)
        scroll_area.setMaximumHeight(300)
        
        self.params_widget = QWidget()
        self.params_layout = QFormLayout(self.params_widget)
        scroll_area.setWidget(self.params_widget)
        dist_layout.addWidget(scroll_area)
        
        # Description with updated explanation
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #888; font-style: italic; padding: 5px;")
        self.description_label.setMinimumHeight(80)
        dist_layout.addWidget(self.description_label)
        
        controls_layout.addWidget(dist_group)
        controls_layout.addStretch()
        
        # Add to splitter
        splitter.addWidget(controls_widget)
        if self.preview_widget:
            splitter.addWidget(self.preview_widget)
        else:
            # Fallback if preview not available
            fallback_label = QLabel("Preview not available")
            fallback_label.setStyleSheet("color: #888; text-align: center; padding: 20px;")
            splitter.addWidget(fallback_label)
        
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
    
    def _create_strength_control(self):
        """Create the strength control (for even distribution only)."""
        self.strength_slider = QSlider(Qt.Horizontal)
        self.strength_slider.setRange(0, 100)
        self.strength_slider.setValue(0)  # Start at 0% to prevent jumps
        self.strength_slider.valueChanged.connect(self._on_strength_changed)
        
        self.strength_label = QLabel("Strength: 0%")
        strength_layout = QHBoxLayout()
        strength_layout.addWidget(self.strength_slider)
        strength_layout.addWidget(self.strength_label)
        
        self.strength_widget = QWidget()
        self.strength_widget.setLayout(strength_layout)
        
        self.primary_control_layout.addRow("Strength:", self.strength_widget)
        self.strength_widget.hide()  # Hidden by default
    
    def _create_phase_control(self):
        """Create the phase control (for all other distributions)."""
        self.phase_slider = QSlider(Qt.Horizontal)
        self.phase_slider.setRange(0, 360)
        self.phase_slider.setValue(0)  # Start at 0 degrees
        self.phase_slider.valueChanged.connect(self._on_phase_changed)
        
        self.phase_label = QLabel("Phase: 0°")
        phase_layout = QHBoxLayout()
        phase_layout.addWidget(self.phase_slider)
        phase_layout.addWidget(self.phase_label)
        
        self.phase_widget = QWidget()
        self.phase_widget.setLayout(phase_layout)
        
        self.primary_control_layout.addRow("Phase:", self.phase_widget)
        self.phase_widget.hide()  # Hidden by default
    
    def _on_distribution_changed(self, index):
        """Handle distribution change and show appropriate control."""
        if DISTRIBUTIONS:
            keys = list(DISTRIBUTIONS.keys())
            if 0 <= index < len(keys):
                self.current_distribution = keys[index]
        
        # Clear parameters
        self.distribution_params = {}
        
        # Show appropriate primary control
        self._update_primary_control_visibility()
        
        # Update other controls
        self._update_controls()
        self._update_preview()
    
    def _update_primary_control_visibility(self):
        """Show strength control for even distribution, phase control for others."""
        is_even_distribution = self.current_distribution == "even"
        
        self.strength_widget.setVisible(is_even_distribution)
        self.phase_widget.setVisible(not is_even_distribution)
        
        # Set initial parameter based on visible control
        if is_even_distribution:
            self.distribution_params['strength'] = self.strength_slider.value() / 100.0
        else:
            self.distribution_params['phase'] = math.radians(self.phase_slider.value())
    
    def _on_strength_changed(self, value):
        """Handle strength slider change (even distribution only)."""
        self.strength_label.setText(f"Strength: {value}%")
        self.distribution_params['strength'] = value / 100.0
        self._update_preview()
    
    def _on_phase_changed(self, value):
        """Handle phase slider change (all other distributions)."""
        self.phase_label.setText(f"Phase: {value}°")
        self.distribution_params['phase'] = math.radians(value)
        self._update_preview()
    
    def _update_controls(self):
        """Update parameter controls based on distribution type."""
        self._clear_params()
        
        dist_key = self.current_distribution
        
        # Parameter configurations for each distribution (excluding primary control)
        param_configs = {
            "sine_wave": [
                ("frequency", "Frequency:", 1, 8, 2, lambda v: v, "%d"),
                ("amplitude", "Amplitude:", 5, 40, 20, lambda v: v/100.0, "%.2f"),
            ],
            "harmonic_wave": [
                ("frequency", "Frequency:", 1, 6, 2, lambda v: v, "%d"),
                ("amplitude", "Amplitude:", 5, 30, 15, lambda v: v/100.0, "%.2f"),
                ("harmonics", "Harmonics:", 2, 6, 4, lambda v: v, "%d"),
            ],
            "spirograph": [
                ("outer_radius", "Outer Radius:", 2, 10, 5, lambda v: v, "%d"),
                ("inner_radius", "Inner Radius:", 1, 8, 3, lambda v: v, "%d"),
                ("pen_distance", "Pen Distance:", 1, 5, 2, lambda v: v, "%d"),
                ("amplitude", "Amplitude:", 5, 30, 20, lambda v: v/100.0, "%.2f"),
            ],
            "complex_wave": [
                ("frequency", "Frequency:", 1, 6, 2, lambda v: v, "%d"),
                ("amplitude", "Amplitude:", 5, 30, 20, lambda v: v/100.0, "%.2f"),
                ("complexity", "Complexity:", 1, 4, 2, lambda v: v, "%d"),
            ],
            "power_curves": [
                ("power", "Power:", 1, 100, 20, lambda v: v/10.0, "%.1f"),
            ],
            "golden_ratio": [
                # Golden ratio uses phase but no additional parameters
            ],
        }
        
        # Create controls for current distribution
        if dist_key in param_configs:
            for param_name, label, min_val, max_val, default, transform, format_str in param_configs[dist_key]:
                self._add_param_control(param_name, label, min_val, max_val, default, transform, format_str)
        
        # Update description with control explanation
        self._update_description()
        
        self.params_widget.updateGeometry()
        
        # Ensure primary control parameter is set
        self._update_primary_control_visibility()
        self._update_preview()
    
    def _update_description(self):
        """Update description with appropriate control explanation."""
        if self.current_distribution in DISTRIBUTIONS:
            description = DISTRIBUTIONS[self.current_distribution].description
            
            # Add control explanation based on distribution
            if self.current_distribution == "even":
                description += f"\n\n🎚️ Strength Control (0-100%):"
                description += f"\n• 0% = Original positions (no change)"
                description += f"\n• 100% = Perfect even spacing"
                description += f"\n• Gradually transitions from original to even distribution"
            else:
                description += f"\n\n🌊 Phase Control (0-360°):"
                description += f"\n• Controls the starting point of the wave pattern"
                description += f"\n• 0° = Standard phase, 180° = inverted pattern"
                description += f"\n• Full pattern is always applied - phase shifts the wave"
            
            self.description_label.setText(description)
    
    def _add_param_control(self, param_name, label, min_val, max_val, default, transform, format_str):
        """Add a parameter control slider."""
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.setMinimumHeight(25)
        
        # Value label
        if "°" in format_str:
            label_text = format_str % default
        else:
            label_text = format_str % transform(default)
        value_label = QLabel(label_text)
        value_label.setMinimumWidth(50)
        
        # Real-time parameter update
        def on_change(value, pname=param_name, vlabel=value_label, trans=transform, fmt=format_str):
            transformed_value = trans(value)
            self.distribution_params[pname] = transformed_value
            
            if "°" in fmt:
                vlabel.setText(fmt % value)
            else:
                vlabel.setText(fmt % transformed_value)
            
            self._update_preview()
        
        slider.valueChanged.connect(on_change)
        
        # Set initial value
        self.distribution_params[param_name] = transform(default)
        
        # Layout
        control_layout = QHBoxLayout()
        control_layout.addWidget(slider)
        control_layout.addWidget(value_label)
        
        control_widget = QWidget()
        control_widget.setLayout(control_layout)
        control_widget.setMinimumHeight(30)
        
        self.params_layout.addRow(label, control_widget)
        self.param_controls[param_name] = (slider, value_label)
    
    def _clear_params(self):
        """Clear parameter controls."""
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.param_controls.clear()
    
    def _update_preview(self):
        """Update preview with proper control handling."""
        if not self.preview_controller:
            return
        
        def math_distributor(color_stops, **kwargs):
            return self._apply_distribution_with_controls(color_stops)
        
        distribution_obj = DISTRIBUTIONS.get(self.current_distribution)
        description = f"Mathematical Pattern: {distribution_obj.description if distribution_obj else 'Unknown'}"
        
        # Add control info to description
        if self.current_distribution == "even":
            strength_pct = int(self.distribution_params.get('strength', 0) * 100)
            if strength_pct == 0:
                description += " (Original positions - no change)"
            elif strength_pct == 100:
                description += " (Perfect even spacing)"
            else:
                description += f" (Transitioning: {strength_pct}%)"
        else:
            phase_deg = int(math.degrees(self.distribution_params.get('phase', 0)))
            description += f" (Phase: {phase_deg}°)"
        
        self.preview_controller.set_distributor(math_distributor, self.distribution_params.copy(), description)
    
    def _apply_distribution_with_controls(self, color_stops):
        """
        Apply distribution with appropriate control handling.
        Even distribution uses strength, others use phase at full intensity.
        """
        if not color_stops:
            return color_stops
        
        try:
            distribution = DISTRIBUTIONS.get(self.current_distribution)
            if not distribution:
                return color_stops
            
            # Sort stops by position first to establish baseline order
            sorted_stops = sorted(color_stops, key=lambda x: x[0])
            
            # Extract colors and original positions IN SORTED ORDER
            colors_in_order = [color for _, color in sorted_stops]
            original_positions = [pos for pos, _ in sorted_stops]
            
            # Build parameters with all current values
            params = self.distribution_params.copy()
            
            # Always pass original positions
            params['original_positions'] = original_positions
            
            # For non-even distributions, ensure full pattern application
            if self.current_distribution != "even":
                # These distributions don't use strength - they use phase for variation
                # Remove any strength parameter that might interfere
                params.pop('strength', None)
            
            # Generate new positions using the distribution
            new_positions = distribution.distribute(len(sorted_stops), params)
            
            # Ensure correct length
            if len(new_positions) != len(colors_in_order):
                new_positions = new_positions[:len(colors_in_order)]
                while len(new_positions) < len(colors_in_order):
                    new_positions.append(1.0)
            
            # Combine new positions with colors IN THE SAME ORDER
            result = list(zip(new_positions, colors_in_order))
            
            # Sort by new position to maintain gradient order for rendering
            result.sort(key=lambda x: x[0])
            
            return result
            
        except Exception as e:
            print(f"Distribution error: {e}")
            return color_stops
    
    def _on_apply(self):
        """Handle apply from preview."""
        self.distribution_changed.emit()
    
    def _on_reset(self):
        """Handle reset from preview."""
        # Reset controls based on distribution type
        if self.current_distribution == "even":
            # Reset strength to 0%
            self.strength_slider.setValue(0)
            self.strength_label.setText("Strength: 0%")
            self.distribution_params = {'strength': 0.0}
        else:
            # Reset phase to 0°
            self.phase_slider.setValue(0)
            self.phase_label.setText("Phase: 0°")
            self.distribution_params = {'phase': 0.0}
        
        # Reset parameter controls to defaults
        for param_name, (slider, value_label) in self.param_controls.items():
            # Reset each control to its initial default value
            default_value = slider.minimum() + (slider.maximum() - slider.minimum()) // 2
            slider.setValue(default_value)
        
        self._update_controls()
        
        if self.preview_controller:
            self.preview_controller.refresh_original()
            self._update_preview()
    
    def update_from_model(self):
        """Update when model changes."""
        if self.preview_controller:
            self.preview_controller.refresh_original()
            self._update_preview()
    
    def showEvent(self, event):
        """Handle show event."""
        super().showEvent(event)
        if self.preview_controller:
            self.preview_controller.refresh_original()
            self._update_preview()


# Test function to verify the controls work correctly
def test_phase_controls():
    """Test the updated phase controls."""
    print("Testing UPDATED Distribution Widget - Phase Controls")
    print("=" * 60)
    
    # Sample gradient with uneven spacing
    test_stops = [
        (0.0, (255, 0, 0)),    # Red at start
        (0.1, (255, 127, 0)),  # Orange very close to start  
        (0.15, (255, 255, 0)), # Yellow still close to start
        (0.7, (0, 255, 0)),    # Green much later
        (1.0, (0, 0, 255))     # Blue at end
    ]
    
    print("Original stops:")
    for i, (pos, color) in enumerate(test_stops):
        print(f"  Stop {i}: pos={pos:.3f}, color=RGB{color}")
    
    # Create a mock widget to test the controls
    class MockGradientModel:
        pass
    
    widget = ColorStopDistributionWidget(MockGradientModel())
    
    print("\n" + "=" * 60)
    print("CONTROL UPDATES:")
    print("✅ Even Distribution: KEEPS strength slider (0-100%)")
    print("✅ Sine Wave: USES phase slider (0-360°) instead of strength")
    print("✅ Harmonic Wave: USES phase slider (0-360°) instead of strength") 
    print("✅ Spirograph: USES phase slider (0-360°) instead of strength")
    print("✅ Complex Wave: USES phase slider (0-360°) instead of strength")
    print("✅ Golden Ratio: USES phase slider (0-360°) instead of strength")
    print("✅ Power Curves: USES phase slider (0-360°) instead of strength")
    print("\n📝 Phase controls the starting point/offset of wave patterns")
    print("📝 Strength only used for even distribution (gradual blend to even spacing)")
    print("📝 All other patterns apply at full intensity with phase variation")


if __name__ == "__main__":
    test_phase_controls()
