#!/usr/bin/env python3
"""
Enhanced Animated Gradient Startup Integration Module with Fade Support

Updated to support the new fade effects when gradients are applied from different modules.
Properly connects the drawing area to the preview for fade coordination.
"""
import sys
import os
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QGridLayout, QVBoxLayout, QHBoxLayout


def initialize_animation():
    """
    Initialize the animation module with fade effect support.
    
    This function:
    1. Checks if QApplication is available and running
    2. Locates the animated preview module
    3. Finds the main application window
    4. Replaces the standard preview with the fade-enabled animated one
    5. Ensures proper fade coordination between components
    6. Connects all necessary signals including fade transition events
    
    Returns:
        True if successful, False otherwise
    """
    # Check if QApplication is available
    app = QApplication.instance()
    if not app:
        print("WARNING: No QApplication instance found - cannot initialize animation")
        return False
    
    print("Initializing enhanced animated gradient preview with fade effects...")
    
    try:
        # Try to import AnimatedGradientPreview from various possible locations
        AnimatedGradientPreview = None
        
        # Attempt various import paths
        import_attempts = [
            "gradient_generator.ui.animation.animated_gradient_preview",
            "ui.animation.animated_gradient_preview",
            "animated_gradient_preview"
        ]
        
        for import_path in import_attempts:
            try:
                module = __import__(import_path, fromlist=['AnimatedGradientPreview'])
                if hasattr(module, 'AnimatedGradientPreview'):
                    AnimatedGradientPreview = module.AnimatedGradientPreview
                    print(f"Successfully imported AnimatedGradientPreview with fade support from {import_path}")
                    break
            except ImportError as e:
                print(f"Failed to import from {import_path}: {e}")
                continue
        
        if not AnimatedGradientPreview:
            print("Could not import AnimatedGradientPreview class from any location")
            return False
        
        # Schedule initialization after main window is fully ready
        # Use a longer delay to ensure everything is properly initialized
        def delayed_initialization():
            return _delayed_initialization(AnimatedGradientPreview)
        
        QTimer.singleShot(1500, delayed_initialization)
        return True
        
    except Exception as e:
        print(f"Error during animation initialization: {e}")
        import traceback
        traceback.print_exc()
        return False


def _delayed_initialization(AnimatedGradientPreview):
    """Perform the actual initialization after delay."""
    try:
        # Find the main window
        main_window = _find_main_window()
        if not main_window:
            print("Could not find main window for animation integration")
            return False
        
        # Check if main window is properly initialized
        if not hasattr(main_window, 'current_gradient'):
            print("Main window not fully initialized yet")
            # Try again after another delay
            QTimer.singleShot(1000, lambda: _delayed_initialization(AnimatedGradientPreview))
            return False
        
        # Replace the standard preview with fade-enabled animated preview
        animated_preview = _replace_preview_widget(main_window, AnimatedGradientPreview)
        if not animated_preview:
            print("Failed to replace preview widget")
            return False
        
        # Ensure linear movement is disabled by default
        animated_preview.continuous_animation_enabled = False
        if hasattr(animated_preview, 'linear_movement_toggle'):
            animated_preview.linear_movement_toggle.setChecked(False)
        
        # Make sure continuous timer is not running
        if hasattr(animated_preview, 'continuous_timer'):
            animated_preview.continuous_timer.stop()
        
        # Set up fade coordination between preview and drawing area
        _setup_fade_coordination(animated_preview)
        
        # Connect all signals including the new fade transition signals
        _connect_signals(main_window, animated_preview)
        
        # Connect fade effects to external modules
        _connect_fade_effects_to_modules(main_window, animated_preview)
        
        # Update the preview to ensure proper initial state
        try:
            animated_preview.update_gradient(animate=False)
        except Exception as e:
            print(f"Error updating initial gradient: {e}")
        
        print("✅ Enhanced animation integration complete - fade effects enabled")
        return True
    
    except Exception as e:
        print(f"Error in delayed initialization: {e}")
        import traceback
        traceback.print_exc()
        return False


