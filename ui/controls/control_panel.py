#!/usr/bin/env python3
"""
Refactored Control Panel Module for Gradient Generator

Streamlined implementation with reduced debug output and redundant code
while maintaining all features and functionality.

Tab order: Colors, Adjustments, Themes, Blend, Distribution, Seamless, Export
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QGroupBox, QLabel)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal

# Import core control widgets
from .color_stops import ColorStopsEditor
from .export_options import ExportOptionsWidget
from .seamless import SeamlessBlendingWidget
from .gradient_adjustments import GradientAdjustmentsWidget

# Import unified distribution system with fallback
try:
    from ..distribution import (
        UnifiedDistributionWidget, 
        ColorStopDistributionWidget, 
        ColorDistributionWidget,
        ensure_distribution_integration
    )
    UNIFIED_DISTRIBUTION_AVAILABLE = True
except ImportError:
    try:
        from ..distribution.distribution_widget import ColorStopDistributionWidget
        from ..distribution.color_distribution_widget import ColorDistributionWidget
        UNIFIED_DISTRIBUTION_AVAILABLE = False
    except ImportError:
        ColorStopDistributionWidget = None
        ColorDistributionWidget = None
        UNIFIED_DISTRIBUTION_AVAILABLE = False

# Import blending functionality with fallback
try:
    from ..gradient_blending.blending_integration import add_blending_tab
    BLENDING_AVAILABLE = True
except ImportError:
    try:
        from .gradient_blending.blending_integration import add_blending_tab
        BLENDING_AVAILABLE = True
    except ImportError:
        BLENDING_AVAILABLE = False

# Import theme generators with fallback
try:
    from ..theme_generators.theme_generator_integration import integrate_theme_generator
    THEMES_AVAILABLE = True
except ImportError:
    try:
        from .theme_generators.theme_generator_integration import integrate_theme_generator
        THEMES_AVAILABLE = True
    except ImportError:
        THEMES_AVAILABLE = False


class ControlPanel(QWidget):
    """Main control panel for the gradient generator with streamlined implementation."""
    
    gradient_updated = pyqtSignal()
    
    def __init__(self, gradient_model):
        super().__init__()
        
        self.gradient_model = gradient_model
        self.current_tab_index = 0
        
        self._init_ui()
        self._init_optional_tabs()
        
        # Auto-integrate distribution system if available
        if UNIFIED_DISTRIBUTION_AVAILABLE:
            self._auto_integrate_distribution()
        
        # Setup enhanced update chain after short delay
        QTimer.singleShot(1000, self._setup_enhanced_update_chain)
    
    def _init_ui(self):
        """Initialize the core UI components."""
        layout = QVBoxLayout(self)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self._on_tab_changed)
        
        # Core tabs in specified order
        self._add_core_tabs()
        
        layout.addWidget(self.tabs)
        layout.addStretch()
    
    def _add_core_tabs(self):
        """Add the core tabs: Colors, Adjustments, Themes, Blend, Distribution, Seamless, Export."""
        
        # 1. Colors tab
        self.color_stops_editor = ColorStopsEditor(self.gradient_model)
        self.color_stops_editor.stops_changed.connect(self.gradient_updated.emit)
        self.tabs.addTab(self.color_stops_editor, "Colors")
        
        # 2. Adjustments tab
        self.adjustments_widget = GradientAdjustmentsWidget(self.gradient_model)
        self.adjustments_widget.adjustments_changed.connect(self.gradient_updated.emit)
        self.tabs.addTab(self.adjustments_widget, "Adjustments")
        
        # 3. Themes tab (placeholder - populated by theme integration)
        self.themes_widget = self._create_placeholder("Themes", THEMES_AVAILABLE)
        self.tabs.addTab(self.themes_widget, "Themes")
        
        # 4. Blend tab (placeholder - populated by blending integration)  
        self.blend_widget = self._create_placeholder("Blend", BLENDING_AVAILABLE)
        self.tabs.addTab(self.blend_widget, "Blend")
        
        # 5. Distribution tab - unified system
        self.distribution_widget = self._create_distribution_tab()
        self.tabs.addTab(self.distribution_widget, "Distribution")
        
        # 6. Seamless tab
        self.seamless_widget = SeamlessBlendingWidget(self.gradient_model)
        self.seamless_widget.settings_changed.connect(self.gradient_updated.emit)
        self.tabs.addTab(self.seamless_widget, "Seamless")
        
        # 7. Export tab
        self.export_options = ExportOptionsWidget(self.gradient_model)
        self.export_options.options_changed.connect(self.gradient_updated.emit)
        self.tabs.addTab(self.export_options, "Export")
    
    def _create_placeholder(self, tab_name, is_available):
        """Create placeholder widget for optional tabs."""
        container = QWidget()
        layout = QVBoxLayout(container)
        
        if is_available:
            info_text = f"{tab_name} functionality is loading..."
            style_class = "loading"
        else:
            info_text = f"{tab_name} functionality will be loaded here automatically if available."
            style_class = "unavailable"
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet(self._get_placeholder_style(style_class))
        layout.addWidget(info_label)
        layout.addStretch()
        
        return container
    
    def _get_placeholder_style(self, style_class):
        """Get stylesheet for placeholder labels."""
        if style_class == "loading":
            return ("color: #4CAF50; font-style: italic; padding: 8px; "
                   "background-color: #1E3A1E; border-radius: 4px; margin: 5px;")
        else:
            return ("color: #888; font-style: italic; padding: 8px; "
                   "background-color: #333; border-radius: 4px; margin: 5px;")
    
    def _create_distribution_tab(self):
        """Create the unified distribution tab."""
        container = QWidget()
        layout = QVBoxLayout(container)
        
        if UNIFIED_DISTRIBUTION_AVAILABLE:
            try:
                self.unified_distribution_widget = UnifiedDistributionWidget(self.gradient_model)
                self._connect_distribution_signals(self.unified_distribution_widget)
                layout.addWidget(self.unified_distribution_widget)
                return container
            except Exception:
                pass  # Fall back to individual widgets
        
        # Create individual distribution widgets
        self._create_individual_distribution_widgets(layout)
        return container
    
    def _connect_distribution_signals(self, unified_widget):
        """Connect signals from unified distribution widget."""
        if hasattr(unified_widget, 'math_widget'):
            unified_widget.math_widget.distribution_changed.connect(self.gradient_updated.emit)
        
        if hasattr(unified_widget, 'color_widget'):
            unified_widget.color_widget.distribution_changed.connect(self.gradient_updated.emit)
    
    def _create_individual_distribution_widgets(self, layout):
        """Create individual distribution widgets when unified widget is not available."""
        # Mathematical Patterns Group
        if ColorStopDistributionWidget:
            try:
                math_group = QGroupBox("Mathematical Patterns")
                math_layout = QVBoxLayout(math_group)
                
                self.math_distribution_widget = ColorStopDistributionWidget(self.gradient_model)
                self.math_distribution_widget.distribution_changed.connect(self.gradient_updated.emit)
                math_layout.addWidget(self.math_distribution_widget)
                
                layout.addWidget(math_group)
            except Exception:
                self._add_error_label(layout, "Mathematical patterns unavailable")
        else:
            self._add_info_label(layout, "Mathematical pattern distribution not available")
        
        # Color-Based Reordering Group
        if ColorDistributionWidget:
            try:
                color_group = QGroupBox("Color-Based Reordering")
                color_layout = QVBoxLayout(color_group)
                
                self.color_distribution_widget = ColorDistributionWidget(self.gradient_model)
                self.color_distribution_widget.distribution_changed.connect(self.gradient_updated.emit)
                color_layout.addWidget(self.color_distribution_widget)
                
                layout.addWidget(color_group)
            except Exception:
                self._add_error_label(layout, "Color distribution unavailable")
        else:
            self._add_info_label(layout, "Color-based reordering not available")
        
        # Info section if both are available
        if ColorStopDistributionWidget and ColorDistributionWidget:
            info_text = (
                "💡 <b>Mathematical Patterns</b>: Distribute stops using algorithms<br/>"
                "💡 <b>Color-Based Reordering</b>: Reorder stops by color properties"
            )
            self._add_info_label(layout, info_text, rich_text=True)
        
        layout.addStretch()
    
    def _add_info_label(self, layout, text, rich_text=False):
        """Add an informational label to a layout."""
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(self._get_placeholder_style("unavailable"))
        if rich_text:
            label.setTextFormat(Qt.RichText)
        layout.addWidget(label)
    
    def _add_error_label(self, layout, text):
        """Add an error label to a layout."""
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(
            "color: #ff6666; font-style: italic; padding: 8px; "
            "background-color: #442222; border-radius: 4px; margin: 5px;"
        )
        layout.addWidget(label)
    
    def _init_optional_tabs(self):
        """Initialize optional tabs that may not be available."""
        # Theme generators - replace placeholder
        if THEMES_AVAILABLE:
            try:
                self._load_theme_generators()
            except Exception:
                pass  # Keep placeholder
        
        # Blending tab - replace placeholder
        if BLENDING_AVAILABLE:
            try:
                self._load_blending_functionality()
            except Exception:
                pass  # Keep placeholder
    
    def _load_theme_generators(self):
        """Load theme generators and replace placeholder."""
        themes_tab_index = self._find_tab_index("Themes")
        if themes_tab_index is None:
            return
        
        current_index = self.tabs.currentIndex()
        
        # Remove placeholder
        old_widget = self.tabs.widget(themes_tab_index)
        self.tabs.removeTab(themes_tab_index)
        if old_widget:
            old_widget.deleteLater()
        
        # Create theme generator widget
        from ..theme_generators.theme_generator_widget import ThemeGeneratorWidget
        
        theme_container = QWidget()
        theme_layout = QVBoxLayout(theme_container)
        theme_layout.setContentsMargins(0, 0, 0, 0)
        
        self.theme_generator_widget = ThemeGeneratorWidget(theme_container)
        theme_layout.addWidget(self.theme_generator_widget)
        
        # Connect signals
        self.theme_generator_widget.gradient_generated.connect(self._on_theme_gradient_generated)
        
        # Insert at the correct position
        self.tabs.insertTab(themes_tab_index, theme_container, "Themes")
        self.tabs.setCurrentIndex(current_index)
        
        # Ensure proper initialization
        QTimer.singleShot(300, self._ensure_theme_initialization)
    
    def _load_blending_functionality(self):
        """Load blending functionality and replace placeholder."""
        blend_tab_index = self._find_tab_index("Blend")
        if blend_tab_index is None:
            return
        
        current_index = self.tabs.currentIndex()
        
        # Remove placeholder
        old_widget = self.tabs.widget(blend_tab_index)
        self.tabs.removeTab(blend_tab_index)
        old_widget.deleteLater()
        
        # Create blending widget
        from ..gradient_blending.gradient_blending_ui import GradientBlendingWidget
        
        blend_container = QWidget()
        blend_layout = QVBoxLayout(blend_container)
        blend_layout.setContentsMargins(0, 0, 0, 0)
        
        self.blending_widget = GradientBlendingWidget(self.gradient_model)
        blend_layout.addWidget(self.blending_widget)
        
        # Connect signals
        self.blending_widget.gradient_blended.connect(self._on_gradient_blended)
        if hasattr(self.blending_widget, 'gradients_added'):
            self.blending_widget.gradients_added.connect(self._on_blending_gradients_added)
        
        # Insert at the correct position
        self.tabs.insertTab(blend_tab_index, blend_container, "Blend")
        self.tabs.setCurrentIndex(current_index)
    
    def _find_tab_index(self, tab_name):
        """Find tab index by name."""
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == tab_name:
                return i
        return None
    
    def _ensure_theme_initialization(self):
        """Ensure theme widget is properly initialized."""
        if not hasattr(self, 'theme_generator_widget'):
            return
        
        try:
            # Check if theme widget has been initialized
            if hasattr(self.theme_generator_widget, '_ui_initialized'):
                if not self.theme_generator_widget._ui_initialized:
                    QTimer.singleShot(500, self._ensure_theme_initialization)
                    return
            
            # Force initialization if needed
            if hasattr(self.theme_generator_widget, '_initialize_first_theme'):
                self.theme_generator_widget._initialize_first_theme()
            
            # Ensure we have a current theme and generator
            if not getattr(self.theme_generator_widget, 'current_theme', None):
                if (hasattr(self.theme_generator_widget, 'theme_generators') and 
                    self.theme_generator_widget.theme_generators):
                    
                    # Set first theme manually
                    first_theme = next(iter(self.theme_generator_widget.theme_generators))
                    self.theme_generator_widget.current_theme = first_theme
                    self.theme_generator_widget.current_generator = self.theme_generator_widget.theme_generators[first_theme]
                    
                    # Generate initial preview
                    if hasattr(self.theme_generator_widget, 'update_preview'):
                        QTimer.singleShot(100, self.theme_generator_widget.update_preview)
            
        except Exception:
            pass  # Silent handling for initialization issues
    
    def _auto_integrate_distribution(self):
        """Automatically integrate the distribution system."""
        try:
            from ..distribution import ensure_distribution_integration
            ensure_distribution_integration()
        except Exception:
            pass  # Silent handling
    
    def _on_tab_changed(self, index):
        """Handle tab change with proper widget updates."""
        self.current_tab_index = index
        current_tab_widget = self.tabs.widget(index)
        tab_text = self.tabs.tabText(index)
        
        # Update specific widgets when their tabs are selected
        if current_tab_widget == self.color_stops_editor:
            self.color_stops_editor.update_from_model()
        
        elif current_tab_widget == self.adjustments_widget:
            if hasattr(self.adjustments_widget, '_update_original_stops'):
                self.adjustments_widget._update_original_stops()
        
        elif current_tab_widget == self.distribution_widget:
            self._update_distribution_widgets()
        
        elif current_tab_widget == self.seamless_widget:
            self._update_seamless_widget()
        
        elif current_tab_widget == self.export_options:
            self.export_options.update_metadata_from_model()
            self.export_options.update_gradient_count()
        
        elif tab_text == "Themes" and hasattr(self, 'theme_generator_widget'):
            self._update_theme_widget()
        
        elif tab_text == "Blend" and hasattr(self, 'blending_widget'):
            if hasattr(self.blending_widget, 'update_from_model'):
                try:
                    self.blending_widget.update_from_model()
                except Exception:
                    pass
    
    def _update_seamless_widget(self):
        """Update seamless widget when tab is selected."""
        self.seamless_widget.seamless_check.setChecked(self.gradient_model.get_seamless_blend())
        self.seamless_widget.blend_region_spin.setValue(self.gradient_model.get_blend_region())
        self.seamless_widget.blend_region_spin.setEnabled(self.gradient_model.get_seamless_blend())
    
    def _update_theme_widget(self):
        """Update theme widget when tab is selected."""
        try:
            if hasattr(self.theme_generator_widget, 'update_from_model'):
                QTimer.singleShot(50, self.theme_generator_widget.update_from_model)
            
            if hasattr(self.theme_generator_widget, 'update_preview'):
                QTimer.singleShot(100, self.theme_generator_widget.update_preview)
        except Exception:
            pass
    
    def _update_distribution_widgets(self):
        """Update distribution widgets when their tab is selected."""
        try:
            # Update unified widget if available
            if hasattr(self, 'unified_distribution_widget'):
                if hasattr(self.unified_distribution_widget, 'update_from_model'):
                    self.unified_distribution_widget.update_from_model()
                
                # Update individual components within unified widget
                if hasattr(self.unified_distribution_widget, 'math_widget'):
                    if hasattr(self.unified_distribution_widget.math_widget, 'update_from_model'):
                        self.unified_distribution_widget.math_widget.update_from_model()
                
                if hasattr(self.unified_distribution_widget, 'color_widget'):
                    if hasattr(self.unified_distribution_widget.color_widget, 'update_from_model'):
                        self.unified_distribution_widget.color_widget.update_from_model()
            
            # Update individual widgets if they exist
            if hasattr(self, 'math_distribution_widget'):
                try:
                    self.math_distribution_widget.update_from_model()
                except Exception:
                    pass
            
            if hasattr(self, 'color_distribution_widget'):
                try:
                    self.color_distribution_widget.update_from_model()
                except Exception:
                    pass
                    
        except Exception:
            pass  # Silent handling for distribution updates
    
    def _on_theme_gradient_generated(self, gradient):
        """Handle a gradient generated by the theme generator."""
        try:
            # Copy the gradient to the main gradient model
            main_gradient = self.gradient_model
            
            # Clear existing stops
            main_gradient._color_stops = []
            
            # Copy color stops
            for stop in gradient.get_color_stop_objects():
                main_gradient.add_color_stop(stop.position, stop.color)
            
            # Copy metadata
            main_gradient.set_name(gradient.get_name())
            main_gradient.set_description(gradient.get_description())
            main_gradient.set_author(gradient.get_author())
            main_gradient.set_ugr_category(gradient.get_ugr_category())
            
            # Emit signal that gradient has been updated
            self.gradient_updated.emit()
            
            # Update all control widgets to reflect the new gradient
            self._update_all_widgets_for_theme_gradient()
            
        except Exception:
            pass  # Silent handling for theme gradient application
    
    def _update_all_widgets_for_theme_gradient(self):
        """Update all control widgets when a theme gradient is applied."""
        try:
            # Update color stops editor
            if hasattr(self, 'color_stops_editor'):
                QTimer.singleShot(100, self.color_stops_editor.update_from_model)
            
            # Update adjustments widget - reset to avoid conflicts
            if hasattr(self, 'adjustments_widget'):
                if hasattr(self.adjustments_widget, '_update_original_stops'):
                    QTimer.singleShot(150, self.adjustments_widget._update_original_stops)
                if hasattr(self.adjustments_widget, 'reset_adjustment_values'):
                    QTimer.singleShot(200, self.adjustments_widget.reset_adjustment_values)
            
            # Update seamless widget
            if hasattr(self, 'seamless_widget'):
                QTimer.singleShot(250, self._update_seamless_widget)
            
            # Update export options
            if hasattr(self, 'export_options'):
                QTimer.singleShot(300, self.export_options.update_metadata_from_model)
            
        except Exception:
            pass  # Silent handling for widget updates
    
    def _on_blending_gradients_added(self):
        """Handle when gradients are added to the blending widget."""
        if self.tabs.currentIndex() != self.current_tab_index:
            self.tabs.setCurrentIndex(self.current_tab_index)
    
    def _on_gradient_blended(self, blended_gradient):
        """Handle a blended gradient from the blend tab."""
        # Clear existing stops
        self.gradient_model._color_stops = []
        
        # Copy color stops
        for stop in blended_gradient.get_color_stop_objects():
            self.gradient_model.add_color_stop(stop.position, stop.color)
        
        # Copy metadata
        self.gradient_model.set_name(blended_gradient.get_name())
        
        # Update UI elements
        self.export_options.update_metadata_from_model()
        
        # Emit change signal
        self.gradient_updated.emit()
    
    def reset_controls(self):
        """Reset all controls to match the current gradient model."""
        # Update color stops
        self.color_stops_editor.update_from_model()
        
        # Update adjustments
        if hasattr(self.adjustments_widget, '_update_original_stops'):
            self.adjustments_widget._update_original_stops()
        if hasattr(self.adjustments_widget, 'reset_adjustments'):
            self.adjustments_widget.reset_adjustments()
        
        # Update distribution widgets
        self._update_distribution_widgets()
        
        # Update seamless settings
        self._update_seamless_widget()
        
        # Update export options
        self.export_options.update_metadata_from_model()
        self.export_options.update_gradient_count()
        
        # Update themes if available
        if hasattr(self, 'theme_generator_widget'):
            try:
                if hasattr(self.theme_generator_widget, 'reset_controls'):
                    self.theme_generator_widget.reset_controls()
                elif hasattr(self.theme_generator_widget, 'update_from_model'):
                    self.theme_generator_widget.update_from_model()
            except Exception:
                pass
        
        # Update blend if available
        if hasattr(self, 'blending_widget'):
            try:
                if hasattr(self.blending_widget, 'reset_controls'):
                    self.blending_widget.reset_controls()
                elif hasattr(self.blending_widget, 'update_blend_preview'):
                    self.blending_widget.update_blend_preview()
            except Exception:
                pass
    
    def _setup_enhanced_update_chain(self):
        """Set up enhanced update chain for animated preview integration."""
        try:
            # Find the main window and animated preview
            main_window = self.window()
            if not hasattr(main_window, 'animated_preview'):
                return False
            
            animated_preview = main_window.animated_preview
            
            # Connect distribution operations to force immediate updates
            if hasattr(self, 'color_stops_editor'):
                editor = self.color_stops_editor
                
                # Override distribute evenly to include preview updates
                if hasattr(editor, 'distribute_evenly_button'):
                    # Store original handler
                    original_distribute = editor.distribute_evenly
                    
                    def enhanced_distribute_evenly():
                        """Enhanced distribute evenly with immediate preview update."""
                        try:
                            # Call original distribution
                            original_distribute()
                            
                            # Force animated preview update
                            animated_preview.force_update_from_model(
                                skip_animation=True,
                                reason="Enhanced distribute evenly"
                            )
                            
                            # Validate consistency
                            QTimer.singleShot(100, lambda: 
                                animated_preview.validate_stop_consistency(verbose=False)
                            )
                            
                        except Exception:
                            pass  # Silent handling
                    
                    # Replace the method
                    editor.distribute_evenly = enhanced_distribute_evenly
            
            # Also connect other randomization buttons
            self._connect_randomization_buttons(animated_preview)
            
            return True
            
        except Exception:
            return False

    def _connect_randomization_buttons(self, animated_preview):
        """Connect randomization buttons to force preview updates."""
        try:
            if hasattr(self, 'color_stops_editor'):
                editor = self.color_stops_editor
                
                # List of methods that need enhanced updates
                methods_to_enhance = [
                    'randomize_positions',
                    'randomize_colors', 
                    'generate_random_gradient'
                ]
                
                for method_name in methods_to_enhance:
                    if hasattr(editor, method_name):
                        original_method = getattr(editor, method_name)
                        
                        def create_enhanced_method(orig_method, name):
                            def enhanced_method(*args, **kwargs):
                                try:
                                    # Call original method
                                    result = orig_method(*args, **kwargs)
                                    
                                    # Force preview update
                                    animated_preview.force_update_from_model(
                                        skip_animation=True,
                                        reason=f"Enhanced {name}"
                                    )
                                    
                                    return result
                                except Exception:
                                    return None
                            return enhanced_method
                        
                        # Replace the method
                        enhanced = create_enhanced_method(original_method, method_name)
                        setattr(editor, method_name, enhanced)
                        
        except Exception:
            pass  # Silent handling
    
    # Utility methods for debugging (streamlined)
    def get_distribution_capabilities(self):
        """Get information about available distribution capabilities."""
        capabilities = {
            'unified_available': UNIFIED_DISTRIBUTION_AVAILABLE,
            'math_available': ColorStopDistributionWidget is not None,
            'color_available': ColorDistributionWidget is not None,
            'blending_available': BLENDING_AVAILABLE,
            'themes_available': THEMES_AVAILABLE,
            'unified_created': hasattr(self, 'unified_distribution_widget'),
            'theme_widget_loaded': hasattr(self, 'theme_generator_widget'),
            'blend_widget_loaded': hasattr(self, 'blending_widget')
        }
        
        if hasattr(self, 'unified_distribution_widget'):
            capabilities['math_widget_available'] = hasattr(self.unified_distribution_widget, 'math_widget')
            capabilities['color_widget_available'] = hasattr(self.unified_distribution_widget, 'color_widget')
        else:
            capabilities['math_widget_available'] = hasattr(self, 'math_distribution_widget')
            capabilities['color_widget_available'] = hasattr(self, 'color_distribution_widget')
        
        return capabilities
    
    def force_distribution_update(self):
        """Force an update of all distribution widgets."""
        try:
            self._update_distribution_widgets()
            return True
        except Exception:
            return False
    
    def get_active_distribution_widget(self):
        """Get the currently active distribution widget."""
        if self.tabs.currentWidget() == self.distribution_widget:
            if hasattr(self, 'unified_distribution_widget'):
                return self.unified_distribution_widget
            elif hasattr(self, 'math_distribution_widget') or hasattr(self, 'color_distribution_widget'):
                return {
                    'math': getattr(self, 'math_distribution_widget', None),
                    'color': getattr(self, 'color_distribution_widget', None)
                }
        return None
    
    def get_theme_status(self):
        """Get detailed status of theme integration."""
        status = {
            'themes_available': THEMES_AVAILABLE,
            'theme_widget_exists': hasattr(self, 'theme_generator_widget'),
            'current_theme': None,
            'theme_count': 0,
            'available_themes': [],
            'tab_index': self._find_tab_index("Themes"),
            'errors': []
        }
        
        try:
            # Check theme widget
            if hasattr(self, 'theme_generator_widget'):
                widget = self.theme_generator_widget
                
                if hasattr(widget, 'theme_generators'):
                    status['theme_count'] = len(widget.theme_generators)
                    status['available_themes'] = list(widget.theme_generators.keys())
                
                if hasattr(widget, 'current_theme'):
                    status['current_theme'] = widget.current_theme
                
                if hasattr(widget, 'update_preview'):
                    status['preview_functional'] = callable(widget.update_preview)
                        
        except Exception as e:
            status['errors'].append(str(e))
        
        return status
    
    def force_theme_update(self):
        """Force an update of the theme widget."""
        try:
            if hasattr(self, 'theme_generator_widget'):
                widget = self.theme_generator_widget
                
                if hasattr(widget, 'update_from_model'):
                    widget.update_from_model()
                elif hasattr(widget, 'update_preview'):
                    widget.update_preview()
                
                return True
            else:
                return False
                
        except Exception:
            return False
    
    def debug_theme_integration(self):
        """Debug theme integration issues (streamlined)."""
        status = self.get_theme_status()
        debug_info = {
            'status': status,
            'themes_import_available': THEMES_AVAILABLE,
            'widget_details': {}
        }
        
        if hasattr(self, 'theme_generator_widget'):
            widget = self.theme_generator_widget
            debug_info['widget_details'] = {
                'class_name': widget.__class__.__name__,
                'has_theme_generators': hasattr(widget, 'theme_generators'),
                'ui_initialized': getattr(widget, '_ui_initialized', False)
            }
            
            if hasattr(widget, 'theme_generators'):
                debug_info['widget_details']['themes'] = {
                    name: generator.__class__.__name__ 
                    for name, generator in widget.theme_generators.items()
                }
        
        return debug_info
    
    # Enhanced public interface methods
    def get_current_tab_name(self):
        """Get the name of the currently selected tab."""
        return self.tabs.tabText(self.tabs.currentIndex())
    
    def switch_to_tab(self, tab_name):
        """Switch to a specific tab by name."""
        tab_index = self._find_tab_index(tab_name)
        if tab_index is not None:
            self.tabs.setCurrentIndex(tab_index)
            return True
        return False
    
    def get_tab_widget(self, tab_name):
        """Get widget for a specific tab by name."""
        tab_index = self._find_tab_index(tab_name)
        if tab_index is not None:
            return self.tabs.widget(tab_index)
        return None
    
    def is_tab_available(self, tab_name):
        """Check if a specific tab is available and functional."""
        widget = self.get_tab_widget(tab_name)
        if not widget:
            return False
        
        # Check if it's a placeholder
        if isinstance(widget, QWidget) and widget.layout():
            layout = widget.layout()
            if layout.count() == 2:  # Placeholder has label + stretch
                first_item = layout.itemAt(0)
                if first_item and isinstance(first_item.widget(), QLabel):
                    return False
        
        return True
    
    def get_available_tabs(self):
        """Get list of available and functional tabs."""
        available_tabs = []
        for i in range(self.tabs.count()):
            tab_name = self.tabs.tabText(i)
            if self.is_tab_available(tab_name):
                available_tabs.append(tab_name)
        return available_tabs
    
    def refresh_all_widgets(self):
        """Refresh all widgets to match current gradient model."""
        current_tab = self.tabs.currentIndex()
        
        # Force update all tabs
        for i in range(self.tabs.count()):
            self.tabs.setCurrentIndex(i)
            self._on_tab_changed(i)
        
        # Return to original tab
        self.tabs.setCurrentIndex(current_tab)
    
    def get_widget_status(self):
        """Get comprehensive status of all widgets."""
        return {
            'current_tab': self.get_current_tab_name(),
            'available_tabs': self.get_available_tabs(),
            'distribution_capabilities': self.get_distribution_capabilities(),
            'theme_status': self.get_theme_status(),
            'total_tabs': self.tabs.count(),
            'features': {
                'themes': THEMES_AVAILABLE,
                'blending': BLENDING_AVAILABLE,
                'unified_distribution': UNIFIED_DISTRIBUTION_AVAILABLE,
                'math_distribution': ColorStopDistributionWidget is not None,
                'color_distribution': ColorDistributionWidget is not None
            }
        }
    
    def export_settings(self):
        """Export current settings from all widgets."""
        settings = {
            'current_tab': self.get_current_tab_name(),
            'gradient_metadata': {
                'name': self.gradient_model.get_name(),
                'author': self.gradient_model.get_author(),
                'description': self.gradient_model.get_description(),
                'ugr_category': self.gradient_model.get_ugr_category(),
                'seamless_blend': self.gradient_model.get_seamless_blend()
            }
        }
        
        # Export adjustment settings if available
        if hasattr(self.adjustments_widget, 'get_adjustment_values'):
            try:
                settings['adjustments'] = self.adjustments_widget.get_adjustment_values()
            except Exception:
                pass
        
        # Export theme settings if available
        if hasattr(self, 'theme_generator_widget'):
            try:
                if hasattr(self.theme_generator_widget, 'current_theme'):
                    settings['current_theme'] = self.theme_generator_widget.current_theme
            except Exception:
                pass
        
        return settings
    
    def import_settings(self, settings):
        """Import settings to all widgets."""
        if not isinstance(settings, dict):
            return False
        
        try:
            # Import gradient metadata
            if 'gradient_metadata' in settings:
                metadata = settings['gradient_metadata']
                for key, value in metadata.items():
                    if hasattr(self.gradient_model, f'set_{key}'):
                        try:
                            getattr(self.gradient_model, f'set_{key}')(value)
                        except Exception:
                            pass
            
            # Import adjustment settings
            if 'adjustments' in settings and hasattr(self.adjustments_widget, 'set_adjustment_values'):
                try:
                    self.adjustments_widget.set_adjustment_values(settings['adjustments'])
                except Exception:
                    pass
            
            # Switch to specified tab
            if 'current_tab' in settings:
                self.switch_to_tab(settings['current_tab'])
            
            # Refresh all widgets
            self.refresh_all_widgets()
            
            return True
            
        except Exception:
            return False
    
    def cleanup(self):
        """Clean up resources and stop any running timers."""
        try:
            # Stop any timers
            for child in self.findChildren(QTimer):
                if child.isActive():
                    child.stop()
            
            # Cleanup individual widgets
            widgets_to_cleanup = [
                'color_stops_editor', 'adjustments_widget', 'seamless_widget',
                'export_options', 'theme_generator_widget', 'blending_widget',
                'unified_distribution_widget', 'math_distribution_widget',
                'color_distribution_widget'
            ]
            
            for widget_name in widgets_to_cleanup:
                if hasattr(self, widget_name):
                    widget = getattr(self, widget_name)
                    if hasattr(widget, 'cleanup'):
                        try:
                            widget.cleanup()
                        except Exception:
                            pass
            
        except Exception:
            pass  # Silent cleanup