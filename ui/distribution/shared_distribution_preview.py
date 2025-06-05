#!/usr/bin/env python3
"""
UPDATED Shared Distribution Preview Widget - Real-time Updates with Clean Interface

Removed range/spacing/variance statistics display and added real-time preview updates
for a cleaner, more responsive user experience.
"""
import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QGroupBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QPainter, QLinearGradient, QFont


class SharedGradientPreviewWidget(QWidget):
    """Enhanced gradient preview widget with real-time updates and clean interface."""
    
    apply_changes = pyqtSignal()
    reset_changes = pyqtSignal()
    randomize_positions = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_stops = []
        self.preview_stops = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the preview UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Preview group
        preview_group = QGroupBox("Live Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        # Description
        self.description_label = QLabel("Adjust settings to see live preview")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #888; font-style: italic; padding: 5px;")
        preview_layout.addWidget(self.description_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        preview_layout.addWidget(separator)
        
        # Preview gradient (removed statistics display)
        self.preview_widget = GradientPreviewLabel()
        preview_layout.addWidget(self.preview_widget)
        
        # Statistics label removed - cleaner interface
        # self.stats_label removed completely
        
        layout.addWidget(preview_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("Apply Changes")
        self.apply_button.clicked.connect(self.apply_changes.emit)
        self.apply_button.setStyleSheet("font-weight: bold; padding: 8px; background-color: #4a7c59;")
        button_layout.addWidget(self.apply_button)
        
        self.randomize_button = QPushButton("Randomize Positions")
        self.randomize_button.clicked.connect(self.randomize_positions.emit)
        self.randomize_button.setStyleSheet("padding: 8px; background-color: #7c5a4a;")
        button_layout.addWidget(self.randomize_button)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_changes.emit)
        button_layout.addWidget(self.reset_button)
        
        layout.addLayout(button_layout)
        
        # Simplified status with just basic info
        self.status_label = QLabel("Make adjustments to see preview")
        self.status_label.setStyleSheet("color: #666; font-style: italic; font-size: 10px; margin-top: 5px;")
        layout.addWidget(self.status_label)
    
    def set_original_stops(self, color_stops):
        """Set the original color stops."""
        self.original_stops = color_stops.copy() if color_stops else []
        # Removed _update_stats() call
    
    def set_preview_stops(self, color_stops):
        """Set the preview color stops with enhanced change detection."""
        self.preview_stops = color_stops.copy() if color_stops else []
        self.preview_widget.set_color_stops(self.preview_stops)
        
        # Update button states
        has_changes = self._has_significant_changes()
        self.apply_button.setEnabled(has_changes and len(self.preview_stops) > 0)
        self.reset_button.setEnabled(has_changes)
        self.randomize_button.setEnabled(len(self.preview_stops) > 0)
        
        # Simplified status without movement calculations
        if not self.preview_stops:
            self.status_label.setText("No preview available")
        elif not has_changes:
            self.status_label.setText("No changes to apply")
        else:
            changes = sum(1 for (o, _), (p, _) in zip(self.original_stops, self.preview_stops) 
                         if abs(o - p) > 0.001) if len(self.original_stops) == len(self.preview_stops) else len(self.preview_stops)
            self.status_label.setText(f"Preview: {len(self.preview_stops)} stops, {changes} changed")
        
        # Removed _update_stats() call
    
    def _has_significant_changes(self):
        """Check if there are significant changes between original and preview."""
        if len(self.original_stops) != len(self.preview_stops):
            return True
        
        for (orig_pos, orig_color), (prev_pos, prev_color) in zip(self.original_stops, self.preview_stops):
            # Check position changes
            if abs(orig_pos - prev_pos) > 0.001:  # 0.1% threshold
                return True
            # Check color changes (for color reordering)
            if orig_color != prev_color:
                return True
        
        return False
    
    def set_description(self, description):
        """Set the description text."""
        self.description_label.setText(description)
    
    # Removed _update_stats method entirely for cleaner interface
    
    def clear_preview(self):
        """Clear the preview."""
        self.preview_stops = []
        self.preview_widget.set_color_stops([])
        self.apply_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.randomize_button.setEnabled(False)
        self.status_label.setText("No preview available")
        # Removed stats_label.setText("")


class GradientPreviewLabel(QLabel):
    """Enhanced gradient preview with better visual indicators and cleaner display."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color_stops = []
        self.show_indicators = True
        self.setMinimumSize(300, 80)
        self.setMaximumHeight(120)
        self.setStyleSheet("border: 1px solid #555; background-color: #2a2a2a;")
        
    def set_color_stops(self, color_stops):
        """Set the color stops to display."""
        self.color_stops = color_stops or []
        self.update()
    
    def paintEvent(self, event):
        """Draw the gradient with enhanced visual indicators."""
        super().paintEvent(event)
        
        if not self.color_stops:
            painter = QPainter(self)
            painter.setPen(QColor(150, 150, 150))
            font = QFont()
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, "No gradient to preview")
            painter.end()
            return
            
        w, h = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create and draw gradient
        qgradient = QLinearGradient(0, 0, w, 0)
        for position, color in self.color_stops:
            qgradient.setColorAt(position, QColor(*color))
        painter.fillRect(0, 0, w, h, qgradient)
        
        # Draw border
        painter.setPen(QColor(85, 85, 85))
        painter.drawRect(0, 0, w-1, h-1)
        
        # Enhanced indicators - show fewer but more detailed
        if self.show_indicators and len(self.color_stops) <= 15:  # Reduced from 25
            for i, (position, color) in enumerate(self.color_stops):
                x = int(position * w)
                
                # Indicator line with gradient
                painter.setPen(QColor(255, 255, 255, 180))
                painter.drawLine(x, 0, x, h)
                
                # Color circle with better contrast
                painter.setBrush(QColor(*color))
                painter.setPen(QColor(255, 255, 255, 240))
                painter.drawEllipse(x - 5, h - 15, 10, 10)
                
                # Position text for first 6 stops only (less clutter)
                if i < 6:
                    painter.setPen(QColor(255, 255, 255, 200))
                    font = painter.font()
                    font.setPointSize(8)
                    painter.setFont(font)
                    text = f"{position:.2f}"
                    text_rect = painter.fontMetrics().boundingRect(text)
                    text_x = max(2, min(w - text_rect.width() - 2, x - text_rect.width() // 2))
                    painter.drawText(text_x, h - 2, text)
        elif len(self.color_stops) > 15:
            # For many stops, just show count
            painter.setPen(QColor(255, 255, 255, 180))
            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(5, h - 5, f"{len(self.color_stops)} stops")
        
        painter.end()


class PreviewController:
    """REAL-TIME controller with immediate updates and proper apply_to_model implementation."""
    
    def __init__(self, preview_widget, gradient_model):
        self.preview_widget = preview_widget
        self.gradient_model = gradient_model
        
        # Timer for real-time updates (reduced delay)
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._do_update)
        
        # Current distribution function
        self.current_distributor = None
        self.current_params = {}
        self.current_description = ""
        
        # Debug flag
        self.debug_mode = False  # Disabled by default for cleaner output
        
        # Connect preview widget signals
        self.preview_widget.apply_changes.connect(self.apply_to_model)
        self.preview_widget.reset_changes.connect(self.reset_to_original)
        self.preview_widget.randomize_positions.connect(self.randomize_positions)
        
        self.refresh_original()
    
    def refresh_original(self):
        """Refresh the original color stops from the model."""
        if self.gradient_model and hasattr(self.gradient_model, 'get_color_stops'):
            try:
                original_stops = self.gradient_model.get_color_stops()
                self.preview_widget.set_original_stops(original_stops)
                if not self.current_distributor:
                    self.preview_widget.set_preview_stops(original_stops)
                
                if self.debug_mode:
                    print(f"PreviewController: Refreshed original stops: {len(original_stops)} stops")
            except Exception as e:
                print(f"Error refreshing original stops: {e}")
    
    def set_distributor(self, distributor_func, params=None, description=""):
        """Set the current distribution function with immediate real-time update."""
        self.current_distributor = distributor_func
        self.current_params = params or {}
        self.current_description = description
        self.preview_widget.set_description(description)
        
        if self.debug_mode:
            print(f"PreviewController: Set distributor with params: {self.current_params}")
        
        # REAL-TIME UPDATE: Reduce delay to 10ms for immediate response
        self.schedule_update(delay_ms=10)
    
    def schedule_update(self, delay_ms=10):
        """Schedule a preview update with minimal debouncing for real-time feel."""
        self.update_timer.stop()
        self.update_timer.start(delay_ms)  # Reduced from 50ms to 10ms
        
        if self.debug_mode:
            print(f"PreviewController: Scheduled update in {delay_ms}ms")
    
    def _do_update(self):
        """Perform the actual preview update with enhanced error handling."""
        if not self.current_distributor or not self.gradient_model:
            if self.debug_mode:
                print("PreviewController: No distributor or model available")
            return
        
        try:
            original_stops = self.gradient_model.get_color_stops()
            if not original_stops:
                if self.debug_mode:
                    print("PreviewController: No original stops available")
                return
            
            if self.debug_mode:
                print(f"PreviewController: Applying distributor to {len(original_stops)} stops")
                print(f"Original positions: {[f'{pos:.3f}' for pos, _ in original_stops]}")
            
            new_stops = self.current_distributor(original_stops, **self.current_params)
            
            if self.debug_mode:
                print(f"PreviewController: Result: {len(new_stops)} stops")
                print(f"New positions: {[f'{pos:.3f}' for pos, _ in new_stops]}")
            
            self.preview_widget.set_preview_stops(new_stops)
            
        except Exception as e:
            print(f"Preview update error: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
            try:
                # Fallback: show original stops
                self.preview_widget.set_preview_stops(self.gradient_model.get_color_stops())
            except:
                pass
    
    def apply_to_model(self):
        """CRITICAL FIX: Properly apply the current preview to the gradient model."""
        if not self.preview_widget.preview_stops:
            print("PreviewController: No preview stops to apply")
            return
        
        try:
            preview_stops = self.preview_widget.preview_stops
            if self.debug_mode:
                print(f"PreviewController: Applying {len(preview_stops)} stops to model")
                print(f"Preview stops: {[(f'{pos:.3f}', color) for pos, color in preview_stops[:3]]}...")
            
            # CRITICAL FIX: Properly clear and repopulate the gradient model
            # Step 1: Clear all existing color stops
            self.gradient_model._color_stops = []
            
            # Step 2: Sort stops by position to maintain proper gradient order
            sorted_stops = sorted(preview_stops, key=lambda x: x[0])
            
            # Step 3: Add each stop individually to ensure proper internal state
            for position, color in sorted_stops:
                # Ensure position is clamped to valid range
                clamped_position = max(0.0, min(1.0, position))
                # Ensure color is valid RGB tuple
                valid_color = tuple(max(0, min(255, int(c))) for c in color)
                
                # Add the color stop using the model's method
                success = self.gradient_model.add_color_stop(clamped_position, valid_color)
                if not success:
                    print(f"Warning: Failed to add color stop at {clamped_position}")
            
            if self.debug_mode:
                print(f"PreviewController: Successfully applied {len(sorted_stops)} stops")
                # Verify the application worked
                new_model_stops = self.gradient_model.get_color_stops()
                print(f"Model now has {len(new_model_stops)} stops")
            
            # Step 4: Refresh the preview to show the new baseline
            self.refresh_original()
            
        except Exception as e:
            print(f"CRITICAL ERROR in apply_to_model: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
    
    def reset_to_original(self):
        """Reset the preview to the original gradient."""
        if self.debug_mode:
            print("PreviewController: Resetting to original")
        
        self.refresh_original()
        if self.current_distributor:
            # REAL-TIME: Immediate update on reset
            self.schedule_update(delay_ms=5)
    
    def randomize_positions(self):
        """Randomize color stop positions while keeping colors - NO sorting or minimum distances."""
        if not self.gradient_model or not hasattr(self.gradient_model, 'get_color_stops'):
            return
        
        try:
            original_stops = self.gradient_model.get_color_stops()
            if len(original_stops) < 2:
                return
            
            colors = [color for _, color in original_stops]
            
            if len(colors) == 2:
                randomized_stops = [(0.0, colors[0]), (1.0, colors[1])]
            else:
                # Generate completely random positions - NO sorting or minimum distances
                positions = [0.0]  # First is always 0.0
                
                # Generate truly random positions for middle stops
                for i in range(len(colors) - 2):
                    pos = random.uniform(0.01, 0.99)
                    positions.append(pos)
                
                positions.append(1.0)  # Last is always 1.0
                
                # Create randomized stops with unsorted middle positions
                randomized_stops = list(zip(positions, colors))
            
            if self.debug_mode:
                print(f"PreviewController: Randomized positions: {[f'{pos:.3f}' for pos, _ in randomized_stops]}")
            
            self.preview_widget.set_preview_stops(randomized_stops)
            self.preview_widget.set_description(f"Randomized Positions ({len(randomized_stops)} stops)")
            
        except Exception as e:
            print(f"Error randomizing positions: {e}")


def create_distribution_preview_system(gradient_model):
    """Factory function to create a distribution preview system with real-time updates."""
    preview_widget = SharedGradientPreviewWidget()
    controller = PreviewController(preview_widget, gradient_model)
    return preview_widget, controller