def _setup_fade_coordination(animated_preview):
    """Set up proper fade coordination between preview and drawing area."""
    try:
        if hasattr(animated_preview, 'drawing_area'):
            # Set the parent preview reference in drawing area
            animated_preview.drawing_area.set_parent_preview(animated_preview)
            print("✅ Fade coordination established between preview and drawing area")
            
            # Connect fade transition signals if available
            if hasattr(animated_preview, 'fade_transition_started'):
                animated_preview.fade_transition_started.connect(
                    lambda: print("🎭 Fade transition started")
                )
            
            if hasattr(animated_preview, 'fade_transition_complete'):
                animated_preview.fade_transition_complete.connect(
                    lambda: print("✅ Fade transition complete")
                )
    
    except Exception as e:
        print(f"Error setting up fade coordination: {e}")


def _connect_fade_effects_to_modules(main_window, animated_preview):
    """Connect fade effects to external modules like themes, random generator, etc."""
    try:
        # Connect to control panel tabs that generate new gradients
        if hasattr(main_window, 'control_panel'):
            control_panel = main_window.control_panel
            
            # Connect to theme generator with fade support
            if hasattr(control_panel, 'theme_generator_widget'):
                try:
                    animated_preview.connect_to_theme_generator(control_panel.theme_generator_widget)
                except Exception as e:
                    print(f"Could not connect theme generator to fade effects: {e}")
            
            # Connect to blend widget with fade support
            if hasattr(control_panel, 'blending_widget'):
                try:
                    animated_preview.connect_to_blend_widget(control_panel.blending_widget)
                except Exception as e:
                    print(f"Could not connect blend widget to fade effects: {e}")
            
            # Connect to distribution widgets with fade support
            if hasattr(control_panel, 'unified_distribution_widget'):
                try:
                    animated_preview.connect_to_distribution_widget(control_panel.unified_distribution_widget)
                except Exception as e:
                    print(f"Could not connect distribution widget to fade effects: {e}")
            
            # Connect to color stops editor random generation
            if hasattr(control_panel, 'color_stops_editor'):
                editor = control_panel.color_stops_editor
                
                # Override random generation methods to trigger fade
                if hasattr(editor, 'generate_random_gradient'):
                    original_generate = editor.generate_random_gradient
                    
                    def enhanced_generate_random():
                        try:
                            original_generate()
                            # Force fade transition for random generation
                            animated_preview.update_gradient_from_external_source(
                                animate=True, source="random_generator"
                            )
                        except Exception as e:
                            print(f"Error in enhanced random generation: {e}")
                    
                    editor.generate_random_gradient = enhanced_generate_random
                    print("✅ Connected random gradient generator to fade effects")
        
        # Connect to gradient list panel for preset loading
        if hasattr(main_window, 'gradient_list_panel'):
            gradient_list = main_window.gradient_list_panel
            
            # Override gradient selection to use fade effects
            if hasattr(gradient_list, 'gradient_selected'):
                original_signal = gradient_list.gradient_selected
                
                def enhanced_gradient_selected(gradient):
                    try:
                        animated_preview.apply_gradient_with_fade(gradient, "preset")
                    except Exception as e:
                        print(f"Error applying gradient with fade: {e}")
                
                # Connect the enhanced handler
                gradient_list.gradient_selected.connect(enhanced_gradient_selected)
                print("✅ Connected gradient list to fade effects")
        
    except Exception as e:
        print(f"Error connecting fade effects to modules: {e}")


def _find_main_window():
    """Find the main application window."""
    app = QApplication.instance()
    if not app:
        print("No QApplication instance available")
        return None
    
    # Look for MainWindow in top-level widgets
    for widget in app.topLevelWidgets():
        if widget.__class__.__name__ == 'MainWindow':
            print(f"Found MainWindow: {widget}")
            return widget
    
    print("No MainWindow found in top-level widgets")
    return None


