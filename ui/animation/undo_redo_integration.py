#!/usr/bin/env python3
"""
Undo/Redo Integration Module

This module integrates the undo/redo functionality with the main application,
connecting the history manager, UI widgets, and animated preview.
"""
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication


def integrate_undo_redo_system(main_window):
    """
    Integrate the undo/redo system with the main application window.
    
    Args:
        main_window: Main application window instance
        
    Returns:
        True if integration was successful, False otherwise
    """
    try:
        # Check if animated preview exists and has history manager
        if not hasattr(main_window, 'animated_preview'):
            print("No animated preview found for undo/redo integration")
            return False
        
        animated_preview = main_window.animated_preview
        
        if not hasattr(animated_preview, 'history_manager'):
            print("Animated preview does not have history manager")
            return False
        
        # Check if undo/redo widget exists
        if not hasattr(main_window, 'undo_redo_widget'):
            print("No undo/redo widget found")
            return False
        
        undo_redo_widget = main_window.undo_redo_widget
        history_manager = animated_preview.history_manager
        
        # Connect history manager signals to undo/redo widget
        history_manager.undo_available.connect(
            lambda available: undo_redo_widget.update_button_states(
                available, undo_redo_widget.redo_available
            )
        )
        
        history_manager.redo_available.connect(
            lambda available: undo_redo_widget.update_button_states(
                undo_redo_widget.undo_available, available
            )
        )
        
        history_manager.history_changed.connect(
            lambda: _update_undo_redo_state(undo_redo_widget, history_manager)
        )
        
        # Connect undo/redo widget signals to animated preview
        undo_redo_widget.undo_requested.connect(animated_preview.undo)
        undo_redo_widget.redo_requested.connect(animated_preview.redo)
        
        # Set up periodic state updates
        def update_state():
            if not main_window._is_destroyed if hasattr(main_window, '_is_destroyed') else False:
                _update_undo_redo_state(undo_redo_widget, history_manager)
        
        # Update state every few seconds
        state_timer = QTimer(main_window)
        state_timer.timeout.connect(update_state)
        state_timer.start(2000)  # Update every 2 seconds
        
        # Store timer reference to prevent garbage collection
        main_window._undo_redo_timer = state_timer
        
        # Initial state update
        QTimer.singleShot(1000, update_state)
        
        print("Undo/redo system integrated successfully")
        return True
        
    except Exception as e:
        print(f"Error integrating undo/redo system: {e}")
        return False


def _update_undo_redo_state(undo_redo_widget, history_manager):
    """
    Update the undo/redo widget state based on history manager.
    
    Args:
        undo_redo_widget: The undo/redo UI widget
        history_manager: The gradient history manager
    """
    try:
        can_undo = history_manager.can_undo()
        can_redo = history_manager.can_redo()
        current_desc = history_manager.get_current_state_description()
        
        undo_redo_widget.update_button_states(can_undo, can_redo)
        undo_redo_widget.set_current_description(current_desc)
        
    except Exception as e:
        print(f"Error updating undo/redo state: {e}")


def setup_undo_redo_for_main_window(main_window):
    """
    Set up undo/redo functionality for the main window.
    This function should be called after the main window is fully initialized.
    
    Args:
        main_window: Main application window instance
    """
    try:
        # Delay integration to ensure everything is properly initialized
        def delayed_integration():
            return integrate_undo_redo_system(main_window)
        
        QTimer.singleShot(2000, delayed_integration)
        
    except Exception as e:
        print(f"Error setting up undo/redo system: {e}")


def connect_gradient_updates_to_history(main_window):
    """
    Connect gradient update signals to automatically save history states.
    
    Args:
        main_window: Main application window instance
    """
    try:
        if (hasattr(main_window, 'control_panel') and 
            hasattr(main_window, 'animated_preview') and
            hasattr(main_window.animated_preview, 'history_manager')):
            
            control_panel = main_window.control_panel
            history_manager = main_window.animated_preview.history_manager
            
            # Connect control panel updates to history saving
            if hasattr(control_panel, 'gradient_updated'):
                def save_on_update():
                    # Save with a small delay to batch rapid updates
                    if hasattr(main_window, '_history_save_timer'):
                        main_window._history_save_timer.stop()
                    else:
                        main_window._history_save_timer = QTimer()
                        main_window._history_save_timer.setSingleShot(True)
                        main_window._history_save_timer.timeout.connect(
                            lambda: history_manager.save_state(main_window.current_gradient)
                        )
                    
                    main_window._history_save_timer.start(200)  # 200ms delay
                
                control_panel.gradient_updated.connect(save_on_update)
                print("Connected gradient updates to history saving")
        
    except Exception as e:
        print(f"Error connecting gradient updates to history: {e}")


def get_undo_redo_status(main_window) -> dict:
    """
    Get the current status of the undo/redo system.
    
    Args:
        main_window: Main application window instance
        
    Returns:
        Dictionary with status information
    """
    try:
        status = {
            "integrated": False,
            "undo_available": False,
            "redo_available": False,
            "history_size": 0,
            "current_description": "Unknown"
        }
        
        if (hasattr(main_window, 'animated_preview') and 
            hasattr(main_window.animated_preview, 'history_manager')):
            
            history_manager = main_window.animated_preview.history_manager
            status.update({
                "integrated": True,
                "undo_available": history_manager.can_undo(),
                "redo_available": history_manager.can_redo(),
                "history_size": len(history_manager.history),
                "current_description": history_manager.get_current_state_description()
            })
        
        return status
        
    except Exception as e:
        print(f"Error getting undo/redo status: {e}")
        return {"error": str(e)}


