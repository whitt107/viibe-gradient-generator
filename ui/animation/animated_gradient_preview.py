#!/usr/bin/env python3
"""
Enhanced Animated Gradient Preview Module with Fade In/Out Effects

Added fade effects when gradients with different numbers of color stops
or from new modules are applied. Keeps the existing functionality while
adding smooth visual transitions.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, 
                           QCheckBox, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor

from .animated_gradient_drawing import AnimatedGradientDrawingArea
from .animation_renderer import GradientRenderer, AnimationTimer, create_gradient_renderer

# Import undo/redo functionality with fallback
try:
    from .gradient_history import GradientHistoryManager
    UNDO_REDO_AVAILABLE = True
except ImportError:
    UNDO_REDO_AVAILABLE = False
    GradientHistoryManager = None


class FadeTransition:
    """Manages fade in/out transitions for gradient changes."""
    
    def __init__(self):
        self.is_fading = False
        self.fade_progress = 0.0
        self.fade_direction = 1  # 1 for fade in, -1 for fade out
        self.fade_speed = 0.08   # Fade speed (0.08 = ~12.5 frames for full fade)
        self.pending_gradient = None
        self.fade_trigger_threshold = 0.3  # Different stop count threshold
        
    def should_trigger_fade(self, current_stops, new_stops):
        """Determine if fade effect should be triggered."""
        if not current_stops or not new_stops:
            return True
        
        # Trigger fade if stop count difference is significant
        current_count = len(current_stops)
        new_count = len(new_stops)
        
        count_diff_ratio = abs(current_count - new_count) / max(current_count, new_count, 1)
        
        return count_diff_ratio >= self.fade_trigger_threshold
    
    def reset(self):
        """Reset fade state."""
        self.is_fading = False
        self.fade_progress = 0.0
        self.fade_direction = 1
        self.pending_gradient = None


class AnimatedGradientPreview(QWidget):
    """Interactive animated gradient preview with fade transition effects."""
    
    # Core signals
    animation_complete = pyqtSignal()
    stop_selected = pyqtSignal(int)
    stop_moved = pyqtSignal(int, float)
    stop_color_changed = pyqtSignal(int, tuple)
    stop_added = pyqtSignal(float, tuple)
    stop_deleted = pyqtSignal(int)
    undo_performed = pyqtSignal()
    redo_performed = pyqtSignal()
    history_changed = pyqtSignal()
    fade_transition_started = pyqtSignal()
    fade_transition_complete = pyqtSignal()
    
    def __init__(self, gradient_model):
        super().__init__()
        
        # Core state
        self.gradient_model = gradient_model
        self._destroyed = False
        
        # Animation renderer - centralized animation handling
        self.renderer = create_gradient_renderer()
        
        # Fade transition manager
        self.fade_transition = FadeTransition()
        
        # History management
        self.history_manager = GradientHistoryManager() if UNDO_REDO_AVAILABLE else None
        self.auto_save_enabled = True
        
        # Gradient state
        self.prev_stops = []
        self.target_stops = []
        self.current_stops = []
        
        # Interactive state
        self.selected_stop_index = -1
        self.hover_stop_index = -1
        
        # Initialize timers
        self._init_timers()
        self._init_ui()
        self._connect_signals()
        
        # Delayed initialization
        QTimer.singleShot(200, self._initialize_state)
        if self.history_manager:
            QTimer.singleShot(500, self._save_initial_state)
    
    def _init_timers(self):
        """Initialize animation timers including fade timer."""
        # Transition animation timer
        self.animation_timer = AnimationTimer(self._animation_frame)
        
        # Continuous animation timer 
        self.continuous_timer = AnimationTimer(self._continuous_frame)
        self.continuous_timer.set_interval(self.renderer.animation_state.get_speed_interval())
        
        # Fade transition timer
        self.fade_timer = AnimationTimer(self._fade_frame)
        
        # Save timer for history
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self._execute_delayed_save)
    
    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        
        # Header controls
        header_layout = self._create_header()
        layout.addLayout(header_layout)
        
        # Drawing area
        self.drawing_area = AnimatedGradientDrawingArea(self.gradient_model)
        # Pass renderer to drawing area
        self.drawing_area.set_renderer(self.renderer)
        
        self.drawing_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.drawing_area.setMinimumHeight(240)
        self.drawing_area.setMaximumHeight(240)
        layout.addWidget(self.drawing_area)
        
        # Widget size
        self.setMinimumSize(300, 140)
        self.setMaximumHeight(240)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addStretch(0)
    
    def _create_header(self):
        """Create header with controls and description."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Title
        title = QLabel("Interactive Preview")
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        title.setFixedHeight(20)
        layout.addWidget(title)
        
        # Undo/Redo buttons
        if self.history_manager:
            self.undo_button = self._create_control_button("↶", "Undo (Ctrl+Z)", self.undo)
            self.redo_button = self._create_control_button("↷", "Redo (Ctrl+Y)", self.redo)
            layout.addWidget(self.undo_button)
            layout.addWidget(self.redo_button)
            self.undo_button.setEnabled(False)
            self.redo_button.setEnabled(False)
        
        # Linear Movement toggle
        self.linear_toggle = QCheckBox("Linear Movement")
        self.linear_toggle.setStyleSheet("font-size: 10px;")
        self.linear_toggle.setFixedHeight(20)
        self.linear_toggle.stateChanged.connect(self._toggle_linear_movement)
        layout.addWidget(self.linear_toggle)
        
        # Description text (updated to mention fade effects)
        hint_text = "Left-click: add • Double-click: edit • Drag: move • Right-click: options"
        if self.history_manager:
            hint_text += " • Ctrl+Z/Y: undo/redo"
        hint_text += " • Smooth fade transitions"
        
        self.hint_label = QLabel(hint_text)
        self.hint_label.setStyleSheet("color: #888; font-size: 9px; font-style: italic;")
        self.hint_label.setFixedHeight(20)
        self.hint_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.hint_label.setWordWrap(False)
        layout.addWidget(self.hint_label)
        
        return layout
    
    def _create_control_button(self, text, tooltip, callback):
        """Create a standardized control button."""
        button = QPushButton(text)
        button.setFixedSize(22, 20)
        button.setToolTip(tooltip)
        button.clicked.connect(callback)
        return button
    
    def _connect_signals(self):
        """Connect all signals."""
        if not self.drawing_area:
            return
        
        # Drawing area signals
        signal_connections = [
            (self.drawing_area.stop_selected, self._handle_stop_selected),
            (self.drawing_area.stop_moved, self._handle_stop_moved),
            (self.drawing_area.stop_hover, self._handle_stop_hover),
            (self.drawing_area.stop_color_edit_requested, self._handle_color_edited),
            (self.drawing_area.stop_added, self._handle_stop_added),
            (self.drawing_area.stop_deleted, self._handle_stop_deleted)
        ]
        
        for signal, handler in signal_connections:
            signal.connect(handler)
        
        # History integration
        if self.history_manager:
            self.drawing_area.set_history_manager(self.history_manager)
            self.drawing_area.undo_requested.connect(self.undo)
            self.drawing_area.redo_requested.connect(self.redo)
            self.drawing_area.state_changed.connect(self.history_changed.emit)
            
            # History state updates
            self.history_manager.undo_available.connect(self._update_undo_button)
            self.history_manager.redo_available.connect(self._update_redo_button)
            self.history_manager.history_changed.connect(self.history_changed.emit)
    
    def _initialize_state(self):
        """Initialize widget state safely."""
        if self._destroyed:
            return
        
        try:
            stops = self.gradient_model.get_color_stops()
            self.current_stops = stops.copy()
            self.prev_stops = stops.copy()
            self.target_stops = stops.copy()
            self.drawing_area.set_stops(stops)
            self.drawing_area.update()
        except Exception as e:
            self._handle_error("State initialization failed", e)
    
    def _save_initial_state(self):
        """Save initial state to history."""
        if self.history_manager and not self._destroyed:
            try:
                self.history_manager.save_state(self.gradient_model, force=True, description="Initial state")
            except Exception as e:
                self._handle_error("Failed to save initial state", e)
    
    def showEvent(self, event):
        """Handle show event."""
        super().showEvent(event)
        if not self._destroyed and self.renderer.animation_state.continuous_enabled:
            self._start_continuous()
    
    # === FADE TRANSITION METHODS ===
    
    def _should_use_fade_transition(self, new_stops):
        """Determine if fade transition should be used."""
        if self.fade_transition.is_fading:
            return False  # Don't interrupt existing fade
        
        return self.fade_transition.should_trigger_fade(self.current_stops, new_stops)
    
    def _start_fade_transition(self, new_stops):
        """Start fade out -> fade in transition."""
        print("🎭 Starting fade transition for gradient change")
        
        self.fade_transition.is_fading = True
        self.fade_transition.fade_direction = -1  # Start with fade out
        self.fade_transition.fade_progress = 1.0  # Start fully visible
        self.fade_transition.pending_gradient = new_stops.copy()
        
        # Start fade timer
        self.fade_timer.start(16)  # 60fps for smooth fade
        self.fade_transition_started.emit()
    
    def _fade_frame(self):
        """Process fade animation frame."""
        if self._destroyed or not self.fade_transition.is_fading:
            self.fade_timer.stop()
            return
        
        # Update fade progress
        self.fade_transition.fade_progress += (
            self.fade_transition.fade_direction * self.fade_transition.fade_speed
        )
        
        if self.fade_transition.fade_direction == -1:  # Fading out
            if self.fade_transition.fade_progress <= 0.0:
                self.fade_transition.fade_progress = 0.0
                self._switch_to_new_gradient()
                self.fade_transition.fade_direction = 1  # Switch to fade in
        else:  # Fading in
            if self.fade_transition.fade_progress >= 1.0:
                self.fade_transition.fade_progress = 1.0
                self._complete_fade_transition()
        
        # Apply fade effect to drawing area
        self._apply_fade_effect()
    
    def _switch_to_new_gradient(self):
        """Switch to the new gradient at the midpoint of fade."""
        if self.fade_transition.pending_gradient:
            print("🔄 Switching to new gradient during fade")
            self.current_stops = self.fade_transition.pending_gradient.copy()
            self.prev_stops = self.fade_transition.pending_gradient.copy()
            self.target_stops = self.fade_transition.pending_gradient.copy()
            self.drawing_area.set_stops(self.current_stops, force_update=True)
    
    def _complete_fade_transition(self):
        """Complete the fade transition."""
        print("✅ Fade transition complete")
        
        self.fade_transition.reset()
        self.fade_timer.stop()
        self._remove_fade_effect()
        self.drawing_area.update()
        self.fade_transition_complete.emit()
    
    def _apply_fade_effect(self):
        """Apply fade effect to the drawing area."""
        if self.drawing_area and hasattr(self.drawing_area, 'setWindowOpacity'):
            # Apply opacity based on fade progress
            opacity = max(0.0, min(1.0, self.fade_transition.fade_progress))
            self.drawing_area.setWindowOpacity(opacity)
        
        # Update the drawing area to show fade effect
        self.drawing_area.update()
    
    def _remove_fade_effect(self):
        """Remove fade effect and restore normal appearance."""
        if self.drawing_area and hasattr(self.drawing_area, 'setWindowOpacity'):
            self.drawing_area.setWindowOpacity(1.0)
    
    def get_fade_opacity(self):
        """Get current fade opacity for drawing area to use."""
        if self.fade_transition.is_fading:
            return max(0.0, min(1.0, self.fade_transition.fade_progress))
        return 1.0
    
    # === ENHANCED UPDATE METHODS WITH FADE SUPPORT ===
    
    def update_gradient(self, animate=True, save_to_history=False, source_hint="unknown"):
        """Update gradient with fade transition support."""
        if self._destroyed or not self.gradient_model:
            return
        
        try:
            new_stops = self.gradient_model.get_color_stops()
            
            if save_to_history:
                self._schedule_save("Gradient updated")
            
            # Check if we should use fade transition
            use_fade = self._should_use_fade_transition(new_stops)
            
            if use_fade:
                print(f"🎭 Using fade transition for gradient from {source_hint}")
                self._start_fade_transition(new_stops)
            elif animate and self.renderer.animation_state.animation_enabled and self.prev_stops:
                self._start_animation(new_stops)
            else:
                self._update_immediate(new_stops)
                
        except Exception as e:
            self._handle_error("Gradient update failed", e)
    
    def update_gradient_from_external_source(self, animate=True, save_to_history=False, source="external"):
        """Update gradient specifically from external sources with fade."""
        print(f"🌟 External gradient update from: {source}")
        self.update_gradient(animate=animate, save_to_history=save_to_history, source_hint=source)
    
    def _start_animation(self, new_stops):
        """Start transition animation using renderer state."""
        self.prev_stops = self.current_stops.copy()
        self.target_stops = new_stops.copy()
        self.renderer.animation_state.animation_progress = 0.0
        self.renderer.animation_state.is_animating = True
        
        if not self.animation_timer.is_running:
            self.animation_timer.start(16)  # 60fps
    
    def _update_immediate(self, new_stops):
        """Update without animation."""
        self.current_stops = new_stops.copy()
        self.prev_stops = new_stops.copy()
        self.target_stops = new_stops.copy()
        self.drawing_area.set_stops(new_stops)
        self.drawing_area.update()
    
    def _animation_frame(self):
        """Process animation frame using renderer interpolation."""
        if self._destroyed or not self.renderer.animation_state.is_animating:
            self.animation_timer.stop()
            return
        
        self.renderer.animation_state.animation_progress += 0.06
        
        if self.renderer.animation_state.animation_progress >= 1.0:
            self._complete_animation()
        else:
            self._update_animation()
    
    def _complete_animation(self):
        """Complete animation sequence."""
        self.renderer.animation_state.animation_progress = 1.0
        self.renderer.animation_state.is_animating = False
        self.animation_timer.stop()
        self.current_stops = self.target_stops.copy()
        self.drawing_area.set_stops(self.current_stops)
        self.drawing_area.update()
        self.animation_complete.emit()
    
    def _update_animation(self):
        """Update animation frame using renderer interpolation."""
        try:
            interpolated = self.renderer.interpolator.interpolate_stops_transition(
                self.prev_stops, self.target_stops, self.renderer.animation_state.animation_progress
            )
            self.current_stops = interpolated
            self.drawing_area.set_stops(interpolated)
            self.drawing_area.update()
        except Exception as e:
            self._handle_error("Animation update failed", e)
            self._complete_animation()
    
    def _continuous_frame(self):
        """Update continuous animation using renderer."""
        if (self._destroyed or not self.renderer.animation_state.animation_enabled or 
            not self.renderer.animation_state.continuous_enabled):
            return
        
        self.renderer.update_animation_step()
        self.drawing_area.update()
    
    # === UNDO/REDO FUNCTIONALITY ===
    
    def undo(self) -> bool:
        """Perform undo operation with fade effect."""
        if self._destroyed or not self.history_manager:
            return False
        
        try:
            success = self.history_manager.undo(self.gradient_model)
            if success:
                self.update_gradient_from_external_source(animate=True, source="undo")
                self._sync_drawing_area()
                self.undo_performed.emit()
                return True
        except Exception as e:
            self._handle_error("Undo failed", e)
        
        return False
    
    def redo(self) -> bool:
        """Perform redo operation with fade effect."""
        if self._destroyed or not self.history_manager:
            return False
        
        try:
            success = self.history_manager.redo(self.gradient_model)
            if success:
                self.update_gradient_from_external_source(animate=True, source="redo")
                self._sync_drawing_area()
                self.redo_performed.emit()
                return True
        except Exception as e:
            self._handle_error("Redo failed", e)
        
        return False
    
    def can_undo(self) -> bool:
        """Check undo availability."""
        return bool(self.history_manager and self.history_manager.can_undo())
    
    def can_redo(self) -> bool:
        """Check redo availability."""
        return bool(self.history_manager and self.history_manager.can_redo())
    
    def save_state_to_history(self, description: str = None, force: bool = False):
        """Save state to history manually."""
        if self.history_manager and self.auto_save_enabled:
            try:
                self.history_manager.save_state(self.gradient_model, force=force, description=description)
                self.history_changed.emit()
            except Exception as e:
                self._handle_error("Failed to save state", e)
    
    def _schedule_save(self, description: str = "Auto-save", delay: int = 200):
        """Schedule delayed save to batch changes."""
        if self.history_manager and self.auto_save_enabled:
            self._pending_save_desc = description
            self.save_timer.stop()
            self.save_timer.start(delay)
    
    def _execute_delayed_save(self):
        """Execute delayed save operation."""
        if not self._destroyed:
            description = getattr(self, '_pending_save_desc', "Auto-save")
            self.save_state_to_history(description)
    
    def _sync_drawing_area(self):
        """Synchronize drawing area state after undo/redo."""
        if hasattr(self.drawing_area, 'update_last_saved_state'):
            try:
                self.drawing_area.update_last_saved_state()
            except Exception as e:
                self._handle_error("Failed to sync drawing area", e)
    
    # === EVENT HANDLERS ===
    
    def _handle_stop_selected(self, index):
        """Handle stop selection."""
        if not self._destroyed:
            self.selected_stop_index = index
            self.stop_selected.emit(index)
    
    def _handle_stop_moved(self, index, position):
        """Handle stop movement."""
        if not self._destroyed:
            try:
                self.gradient_model.set_position_at_index(index, position)
                self.current_stops = self.gradient_model.get_color_stops()
                self.stop_moved.emit(index, position)
            except Exception as e:
                self._handle_error("Failed to move stop", e)
    
    def _handle_stop_hover(self, index):
        """Handle stop hover."""
        if not self._destroyed:
            self.hover_stop_index = index
    
    def _handle_color_edited(self, index):
        """Handle color edit completion."""
        if not self._destroyed:
            try:
                self.current_stops = self.gradient_model.get_color_stops()
                if 0 <= index < len(self.current_stops):
                    _, new_color = self.current_stops[index]
                    self.stop_color_changed.emit(index, new_color)
            except Exception as e:
                self._handle_error("Failed to handle color edit", e)
    
    def _handle_stop_added(self, position, color):
        """Handle stop addition."""
        if not self._destroyed:
            try:
                self.current_stops = self.gradient_model.get_color_stops()
                self.drawing_area.set_stops(self.current_stops)
                self.stop_added.emit(position, color)
            except Exception as e:
                self._handle_error("Failed to add stop", e)
    
    def _handle_stop_deleted(self, index):
        """Handle stop deletion."""
        if not self._destroyed:
            try:
                self.current_stops = self.gradient_model.get_color_stops()
                self.drawing_area.set_stops(self.current_stops)
                
                # Update selection
                if self.selected_stop_index == index:
                    self.selected_stop_index = -1
                elif self.selected_stop_index > index:
                    self.selected_stop_index -= 1
                
                self.stop_deleted.emit(index)
            except Exception as e:
                self._handle_error("Failed to delete stop", e)
    
    # === CONTROL EVENT HANDLERS ===
    
    def _toggle_linear_movement(self, state):
        """Toggle linear movement using renderer state."""
        if self._destroyed:
            return
        
        enabled = state == Qt.Checked
        self.renderer.set_continuous_enabled(enabled)
        
        if self.renderer.animation_state.animation_enabled and enabled:
            self._start_continuous()
        else:
            self._stop_continuous()
            # Reset to starting position
            self.renderer.set_animation_step(0)
            self.renderer.set_animation_direction(1)
            self.drawing_area.update()
    
    def _start_continuous(self):
        """Start continuous animation."""
        if (self.renderer.animation_state.animation_enabled and 
            self.renderer.animation_state.continuous_enabled and 
            not self.continuous_timer.is_running):
            self.continuous_timer.start()
    
    def _stop_continuous(self):
        """Stop continuous animation."""
        self.continuous_timer.stop()
    
    # === BUTTON STATE UPDATES ===
    
    def _update_undo_button(self, available):
        """Update undo button state."""
        if hasattr(self, 'undo_button'):
            self.undo_button.setEnabled(available)
    
    def _update_redo_button(self, available):
        """Update redo button state."""
        if hasattr(self, 'redo_button'):
            self.redo_button.setEnabled(available)
    
    # === LIFECYCLE METHODS ===
    
    def hideEvent(self, event):
        """Handle hide event."""
        super().hideEvent(event)
        if not self._destroyed:
            self.stop_all_animations()
    
    def closeEvent(self, event):
        """Handle close event."""
        self._destroyed = True
        self.stop_all_animations()
        
        if self.history_manager and self.auto_save_enabled:
            try:
                self.save_state_to_history("Final state", force=True)
            except:
                pass
        
        super().closeEvent(event)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if self._destroyed:
            return
        
        try:
            ctrl = event.modifiers() == Qt.ControlModifier
            ctrl_shift = event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier)
            
            if event.key() == Qt.Key_Z and ctrl and self.can_undo():
                self.undo()
                event.accept()
                return
            elif event.key() == Qt.Key_Y and ctrl and self.can_redo():
                self.redo()
                event.accept()
                return
            elif event.key() == Qt.Key_Z and ctrl_shift and self.can_redo():
                self.redo()
                event.accept()
                return
            
            # Pass to drawing area
            if self.drawing_area and self.drawing_area.hasFocus():
                self.drawing_area.keyPressEvent(event)
                return
                
        except Exception as e:
            self._handle_error("Keyboard event failed", e)
        
        super().keyPressEvent(event)
    
    def stop_all_animations(self):
        """Stop all animation timers safely including fade timer."""
        if self._destroyed:
            return
        
        try:
            self.animation_timer.stop()
            self.continuous_timer.stop()
            self.fade_timer.stop()
            self.save_timer.stop()
            self.renderer.animation_state.is_animating = False
            self.fade_transition.reset()
            self._remove_fade_effect()
        except:
            pass
    
    # === UTILITY METHODS ===
    
    def _handle_error(self, message, exception):
        """Centralized error handling."""
        error_msg = f"AnimatedGradientPreview: {message}: {str(exception)}"
        print(error_msg)
        
        # Show critical errors to user
        if "failed" in message.lower():
            try:
                QMessageBox.warning(self.window(), "Gradient Preview Error", 
                                  f"An error occurred: {message}")
            except:
                pass
    
    # === PUBLIC INTERFACE WITH FADE SUPPORT ===
    
    def set_animation_type(self, animation_type):
        """Set animation type using renderer."""
        if animation_type in ["linear", "radial", "conical"]:
            try:
                self.renderer.set_animation_type(animation_type)
                self.drawing_area.update()
            except Exception as e:
                self._handle_error("Failed to set animation type", e)
    
    def set_history_enabled(self, enabled):
        """Enable/disable history tracking."""
        if isinstance(enabled, bool):
            self.auto_save_enabled = enabled
            if self.history_manager:
                self.history_manager.set_enabled(enabled)
            if self.drawing_area:
                self.drawing_area.set_auto_save_enabled(enabled)
    
    def force_update_from_model(self, skip_animation=False, reason="Manual update", source="unknown"):
        """Force update from gradient model with fade support."""
        if self._destroyed:
            return
            
        try:
            new_stops = self.gradient_model.get_color_stops()
            
            # Use fade for external updates
            if source in ["theme", "random", "external", "batch", "import", "load", "preset"]:
                self.update_gradient_from_external_source(
                    animate=not skip_animation, 
                    save_to_history=False, 
                    source=source
                )
            else:
                self.current_stops = new_stops.copy()
                self.drawing_area.set_stops(new_stops, force_update=True)
                
            self._schedule_save(reason, delay=50)
        except Exception as e:
            self._handle_error(f"Failed to force update: {reason}", e)
    
    def apply_gradient_with_fade(self, new_gradient, source="external"):
        """Apply a new gradient with automatic fade transition."""
        if self._destroyed:
            return
        
        try:
            # Store the new gradient in the model
            self.gradient_model._color_stops = []
            for stop in new_gradient.get_color_stop_objects():
                self.gradient_model.add_color_stop(stop.position, stop.color)
            
            # Copy metadata
            for attr in ['name', 'author', 'description', 'ugr_category']:
                if hasattr(new_gradient, f'get_{attr}') and hasattr(self.gradient_model, f'set_{attr}'):
                    try:
                        value = getattr(new_gradient, f'get_{attr}')()
                        getattr(self.gradient_model, f'set_{attr}')(value)
                    except:
                        pass
            
            # Trigger fade transition
            self.update_gradient_from_external_source(animate=True, source=source)
            print(f"🎭 Applied gradient with fade from {source}")
            
        except Exception as e:
            self._handle_error(f"Failed to apply gradient with fade from {source}", e)
    
    def validate_stop_consistency(self, verbose=False) -> bool:
        """Validate current state for consistency."""
        try:
            if not self.gradient_model:
                return False
            
            model_stops = self.gradient_model.get_color_stops()
            consistent = len(self.current_stops) == len(model_stops)
            
            if verbose and not consistent:
                print(f"Inconsistency: current_stops={len(self.current_stops)}, model_stops={len(model_stops)}")
            
            return consistent
            
        except Exception as e:
            if verbose:
                self._handle_error("State validation failed", e)
            return False
    
    def get_undo_redo_status(self) -> dict:
        """Get undo/redo status."""
        try:
            return {
                "can_undo": self.can_undo(),
                "can_redo": self.can_redo(),
                "history_size": len(self.history_manager.history) if self.history_manager else 0,
                "auto_save_enabled": self.auto_save_enabled,
                "undo_redo_available": UNDO_REDO_AVAILABLE
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_fade_status(self) -> dict:
        """Get fade transition status."""
        return {
            "is_fading": self.fade_transition.is_fading,
            "fade_progress": self.fade_transition.fade_progress,
            "fade_direction": "out" if self.fade_transition.fade_direction == -1 else "in",
            "has_pending_gradient": self.fade_transition.pending_gradient is not None,
            "fade_speed": self.fade_transition.fade_speed,
            "fade_threshold": self.fade_transition.fade_trigger_threshold
        }
    
    # === PROGRAMMATIC CONTROL METHODS ===
    
    def set_animation_enabled(self, enabled: bool):
        """Programmatically enable/disable animation."""
        self.renderer.set_animation_enabled(enabled)
        if not enabled:
            self._stop_continuous()
        elif self.renderer.animation_state.continuous_enabled:
            self._start_continuous()
    
    def set_animation_speed(self, speed: int):
        """Programmatically set animation speed."""
        self.renderer.set_animation_speed(speed)
        interval = self.renderer.animation_state.get_speed_interval()
        self.continuous_timer.set_interval(interval)
    
    def set_fade_speed(self, speed: float):
        """Set fade transition speed (0.01 - 0.5)."""
        self.fade_transition.fade_speed = max(0.01, min(0.5, speed))
    
    def set_fade_threshold(self, threshold: float):
        """Set fade trigger threshold (0.1 - 1.0)."""
        self.fade_transition.fade_trigger_threshold = max(0.1, min(1.0, threshold))
    
    def reverse_animation_direction(self):
        """Programmatically reverse animation direction."""
        current_direction = self.renderer.animation_state.animation_direction
        self.renderer.set_animation_direction(-current_direction)
    
    def get_animation_settings(self) -> dict:
        """Get current animation settings from renderer."""
        settings = self.renderer.get_animation_state()
        settings.update(self.get_fade_status())
        return settings
    
    # === INTEGRATION METHODS FOR EXTERNAL COMPONENTS ===
    
    def connect_to_theme_generator(self, theme_widget):
        """Connect to theme generator with fade support."""
        if hasattr(theme_widget, 'gradient_generated'):
            theme_widget.gradient_generated.connect(
                lambda grad: self.apply_gradient_with_fade(grad, "theme")
            )
            print("🎭 Connected to theme generator with fade transitions")
    
    def connect_to_random_generator(self, random_widget):
        """Connect to random generator with fade support."""
        if hasattr(random_widget, 'gradient_generated'):
            random_widget.gradient_generated.connect(
                lambda grad: self.apply_gradient_with_fade(grad, "random")
            )
            print("🎭 Connected to random generator with fade transitions")
    
    def connect_to_blend_widget(self, blend_widget):
        """Connect to blend widget with fade support."""
        if hasattr(blend_widget, 'gradient_blended'):
            blend_widget.gradient_blended.connect(
                lambda grad: self.apply_gradient_with_fade(grad, "blend")
            )
            print("🎭 Connected to blend widget with fade transitions")
    
    def connect_to_distribution_widget(self, dist_widget):
        """Connect to distribution widget with fade support."""
        if hasattr(dist_widget, 'distribution_changed'):
            dist_widget.distribution_changed.connect(
                lambda: self.update_gradient_from_external_source(True, False, "distribution")
            )
            print("🎭 Connected to distribution widget with fade transitions")
    
    def connect_to_preset_loader(self, preset_loader):
        """Connect to preset loader with fade support."""
        if hasattr(preset_loader, 'preset_loaded'):
            preset_loader.preset_loaded.connect(
                lambda grad: self.apply_gradient_with_fade(grad, "preset")
            )
            print("🎭 Connected to preset loader with fade transitions")
    
    # === FACTORY METHOD ===
    
    @staticmethod
    def create_with_fade_effects(gradient_model, max_history_size: int = 50, fade_speed: float = 0.08):
        """Factory method to create preview with fade effects and undo/redo."""
        preview = AnimatedGradientPreview(gradient_model)
        
        if preview.history_manager:
            preview.history_manager.max_history_size = max_history_size
            preview.auto_save_enabled = True
        
        preview.set_fade_speed(fade_speed)
        
        print(f"🎭 Created animated preview with fade effects (speed: {fade_speed})")
        return preview
    
    def __del__(self):
        """Destructor for cleanup."""
        try:
            self._destroyed = True
            self.stop_all_animations()
            self.fade_transition.reset()
        except:
            pass
                