def _replace_preview_widget(main_window, AnimatedGradientPreview):
    """Replace standard preview widget with fade-enabled animated version."""
    try:
        # Find the current preview widget
        current_preview = None
        preview_candidates = ['preview_widget', 'gradient_preview', 'animated_preview']
        
        for attr_name in preview_candidates:
            if hasattr(main_window, attr_name):
                candidate = getattr(main_window, attr_name)
                if candidate is not None:
                    current_preview = candidate
                    print(f"Found existing preview widget: {attr_name}")
                    break
        
        if not current_preview:
            print("Could not find preview widget in main window")
            return None
        
        # Get parent and layout
        parent = current_preview.parent()
        if not parent or not parent.layout():
            print("Cannot find parent or layout for preview widget")
            return None
        
        layout = parent.layout()
        
        # Create new fade-enabled animated preview
        try:
            animated_preview = AnimatedGradientPreview.create_with_fade_effects(
                main_window.current_gradient, 
                max_history_size=50,
                fade_speed=0.08
            )
            print("✅ Created new AnimatedGradientPreview with fade effects")
        except Exception as e:
            print(f"Failed to create fade-enabled AnimatedGradientPreview: {e}")
            # Try fallback without fade factory method
            try:
                animated_preview = AnimatedGradientPreview(main_window.current_gradient)
                print("Created AnimatedGradientPreview with basic fade support")
            except Exception as e2:
                print(f"Failed to create any AnimatedGradientPreview: {e2}")
                return None
        
        # Find position in layout and replace widget
        widget_replaced = False
        
        # Handle different layout types
        if isinstance(layout, QGridLayout):
            # For grid layouts, find position
            for row in range(layout.rowCount()):
                for col in range(layout.columnCount()):
                    item = layout.itemAtPosition(row, col)
                    if item and item.widget() == current_preview:
                        # Get span info
                        row_span = 1
                        col_span = 1
                        try:
                            # Try to get span info (this might not be available in all Qt versions)
                            row_span = layout.rowSpan(row, col)
                            col_span = layout.columnSpan(row, col)
                        except:
                            pass
                        
                        # Replace widget
                        layout.removeWidget(current_preview)
                        current_preview.hide()
                        current_preview.deleteLater()
                        
                        layout.addWidget(animated_preview, row, col, row_span, col_span)
                        widget_replaced = True
                        print(f"Replaced widget in grid layout at ({row}, {col})")
                        break
                if widget_replaced:
                    break
                    
        elif isinstance(layout, (QVBoxLayout, QHBoxLayout)):
            # For box layouts, find position by index
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item and item.widget() == current_preview:
                    # Replace widget
                    layout.removeWidget(current_preview)
                    current_preview.hide()
                    current_preview.deleteLater()
                    
                    layout.insertWidget(i, animated_preview)
                    widget_replaced = True
                    print(f"Replaced widget in box layout at index {i}")
                    break
        
        if not widget_replaced:
            print("Failed to replace widget in layout - trying direct replacement")
            # Try direct replacement as last resort
            try:
                layout.addWidget(animated_preview)
                current_preview.hide()
                current_preview.deleteLater()
                widget_replaced = True
                print("Used direct widget addition as fallback")
            except Exception as e:
                print(f"Direct replacement also failed: {e}")
                return None
        
        # Update reference in main window
        for attr_name in preview_candidates:
            if hasattr(main_window, attr_name):
                setattr(main_window, attr_name, animated_preview)
                print(f"Updated main window reference: {attr_name}")
        
        return animated_preview
    
    except Exception as e:
        print(f"Error replacing preview widget: {e}")
        import traceback
        traceback.print_exc()
        return None


