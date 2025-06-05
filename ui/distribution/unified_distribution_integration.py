#!/usr/bin/env python3
"""
Updated Unified Distribution Integration Module for VIIBE Gradient Generator

This module integrates both mathematical and color distribution widgets
with the simplified preview system into the control panel.
"""
import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QLabel, QApplication,
                           QHBoxLayout, QPushButton, QComboBox, QFormLayout, 
                           QCheckBox, QColorDialog, QSlider, QSpinBox, QTabWidget)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QLinearGradient


def find_application_components():
    """Find the main application components."""
    try:
        app = QApplication.instance()
        if not app:
            return None, None, None
        
        # Find main window
        main_window = None
        for widget in app.topLevelWidgets():
            if widget.__class__.__name__ == 'MainWindow':
                main_window = widget
                break
        
        if not main_window:
            return None, None, None
        
        # Find control panel
        control_panel = getattr(main_window, 'control_panel', None)
        if not control_panel:
            return main_window, None, None
        
        # Find distribution tab or container
        distribution_container = None
        
        # Check if there's a tabs widget
        if hasattr(control_panel, 'tabs'):
            tabs = control_panel.tabs
            for i in range(tabs.count()):
                tab_text = tabs.tabText(i).lower()
                if 'distribution' in tab_text:
                    distribution_container = tabs.widget(i)
                    break
        
        # Alternative: check for distribution_widget attribute
        if not distribution_container and hasattr(control_panel, 'distribution_widget'):
            distribution_container = control_panel.distribution_widget
        
        return main_window, control_panel, distribution_container
    except Exception as e:
        print(f"Error finding application components: {e}")
        return None, None, None


def create_unified_distribution_widget(gradient_model):
    """Create a unified distribution widget with both mathematical and color distribution."""
    
    # Import the updated widgets
    try:
        from .distribution_widget import ColorStopDistributionWidget as MathDistributionWidget
        from .color_distribution_widget import ColorDistributionWidget as ColorDistributionWidget
        WIDGETS_AVAILABLE = True
    except ImportError:
        try:
            # Try importing from current directory
            import importlib.util
            
            # Math distribution widget
            math_spec = importlib.util.spec_from_file_location(
                "distribution_widget", 
                os.path.join(os.path.dirname(__file__), "distribution_widget.py")
            )
            math_module = importlib.util.module_from_spec(math_spec)
            math_spec.loader.exec_module(math_module)
            MathDistributionWidget = math_module.ColorStopDistributionWidget
            
            # Color distribution widget  
            color_spec = importlib.util.spec_from_file_location(
                "color_distribution_widget",
                os.path.join(os.path.dirname(__file__), "color_distribution_widget.py")
            )
            color_module = importlib.util.module_from_spec(color_spec)
            color_spec.loader.exec_module(color_module)
            ColorDistributionWidget = color_module.ColorDistributionWidget
            
            WIDGETS_AVAILABLE = True
        except Exception as e:
            print(f"Could not import distribution widgets: {e}")
            WIDGETS_AVAILABLE = False
    
    if not WIDGETS_AVAILABLE:
        # Create a placeholder widget
        placeholder = QWidget()
        layout = QVBoxLayout(placeholder)
        label = QLabel("Distribution widgets not available")
        label.setStyleSheet("color: #888; font-style: italic; text-align: center; padding: 20px;")
        layout.addWidget(label)
        return placeholder
    
    # Create the unified widget
    unified_widget = QWidget()
    layout = QVBoxLayout(unified_widget)
    layout.setContentsMargins(5, 5, 5, 5)
    
    # Create tab widget for the two distribution types
    tabs = QTabWidget()
    
    # Mathematical Distribution tab
    try:
        math_widget = MathDistributionWidget(gradient_model)
        tabs.addTab(math_widget, "Mathematical Patterns")
        print("✓ Added Mathematical Distribution widget")
    except Exception as e:
        print(f"Error creating mathematical distribution widget: {e}")
        # Add placeholder
        placeholder = QLabel(f"Mathematical distribution error: {e}")
        placeholder.setWordWrap(True)
        tabs.addTab(placeholder, "Mathematical Patterns")
    
    # Color Distribution tab
    try:
        color_widget = ColorDistributionWidget(gradient_model)
        tabs.addTab(color_widget, "Color-Based Reordering")
        print("✓ Added Color Distribution widget")
    except Exception as e:
        print(f"Error creating color distribution widget: {e}")
        # Add placeholder
        placeholder = QLabel(f"Color distribution error: {e}")
        placeholder.setWordWrap(True)
        tabs.addTab(placeholder, "Color-Based Reordering")
    
    layout.addWidget(tabs)
    
    # Store references to the widgets for external access
    unified_widget.math_distribution_widget = tabs.widget(0) if tabs.count() > 0 else None
    unified_widget.color_distribution_widget = tabs.widget(1) if tabs.count() > 1 else None
    unified_widget.tabs = tabs
    
    # Create a unified signal for distribution changes
    class UnifiedDistributionWidget(QWidget):
        distribution_changed = pyqtSignal()
    
    # Copy all attributes to the new class instance
    unified_widget.__class__ = UnifiedDistributionWidget
    unified_widget.distribution_changed = pyqtSignal()
    
    # Connect individual widget signals to unified signal
    for i in range(tabs.count()):
        widget = tabs.widget(i)
        if hasattr(widget, 'distribution_changed'):
            try:
                widget.distribution_changed.connect(unified_widget.distribution_changed.emit)
            except:
                pass  # Signal connection might fail, ignore
    
    # Add update method
    def update_from_model():
        """Update all distribution widgets when model changes."""
        for i in range(tabs.count()):
            widget = tabs.widget(i)
            if hasattr(widget, 'update_from_model'):
                try:
                    widget.update_from_model()
                except Exception as e:
                    print(f"Error updating widget {i}: {e}")
    
    unified_widget.update_from_model = update_from_model
    
    return unified_widget


