#!/usr/bin/env python3
"""
FIXED Theme Generator Integration Module for Gradient Generator

This module integrates the theme-based gradient generators with the main application
with proper signal handling and preview initialization.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer

# Import the theme generator widget
try:
    from theme_generator_widget import ThemeGeneratorWidget
except ImportError:
    try:
        from gradient_generator.ui.theme_generators.theme_generator_widget import ThemeGeneratorWidget
    except ImportError:
        import sys, os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
        from gradient_generator.ui.theme_generators.theme_generator_widget import ThemeGeneratorWidget


def integrate_theme_generator(control_panel):
    """
    FIXED: Integrates the theme generator into the control panel with proper initialization.
    
    Args:
        control_panel: ControlPanel instance to integrate with
    
    Returns:
        True if integration was successful, False otherwise
    """
    try:
        # Create container widget for the theme generator
        container = QWidget(control_panel)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the theme generator widget (now includes Metal & Stone)
        theme_generator = ThemeGeneratorWidget(container)
        layout.addWidget(theme_generator)
        
        # FIXED: Properly connect the gradient generated signal
        theme_generator.gradient_generated.connect(
            lambda gradient: on_theme_gradient_generated(control_panel, gradient)
        )
        
        # Add the container widget to the tab widget
        # Find the correct position for the Themes tab (should be after Adjustments)
        themes_tab_index = None
        for i in range(control_panel.tabs.count()):
            tab_text = control_panel.tabs.tabText(i)
            if tab_text == "Themes":
                # Replace existing themes tab
                old_widget = control_panel.tabs.widget(i)
                control_panel.tabs.removeTab(i)
                if old_widget:
                    old_widget.deleteLater()
                themes_tab_index = control_panel.tabs.insertTab(i, container, "Themes")
                break
        
        if themes_tab_index is None:
            # Add new themes tab in the correct position (after Adjustments, before Blend)
            insert_position = 2  # Default position
            for i in range(control_panel.tabs.count()):
                if control_panel.tabs.tabText(i) == "Adjustments":
                    insert_position = i + 1
                    break
            themes_tab_index = control_panel.tabs.insertTab(insert_position, container, "Themes")
        
        # Store references to prevent garbage collection
        if not hasattr(control_panel, '_theme_generators'):
            control_panel._theme_generators = {}
        
        # Store references with tab index as key
        control_panel._theme_generators[themes_tab_index] = {
            'container': container,
            'generator': theme_generator,
            'layout': layout
        }
        
        # FIXED: Set up proper tab change handling for theme updates
        def on_themes_tab_selected():
            """Handle when themes tab is selected to ensure proper preview."""
            try:
                if hasattr(theme_generator, 'update_from_model'):
                    # Small delay to ensure tab is fully visible
                    QTimer.singleShot(100, theme_generator.update_from_model)
                else:
                    # Fallback: force preview update
                    QTimer.singleShot(100, lambda: theme_generator.update_preview())
            except Exception as e:
                print(f"Error updating theme generator when tab selected: {e}")
        
        # Connect tab change signal to handle theme updates
        original_tab_changed = getattr(control_panel, 'on_tab_changed', None)
        
        def enhanced_tab_changed(index):
            """Enhanced tab changed handler that includes theme handling."""
            try:
                # Call original handler if it exists
                if original_tab_changed and callable(original_tab_changed):
                    original_tab_changed(index)
                
                # Check if themes tab was selected
                if index == themes_tab_index:
                    QTimer.singleShot(50, on_themes_tab_selected)
                    
            except Exception as e:
                print(f"Error in enhanced tab changed handler: {e}")
        
        # Replace the tab changed handler
        control_panel.on_tab_changed = enhanced_tab_changed
        
        # Also connect to the QTabWidget signal directly
        if hasattr(control_panel, 'tabs'):
            try:
                # Disconnect existing connections to avoid duplicates
                control_panel.tabs.currentChanged.disconnect()
            except:
                pass  # No existing connections
            
            # Connect our enhanced handler
            control_panel.tabs.currentChanged.connect(enhanced_tab_changed)
        
        print(f"✓ Theme generator integrated successfully with {len(theme_generator.theme_generators)} themes")
        if hasattr(theme_generator, 'theme_generators') and 'metal_stone' in theme_generator.theme_generators:
            print("✓ Metal & Stone theme generator loaded successfully")
        
        # FIXED: Initialize the theme generator properly
        def delayed_initialization():
            """Perform delayed initialization to ensure proper theme setup."""
            try:
                # Force the theme generator to initialize its first theme properly
                if hasattr(theme_generator, '_initialize_first_theme'):
                    theme_generator._initialize_first_theme()
                elif hasattr(theme_generator, 'update_preview'):
                    # Fallback: just try to update preview
                    theme_generator.update_preview()
                
                # Additional check: ensure we have a current theme set
                if not getattr(theme_generator, 'current_theme', None):
                    print("Warning: No current theme set after initialization")
                    # Try to set first available theme
                    if hasattr(theme_generator, 'theme_generators') and theme_generator.theme_generators:
                        first_theme = next(iter(theme_generator.theme_generators))
                        theme_generator.current_theme = first_theme
                        theme_generator.current_generator = theme_generator.theme_generators[first_theme]
                        print(f"Set fallback theme: {first_theme}")
                        
                        # Generate initial gradient
                        if hasattr(theme_generator, 'update_preview'):
                            theme_generator.update_preview()
                
                print("✓ Theme generator initialization completed")
            except Exception as e:
                print(f"Warning: Theme generator delayed initialization failed: {e}")
        
        # Schedule delayed initialization with longer delay to ensure everything is ready
        QTimer.singleShot(800, delayed_initialization)
        
        return True
        
    except Exception as e:
        print(f"Error integrating theme generator: {e}")
        import traceback
        traceback.print_exc()
        return False


def on_theme_gradient_generated(control_panel, gradient):
    """
    FIXED: Handle a gradient generated by the theme generator with proper error handling.
    
    Args:
        control_panel: ControlPanel instance
        gradient: Generated gradient (includes Metal & Stone gradients)
    """
    try:
        if not gradient:
            print("Warning: No gradient provided to on_theme_gradient_generated")
            return
        
        print(f"Applying theme gradient: {gradient.get_name()}")
        
        # Get the main gradient model
        main_gradient = control_panel.gradient_model
        if not main_gradient:
            print("Error: No gradient model found in control panel")
            return
        
        # Clear existing stops
        main_gradient._color_stops = []
        
        # Copy color stops with error handling
        try:
            for stop in gradient.get_color_stop_objects():
                main_gradient.add_color_stop(stop.position, stop.color)
        except Exception as e:
            print(f"Error copying color stops: {e}")
            # Fallback: try to get stops as tuples
            try:
                for position, color in gradient.get_color_stops():
                    main_gradient.add_color_stop(position, color)
            except Exception as e2:
                print(f"Error with fallback color stop copying: {e2}")
                return
        
        # Copy metadata safely
        try:
            main_gradient.set_name(gradient.get_name())
            main_gradient.set_description(gradient.get_description())
            main_gradient.set_author(gradient.get_author())
            main_gradient.set_ugr_category(gradient.get_ugr_category())
        except Exception as e:
            print(f"Warning: Could not copy all metadata: {e}")
            # At minimum, try to set the name
            try:
                main_gradient.set_name(gradient.get_name() or "Theme Gradient")
            except:
                pass
        
        # Emit signal that gradient has been updated
        if hasattr(control_panel, 'gradient_updated'):
            control_panel.gradient_updated.emit()
        
        # Update other UI components
        try:
            # Update control panel widgets to reflect the new gradient
            if hasattr(control_panel, 'reset_controls'):
                # Small delay to let the gradient update propagate
                QTimer.singleShot(100, control_panel.reset_controls)
        except Exception as e:
            print(f"Warning: Could not update control panel widgets: {e}")
        
        # Log successful application
        theme_name = gradient.get_name()
        if "Metal" in theme_name or "Stone" in theme_name:
            print(f"✓ Applied Metal & Stone gradient: {theme_name}")
        else:
            print(f"✓ Applied theme gradient: {theme_name}")
        
    except Exception as e:
        print(f"Error applying theme gradient: {e}")
        import traceback
        traceback.print_exc()


def add_theme_generator_tab(control_panel):
    """
    Manually add the theme generator tab to an existing control panel.
    
    Args:
        control_panel: ControlPanel instance
        
    Returns:
        The theme generator widget or None if failed
    """
    success = integrate_theme_generator(control_panel)
    if success and hasattr(control_panel, '_theme_generators'):
        # Return the most recently added generator
        if control_panel._theme_generators:
            last_index = max(control_panel._theme_generators.keys())
            return control_panel._theme_generators[last_index]['generator']
    return None


def verify_theme_integration(control_panel):
    """
    FIXED: Verify that theme integration was successful and Metal & Stone is available.
    
    Args:
        control_panel: ControlPanel instance
        
    Returns:
        Dictionary with integration status
    """
    status = {
        'integrated': False,
        'theme_count': 0,
        'metal_stone_available': False,
        'available_themes': [],
        'current_theme': None,
        'preview_working': False,
        'errors': []
    }
    
    try:
        if hasattr(control_panel, '_theme_generators') and control_panel._theme_generators:
            status['integrated'] = True
            
            # Get the theme generator widget
            theme_gen_data = list(control_panel._theme_generators.values())[0]
            theme_widget = theme_gen_data['generator']
            
            if hasattr(theme_widget, 'theme_generators'):
                status['theme_count'] = len(theme_widget.theme_generators)
                status['available_themes'] = list(theme_widget.theme_generators.keys())
                status['metal_stone_available'] = 'metal_stone' in theme_widget.theme_generators
                status['current_theme'] = getattr(theme_widget, 'current_theme', None)
                
                # Test if preview is working
                try:
                    if theme_widget.current_generator and hasattr(theme_widget, 'update_preview'):
                        status['preview_working'] = True
                except Exception as e:
                    status['errors'].append(f"Preview test failed: {str(e)}")
                
                # Check if old metals theme is still present (should not be)
                if 'metals' in theme_widget.theme_generators:
                    status['errors'].append("Old metals theme still present - should be replaced by metal_stone")
                
            else:
                status['errors'].append("Theme generators not properly initialized")
        else:
            status['errors'].append("Theme generators not integrated into control panel")
            
    except Exception as e:
        status['errors'].append(f"Error during verification: {str(e)}")
    
    return status


def get_metal_stone_materials():
    """
    Get the list of available Metal & Stone materials.
    
    Returns:
        List of material names or None if not available
    """
    try:
        from .metal_stone_theme import MetalAndStoneThemeGenerator
        generator = MetalAndStoneThemeGenerator()
        
        if hasattr(generator, 'MATERIAL_TYPE_NAMES'):
            return generator.MATERIAL_TYPE_NAMES
        else:
            return None
            
    except ImportError:
        return None


def create_metal_stone_gradient(material_type, **kwargs):
    """
    Create a Metal & Stone gradient with specific parameters.
    
    Args:
        material_type: Material type index or name
        **kwargs: Additional parameters for the generator
        
    Returns:
        Generated gradient or None if failed
    """
    try:
        from .metal_stone_theme import MetalAndStoneThemeGenerator
        generator = MetalAndStoneThemeGenerator()
        
        # Set material type
        if isinstance(material_type, str):
            # Convert name to index
            if hasattr(generator, 'MATERIAL_TYPE_NAMES'):
                try:
                    material_index = generator.MATERIAL_TYPE_NAMES.index(material_type)
                    generator.set_parameter_value('material_type', float(material_index))
                except ValueError:
                    print(f"Warning: Unknown material type '{material_type}'")
        else:
            generator.set_parameter_value('material_type', float(material_type))
        
        # Set additional parameters
        for param_name, value in kwargs.items():
            if generator.get_parameter(param_name):
                generator.set_parameter_value(param_name, value)
        
        # Generate and return gradient
        return generator.generate_gradient()
        
    except ImportError:
        print("Metal & Stone theme generator not available")
        return None
    except Exception as e:
        print(f"Error creating Metal & Stone gradient: {e}")
        return None


def debug_theme_integration(control_panel):
    """
    Debug function to check theme integration status and provide detailed information.
    
    Args:
        control_panel: ControlPanel instance
        
    Returns:
        Detailed debug information
    """
    debug_info = {
        'control_panel_has_tabs': hasattr(control_panel, 'tabs'),
        'themes_tab_exists': False,
        'themes_tab_index': None,
        'theme_generators_attr': hasattr(control_panel, '_theme_generators'),
        'tab_count': 0,
        'tab_names': [],
        'theme_widget_details': {},
        'errors': []
    }
    
    try:
        # Check basic control panel structure
        if hasattr(control_panel, 'tabs'):
            debug_info['tab_count'] = control_panel.tabs.count()
            debug_info['tab_names'] = [control_panel.tabs.tabText(i) for i in range(control_panel.tabs.count())]
            
            # Look for Themes tab
            for i in range(control_panel.tabs.count()):
                if control_panel.tabs.tabText(i) == "Themes":
                    debug_info['themes_tab_exists'] = True
                    debug_info['themes_tab_index'] = i
                    break
        
        # Check theme generators
        if hasattr(control_panel, '_theme_generators'):
            for key, value in control_panel._theme_generators.items():
                theme_widget = value.get('generator')
                if theme_widget:
                    debug_info['theme_widget_details'][key] = {
                        'has_theme_generators': hasattr(theme_widget, 'theme_generators'),
                        'current_theme': getattr(theme_widget, 'current_theme', None),
                        'current_generator': getattr(theme_widget, 'current_generator', None) is not None,
                        'ui_initialized': getattr(theme_widget, '_ui_initialized', False),
                        'theme_count': len(getattr(theme_widget, 'theme_generators', {}))
                    }
                    
                    if hasattr(theme_widget, 'theme_generators'):
                        debug_info['theme_widget_details'][key]['available_themes'] = list(theme_widget.theme_generators.keys())
        
    except Exception as e:
        debug_info['errors'].append(f"Debug error: {str(e)}")
    
    return debug_info


# Legacy function name mapping for backward compatibility
def add_metals_theme_tab(control_panel):
    """
    Legacy function - redirects to Metal & Stone theme.
    
    Args:
        control_panel: ControlPanel instance
        
    Returns:
        The theme generator widget
    """
    print("Warning: add_metals_theme_tab is deprecated, use add_theme_generator_tab instead")
    return add_theme_generator_tab(control_panel)