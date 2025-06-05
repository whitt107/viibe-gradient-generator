#!/usr/bin/env python3
"""
Refactored Theme Generator Widget Module for Gradient Generator

Streamlined implementation with responsive leaf integration, reduced debug code,
and enhanced signal connections for immediate preview updates.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QComboBox, QDoubleSpinBox, QGroupBox, 
                            QFormLayout, QSplitter, QMessageBox, QSlider,
                            QScrollArea, QTabWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QColor, QLinearGradient
import random
import sys
import os
import importlib
import importlib.util


class ThemePreviewWidget(QWidget):
    """Widget for displaying a live preview of a theme-generated gradient."""
    
    def __init__(self, gradient, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 100)
        self.setStyleSheet("border: 1px solid #555;")
        self.gradient = gradient

    def set_gradient(self, gradient):
        """Set the gradient to preview."""
        self.gradient = gradient
        self.update()

    def paintEvent(self, event):
        """Override paintEvent to draw the gradient preview."""
        super().paintEvent(event)
        
        if self.gradient is None:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill with dark background
        painter.fillRect(self.rect(), QColor("#333"))
        
        # Create linear gradient
        qgradient = QLinearGradient(0, 0, self.width(), 0)
        
        # Add color stops
        for position, color in self.gradient.get_color_stops():
            qgradient.setColorAt(position, QColor(*color))
        
        # Draw gradient
        painter.fillRect(self.rect(), qgradient)
        
        # Draw border
        painter.setPen(QColor(85, 85, 85))
        painter.drawRect(0, 0, self.width()-1, self.height()-1)
        
        painter.end()


class ThemeControlsWidget(QWidget):
    """Widget for theme-specific controls with enhanced responsiveness."""
    
    parameter_changed = pyqtSignal(str, float)
    
    def __init__(self, theme_generator, parent=None):
        super().__init__(parent)
        self.theme_generator = theme_generator
        self.controls = {}
        self.value_labels = {}
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components with enhanced signal connections."""
        layout = QFormLayout(self)
        layout.setSpacing(8)
        
        # Create controls for each parameter
        for param in self.theme_generator.get_parameter_list():
            # Check if this is a type parameter that should use a dropdown
            is_type_param = param.name.endswith("_type")
            type_names_attr = f"{param.name.upper()[:-5]}_TYPE_NAMES"
            
            if is_type_param and hasattr(self.theme_generator, type_names_attr):
                # Create dropdown for type selection parameters
                dropdown = QComboBox()
                dropdown.addItems(getattr(self.theme_generator, type_names_attr))
                dropdown.setCurrentIndex(int(param.value))
                dropdown.setToolTip(param.description)
                
                dropdown.currentIndexChanged.connect(
                    lambda idx, name=param.name: self._on_dropdown_changed(name, idx)
                )
                
                layout.addRow(f"{param.label}:", dropdown)
                self.controls[param.name] = dropdown
                
            # For discrete parameters (integer steps), use a slider with integer labels
            elif param.step >= 1.0:
                param_layout = QHBoxLayout()
                
                slider = QSlider(Qt.Horizontal)
                slider.setRange(int(param.min_value), int(param.max_value))
                slider.setValue(int(param.value))
                slider.setSingleStep(int(param.step))
                slider.setTickPosition(QSlider.TicksBelow)
                slider.setTickInterval(max(1, int((param.max_value - param.min_value) // 5)))
                slider.setToolTip(param.description)
                
                # Enhanced: Connect both signals for immediate responsiveness
                slider.valueChanged.connect(
                    lambda value, name=param.name: self._on_slider_changed(name, value)
                )
                slider.sliderMoved.connect(
                    lambda value, name=param.name: self._on_slider_changed(name, value)
                )
                
                param_layout.addWidget(slider)
                
                # Add value label
                value_label = QLabel(f"{int(param.value)}")
                value_label.setFixedWidth(30)
                value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                param_layout.addWidget(value_label)
                
                self.controls[param.name] = slider
                self.value_labels[param.name] = value_label
                
                layout.addRow(f"{param.label}:", param_layout)
            else:
                # Continuous parameter - use slider with float labels
                slider = QSlider(Qt.Horizontal)
                
                # Scale to 0-100 range for integer slider
                min_val_int = int(param.min_value * 100)
                max_val_int = int(param.max_value * 100)
                value_int = int(param.value * 100)
                step_int = max(1, int(param.step * 100))
                
                slider.setRange(min_val_int, max_val_int)
                slider.setValue(value_int)
                slider.setSingleStep(step_int)
                slider.setTickPosition(QSlider.TicksBelow)
                slider.setTickInterval(max(1, (max_val_int - min_val_int) // 5))
                slider.setToolTip(param.description)
                
                # Enhanced: Connect both signals for immediate responsiveness
                slider.valueChanged.connect(
                    lambda value, name=param.name: self._on_slider_changed(name, value)
                )
                slider.sliderMoved.connect(
                    lambda value, name=param.name: self._on_slider_changed(name, value)
                )
                
                param_layout = QHBoxLayout()
                param_layout.addWidget(slider)
                
                value_label = QLabel(f"{param.value:.2f}")
                value_label.setFixedWidth(50)
                value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                param_layout.addWidget(value_label)
                
                self.controls[param.name] = slider
                self.value_labels[param.name] = value_label
                
                layout.addRow(f"{param.label}:", param_layout)

    def _on_slider_changed(self, param_name, value_int):
        """Handle slider value change with immediate parameter updates."""
        param = self.theme_generator.get_parameter(param_name)
        
        # Convert to parameter range
        if param.step >= 1.0:
            value = float(value_int)
            if param_name in self.value_labels:
                self.value_labels[param_name].setText(f"{int(value)}")
        else:
            value = value_int / 100.0
            if param_name in self.value_labels:
                self.value_labels[param_name].setText(f"{value:.2f}")
        
        # Emit immediately for responsive updates
        self.parameter_changed.emit(param_name, value)

    def _on_dropdown_changed(self, param_name, index):
        """Handle dropdown value change."""
        self.parameter_changed.emit(param_name, float(index))

    def update_from_generator(self):
        """Update control values from the theme generator."""
        for name, control in self.controls.items():
            param = self.theme_generator.get_parameter(name)
            if not param:
                continue
                
            if isinstance(control, QSlider):
                if param.step >= 1.0:
                    value_int = int(param.value)
                else:
                    value_int = int(param.value * 100)
                
                control.blockSignals(True)
                control.setValue(value_int)
                control.blockSignals(False)
                
                if name in self.value_labels:
                    value_label = self.value_labels[name]
                    if param.step >= 1.0:
                        value_label.setText(f"{int(param.value)}")
                    else:
                        value_label.setText(f"{param.value:.2f}")
            
            elif isinstance(control, QComboBox):
                index = int(param.value)
                if 0 <= index < control.count():
                    control.blockSignals(True)
                    control.setCurrentIndex(index)
                    control.blockSignals(False)

    def reset_controls(self):
        """Reset all controls to their default values."""
        for param in self.theme_generator.get_parameter_list():
            param.reset()
            
            if param.name in self.controls:
                control = self.controls[param.name]
                
                if isinstance(control, QSlider):
                    if param.step >= 1.0:
                        value = int(param.default_value)
                    else:
                        value = int(param.default_value * 100)
                    
                    control.blockSignals(True)
                    control.setValue(value)
                    control.blockSignals(False)
                    
                    if param.name in self.value_labels:
                        value_label = self.value_labels[param.name]
                        if param.step >= 1.0:
                            value_label.setText(f"{int(param.default_value)}")
                        else:
                            value_label.setText(f"{param.default_value:.2f}")
                
                elif isinstance(control, QComboBox):
                    index = int(param.default_value)
                    if 0 <= index < control.count():
                        control.blockSignals(True)
                        control.setCurrentIndex(index)
                        control.blockSignals(False)


class ThemeGeneratorWidget(QWidget):
    """Main widget for the theme-based gradient generator with streamlined implementation."""
    
    gradient_generated = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Import theme generators
        self.theme_generators = self._import_theme_generators()
        
        # Initialize theme state
        self.current_theme = None
        self.current_generator = None
        self.current_gradient = None
        
        # Preview update management
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self._update_preview_delayed)
        
        # Track initialization state
        self._ui_initialized = False
        
        self.init_ui()
        self._initialize_first_theme()

    def _import_theme_generators(self):
        """Import all available theme generators with streamlined error handling."""
        generators = {}
        
        current_dir = os.path.dirname(__file__)
        package_name = "gradient_generator.ui.theme_generators"
        
        # Core theme generators
        core_generators = [
            ("foliage_theme", "FoliageThemeGenerator", "foliage"),
            ("flower_theme", "FlowerThemeGenerator", "flowers"), 
            ("cosmic_theme", "CosmicThemeGenerator", "cosmic"),
            ("fire_theme", "FireThemeGenerator", "fire"),
            ("mood_theme", "MoodThemeGenerator", "mood"),
            ("metal_stone_theme", "MetalAndStoneThemeGenerator", "metal_stone")
        ]
        
        # Optional generators
        optional_generators = [
            ("sky_theme", "SkyThemeGenerator", "sky"),
            ("artistic_style_theme", "ArtisticStyleThemeGenerator", "artistic"),
            ("holiday_theme", "HolidayThemeGenerator", "holidays")
        ]
        
        # Load core generators
        for module_name, class_name, key in core_generators:
            try:
                generator_class = self._import_generator_class(module_name, class_name, package_name)
                if generator_class:
                    generators[key] = generator_class()
            except Exception:
                pass  # Streamlined error handling
        
        # Load optional generators
        for module_name, class_name, key in optional_generators:
            try:
                generator_class = self._import_generator_class(module_name, class_name, package_name)
                if generator_class:
                    generators[key] = generator_class()
            except Exception:
                pass  # Silent failure for optional generators
        
        return generators

    def _import_generator_class(self, module_name, class_name, package_name):
        """Import a single generator class with multiple strategies."""
        # Strategy 1: Try relative import from current package
        try:
            full_module_name = f"{package_name}.{module_name}"
            module = importlib.import_module(full_module_name)
            return getattr(module, class_name)
        except (ImportError, AttributeError):
            pass
        
        # Strategy 2: Try direct file path import
        try:
            current_dir = os.path.dirname(__file__)
            module_file = os.path.join(current_dir, f"{module_name}.py")
            
            if os.path.exists(module_file):
                spec = importlib.util.spec_from_file_location(module_name, module_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return getattr(module, class_name)
        except Exception:
            pass
        
        # Strategy 3: Try adding current directory to path
        try:
            current_dir = os.path.dirname(__file__)
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            module = importlib.import_module(module_name)
            return getattr(module, class_name)
        except (ImportError, AttributeError):
            pass
        
        return None

    def init_ui(self):
        """Initialize the UI components with alphabetically sorted tabs."""
        self.main_layout = QVBoxLayout(self)
        
        # Create splitter for controls and preview
        self.splitter = QSplitter(Qt.Vertical)
        
        # Controls section
        self.controls_widget = QWidget()
        self.controls_layout = QVBoxLayout(self.controls_widget)
        
        # Theme tabs widget
        self.theme_tabs = QTabWidget()
        self.theme_tabs.currentChanged.connect(self.on_tab_changed)
        
        # Dictionary to map tab indices to theme names
        self.tab_to_theme = {}
        self.theme_control_widgets = {}
        
        # Define tab titles with alphabetical sorting
        tab_titles = {
            "artistic": "Artistic Styles",
            "cosmic": "Cosmic",
            "fire": "Fire",
            "flowers": "Flowers",
            "foliage": "Foliage",
            "holidays": "Holidays",
            "metal_stone": "Metal & Stone",
            "mood": "Mood",
            "sky": "Sky"
        }
        
        # Sort themes alphabetically by tab title
        sorted_themes = sorted(
            [(theme_name, tab_titles.get(theme_name, generator.name)) 
             for theme_name, generator in self.theme_generators.items()], 
            key=lambda x: x[1]
        )
        
        # Create tabs in alphabetical order
        for theme_name, tab_title in sorted_themes:
            generator = self.theme_generators[theme_name]
            
            # Create controls widget
            controls_widget = ThemeControlsWidget(generator)
            controls_widget.parameter_changed.connect(self.on_parameter_changed)
            
            # Create scroll area
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(controls_widget)
            
            # Add to tabs
            tab_index = self.theme_tabs.addTab(scroll, tab_title)
            
            # Map tab index to theme name
            self.tab_to_theme[tab_index] = theme_name
            
            # Store references
            self.theme_control_widgets[theme_name] = {
                'widget': controls_widget,
                'scroll': scroll,
                'tab_index': tab_index
            }
        
        self.controls_layout.addWidget(self.theme_tabs)
        
        # Preview section
        self.preview_widget = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_widget)
        
        # Preview title
        self.preview_title = QLabel("Theme Gradient Preview")
        self.preview_title.setAlignment(Qt.AlignCenter)
        self.preview_layout.addWidget(self.preview_title)
        
        # Gradient preview
        self.preview = ThemePreviewWidget(None)
        self.preview_layout.addWidget(self.preview)
        
        # Info label
        self.info_label = QLabel("Adjust parameters to generate a theme gradient")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.preview_layout.addWidget(self.info_label)
        
        # Add controls and preview to splitter
        self.splitter.addWidget(self.controls_widget)
        self.splitter.addWidget(self.preview_widget)
        
        # Set initial splitter sizes
        self.splitter.setSizes([600, 400])
        
        self.main_layout.addWidget(self.splitter)
        
        # Action buttons
        self.buttons_layout = QHBoxLayout()
        
        buttons = [
            ("Generate New", self.on_generate_clicked),
            ("Reset Parameters", self.on_reset_clicked),
            ("Randomize Parameters", self.on_random_clicked),
            ("Apply to Gradient", self.on_apply_clicked)
        ]
        
        for text, handler in buttons:
            button = QPushButton(text)
            button.clicked.connect(handler)
            self.buttons_layout.addWidget(button)
            
            if text == "Apply to Gradient":
                self.apply_button = button
        
        self.main_layout.addLayout(self.buttons_layout)
        
        # Mark UI as initialized
        self._ui_initialized = True

    def _initialize_first_theme(self):
        """Initialize the first theme and generate initial gradient."""
        if not self._ui_initialized or not self.theme_generators:
            return
        
        # Set current tab to index 0 if we have tabs
        if self.theme_tabs.count() > 0:
            self.theme_tabs.setCurrentIndex(0)
            
            # Force set the theme if on_tab_changed didn't work
            if self.current_theme is None and self.tab_to_theme:
                first_theme = self.tab_to_theme.get(0)
                if first_theme:
                    self.current_theme = first_theme
                    self.current_generator = self.theme_generators[first_theme]
            
            # Generate initial gradient
            QTimer.singleShot(200, self._generate_initial_gradient)
    
    def _generate_initial_gradient(self):
        """Generate the initial gradient for the first theme."""
        try:
            if self.current_generator:
                initial_gradient = self.current_generator.generate_gradient()
                
                if initial_gradient:
                    self.current_gradient = initial_gradient
                    self.preview.set_gradient(initial_gradient)
                    
                    theme_name = getattr(self.current_generator, 'name', self.current_theme)
                    self.info_label.setText(f"Ready: {theme_name} - Click 'Apply to Gradient' to use")
                else:
                    self.info_label.setText("Error: Could not generate initial gradient")
            else:
                self.info_label.setText("No theme generator available")
                
        except Exception as e:
            self.info_label.setText(f"Error generating initial gradient: {str(e)}")

    def on_tab_changed(self, tab_index):
        """Handle tab change to switch theme type."""
        if tab_index in self.tab_to_theme:
            new_theme = self.tab_to_theme[tab_index]
            
            # Only update if theme actually changed
            if self.current_theme != new_theme:
                self.current_theme = new_theme
                self.current_generator = self.theme_generators[self.current_theme]
                
                # Update preview for the new theme
                self.update_preview()
            else:
                # Even if theme didn't change, ensure we have a gradient
                if self.current_gradient is None:
                    self.update_preview()

    def on_parameter_changed(self, param_name, value):
        """Handle parameter value change with enhanced responsiveness."""
        if self.current_generator:
            self.current_generator.set_parameter_value(param_name, value)
            
            # Enhanced: Immediate update for foliage_mix and other key parameters
            if param_name in ['foliage_mix', 'flower_type', 'material_type']:
                # Force immediate regeneration for key parameters
                self.current_generator.base_structure = None  # Force regeneration
                self.preview_timer.stop()
                self.preview_timer.start(100)  # Shorter delay for key parameters
            else:
                # Standard debounced update for other parameters
                self.preview_timer.stop()
                self.preview_timer.start(250)

    def _update_preview_delayed(self):
        """Update preview with debouncing."""
        self.update_preview()

    def on_generate_clicked(self):
        """Handle generate button click."""
        try:
            if not self.current_generator:
                self.info_label.setText("No theme generator available")
                return
                
            # Request new seed if available
            if hasattr(self.current_generator, 'request_new_seed'):
                self.current_generator.request_new_seed()
            elif hasattr(self.current_generator, 'base_structure'):
                self.current_generator.base_structure = None
            
            self.current_gradient = self.current_generator.generate_gradient()
            self.preview.set_gradient(self.current_gradient)
            self.info_label.setText(f"Generated: {self.current_gradient.get_name()}")
        except Exception as e:
            self.info_label.setText(f"Error generating gradient: {str(e)}")

    def on_reset_clicked(self):
        """Handle reset button click."""
        try:
            if not self.current_generator:
                self.info_label.setText("No theme generator available")
                return
                
            self.current_generator.reset_parameters()
            
            if self.current_theme in self.theme_control_widgets:
                controls = self.theme_control_widgets[self.current_theme]['widget']
                controls.update_from_generator()
            
            # Force regeneration
            if hasattr(self.current_generator, 'base_structure'):
                self.current_generator.base_structure = None
            
            self.update_preview()
            self.info_label.setText("Parameters reset to defaults")
        except Exception as e:
            self.info_label.setText(f"Error resetting parameters: {str(e)}")

    def on_random_clicked(self):
        """Handle randomize button click."""
        try:
            if not self.current_generator:
                self.info_label.setText("No theme generator available")
                return
                
            # Randomize parameters within their ranges
            for param in self.current_generator.get_parameter_list():
                if param.name.endswith("_type"):
                    continue
                
                if param.max_value > param.min_value:
                    random_value = param.min_value + random.random() * (param.max_value - param.min_value)
                    
                    if param.step >= 1.0:
                        random_value = round(random_value / param.step) * param.step
                    
                    self.current_generator.set_parameter_value(param.name, random_value)
            
            if self.current_theme in self.theme_control_widgets:
                controls = self.theme_control_widgets[self.current_theme]['widget']
                controls.update_from_generator()
            
            # Force regeneration
            if hasattr(self.current_generator, 'base_structure'):
                self.current_generator.base_structure = None
            
            self.update_preview()
            self.info_label.setText("Parameters randomized")
        except Exception as e:
            self.info_label.setText(f"Error randomizing parameters: {str(e)}")

    def on_apply_clicked(self):
        """Handle apply button click."""
        try:
            if not self.current_generator:
                self.info_label.setText("No theme generator available")
                return
                
            if self.current_gradient is None:
                self.current_gradient = self.current_generator.generate_gradient()
                
            self.gradient_generated.emit(self.current_gradient)
            self.info_label.setText(f"Applied: {self.current_gradient.get_name()}")
        except Exception as e:
            self.info_label.setText(f"Error applying gradient: {str(e)}")

    def update_preview(self):
        """Update the gradient preview with streamlined error handling."""
        if not self.current_generator:
            # Try to initialize if we have generators but no current one set
            if self.theme_generators and not self.current_theme:
                if self.theme_tabs.count() > 0:
                    first_tab_index = 0
                    if first_tab_index in self.tab_to_theme:
                        self.current_theme = self.tab_to_theme[first_tab_index]
                        self.current_generator = self.theme_generators[self.current_theme]
                    else:
                        # Fallback to first available theme
                        self.current_theme = next(iter(self.theme_generators))
                        self.current_generator = self.theme_generators[self.current_theme]
            
            if not self.current_generator:
                self.info_label.setText("No theme generator available - check theme integration")
                return
            
        try:
            preview_gradient = self.current_generator.generate_gradient()
            
            if not preview_gradient:
                self.info_label.setText("Error: Failed to generate gradient")
                return
            
            self.preview.set_gradient(preview_gradient)
            self.current_gradient = preview_gradient
            
            theme_name = getattr(self.current_generator, 'name', self.current_theme)
            self.info_label.setText(f"Preview: {theme_name} - Click 'Apply to Gradient' to use")
            
        except Exception as e:
            self.info_label.setText(f"Error updating preview: {str(e)}")

    def update_from_model(self):
        """Update widget from gradient model (called when tab is selected)."""
        try:
            if self.current_generator:
                self.update_preview()
        except Exception:
            pass  # Streamlined error handling

    def reset_controls(self):
        """Reset controls for current theme."""
        try:
            if self.current_theme and self.current_theme in self.theme_control_widgets:
                controls = self.theme_control_widgets[self.current_theme]['widget']
                controls.reset_controls()
                self.update_preview()
        except Exception:
            pass  # Streamlined error handling