def integrate_unified_distribution():
    """Integrate the unified distribution system with the application."""
    try:
        print("Starting unified distribution integration...")
        
        # Find application components
        main_window, control_panel, distribution_container = find_application_components()
        
        if not main_window:
            print("Main window not found")
            return False
        
        if not control_panel:
            print("Control panel not found")
            return False
        
        if not distribution_container:
            print("Distribution container not found")
            return False
        
        print("Found all required components")
        
        # Get gradient model
        gradient_model = getattr(main_window, 'current_gradient', None)
        if not gradient_model:
            gradient_model = getattr(control_panel, 'gradient_model', None)
        
        if not gradient_model:
            print("Gradient model not found")
            return False
        
        print("Found gradient model")
        
        # Check if already integrated
        if hasattr(distribution_container, 'unified_distribution_widget'):
            print("Unified distribution already integrated")
            return True
        
        # Create the unified widget
        try:
            unified_widget = create_unified_distribution_widget(gradient_model)
            print("Created unified distribution widget")
        except Exception as e:
            print(f"Failed to create unified widget: {e}")
            return False
        
        # Find the layout of the distribution container
        layout = distribution_container.layout()
        if not layout:
            layout = QVBoxLayout(distribution_container)
            print("Created new layout for distribution container")
        
        # Clear existing content and add unified widget
        try:
            # Remove existing widgets (except those we want to keep)
            items_to_remove = []
            for i in range(layout.count()):
                item = layout.itemAt(i)
                widget = item.widget()
                if widget and not hasattr(widget, 'keep_in_layout'):
                    items_to_remove.append(widget)
            
            for widget in items_to_remove:
                layout.removeWidget(widget)
                widget.deleteLater()
            
            # Add the unified widget
            layout.addWidget(unified_widget)
            print("Added unified widget to layout")
        except Exception as e:
            print(f"Error updating layout: {e}")
            return False
        
        # Connect signals if available
        if hasattr(control_panel, 'gradient_updated') and hasattr(unified_widget, 'distribution_changed'):
            try:
                unified_widget.distribution_changed.connect(
                    control_panel.gradient_updated.emit
                )
                print("Connected unified distribution signals")
            except Exception as e:
                print(f"Error connecting signals: {e}")
        
        # Store reference to prevent garbage collection
        distribution_container.unified_distribution_widget = unified_widget
        control_panel.unified_distribution_widget = unified_widget
        
        # Update the widget from the current model
        try:
            unified_widget.update_from_model()
        except Exception as e:
            print(f"Error updating from model: {e}")
        
        print("Unified distribution integration completed successfully")
        return True
        
    except Exception as e:
        print(f"Error during unified distribution integration: {e}")
        import traceback
        traceback.print_exc()
        return False


def delayed_integrate():
    """Integrate after a delay to ensure UI is ready."""
    def do_integration():
        try:
            success = integrate_unified_distribution()
            if success:
                print("✓ Unified distribution successfully integrated")
            else:
                print("✗ Unified distribution integration failed")
        except Exception as e:
            print(f"Delayed integration error: {e}")
    
    # Start with a 3-second delay
    QTimer.singleShot(3000, do_integration)


def check_integration_requirements():
    """Check if integration requirements are met."""
    try:
        app = QApplication.instance()
        if not app:
            return False, "No QApplication instance found"
        
        main_window, control_panel, distribution_container = find_application_components()
        
        if not main_window:
            return False, "Main window not found"
        if not control_panel:
            return False, "Control panel not found"
        if not distribution_container:
            return False, "Distribution container not found"
        
        gradient_model = getattr(main_window, 'current_gradient', None)
        if not gradient_model:
            gradient_model = getattr(control_panel, 'gradient_model', None)
        
        if not gradient_model:
            return False, "Gradient model not found"
        
        return True, "All requirements met"
        
    except Exception as e:
        return False, f"Error checking requirements: {e}"


def manual_integrate():
    """Manual integration function for testing."""
    try:
        success = integrate_unified_distribution()
        if success:
            print("✓ Manual unified integration successful")
            return True
        else:
            print("✗ Manual unified integration failed")
            return False
    except Exception as e:
        print(f"Manual integration error: {e}")
        return False


# Initialize integration when module is imported
def init_integration():
    """Initialize the integration process."""
    if __name__ == '__main__':
        return
    
    try:
        app = QApplication.instance()
        if app:
            delayed_integrate()
        else:
            print("No QApplication instance found - skipping auto-integration")
    except ImportError:
        print("PyQt5 not available - skipping auto-integration")
    except Exception as e:
        print(f"Integration initialization error: {e}")


# Auto-integrate when module is imported (unless running as main)
init_integration()


if __name__ == "__main__":
    # Test integration when run directly
    print("Testing unified distribution integration...")
    print("=" * 50)
    
    # Check requirements
    success, message = check_integration_requirements()
    print(f"Requirements check: {'✓' if success else '✗'} {message}")
    
    if success:
        result = manual_integrate()
        print(f"Integration test result: {'Success' if result else 'Failed'}")
    else:
        print("Cannot proceed with integration - requirements not met")
    
    print("\nUnified integration features:")
    print("• Combined mathematical and color distribution")
    print("• Simplified real-time preview system")
    print("• Tabbed interface for different distribution types")
    print("• Live preview with randomize positions feature")
    print("• Apply/Reset functionality")
    print("• Unified signal handling")