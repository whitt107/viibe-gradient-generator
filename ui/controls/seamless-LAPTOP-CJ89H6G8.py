#!/usr/bin/env python3
"""
Refactored Seamless Blending Module - Fixed Progressive Blending

Key changes:
- Progressive blending now only modifies existing color stops within blend regions
- No new color stops are added during progressive blending
- Significantly reduced code size while preserving all functionality
- Cleaner separation between basic and progressive seamless operations
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
        """Apply seamless effects - FIXED to not add color stops."""
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
            
            if self.progressive_check.isChecked():
                self._apply_progressive_seamless()
            else:
                self._apply_basic_seamless()
            
            # Update preview
            if self.animated_preview:
                self.animated_preview.update_gradient(animate=False, save_to_history=False)
                if hasattr(self.animated_preview, 'drawing_area'):
                    self.animated_preview.drawing_area.set_stops(self.gradient_model.get_color_stops())
                    self.animated_preview.drawing_area.update()
            
            self.seamless_applied.emit()
            self.gradient_modified.emit()
            self.settings_changed.emit()
            
            mode = "Progressive" if self.progressive_check.isChecked() else "Basic"
            QMessageBox.information(self, "Applied", f"{mode} seamless blending applied!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply: {str(e)}")
    
    def _apply_progressive_seamless(self):
        """Apply progressive seamless - ONLY modify existing stops, then ensure last = first."""
        current_stops = self.gradient_model.get_color_stops()
        blend_region = self.blend_region_spin.value()
        intensity = self.intensity_spin.value()
        
        first_color = current_stops[0][1]
        last_color = current_stops[-1][1]
        
        # Modify existing stops within blend regions (except first and last)
        for i in range(1, len(current_stops) - 1):  # Skip first (0) and last (-1)
            position, color = current_stops[i]
            new_color = color
            
            if position <= blend_region:
                # Start region - blend with last color
                blend_factor = (blend_region - position) / blend_region * intensity * 0.3
                new_color = self._blend_colors(color, last_color, blend_factor)
                
            elif position >= (1.0 - blend_region):
                # End region - blend with first color
                blend_factor = (position - (1.0 - blend_region)) / blend_region * intensity
                new_color = self._blend_colors(color, first_color, blend_factor)
            
            # Update the stop's color if it changed
            if new_color != color:
                self.gradient_model.set_color_at_index(i, new_color)
        
        # CRITICAL: Always ensure last stop equals first stop (both modes)
        self.gradient_model.set_color_at_index(-1, first_color)
    
    def _apply_basic_seamless(self):
        """Apply basic seamless - just change last color to first color."""
        current_stops = self.gradient_model.get_color_stops()
        first_color = current_stops[0][1]
        
        # Simply change the last stop's color to match the first
        last_index = len(current_stops) - 1
        self.gradient_model.set_color_at_index(last_index, first_color)
    
    def _blend_colors(self, color1, color2, factor):
        """Blend two RGB colors."""
        factor = max(0.0, min(1.0, factor))
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        
        r = int(r1 * (1 - factor) + r2 * factor)
        g = int(g1 * (1 - factor) + g2 * factor)
        b = int(b1 * (1 - factor) + b2 * factor)
        
        return (r, g, b)
    
    def _update_seamless_config(self):
        """Update seamless configuration in gradient model."""
        if hasattr(self.gradient_model, '_seamless'):
            seamless = self.gradient_model._seamless
            if hasattr(seamless, 'set_progressive_blending'):
                seamless.set_progressive_blending(self.progressive_check.isChecked())
            if hasattr(seamless, 'set_intensity_falloff'):
                seamless.set_intensity_falloff(self.intensity_spin.value())
            if hasattr(seamless, 'blend_region'):
                seamless.blend_region = self.blend_region_spin.value()