# Auto-integration function for startup
def auto_integrate_undo_redo():
    """
    Automatically integrate undo/redo if conditions are met.
    This should be called from the main application startup.
    """
    try:
        app = QApplication.instance()
        if not app:
            return False
        
        # Find main window
        main_window = None
        for widget in app.topLevelWidgets():
            if widget.__class__.__name__ == 'MainWindow':
                main_window = widget
                break
        
        if main_window:
            # Set up undo/redo with proper timing
            setup_undo_redo_for_main_window(main_window)
            
            # Also set up gradient update connections
            QTimer.singleShot(3000, lambda: connect_gradient_updates_to_history(main_window))
            
            return True
        
        return False
        
    except Exception as e:
        print(f"Error in auto undo/redo integration: {e}")
        return False


def cleanup_undo_redo_system(main_window):
    """
    Clean up undo/redo system resources.
    
    Args:
        main_window: Main application window instance
    """
    try:
        # Stop timers
        if hasattr(main_window, '_undo_redo_timer'):
            main_window._undo_redo_timer.stop()
            delattr(main_window, '_undo_redo_timer')
        
        if hasattr(main_window, '_history_save_timer'):
            main_window._history_save_timer.stop()
            delattr(main_window, '_history_save_timer')
        
        # Clear history
        if (hasattr(main_window, 'animated_preview') and 
            hasattr(main_window.animated_preview, 'history_manager')):
            main_window.animated_preview.history_manager.clear_history()
        
        print("Undo/redo system cleaned up")
        
    except Exception as e:
        print(f"Error cleaning up undo/redo system: {e}")


# Testing and debugging functions
def test_undo_redo_system(main_window):
    """
    Test the undo/redo system functionality.
    
    Args:
        main_window: Main application window instance
    """
    try:
        print("Testing undo/redo system...")
        
        # Get status
        status = get_undo_redo_status(main_window)
        print(f"System status: {status}")
        
        if not status.get("integrated"):
            print("System not integrated - attempting integration...")
            success = integrate_undo_redo_system(main_window)
            print(f"Integration result: {success}")
            return success
        
        # Test history manager
        if (hasattr(main_window, 'animated_preview') and 
            hasattr(main_window.animated_preview, 'history_manager')):
            
            history_manager = main_window.animated_preview.history_manager
            gradient_model = main_window.current_gradient
            
            print(f"History size: {len(history_manager.history)}")
            print(f"Current index: {history_manager.current_index}")
            print(f"Can undo: {history_manager.can_undo()}")
            print(f"Can redo: {history_manager.can_redo()}")
            
            # Test saving a state
            print("Testing state save...")
            history_manager.save_state(gradient_model, force=True, description="Test state")
            
            print(f"After save - History size: {len(history_manager.history)}")
            print(f"Can undo: {history_manager.can_undo()}")
            
            return True
        
        return False
        
    except Exception as e:
        print(f"Error testing undo/redo system: {e}")
        return False


def debug_undo_redo_state(main_window):
    """
    Print detailed debug information about the undo/redo state.
    
    Args:
        main_window: Main application window instance
    """
    try:
        print("=== Undo/Redo Debug Information ===")
        
        # Check main window components
        print(f"Has animated_preview: {hasattr(main_window, 'animated_preview')}")
        print(f"Has undo_redo_widget: {hasattr(main_window, 'undo_redo_widget')}")
        print(f"Has current_gradient: {hasattr(main_window, 'current_gradient')}")
        
        if hasattr(main_window, 'animated_preview'):
            preview = main_window.animated_preview
            print(f"Preview has history_manager: {hasattr(preview, 'history_manager')}")
            
            if hasattr(preview, 'history_manager'):
                hm = preview.history_manager
                print(f"History manager info: {hm.get_history_info()}")
                print(f"History states: {len(hm.history)}")
                
                # Print recent history states
                if hm.history:
                    print("Recent states:")
                    for i, state in enumerate(hm.history[-5:]):  # Last 5 states
                        marker = " <-- CURRENT" if i + len(hm.history) - 5 == hm.current_index else ""
                        print(f"  {i + len(hm.history) - 5}: {state.description}{marker}")
        
        if hasattr(main_window, 'undo_redo_widget'):
            widget = main_window.undo_redo_widget
            state_info = widget.get_state_info()
            print(f"Widget state: {state_info}")
        
        print("=== End Debug Information ===")
        
    except Exception as e:
        print(f"Error in debug function: {e}")


# Export main integration function for easy import
__all__ = [
    'integrate_undo_redo_system',
    'setup_undo_redo_for_main_window', 
    'connect_gradient_updates_to_history',
    'get_undo_redo_status',
    'auto_integrate_undo_redo',
    'cleanup_undo_redo_system',
    'test_undo_redo_system',
    'debug_undo_redo_state'
]