#!/usr/bin/env python3
"""
Enhanced Gradient Blending UI Module for Gradient Generator - UPDATED BUTTON ORDER

Modified to reorder buttons: Add Current, Add Selected, Add All (no popups)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QListWidget, QListWidgetItem, QComboBox,
                           QDoubleSpinBox, QGroupBox, QFormLayout, QSplitter,
                           QMessageBox, QCheckBox, QRadioButton, QButtonGroup,
                           QStackedWidget, QSlider, QScrollArea, QTabWidget,
                           QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QPainter, QLinearGradient, QColor, QIcon

import copy
from typing import List, Dict, Tuple, Optional, Any

try:
    from .blend_core import BlendRegistry, GradientBlender
    from ..core.gradient import Gradient
    # Import the enhanced parameter widget
    from .blend_parameter_widget import BlendParameterWidget
except ImportError:
    try:
        from gradient_generator.ui.gradient_blending.blend_core import BlendRegistry, GradientBlender
        from gradient_generator.core.gradient import Gradient
        from gradient_generator.ui.gradient_blending.blend_parameter_widget import BlendParameterWidget
    except ImportError:
        from blend_core import BlendRegistry, GradientBlender
        from core.gradient import Gradient
        from blend_parameter_widget import BlendParameterWidget


class GradientPreviewWidget(QWidget):
    """Widget for displaying a gradient preview."""
    
    def __init__(self, gradient, title="Preview"):
        super().__init__()
        
        self.gradient = gradient
        self.title = title
        
        # Set fixed height for preview to prevent expansion
        self.setFixedHeight(100)
        # Set minimum width but allow horizontal expansion
        self.setMinimumWidth(200)
        
        # Set size policy to prevent vertical expansion
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setSizePolicy(size_policy)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFixedHeight(20)
        layout.addWidget(self.title_label)
        
        # Preview area
        self.preview_area = QLabel()
        self.preview_area.setFixedHeight(80)
        self.preview_area.setStyleSheet("border: 1px solid #555;")
        self.preview_area.setMinimumWidth(200)
        layout.addWidget(self.preview_area)
        
        # Update preview
        self.update_preview()
    
    def update_preview(self):
        """Update the gradient preview."""
        if not self.gradient:
            return
            
        width = self.preview_area.width() or 300
        height = self.preview_area.height() or 80
        
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create linear gradient
        qgradient = QLinearGradient(0, 0, width, 0)
        
        # Add color stops
        for position, color in self.gradient.get_color_stops():
            qgradient.setColorAt(position, QColor(*color))
        
        # Draw gradient
        painter.fillRect(0, 0, width, height, qgradient)
        
        # Draw border
        painter.setPen(QColor(80, 80, 80))
        painter.drawRect(0, 0, width-1, height-1)
        
        painter.end()
        
        self.preview_area.setPixmap(pixmap)
    
    def set_gradient(self, gradient):
        """Set the gradient to display."""
        self.gradient = gradient
        self.update_preview()
    
    def set_title(self, title):
        """Set the preview title."""
        self.title = title
        self.title_label.setText(title)
    
    def resizeEvent(self, event):
        """Handle resize event."""
        super().resizeEvent(event)
        self.update_preview()
    
    def sizeHint(self):
        """Override size hint to provide fixed height."""
        return QSize(300, 140)
    
    def minimumSizeHint(self):
        """Override minimum size hint to provide fixed height."""
        return QSize(200, 140)


class GradientListItem(QListWidgetItem):
    """Custom list item that holds a gradient."""
    
    def __init__(self, gradient, name=None, weight=1.0):
        super().__init__()
        
        self.gradient = gradient
        self.name = name or gradient.get_name() or "Unnamed Gradient"
        self.weight = weight
        
        # Set text
        self.setText(f"{self.name} (weight: {self.weight:.2f})")
        
        # Create preview pixmap
        self.create_preview()
        
        # Set size hint
        self.setSizeHint(QSize(200, 60))
    
    def create_preview(self):
        """Create a preview pixmap of the gradient."""
        # Create pixmap
        pixmap = QPixmap(150, 25)
        pixmap.fill(Qt.transparent)
        
        # Create painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create linear gradient
        gradient = QLinearGradient(0, 0, pixmap.width(), 0)
        
        # Add color stops
        for position, color in self.gradient.get_color_stops():
            gradient.setColorAt(position, QColor(*color))
        
        # Draw gradient
        painter.fillRect(pixmap.rect(), gradient)
        
        # Draw border
        painter.setPen(QColor(80, 80, 80))
        painter.drawRect(pixmap.rect())
        
        painter.end()
        
        # Set icon
        self.setIcon(QIcon(pixmap))
    
    def set_weight(self, weight):
        """Set the gradient weight."""
        self.weight = weight
        self.setText(f"{self.name} (weight: {self.weight:.2f})")


class EnhancedBlendMethodPanel(QWidget):
    """Enhanced panel for a specific blend method with improved parameter controls."""
    
    parameters_changed = pyqtSignal()
    
    def __init__(self, blender, parent=None):
        super().__init__(parent)
        
        self.blender = blender
        self.param_widgets = {}
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components with enhanced controls."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Method description
        desc_label = QLabel(self.blender.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #aaa; font-style: italic; padding: 8px; background-color: #2a2a2a; border-radius: 4px;")
        desc_label.setFixedHeight(45)
        layout.addWidget(desc_label)
        
        # Parameters group with enhanced styling
        param_group = QGroupBox("Parameters")
        param_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        param_layout = QVBoxLayout(param_group)
        param_layout.setSpacing(12)  # Better spacing between parameters
        
        # Add enhanced parameter controls
        parameters = self.blender.get_parameter_list()
        if parameters:
            for param in parameters:
                # Use the enhanced BlendParameterWidget
                widget = BlendParameterWidget(param)
                widget.parameter_changed.connect(self.on_parameter_changed)
                
                # Add the widget directly to the layout
                param_layout.addWidget(widget)
                self.param_widgets[param.name] = widget
        else:
            # No parameters available
            no_params_label = QLabel("No adjustable parameters for this blend method.")
            no_params_label.setStyleSheet("color: #888; font-style: italic; padding: 10px;")
            param_layout.addWidget(no_params_label)
        
        layout.addWidget(param_group)
        layout.addStretch()
    
    def on_parameter_changed(self, param_name, value):
        """Handle parameter change from enhanced controls."""
        # Update the parameter in the blender
        self.blender.set_parameter_value(param_name, value)
        
        # Emit signal to update preview
        self.parameters_changed.emit()
    
    def update_from_blender(self):
        """Update enhanced controls from the blender parameters."""
        for name, widget in self.param_widgets.items():
            param = self.blender.get_parameter(name)
            if param:
                widget.update_value(param.value)


class GradientBlendingWidget(QWidget):
    """Enhanced main widget for gradient blending functionality with REORDERED BUTTONS."""
    
    gradient_blended = pyqtSignal(object)  # Emitted when a gradient is blended
    gradients_added = pyqtSignal()  # Signal to indicate gradients were added
    
    def __init__(self, gradient_model):
        super().__init__()
        
        self.gradient_model = gradient_model
        self.merge_list = []  # List of (gradient, weight) tuples
        self.blender_panels = {}  # Map of blender name to panel widget
        self.current_blender = None
        
        self.init_ui()
        self.initialize_blenders()
    
    def init_ui(self):
        """Initialize the UI components with REORDERED BUTTONS."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for left and right panels
        splitter = QSplitter(Qt.Horizontal)
        
        # === Left panel: Gradient selection ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Source selection group with enhanced styling
        source_group = QGroupBox("Source Gradients")
        source_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        source_layout = QVBoxLayout(source_group)
        
        # Enhanced button styling
        button_style = """
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #666;
                border-radius: 4px;
                background-color: #4a4a4a;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border-color: #777;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """
        
        # REORDERED BUTTONS: Current -> Selected -> All
        
        # 1. Add current gradient button (FIRST)
        self.add_current_button = QPushButton("Add Current Gradient")
        self.add_current_button.setStyleSheet(button_style)
        self.add_current_button.clicked.connect(self.add_current_gradient)
        source_layout.addWidget(self.add_current_button)
        
        # 2. Add selected from list button (SECOND)
        self.add_selected_button = QPushButton("Add Selected From List")
        self.add_selected_button.setStyleSheet(button_style)
        self.add_selected_button.clicked.connect(self.add_selected_from_gradient_list)
        self.add_selected_button.setToolTip("Add only the selected gradients from the gradient list")
        source_layout.addWidget(self.add_selected_button)
        
        # 3. Add all from list button (THIRD)
        self.add_from_list_button = QPushButton("Add All From List")
        self.add_from_list_button.setStyleSheet(button_style)
        self.add_from_list_button.clicked.connect(self.add_from_gradient_list)
        source_layout.addWidget(self.add_from_list_button)
        
        left_layout.addWidget(source_group)
        
        # Merge list group with enhanced styling
        merge_list_group = QGroupBox("Gradients to Blend")
        merge_list_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        merge_list_layout = QVBoxLayout(merge_list_group)
        
        # Gradient list widget
        self.merge_list_widget = QListWidget()
        self.merge_list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        self.merge_list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.merge_list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        merge_list_layout.addWidget(self.merge_list_widget)
        
        # Weight control
        weight_layout = QHBoxLayout()
        weight_layout.addWidget(QLabel("Weight:"))
        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0.0, 10.0)
        self.weight_spin.setSingleStep(0.1)
        self.weight_spin.setValue(1.0)
        self.weight_spin.valueChanged.connect(self.on_weight_changed)
        self.weight_spin.setEnabled(False)
        weight_layout.addWidget(self.weight_spin)
        merge_list_layout.addLayout(weight_layout)
        
        # Button row
        button_layout = QHBoxLayout()
        
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.setStyleSheet(button_style)
        self.remove_button.clicked.connect(self.remove_selected)
        self.remove_button.setEnabled(False)
        button_layout.addWidget(self.remove_button)
        
        self.clear_button = QPushButton("Clear All")
        self.clear_button.setStyleSheet(button_style)
        self.clear_button.clicked.connect(self.clear_merge_list)
        button_layout.addWidget(self.clear_button)
        
        merge_list_layout.addLayout(button_layout)
        
        left_layout.addWidget(merge_list_group)
        
        # === Right panel: Blend options and preview ===
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Blend method selection with enhanced styling
        method_group = QGroupBox("Blend Method")
        method_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        method_layout = QVBoxLayout(method_group)
        
        # Method selector with enhanced styling
        self.method_combo = QComboBox()
        self.method_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border: 1px solid #666;
                border-radius: 4px;
                background-color: #4a4a4a;
                color: white;
                font-weight: bold;
                min-height: 20px;
            }
            QComboBox:hover {
                border-color: #777;
                background-color: #5a5a5a;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
        """)
        self.method_combo.currentTextChanged.connect(self.on_method_changed)
        method_layout.addWidget(self.method_combo)
        
        # Stacked widget for method-specific parameters
        self.method_stack = QStackedWidget()
        method_layout.addWidget(self.method_stack)
        
        right_layout.addWidget(method_group)
        
        # Preview group - set fixed height to prevent expansion
        preview_group = QGroupBox("Preview")
        preview_group.setFixedHeight(200)
        preview_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        preview_layout = QVBoxLayout(preview_group)
        
        # Merged gradient preview
        self.merged_preview = GradientPreviewWidget(None, "Blended Gradient")
        preview_layout.addWidget(self.merged_preview)
        
        # Blend button with enhanced styling
        self.blend_button = QPushButton("Apply Blended Gradient")
        self.blend_button.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                border: 2px solid #666;
                border-radius: 6px;
                background-color: #2a7a2a;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3a8a3a;
                border-color: #777;
            }
            QPushButton:pressed {
                background-color: #1a6a1a;
            }
            QPushButton:disabled {
                background-color: #3a3a3a;
                color: #888;
                border-color: #444;
            }
        """)
        self.blend_button.clicked.connect(self.apply_blended_gradient)
        self.blend_button.setEnabled(False)
        preview_layout.addWidget(self.blend_button)
        
        right_layout.addWidget(preview_group)
        
        # Method details with enhanced styling
        details_group = QGroupBox("Method Description")
        details_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        details_layout = QVBoxLayout(details_group)
        
        self.details_label = QLabel()
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet("color: #aaa; font-style: italic; padding: 8px;")
        self.update_method_description()
        
        details_layout.addWidget(self.details_label)
        
        # Set size policy for details group to expand vertically
        details_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        right_layout.addWidget(details_group)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set initial splitter sizes
        splitter.setSizes([400, 600])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
    
    def initialize_blenders(self):
        """Initialize enhanced blend method panels."""
        # Clear existing items
        self.method_combo.clear()
        
        # Get all registered blenders
        blenders = BlendRegistry.get_all_blenders()
        
        if not blenders:
            # No blenders registered, create a message
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_label = QLabel("No blend methods available.\nPlease check your installation.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
            empty_layout.addWidget(empty_label)
            self.method_stack.addWidget(empty_widget)
            
            # Add dummy item to combo
            self.method_combo.addItem("None")
            return
        
        # Add each blender with enhanced panels
        for blender in blenders:
            # Create enhanced panel for this blender
            panel = EnhancedBlendMethodPanel(blender)
            panel.parameters_changed.connect(self.update_blend_preview)
            
            # Add to stack widget
            self.method_stack.addWidget(panel)
            
            # Add to combo box
            self.method_combo.addItem(blender.name)
            
            # Store in map
            self.blender_panels[blender.name] = panel
        
        # Select first blender
        if blenders:
            self.method_combo.setCurrentText(blenders[0].name)
            self.current_blender = blenders[0]
    
    def add_current_gradient(self):
        """Add the current gradient to the merge list - NO POPUPS."""
        gradient_copy = self.gradient_model.clone()
        name = gradient_copy.get_name() or "Current Gradient"
        self.add_gradient_to_list(gradient_copy, name, 1.0)
        self.gradients_added.emit()
        
        # Show status in main window status bar if available (no popup)
        try:
            main_window = self.window()
            if hasattr(main_window, 'statusBar'):
                main_window.statusBar().showMessage(f"Added current gradient: {name}", 3000)
        except:
            pass
    
    def add_selected_from_gradient_list(self):
        """Add only SELECTED gradients from the main gradient list panel - NO POPUPS."""
        main_window = self.window()
        
        if hasattr(main_window, 'gradient_list_panel'):
            gradient_list_panel = main_window.gradient_list_panel
            selected_items = gradient_list_panel.list_widget.selectedItems()
            
            if not selected_items:
                # Show status instead of popup
                try:
                    if hasattr(main_window, 'statusBar'):
                        main_window.statusBar().showMessage("No gradients selected in list panel", 3000)
                except:
                    pass
                return
            
            if not gradient_list_panel.gradients:
                # Show status instead of popup
                try:
                    if hasattr(main_window, 'statusBar'):
                        main_window.statusBar().showMessage("No gradients found in list panel", 3000)
                except:
                    pass
                return
            
            added_count = 0
            for item in selected_items:
                index = gradient_list_panel.list_widget.row(item)
                
                if 0 <= index < len(gradient_list_panel.gradients):
                    gradient, name = gradient_list_panel.gradients[index]
                    gradient_copy = gradient.clone()
                    self.add_gradient_to_list(gradient_copy, name, 1.0)
                    added_count += 1
            
            if added_count > 0:
                self.update_blend_preview()
                self.gradients_added.emit()
                
                # Show status instead of popup
                try:
                    if hasattr(main_window, 'statusBar'):
                        main_window.statusBar().showMessage(f"Added {added_count} selected gradient(s)", 3000)
                except:
                    pass
            else:
                # Show status instead of popup
                try:
                    if hasattr(main_window, 'statusBar'):
                        main_window.statusBar().showMessage("Failed to add selected gradients", 3000)
                except:
                    pass
        else:
            # Show status instead of popup
            try:
                if hasattr(main_window, 'statusBar'):
                    main_window.statusBar().showMessage("Could not access gradient list panel", 3000)
            except:
                pass
    
    def add_from_gradient_list(self):
        """Add ALL gradients from the main gradient list panel - NO POPUPS."""
        main_window = self.window()
        
        if hasattr(main_window, 'gradient_list_panel'):
            gradients = main_window.gradient_list_panel.gradients
            
            if not gradients:
                # Show status instead of popup
                try:
                    if hasattr(main_window, 'statusBar'):
                        main_window.statusBar().showMessage("No gradients found in list panel", 3000)
                except:
                    pass
                return
            
            for gradient, name in gradients:
                gradient_copy = gradient.clone()
                self.add_gradient_to_list(gradient_copy, name, 1.0)
                
            self.update_blend_preview()
            self.gradients_added.emit()
            
            # Show status instead of popup
            try:
                if hasattr(main_window, 'statusBar'):
                    main_window.statusBar().showMessage(f"Added all {len(gradients)} gradients from list", 3000)
            except:
                pass
        else:
            # Show status instead of popup
            try:
                if hasattr(main_window, 'statusBar'):
                    main_window.statusBar().showMessage("Could not access gradient list panel", 3000)
            except:
                pass
    
    def add_gradient_to_list(self, gradient, name, weight):
        """Add a gradient to the merge list."""
        item = GradientListItem(gradient, name, weight)
        self.merge_list_widget.addItem(item)
        self.merge_list.append((gradient, weight))
        self.update_blend_preview()
    
    def remove_selected(self):
        """Remove the selected gradients from the merge list."""
        selected_items = self.merge_list_widget.selectedItems()
        
        if not selected_items:
            return
            
        for item in selected_items:
            index = self.merge_list_widget.row(item)
            self.merge_list_widget.takeItem(index)
            if 0 <= index < len(self.merge_list):
                self.merge_list.pop(index)
        
        self.update_blend_preview()
        self.on_selection_changed()
    
    def clear_merge_list(self):
        """Clear the merge list."""
        if not self.merge_list:
            return
            
        self.merge_list_widget.clear()
        self.merge_list = []
        self.update_blend_preview()
        self.on_selection_changed()
    
    def on_selection_changed(self):
        """Handle selection change in the merge list."""
        selected_items = self.merge_list_widget.selectedItems()
        has_selection = len(selected_items) > 0
        
        self.remove_button.setEnabled(has_selection)
        self.weight_spin.setEnabled(len(selected_items) == 1)
        
        if len(selected_items) == 1:
            item = selected_items[0]
            self.weight_spin.setValue(item.weight)
    
    def on_weight_changed(self, value):
        """Handle weight change."""
        selected_items = self.merge_list_widget.selectedItems()
        
        if len(selected_items) == 1:
            item = selected_items[0]
            item.set_weight(value)
            
            index = self.merge_list_widget.row(item)
            if 0 <= index < len(self.merge_list):
                gradient, _ = self.merge_list[index]
                self.merge_list[index] = (gradient, value)
            
            self.update_blend_preview()
    
    def on_method_changed(self, method_name):
        """Handle method selection change."""
        blender = BlendRegistry.get_blender(method_name)
        
        if not blender:
            return
            
        self.current_blender = blender
        
        if method_name in self.blender_panels:
            panel = self.blender_panels[method_name]
            self.method_stack.setCurrentWidget(panel)
        
        self.update_blend_preview()
        self.update_method_description()
    
    def update_method_description(self):
        """Update the method description based on the selected method."""
        if not self.current_blender:
            self.details_label.setText("")
            return
            
        self.details_label.setText(self.current_blender.description)
    
    def update_blend_preview(self):
        """Update the merged gradient preview."""
        # Check if we have gradients to merge
        if not self.merge_list or not self.current_blender:
            self.merged_preview.set_gradient(None)
            self.blend_button.setEnabled(False)
            return
        
        try:
            # Blend gradients using the current method
            merged_gradient = self.current_blender.blend_gradients(self.merge_list)
            
            # Update preview
            self.merged_preview.set_gradient(merged_gradient)
            
            # Update merged gradient name based on method
            name = f"Blended Gradient ({self.current_blender.name})"
            merged_gradient.set_name(name)
            self.merged_preview.set_title(name)
            
            # Enable blend button
            self.blend_button.setEnabled(True)
            
            # Update method description with current parameters
            self.update_method_description()
            
        except Exception as e:
            # Handle blend errors gracefully
            self.merged_preview.set_gradient(None)
            self.blend_button.setEnabled(False)
            print(f"Blend error: {e}")
    
    def apply_blended_gradient(self):
        """Apply the merged gradient to the current gradient model."""
        # Check if we have a merged gradient
        if not self.merge_list or not self.current_blender:
            return
            
        try:
            # Blend gradients using the current method
            merged_gradient = self.current_blender.blend_gradients(self.merge_list)
            
            # Emit the merged gradient
            self.gradient_blended.emit(merged_gradient)
            
            # Show status instead of popup
            try:
                main_window = self.window()
                if hasattr(main_window, 'statusBar'):
                    main_window.statusBar().showMessage(f"Applied blended gradient using {self.current_blender.name} method", 3000)
            except:
                pass
            
        except Exception as e:
            # Show status instead of popup
            try:
                main_window = self.window()
                if hasattr(main_window, 'statusBar'):
                    main_window.statusBar().showMessage(f"Failed to apply blended gradient: {str(e)}", 5000)
            except:
                pass


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    # Import blending methods to register them
    try:
        from . import interleave_blend, mix_blend, crossfade_blend, stack_blend, new_blend_types
    except ImportError:
        try:
            import interleave_blend, mix_blend, crossfade_blend, stack_blend, new_blend_types
        except ImportError:
            print("Warning: Could not import blending methods. Using empty registry.")
    
    app = QApplication(sys.argv)
    
    # Apply dark theme
    try:
        from gradient_generator.utils.styles import apply_dark_theme
        apply_dark_theme(app)
    except ImportError:
        pass
    
    # Create a test gradient
    from gradient_generator.core.gradient import Gradient
    gradient = Gradient()
    
    # Create enhanced widget
    widget = GradientBlendingWidget(gradient)
    widget.setWindowTitle("Enhanced Gradient Blending - REORDERED BUTTONS (No Popups)")
    widget.setGeometry(100, 100, 1000, 700)
    widget.show()
    
    print("Updated Button Order:")
    print("1. Add Current Gradient (FIRST)")
    print("2. Add Selected From List (SECOND)")
    print("3. Add All From List (THIRD)")
    print("✓ All popup dialogs removed")
    print("✓ Status messages now show in status bar instead")
    print("✓ Functionality unchanged - only UI order and feedback method changed")
    
    sys.exit(app.exec_())