def _connect_signals(main_window, animated_preview):
    """Connect all necessary signals including fade transition signals."""
    try:
        # Connect preview to gradient updates from control panel
        if hasattr(main_window, 'control_panel'):
            if hasattr(main_window.control_panel, 'gradient_updated'):
                main_window.control_panel.gradient_updated.connect(
                    lambda: _safe_update_gradient(animated_preview)
                )
                print("Connected control panel gradient_updated signal")
        
        # Connect color stop selection and movement signals
        if hasattr(animated_preview, 'stop_selected'):
            animated_preview.stop_selected.connect(
                lambda index: _handle_stop_selection(main_window, index)
            )
            print("Connected stop_selected signal")
            
        if hasattr(animated_preview, 'stop_moved'):
            animated_preview.stop_moved.connect(
                lambda index, pos: _handle_stop_movement(main_window, index, pos)
            )
            print("Connected stop_moved signal")
        
        # Connect color change signal
        if hasattr(animated_preview, 'stop_color_changed'):
            animated_preview.stop_color_changed.connect(
                lambda index, color: _handle_stop_color_change(main_window, index, color)
            )
            print("Connected stop_color_changed signal")
        
        # Connect add/delete signals
        if hasattr(animated_preview, 'stop_added'):
            animated_preview.stop_added.connect(
                lambda pos, color: _handle_stop_added(main_window, pos, color)
            )
            print("Connected stop_added signal")
        
        if hasattr(animated_preview, 'stop_deleted'):
            animated_preview.stop_deleted.connect(
                lambda index: _handle_stop_deleted(main_window, index)
            )
            print("Connected stop_deleted signal")
        
        # Connect fade transition signals
        if hasattr(animated_preview, 'fade_transition_started'):
            animated_preview.fade_transition_started.connect(
                lambda: _handle_fade_started(main_window)
            )
            print("Connected fade_transition_started signal")
        
        if hasattr(animated_preview, 'fade_transition_complete'):
            animated_preview.fade_transition_complete.connect(
                lambda: _handle_fade_complete(main_window)
            )
            print("Connected fade_transition_complete signal")
        
        return True
    
    except Exception as e:
        print(f"Error connecting signals: {e}")
        return False


def _handle_fade_started(main_window):
    """Handle fade transition start."""
    try:
        if hasattr(main_window, 'statusBar'):
            main_window.statusBar().showMessage("🎭 Transitioning gradient...", 2000)
    except Exception as e:
        print(f"Error handling fade start: {e}")


def _handle_fade_complete(main_window):
    """Handle fade transition completion."""
    try:
        if hasattr(main_window, 'statusBar'):
            main_window.statusBar().showMessage("✅ Gradient transition complete", 1500)
    except Exception as e:
        print(f"Error handling fade complete: {e}")


def _safe_update_gradient(animated_preview):
    """Safely update the gradient preview."""
    try:
        if animated_preview and not animated_preview._destroyed:
            animated_preview.update_gradient(animate=True)
    except (RuntimeError, AttributeError):
        # Widget was destroyed or not available
        pass


def _handle_stop_selection(main_window, index):
    """Handle color stop selection."""
    try:
        if hasattr(main_window, 'control_panel') and hasattr(main_window.control_panel, 'color_stops_editor'):
            editor = main_window.control_panel.color_stops_editor
            
            # Try to highlight the selected stop in the editor
            if hasattr(editor, 'color_stops') and index < len(editor.color_stops):
                if hasattr(editor, 'list_widget'):
                    editor.list_widget.setCurrentRow(index)
            
            # Show status message
            if hasattr(main_window, 'statusBar'):
                main_window.statusBar().showMessage(f"Selected color stop #{index+1}")
    except Exception as e:
        print(f"Error handling stop selection: {e}")


