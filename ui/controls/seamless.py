#!/usr/bin/env python3
"""
Refactored Seamless Blending Module - Fixed Progressive Blending

Key changes:
- Progressive blending now only modifies existing color stops within blend regions
- No new color stops are added during progressive blending
- Significantly reduced code size while preserving all functionality
- Cleaner separation between basic and progressive seamless operations
- FIXED: Added missing _update_seamless_config method and other missing methods
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QGroupBox, QCheckBox, QDoubleSpinBox, QSlider, 
                           QFormLayout, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal


class SeamlessBlendingWidget(QWidget):
    """Streamlined seamless blending widget with fixed progressive functionality."""
    
    settings_changed = pyqtSignal()
    seamless_applied = pyqtSignal()
    gradient_modified = pyqtSignal()
    
    def __init__(self, gradient_model):
        super().__init__()
        self.gradient_model = gradient_model
        self.animated_preview = None
        self.init_ui()
        self.update_from_model()
    
    def set_animated_preview(self, preview):
        """Set reference to animated preview for coordination."""
        self.animated_preview = preview
    
    def init_ui(self):
        """Initialize streamlined UI."""
        layout = QVBoxLayout(self)
        
        # Basic seamless group
        basic_group = QGroupBox("Seamless Blending")
        basic_layout = QVBoxLayout(basic_group)
        
        self.seamless_check = QCheckBox("Enable Seamless Blending")
        self.seamless_check.stateChanged.connect(self.on_seamless_changed)
        self.seamless_check.setToolTip("Make first and last colors identical for seamless wrapping")
        basic_layout.addWidget(self.seamless_check)
        
        self.preview_overlay_check = QCheckBox("Show Preview Overlay")
        self.preview_overlay_check.setChecked(True)
        self.preview_overlay_check.stateChanged.connect(self.on_preview_overlay_changed)
        basic_layout.addWidget(self.preview_overlay_check)
        
        layout.addWidget(basic_group)
        
        # Progressive group - simplified
        progressive_group = QGroupBox("Progressive Blending")
        progressive_layout = QFormLayout(progressive_group)
        
        self.progressive_check = QCheckBox("Enable Progressive Blending")
        self.progressive_check.setToolTip("Gradually blend colors in transition regions")
        self.progressive_check.stateChanged.connect(self.on_progressive_changed)
        progressive_layout.addRow(self.progressive_check)
        
        # Blend region slider
        blend_layout = QHBoxLayout()
        self.blend_region_spin = QDoubleSpinBox()
        self.blend_region_spin.setRange(0.01, 0.5)
        self.blend_region_spin.setValue(0.1)
        self.blend_region_spin.setDecimals(3)
        self.blend_region_spin.valueChanged.connect(self.on_blend_region_changed)
        self.blend_region_spin.setEnabled(False)
        
        self.blend_region_slider = QSlider(Qt.Horizontal)
        self.blend_region_slider.setRange(1, 50)
        self.blend_region_slider.setValue(10)
        self.blend_region_slider.valueChanged.connect(self.on_blend_region_slider_changed)
        self.blend_region_slider.setEnabled(False)
        
        blend_layout.addWidget(self.blend_region_spin)
        blend_layout.addWidget(self.blend_region_slider)
        progressive_layout.addRow("Blend Region:", blend_layout)
        
        # Intensity slider
        intensity_layout = QHBoxLayout()
        self.intensity_spin = QDoubleSpinBox()
        self.intensity_spin.setRange(0.0, 1.0)
        self.intensity_spin.setValue(0.7)
        self.intensity_spin.setDecimals(2)
        self.intensity_spin.valueChanged.connect(self.on_intensity_changed)
        self.intensity_spin.setEnabled(False)
        
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setRange(0, 100)
        self.intensity_slider.setValue(70)
        self.intensity_slider.valueChanged.connect(self.on_intensity_slider_changed)
        self.intensity_slider.setEnabled(False)
        
        intensity_layout.addWidget(self.intensity_spin)
        intensity_layout.addWidget(self.intensity_slider)
        progressive_layout.addRow("Blend Intensity:", intensity_layout)
        
        layout.addWidget(progressive_group)
        
        # Apply section
        apply_group = QGroupBox("Apply Effects")
        apply_layout = QVBoxLayout(apply_group)
        
        self.apply_button = QPushButton("Apply Seamless Effects")
        self.apply_button.clicked.connect(self.on_apply_seamless)
        self.apply_button.setEnabled(False)
        self.apply_button.setStyleSheet("font-weight: bold; padding: 8px;")
        apply_layout.addWidget(self.apply_button)
        
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #888; font-size: 10px;")
        apply_layout.addWidget(self.info_label)
        
        layout.addWidget(apply_group)
        
        # Compact info
        info_text = ("<b>Basic:</b> Makes first/last colors identical<br>"
                    "<b>Progressive:</b> Smoothly blends existing stops in edge regions")
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #888; font-size: 9pt; padding: 4px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        self._update_ui_state()
    
    def update_from_model(self):
        """Update controls from model."""
        self.seamless_check.blockSignals(True)
        self.seamless_check.setChecked(self.gradient_model.get_seamless_blend())
        self.seamless_check.blockSignals(False)
        self._update_ui_state()
    
    def _update_ui_state(self):
        """Update UI control states."""
        seamless_enabled = self.seamless_check.isChecked()
        progressive_enabled = self.progressive_check.isChecked() and seamless_enabled
        
        self.progressive_check.setEnabled(seamless_enabled)
        self.blend_region_spin.setEnabled(progressive_enabled)
        self.blend_region_slider.setEnabled(progressive_enabled)
        self.intensity_spin.setEnabled(progressive_enabled)
        self.intensity_slider.setEnabled(progressive_enabled)
        self.apply_button.setEnabled(seamless_enabled)
        
        # Update info
        if not seamless_enabled:
            self.info_label.setText("Enable seamless blending to apply effects")
        elif progressive_enabled:
            self.info_label.setText(f"Will blend existing stops in {self.blend_region_spin.value():.3f} regions")
        else:
            self.info_label.setText("Will make first and last colors identical")
    
    def _update_seamless_config(self):
        """FIXED: Update seamless configuration in the gradient model."""
        try:
            # Update basic seamless settings
            self.gradient_model.set_seamless_blend(self.seamless_check.isChecked())
            self.gradient_model.set_blend_region(self.blend_region_spin.value())
            
            # Update progressive settings if the gradient model supports them
            if hasattr(self.gradient_model, 'set_progressive_blending'):
                self.gradient_model.set_progressive_blending(self.progressive_check.isChecked())
            
            if hasattr(self.gradient_model, 'set_intensity_falloff'):
                self.gradient_model.set_intensity_falloff(self.intensity_spin.value())
            
            # Update preview overlay setting
            if hasattr(self.gradient_model, 'set_preview_overlay'):
                self.gradient_model.set_preview_overlay(self.preview_overlay_check.isChecked())
            elif hasattr(self.gradient_model, '_seamless'):
                self.gradient_model._seamless.set_preview_overlay(self.preview_overlay_check.isChecked())
            
        except Exception as e:
            print(f"Error updating seamless config: {e}")
    
    def _update_diagnostic_info(self):
        """FIXED: Update diagnostic information display."""
        try:
            current_stops = self.gradient_model.get_color_stops()
            if not current_stops:
                self.info_label.setText("No color stops available")
                return
            
            sorted_stops = sorted(current_stops, key=lambda x: x[0])
            first_stop = sorted_stops[0]
            last_stop = sorted_stops[-1]
            
            first_pos, first_color = first_stop
            last_pos, last_color = last_stop
            
            # Check if colors match
            colors_match = first_color == last_color
            
            if colors_match:
                self.info_label.setText(f"✓ Seamless: First/last colors match RGB{first_color}")
            else:
                self.info_label.setText(f"⚠ First: RGB{first_color}, Last: RGB{last_color} (different)")
                
        except Exception as e:
            self.info_label.setText(f"Error checking seamless state: {e}")

    def _identify_first_last_stops_robust(self):
        """
        ROBUST: Identify first and last stops with multiple fallback strategies.
        Same logic as the preview fix, but for apply operations.
        
        Returns:
            tuple: (first_stop, last_stop) where each is (position, color) or None if not found
        """
        current_stops = self.gradient_model.get_color_stops()
        
        if not current_stops:
            return None, None
        
        if len(current_stops) == 1:
            # Single stop - it's both first and last
            return current_stops[0], current_stops[0]
        
        # Strategy 1: Sort stops by position and take actual first/last
        sorted_stops = sorted(current_stops, key=lambda x: x[0])
        
        # Get the absolute first and last by position
        first_by_position = sorted_stops[0]
        last_by_position = sorted_stops[-1]
        
        # Strategy 2: Check for stops at positions 0.0 and 1.0 specifically
        stops_at_zero = [(pos, color) for pos, color in current_stops if abs(pos - 0.0) < 1e-6]
        stops_at_one = [(pos, color) for pos, color in current_stops if abs(pos - 1.0) < 1e-6]
        
        # Strategy 3: For JWildfire compatibility, prefer 0.0 and 1.0 if they exist
        first_stop = None
        last_stop = None
        
        # Prefer stop at 0.0 for first, otherwise use minimum position
        if stops_at_zero:
            first_stop = stops_at_zero[0]  # Take first occurrence at 0.0
        else:
            first_stop = first_by_position
        
        # Prefer stop at 1.0 for last, otherwise use maximum position  
        if stops_at_one:
            last_stop = stops_at_one[0]  # Take first occurrence at 1.0
        else:
            last_stop = last_by_position
        
        # Debug information for apply operations
        print(f"APPLY DEBUG: Identified stops for seamless application:")
        print(f"  First stop: pos={first_stop[0]:.6f}, color=RGB{first_stop[1]}")
        print(f"  Last stop:  pos={last_stop[0]:.6f}, color=RGB{last_stop[1]}")
        print(f"  Stops at 0.0: {len(stops_at_zero)}")
        print(f"  Stops at 1.0: {len(stops_at_one)}")
        print(f"  Total stops: {len(current_stops)}")
        print(f"  All positions: {[f'{pos:.3f}' for pos, _ in sorted_stops]}")
        
        return first_stop, last_stop
    
    def _find_all_stop_indices_at_position(self, target_pos):
        """
        Find ALL stop indices that have the given position.
        This is crucial for handling multiple stops at the same position.
        
        Args:
            target_pos: Position to search for
            
        Returns:
            list: List of indices with matching positions
        """
        current_stops = self.gradient_model.get_color_stops()
        indices = []
        
        for i, (pos, _) in enumerate(current_stops):
            if abs(pos - target_pos) < 1e-6:  # Use epsilon for float comparison
                indices.append(i)
        
        return indices
    
    def _apply_basic_seamless_fixed(self, first_stop, last_stop):
        """FIXED: Apply basic seamless by making last color match first color."""
        first_pos, first_color = first_stop
        last_pos, last_color = last_stop
        
        print(f"BASIC SEAMLESS: Changing last stop from RGB{last_color} to RGB{first_color}")
        
        # Find all indices at the last position and update them
        last_indices = self._find_all_stop_indices_at_position(last_pos)
        
        for index in last_indices:
            self.gradient_model.set_color_at_index(index, first_color)
            print(f"  Updated stop {index} at position {last_pos:.3f} to RGB{first_color}")
    
    def _apply_progressive_seamless_fixed(self, first_stop, last_stop):
        """FIXED: Apply progressive seamless blending to existing stops."""
        first_pos, first_color = first_stop
        last_pos, last_color = last_stop
        
        print(f"PROGRESSIVE SEAMLESS: Blending in {self.blend_region_spin.value():.3f} regions")
        
        # First, apply basic seamless
        self._apply_basic_seamless_fixed(first_stop, last_stop)
        
        # Then apply progressive blending to existing stops in blend regions
        current_stops = self.gradient_model.get_color_stops()
        blend_region = self.blend_region_spin.value()
        intensity = self.intensity_spin.value()
        
        modified_count = 0
        
        for i, (pos, color) in enumerate(current_stops):
            # Skip the exact first and last stops to avoid double-processing
            if abs(pos - first_pos) < 1e-6 or abs(pos - last_pos) < 1e-6:
                continue
            
            # Check if stop is in end blend region (blend towards first color)
            if pos > (1.0 - blend_region):
                blend_factor = (pos - (1.0 - blend_region)) / blend_region
                blend_strength = blend_factor * intensity
                blended_color = self._blend_colors(color, first_color, blend_strength)
                
                if blended_color != color:  # Only update if color actually changes
                    self.gradient_model.set_color_at_index(i, blended_color)
                    print(f"  End region: Stop {i} at {pos:.3f} blended from RGB{color} to RGB{blended_color}")
                    modified_count += 1
            
            # Check if stop is in start blend region (subtle blend towards last color)
            elif pos < blend_region:
                blend_factor = (blend_region - pos) / blend_region
                blend_strength = blend_factor * intensity * 0.3  # Weaker blending at start
                blended_color = self._blend_colors(color, last_color, blend_strength)
                
                if blended_color != color:  # Only update if color actually changes
                    self.gradient_model.set_color_at_index(i, blended_color)
                    print(f"  Start region: Stop {i} at {pos:.3f} blended from RGB{color} to RGB{blended_color}")
                    modified_count += 1
        
        print(f"Progressive blending modified {modified_count} existing stops")
    
    def _blend_colors(self, color1, color2, factor):
        """Blend two RGB colors with given factor (0.0 to 1.0)."""
        factor = max(0.0, min(1.0, factor))
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        
        r = max(0, min(255, int(r1 * (1 - factor) + r2 * factor)))
        g = max(0, min(255, int(g1 * (1 - factor) + g2 * factor)))
        b = max(0, min(255, int(b1 * (1 - factor) + b2 * factor)))
        
        return (r, g, b)

    def on_seamless_changed(self, state):
        """Handle seamless checkbox change."""
        self.gradient_model.set_seamless_blend(state == Qt.Checked)
        self._update_ui_state()
        self._update_seamless_config()
        self.settings_changed.emit()
    
    def on_progressive_changed(self, state):
        """Handle progressive checkbox change."""
        self._update_ui_state()
        self._update_seamless_config()
        self.settings_changed.emit()
    
    def on_preview_overlay_changed(self, state):
        """Handle overlay checkbox change."""
        if hasattr(self.gradient_model, '_seamless'):
            self.gradient_model._seamless.set_preview_overlay(state == Qt.Checked)
        self.settings_changed.emit()
    
    def on_blend_region_changed(self, value):
        """Handle blend region change."""
        self.blend_region_slider.blockSignals(True)
        self.blend_region_slider.setValue(int(value * 100))
        self.blend_region_slider.blockSignals(False)
        self._update_ui_state()
        self._update_seamless_config()
        self.settings_changed.emit()
    
    def on_blend_region_slider_changed(self, value):
        """Handle blend region slider change."""
        float_value = value / 100.0
        self.blend_region_spin.blockSignals(True)
        self.blend_region_spin.setValue(float_value)
        self.blend_region_spin.blockSignals(False)
        self._update_ui_state()
        self._update_seamless_config()
        self.settings_changed.emit()
    
    def on_intensity_changed(self, value):
        """Handle intensity change."""
        self.intensity_slider.blockSignals(True)
        self.intensity_slider.setValue(int(value * 100))
        self.intensity_slider.blockSignals(False)
        self._update_seamless_config()
        self.settings_changed.emit()
    
    def on_intensity_slider_changed(self, value):
        """Handle intensity slider change."""
        float_value = value / 100.0
        self.intensity_spin.blockSignals(True)
        self.intensity_spin.setValue(float_value)
        self.intensity_spin.blockSignals(False)
        self._update_seamless_config()
        self.settings_changed.emit()
    
    def on_apply_seamless(self):
        """FIXED: Apply seamless effects with proper first/last stop identification."""
        if not self.gradient_model.get_seamless_blend():
            QMessageBox.warning(self, "Not Enabled", "Enable seamless blending first.")
            return
        
        current_stops = self.gradient_model.get_color_stops()
        if len(current_stops) < 2:
            QMessageBox.information(self, "Need More Stops", "Need at least 2 color stops.")
            return
        
        try:
            # Save state for undo
            if self.animated_preview and hasattr(self.animated_preview, 'save_state_to_history'):
                self.animated_preview.save_state_to_history("Before seamless apply", force=True)
            
            # FIXED: Identify first and last stops properly by position
            sorted_stops = sorted(current_stops, key=lambda x: x[0])
            first_stop = sorted_stops[0]   # True first by position
            last_stop = sorted_stops[-1]   # True last by position
            
            first_pos, first_color = first_stop
            last_pos, last_color = last_stop
            
            print(f"APPLY: First stop at {first_pos:.3f} RGB{first_color}")
            print(f"APPLY: Last stop at {last_pos:.3f} RGB{last_color}")
            
            if self.progressive_check.isChecked():
                self._apply_progressive_seamless_fixed(first_stop, last_stop)
            else:
                self._apply_basic_seamless_fixed(first_stop, last_stop)
            
            # Update preview
            if self.animated_preview:
                self.animated_preview.update_gradient(animate=False, save_to_history=False)
                if hasattr(self.animated_preview, 'drawing_area'):
                    self.animated_preview.drawing_area.set_stops(self.gradient_model.get_color_stops())
                    self.animated_preview.drawing_area.update()
            
            # Update diagnostic info
            self._update_diagnostic_info()
            
            self.seamless_applied.emit()
            self.gradient_modified.emit()
            self.settings_changed.emit()
            
            mode = "Progressive" if self.progressive_check.isChecked() else "Basic"
            QMessageBox.information(self, "Applied", 
                f"{mode} seamless blending applied successfully!\n\n"
                f"First stop: pos {first_pos:.3f}, RGB{first_color}\n"
                f"Last stop: pos {last_pos:.3f}, changed to RGB{first_color}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply: {str(e)}")
            print(f"Apply error: {e}")
            import traceback
            traceback.print_exc()
