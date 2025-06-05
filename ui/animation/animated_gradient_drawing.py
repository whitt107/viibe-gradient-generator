#!/usr/bin/env python3
"""
Enhanced Animated Gradient Drawing Module with Fade Effect Support

Updated to support fade in/out effects when gradients with different numbers
of color stops are applied. Integrates with the fade transition system.
"""
import time
from PyQt5.QtWidgets import QWidget, QMenu, QColorDialog, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QTimer, QPointF
from PyQt5.QtGui import QPainter, QCursor, QKeySequence, QColor

from .animation_renderer import GradientRenderer, create_gradient_renderer


class AnimatedGradientDrawingArea(QWidget):
    """Interactive gradient drawing area with fade effect support."""
    
    # Core signals
    stop_selected = pyqtSignal(int)
    stop_moved = pyqtSignal(int, float)
    stop_hover = pyqtSignal(int)
    stop_color_edit_requested = pyqtSignal(int)
    stop_added = pyqtSignal(float, tuple)
    stop_deleted = pyqtSignal(int)
    state_changed = pyqtSignal()
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()
    
    def __init__(self, gradient_model):
        super().__init__()
        self.gradient_model = gradient_model
        
        # Centralized renderer - handles all animation and rendering
        self.renderer = None  # Will be set by parent or explicitly
        
        # Fade effect support
        self.fade_opacity = 1.0
        self.parent_preview = None  # Reference to parent preview for fade info
        
        # Color stops cache
        self.color_stops = []
        
        # Interaction state
        self.selected_stop_index = -1
        self.hover_stop_index = -1
        self.dragging = False
        self.drag_stop_index = -1
        self.drag_start_pos = 0.0
        self.mouse_press_pos = None
        self.mouse_press_time = 0
        self.last_click_index = -1
        
        # Configuration
        self.stop_radius = 10
        self.drag_threshold = 5
        self.double_click_threshold = 300
        
        # History management
        self.history_manager = None
        self.auto_save_enabled = True
        self.last_saved_state = None
        self.operation_in_progress = False
        
        self.state_save_timer = QTimer()
        self.state_save_timer.setSingleShot(True)
        self.state_save_timer.timeout.connect(self._save_delayed_state)
        
        self._setup_ui()
        self._store_state()
    
    def set_renderer(self, renderer: GradientRenderer):
        """Set the centralized renderer."""
        self.renderer = renderer
    
    def set_parent_preview(self, parent_preview):
        """Set reference to parent preview for fade coordination."""
        self.parent_preview = parent_preview
    
    def get_fade_opacity(self) -> float:
        """Get current fade opacity from parent preview."""
        if self.parent_preview and hasattr(self.parent_preview, 'get_fade_opacity'):
            return self.parent_preview.get_fade_opacity()
        return 1.0
    
    def _setup_ui(self):
        """Initialize UI settings."""
        self.setMinimumSize(200, 100)
        self.setMouseTracking(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.setFocusPolicy(Qt.StrongFocus)
    
    # === HISTORY MANAGEMENT ===
    
    def set_history_manager(self, manager):
        """Set history manager for undo/redo."""
        self.history_manager = manager
    
    def _store_state(self):
        """Store current state for change detection."""
        if self.gradient_model:
            self.last_saved_state = self.gradient_model.get_color_stops().copy()
    
    def _has_changes(self) -> bool:
        """Check for significant changes."""
        if not self.last_saved_state:
            return True
        current = self.gradient_model.get_color_stops()
        return (len(current) != len(self.last_saved_state) or 
                any(abs(p1-p2) > 0.001 or c1 != c2 
                    for (p1,c1), (p2,c2) in zip(current, self.last_saved_state)))
    
    def _schedule_save(self, desc: str = "Auto-save", delay: int = 150):
        """Schedule delayed save to batch changes."""
        if self.auto_save_enabled and self.history_manager:
            self._pending_desc = desc
            self.state_save_timer.stop()
            self.state_save_timer.start(delay)
    
    def _save_delayed_state(self):
        """Perform delayed save with change detection."""
        if (self.auto_save_enabled and self.history_manager and 
            not self.operation_in_progress and self._has_changes()):
            try:
                desc = getattr(self, '_pending_desc', "Auto-save")
                self.history_manager.save_state(self.gradient_model, force=False, description=desc)
                self._store_state()
                self.state_changed.emit()
            except Exception as e:
                print(f"Save error: {e}")
    
    def save_immediate(self, desc: str, force: bool = True):
        """Save state immediately."""
        if self.history_manager:
            try:
                self.operation_in_progress = True
                self.history_manager.save_state(self.gradient_model, force=force, description=desc)
                self._store_state()
                self.state_changed.emit()
            finally:
                self.operation_in_progress = False
    
    # === EVENT HANDLING ===
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
            self.undo_requested.emit()
            event.accept()
        elif (event.key() == Qt.Key_Y and event.modifiers() == Qt.ControlModifier or
              event.key() == Qt.Key_Z and event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier)):
            self.redo_requested.emit()
            event.accept()
        elif event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            if self.selected_stop_index >= 0:
                self._delete_stop(self.selected_stop_index)
            event.accept()
        elif event.key() == Qt.Key_Escape:
            self.selected_stop_index = -1
            self.update()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press with interaction detection."""
        current_time = time.time() * 1000
        
        if event.button() == Qt.LeftButton:
            hit_index = self._hit_test_stops(event.pos())
            
            if hit_index >= 0:
                # Double-click detection for color editing
                if (hit_index == self.last_click_index and 
                    current_time - self.mouse_press_time < self.double_click_threshold):
                    self._edit_color(hit_index)
                    return
                
                # Setup for potential drag
                self.mouse_press_pos = event.pos()
                self.mouse_press_time = current_time
                self.last_click_index = hit_index
                self.selected_stop_index = hit_index
                self.stop_selected.emit(hit_index)
                self.update()
            else:
                # Add new stop
                self._handle_add_stop(event)
                self.last_click_index = -1
        
        elif event.button() == Qt.RightButton:
            hit_index = self._hit_test_stops(event.pos())
            self.selected_stop_index = hit_index if hit_index >= 0 else -1
            self.update()
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement for dragging and hover."""
        if event.buttons() & Qt.LeftButton:
            if (self.mouse_press_pos and self.selected_stop_index >= 0 and not self.dragging):
                delta = event.pos() - self.mouse_press_pos
                if delta.manhattanLength() >= self.drag_threshold:
                    self._start_drag()
            
            if self.dragging:
                self._handle_drag(event)
        else:
            self._handle_hover(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton and self.dragging:
            self._end_drag()
        self.mouse_press_pos = None
    
    def leaveEvent(self, event):
        """Handle mouse leave."""
        if self.hover_stop_index >= 0:
            self.hover_stop_index = -1
            self.stop_hover.emit(-1)
            self.setCursor(Qt.ArrowCursor)
            self.update()
        super().leaveEvent(event)
    
    # === INTERACTION METHODS ===
    
    def _hit_test_stops(self, pos) -> int:
        """Test for stop collision."""
        if not self.color_stops:
            return -1
        
        h = self.height()
        track_y = int(h * 0.6) + int(h * 0.4) // 2 - 8
        
        for i, (position, _) in enumerate(self.color_stops):
            x = position * self.width()
            dx, dy = x - pos.x(), track_y - pos.y()
            if (dx * dx + dy * dy) ** 0.5 <= self.stop_radius:
                return i
        return -1
    
    def _start_drag(self):
        """Start drag operation."""
        if not self.operation_in_progress:
            self.save_immediate("Before drag")
        
        self.dragging = True
        self.operation_in_progress = True
        self.drag_stop_index = self.selected_stop_index
        self.drag_start_pos = self.color_stops[self.selected_stop_index][0]
        self.setCursor(Qt.ClosedHandCursor)
    
    def _handle_drag(self, event):
        """Handle drag movement."""
        if not self.dragging or self.drag_stop_index < 0:
            return
        
        delta_x = event.x() - self.mouse_press_pos.x()
        new_pos = max(0.0, min(1.0, self.drag_start_pos + delta_x / self.width()))
        
        if self.drag_stop_index < len(self.color_stops):
            _, color = self.color_stops[self.drag_stop_index]
            self.color_stops[self.drag_stop_index] = (new_pos, color)
        
        self.gradient_model.set_position_at_index(self.drag_stop_index, new_pos)
        self.stop_moved.emit(self.drag_stop_index, new_pos)
        self.update()
    
    def _end_drag(self):
        """End drag operation."""
        self.dragging = False
        if self._has_changes():
            self.save_immediate("After drag")
        self.operation_in_progress = False
        self.setCursor(Qt.ArrowCursor)
        self.update()
    
    def _handle_hover(self, event):
        """Handle hover and cursor changes."""
        hit_index = self._hit_test_stops(event.pos())
        
        if hit_index != self.hover_stop_index:
            self.hover_stop_index = hit_index
            self.stop_hover.emit(hit_index)
            
            if hit_index >= 0:
                cursor = Qt.PointingHandCursor
            else:
                gradient_rect = QRect(0, 0, self.width(), int(self.height() * 0.6))
                cursor = Qt.PointingHandCursor if gradient_rect.contains(event.pos()) else Qt.ArrowCursor
            
            self.setCursor(cursor)
            self.update()
    
    def _handle_add_stop(self, event):
        """Handle adding new stop with color interpolation."""
        gradient_rect = QRect(0, 0, self.width(), int(self.height() * 0.6))
        
        if gradient_rect.contains(event.pos()):
            self.save_immediate("Before add stop")
            position = max(0.0, min(1.0, event.x() / self.width()))
            
            # Get interpolated color using renderer
            interpolated_color = self._interpolate_color(position)
            
            # Show color dialog
            color_dialog = QColorDialog(QColor(*interpolated_color), self)
            color_dialog.setWindowTitle(f"Choose Color for New Stop at {position:.3f}")
            
            if color_dialog.exec_() == QColorDialog.Accepted:
                selected = color_dialog.selectedColor()
                new_color = (selected.red(), selected.green(), selected.blue())
                
                if self.gradient_model.add_color_stop(position, new_color):
                    self.color_stops = self.gradient_model.get_color_stops()
                    self.stop_added.emit(position, new_color)
                    self._schedule_save("After add stop", 100)
                    self.update()
    
    def _interpolate_color(self, position: float) -> tuple:
        """Interpolate color at position using centralized renderer."""
        if self.renderer:
            return self.renderer.interpolator.interpolate_color_at_position(position, self.color_stops)
        
        # Fallback interpolation if no renderer
        position = max(0.0, min(1.0, position))
        
        if not self.color_stops:
            return (128, 128, 128)
        
        if len(self.color_stops) == 1:
            return self.color_stops[0][1]
        
        # Sort stops for proper interpolation
        sorted_stops = sorted(self.color_stops, key=lambda x: x[0])
        
        # Find bracketing stops
        before_stop = None
        after_stop = None
        
        for stop_pos, stop_color in sorted_stops:
            if stop_pos <= position:
                before_stop = (stop_pos, stop_color)
            if stop_pos >= position and after_stop is None:
                after_stop = (stop_pos, stop_color)
                break
        
        # Handle edge cases
        if before_stop is None:
            return sorted_stops[0][1]
        if after_stop is None:
            return sorted_stops[-1][1]
        if before_stop[0] == after_stop[0]:
            return before_stop[1]
        
        # Interpolate colors
        pos1, color1 = before_stop
        pos2, color2 = after_stop
        
        blend_factor = (position - pos1) / (pos2 - pos1)
        blend_factor = max(0.0, min(1.0, blend_factor))
        
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        
        r = int(r1 * (1 - blend_factor) + r2 * blend_factor)
        g = int(g1 * (1 - blend_factor) + g2 * blend_factor)
        b = int(b1 * (1 - blend_factor) + b2 * blend_factor)
        
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
    
    # === CONTEXT MENU ===
    
    def _show_context_menu(self, position):
        """Show context menu with operations."""
        menu = QMenu(self)
        hit_index = self._hit_test_stops(position)
        
        # Undo/Redo
        if self.history_manager:
            undo = menu.addAction("Undo")
            undo.setShortcut(QKeySequence.Undo)
            undo.setEnabled(self.history_manager.can_undo())
            undo.triggered.connect(lambda: self.undo_requested.emit())
            
            redo = menu.addAction("Redo")
            redo.setShortcut(QKeySequence.Redo)
            redo.setEnabled(self.history_manager.can_redo())
            redo.triggered.connect(lambda: self.redo_requested.emit())
            
            menu.addSeparator()
        
        if hit_index >= 0:
            # Stop operations
            edit = menu.addAction("Edit Color...")
            edit.triggered.connect(lambda: self._edit_color_with_undo(hit_index))
            
            if len(self.color_stops) > 1:
                delete = menu.addAction("Delete Stop")
                delete.triggered.connect(lambda: self._delete_stop_with_undo(hit_index))
        else:
            # Add stop
            gradient_rect = QRect(0, 0, self.width(), int(self.height() * 0.6))
            if gradient_rect.contains(position):
                add = menu.addAction("Add Color Stop Here")
                add.triggered.connect(lambda: self._add_stop_at_pos(position, gradient_rect))
        
        menu.exec_(self.mapToGlobal(position))
    
    def _edit_color_with_undo(self, index):
        """Edit color with undo state."""
        self.save_immediate("Before color edit")
        self._edit_color(index)
    
    def _delete_stop_with_undo(self, index):
        """Delete stop with undo state."""
        self.save_immediate("Before delete stop")
        self._delete_stop(index)
    
    def _add_stop_at_pos(self, position, gradient_rect):
        """Add stop at specific position."""
        self.save_immediate("Before add stop")
        self._handle_add_stop_at_position(position, gradient_rect)
    
    # === CORE OPERATIONS ===
    
    def _edit_color(self, index):
        """Edit stop color."""
        if not (0 <= index < len(self.color_stops)):
            return
        
        pos, current_color = self.color_stops[index]
        
        dialog = QColorDialog(QColor(*current_color), self)
        dialog.setWindowTitle(f"Edit Color for Stop at {pos:.3f}")
        
        if dialog.exec_() == QColorDialog.Accepted:
            new_color = dialog.selectedColor()
            color_tuple = (new_color.red(), new_color.green(), new_color.blue())
            
            self.gradient_model.set_color_at_index(index, color_tuple)
            self.color_stops[index] = (pos, color_tuple)
            self.stop_color_edit_requested.emit(index)
            self._schedule_save("After color edit", 100)
            self.update()
    
    def _delete_stop(self, index):
        """Delete color stop with confirmation."""
        if len(self.color_stops) <= 1:
            QMessageBox.information(self, "Cannot Delete", 
                "Cannot delete the last color stop.")
            return
        
        if 0 <= index < len(self.color_stops):
            pos = self.color_stops[index][0]
            reply = QMessageBox.question(self, "Delete Color Stop",
                f"Delete color stop at position {pos:.3f}?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.gradient_model.remove_color_stop_at_index(index)
                self.color_stops = self.gradient_model.get_color_stops()
                
                if self.selected_stop_index == index:
                    self.selected_stop_index = -1
                elif self.selected_stop_index > index:
                    self.selected_stop_index -= 1
                
                self.stop_deleted.emit(index)
                self._schedule_save("After delete", 100)
                self.update()
    
    def _handle_add_stop_at_position(self, mouse_pos, gradient_rect):
        """Add stop at mouse position."""
        position = max(0.0, min(1.0, (mouse_pos.x() - gradient_rect.left()) / gradient_rect.width()))
        
        interpolated = self._interpolate_color(position)
        dialog = QColorDialog(QColor(*interpolated), self)
        dialog.setWindowTitle(f"Choose Color for New Stop at {position:.3f}")
        
        if dialog.exec_() == QColorDialog.Accepted:
            selected = dialog.selectedColor()
            new_color = (selected.red(), selected.green(), selected.blue())
            
            if self.gradient_model.add_color_stop(position, new_color):
                self.color_stops = self.gradient_model.get_color_stops()
                self.stop_added.emit(position, new_color)
                self._schedule_save("After add stop", 100)
                self.update()
    
    # === PAINTING WITH FADE SUPPORT ===
    
    def paintEvent(self, event):
        """Paint gradient with fade effect support using centralized renderer."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get current fade opacity
        fade_opacity = self.get_fade_opacity()
        
        # Apply fade effect to the entire drawing
        if fade_opacity < 1.0:
            painter.setOpacity(fade_opacity)
        
        # Background
        bg_color = QColor(42, 42, 42)
        if fade_opacity < 1.0:
            # Slightly lighten background during fade for better visibility
            bg_color = QColor(60, 60, 60)
        
        painter.fillRect(self.rect(), bg_color)
        
        w, h = self.width(), self.height()
        gradient_height = int(h * 0.6)
        gradient_rect = QRect(0, 0, w, gradient_height)
        
        # Use centralized renderer if available
        if self.renderer:
            # Draw gradient using renderer
            self.renderer.render_gradient(
                painter, gradient_rect, self.color_stops, 
                self.gradient_model, use_seamless_preview=True
            )
            
            # Draw seamless overlay if enabled (with fade consideration)
            if (self.gradient_model.get_seamless_blend() and 
                self.gradient_model.get_preview_overlay()):
                # Adjust seamless overlay opacity during fade
                if fade_opacity < 1.0:
                    painter.setOpacity(fade_opacity * 0.7)
                
                self.renderer.draw_seamless_overlay(painter, gradient_rect, self.gradient_model)
                
                if fade_opacity < 1.0:
                    painter.setOpacity(fade_opacity)
            
            # Draw interactive elements
            stop_y = gradient_height + int(h * 0.4) // 2
            self.renderer.draw_color_stops(
                painter, self.color_stops, 0, w, stop_y,
                self.selected_stop_index, self.hover_stop_index, self.stop_radius
            )
            
            # Add hints with fade consideration
            if not self.dragging and fade_opacity > 0.3:  # Only show hints when not too faded
                mouse_pos = self.mapFromGlobal(QCursor.pos())
                self.renderer.draw_add_hints(painter, gradient_rect, QPointF(mouse_pos))
            
            # Add fade indicator if fading
            if fade_opacity < 1.0:
                self._draw_fade_indicator(painter, gradient_rect, fade_opacity)
                
        else:
            # Fallback rendering if no renderer available
            self._fallback_paint(painter, gradient_rect, gradient_height, fade_opacity)
        
        # Reset opacity for any additional drawing
        painter.setOpacity(1.0)
    
    def _draw_fade_indicator(self, painter, gradient_rect, fade_opacity):
        """Draw fade transition indicator."""
        if fade_opacity >= 1.0:
            return
        
        # Draw subtle fade indicator
        indicator_alpha = int((1.0 - fade_opacity) * 100)
        fade_color = QColor(255, 255, 255, indicator_alpha)
        
        painter.setPen(fade_color)
        painter.drawText(
            gradient_rect.right() - 80, gradient_rect.top() + 15,
            f"Fading... {fade_opacity:.1%}"
        )
        
        # Draw fade progress bar
        progress_rect = QRect(gradient_rect.right() - 60, gradient_rect.top() + 25, 50, 4)
        painter.fillRect(progress_rect, QColor(100, 100, 100, 50))
        
        progress_width = int(progress_rect.width() * fade_opacity)
        progress_fill = QRect(progress_rect.left(), progress_rect.top(), progress_width, progress_rect.height())
        painter.fillRect(progress_fill, QColor(255, 255, 255, indicator_alpha))
    
    def _fallback_paint(self, painter, gradient_rect, gradient_height, fade_opacity):
        """Fallback painting when no renderer is available."""
        if not self.color_stops:
            bg_color = QColor(60, 60, 60) if fade_opacity < 1.0 else QColor(60, 60, 60)
            painter.fillRect(gradient_rect, bg_color)
            
            text_color = QColor(100, 100, 100)
            painter.setPen(text_color)
            painter.drawText(gradient_rect, Qt.AlignCenter, "No Gradient Data")
            return
        
        # Simple linear gradient fallback
        from PyQt5.QtGui import QLinearGradient
        
        gradient = QLinearGradient(0, 0, gradient_rect.width(), 0)
        sorted_stops = sorted(self.color_stops, key=lambda x: x[0])
        
        for position, color in sorted_stops:
            gradient.setColorAt(position, QColor(*color))
        
        painter.fillRect(gradient_rect, gradient)
        painter.setPen(QColor(85, 85, 85))
        painter.drawRect(gradient_rect)
        
        # Draw basic color stops
        stop_y = gradient_height + 20
        for i, (position, color) in enumerate(self.color_stops):
            x = position * gradient_rect.width()
            selected = (i == self.selected_stop_index)
            
            painter.setPen(Qt.white if selected else QColor(200, 200, 200))
            painter.setBrush(QColor(*color))
            painter.drawEllipse(int(x - 8), stop_y - 8, 16, 16)
    
    # === PUBLIC INTERFACE ===
    
    def set_animation_step(self, step):
        """Set animation step via renderer."""
        if self.renderer:
            self.renderer.set_animation_step(step)
    
    def set_animation_direction(self, direction):
        """Set animation direction via renderer."""
        if self.renderer:
            self.renderer.set_animation_direction(direction)
    
    def set_animation_enabled(self, enabled):
        """Enable/disable animation via renderer."""
        if self.renderer:
            self.renderer.set_animation_enabled(enabled)
        self.update()
    
    def set_stops(self, stops, force_update=False):
        """Set color stops with proper synchronization."""
        try:
            if force_update or not self.dragging:
                self.color_stops = []
                for pos, color in stops:
                    self.color_stops.append((pos, color))
                self.update()
            elif self.dragging and stops:
                self._update_non_dragged_stops(stops)
        except Exception as e:
            print(f"Error setting stops: {e}")
    
    def set_animation_type(self, animation_type):
        """Set animation type via renderer."""
        if self.renderer and animation_type in ["linear", "radial", "conical"]:
            self.renderer.set_animation_type(animation_type)
            self.update()
    
    def set_auto_save_enabled(self, enabled):
        """Enable/disable auto-save."""
        self.auto_save_enabled = enabled
        if not enabled:
            self.state_save_timer.stop()
    
    def update_last_saved_state(self):
        """Update last saved state for undo/redo sync."""
        self._store_state()
    
    def _update_non_dragged_stops(self, new_stops):
        """Update stops that aren't being dragged."""
        if not self.dragging or self.drag_stop_index < 0:
            return
        
        try:
            updated_stops = []
            for i, (pos, color) in enumerate(new_stops):
                if i == self.drag_stop_index:
                    # Keep the current dragged stop's position
                    if i < len(self.color_stops):
                        updated_stops.append(self.color_stops[i])
                    else:
                        updated_stops.append((pos, color))
                else:
                    updated_stops.append((pos, color))
            
            self.color_stops = updated_stops
            self.update()
        except Exception as e:
            print(f"Error updating non-dragged stops: {e}")

    def force_refresh(self):
        """Force complete refresh of the drawing area."""
        try:
            if self.gradient_model:
                self.color_stops = self.gradient_model.get_color_stops().copy()
            self.update()
        except Exception as e:
            print(f"Error in force refresh: {e}")
    
    def set_fade_opacity(self, opacity):
        """Set fade opacity directly (for testing)."""
        self.fade_opacity = max(0.0, min(1.0, opacity))
        self.update()

    def cleanup(self):
        """Clean up resources."""
        self.state_save_timer.stop()
        self.dragging = False
        self.operation_in_progress = False