def _handle_stop_movement(main_window, index, position):
    """Handle color stop position changes with improved responsiveness."""
    try:
        if hasattr(main_window, 'current_gradient'):
            # Update position in model immediately for responsive feel
            main_window.current_gradient.set_position_at_index(index, position)
            
            # Update UI components
            if hasattr(main_window, 'control_panel'):
                control_panel = main_window.control_panel
                
                # Update editor if available (but don't trigger full refresh for responsiveness)
                if hasattr(control_panel, 'color_stops_editor'):
                    editor = control_panel.color_stops_editor
                    # Update specific stop widget position if available
                    if hasattr(editor, 'color_stops') and index < len(editor.color_stops):
                        stop_widget = editor.color_stops[index]
                        if hasattr(stop_widget, 'position_spin'):
                            stop_widget.position_spin.blockSignals(True)
                            stop_widget.position_spin.setValue(position)
                            stop_widget.position_spin.blockSignals(False)
                
                # Notify of update (but avoid triggering full animation for responsiveness)
                if hasattr(control_panel, 'gradient_updated'):
                    # Use a timer to debounce rapid updates during dragging
                    if not hasattr(main_window, '_update_timer'):
                        main_window._update_timer = QTimer()
                        main_window._update_timer.setSingleShot(True)
                        main_window._update_timer.timeout.connect(
                            lambda: control_panel.gradient_updated.emit()
                        )
                    
                    # Restart timer for debounced update
                    main_window._update_timer.stop()
                    main_window._update_timer.start(50)  # 50ms debounce
                    
            # Show status message with position
            if hasattr(main_window, 'statusBar'):
                main_window.statusBar().showMessage(f"Color stop #{index+1} at position {position:.3f}")
    except Exception as e:
        print(f"Error handling stop movement: {e}")


def _handle_stop_color_change(main_window, index, color):
    """Handle color stop color changes from double-click color picker."""
    try:
        if hasattr(main_window, 'current_gradient'):
            # Update color in model
            main_window.current_gradient.set_color_at_index(index, color)
            
            # Update UI components
            if hasattr(main_window, 'control_panel'):
                control_panel = main_window.control_panel
                
                # Update color stops editor
                if hasattr(control_panel, 'color_stops_editor'):
                    editor = control_panel.color_stops_editor
                    if hasattr(editor, 'update_from_model'):
                        editor.update_from_model()
                
                # Notify of update
                if hasattr(control_panel, 'gradient_updated'):
                    control_panel.gradient_updated.emit()
                    
            # Show status message
            if hasattr(main_window, 'statusBar'):
                r, g, b = color
                main_window.statusBar().showMessage(f"Changed color stop #{index+1} to RGB({r}, {g}, {b})")
    except Exception as e:
        print(f"Error handling stop color change: {e}")


def _handle_stop_added(main_window, position, color):
    """Handle new color stop addition from the animated preview."""
    try:
        if hasattr(main_window, 'control_panel'):
            control_panel = main_window.control_panel
            
            # Update color stops editor to reflect the new stop
            if hasattr(control_panel, 'color_stops_editor'):
                editor = control_panel.color_stops_editor
                if hasattr(editor, 'update_from_model'):
                    editor.update_from_model()
            
            # Notify of update
            if hasattr(control_panel, 'gradient_updated'):
                control_panel.gradient_updated.emit()
                
        # Show status message
        if hasattr(main_window, 'statusBar'):
            r, g, b = color
            main_window.statusBar().showMessage(
                f"Added color stop at position {position:.3f} with color RGB({r}, {g}, {b})"
            )
            
    except Exception as e:
        print(f"Error handling stop addition: {e}")


def _handle_stop_deleted(main_window, index):
    """Handle color stop deletion from the animated preview."""
    try:
        if hasattr(main_window, 'control_panel'):
            control_panel = main_window.control_panel
            
            # Update color stops editor to reflect the deletion
            if hasattr(control_panel, 'color_stops_editor'):
                editor = control_panel.color_stops_editor
                if hasattr(editor, 'update_from_model'):
                    editor.update_from_model()
            
            # Notify of update
            if hasattr(control_panel, 'gradient_updated'):
                control_panel.gradient_updated.emit()
                
        # Show status message
        if hasattr(main_window, 'statusBar'):
            main_window.statusBar().showMessage(f"Deleted color stop #{index+1}")
            
    except Exception as e:
        print(f"Error handling stop deletion: {e}")


# Disable auto-integration on import to prevent the QApplication error
# Auto-integration will only happen when explicitly called
