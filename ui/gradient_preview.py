#!/usr/bin/env python3
"""
Refactored Gradient Preview Module - Streamlined Implementation

Clean, efficient gradient preview widgets with all functionality preserved
but redundant code and excessive debug statements removed.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QListWidget, QListWidgetItem, QComboBox,
                           QDoubleSpinBox, QGroupBox, QFormLayout, QSplitter,
                           QMessageBox, QCheckBox, QSlider, QScrollArea,
                           QSizePolicy, QStackedWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QPainter, QLinearGradient, QColor, QIcon
import copy
from typing import List, Dict, Tuple, Optional, Any

# Import blending core with fallback
try:
    from .blend_core import BlendRegistry, GradientBlender
    from ..core.gradient import Gradient
    BLENDING_AVAILABLE = True
except ImportError:
    try:
        from gradient_generator.ui.gradient_blending.blend_core import BlendRegistry, GradientBlender
        from gradient_generator.core.gradient import Gradient
        BLENDING_AVAILABLE = True
    except ImportError:
        BLENDING_AVAILABLE = False
        
        class BlendRegistry:
            @staticmethod
            def get_all_blenders(): return []
            @staticmethod
            def get_blender(name): return None
        
        class GradientBlender:
            def __init__(self):
                self.name = "Fallback"
                self.description = "Blending not available"
            def blend_gradients(self, gradients):
                return gradients[0][0] if gradients else None
            def get_parameter_list(self): return []


class GradientPreviewWidget(QWidget):
    """Streamlined gradient preview widget."""
    
    def __init__(self, gradient, title="Preview"):
        super().__init__()
        self.gradient = gradient
        self.title = title
        
        self.setFixedHeight(140)
        self.setMinimumWidth(200)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
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
        
        # Create and draw gradient
        qgradient = QLinearGradient(0, 0, width, 0)
        for position, color in self.gradient.get_color_stops():
            qgradient.setColorAt(position, QColor(*color))
        
        painter.fillRect(0, 0, width, height, qgradient)
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
        """Size hint for layout."""
        return QSize(300, 140)


class GradientListItem(QListWidgetItem):
    """List item that holds a gradient with preview."""
    
    def __init__(self, gradient, name=None, weight=1.0):
        super().__init__()
        self.gradient = gradient
        self.name = name or gradient.get_name() or "Unnamed Gradient"
        self.weight = weight
        
        self.setText(f"{self.name} (weight: {self.weight:.2f})")
        self._create_preview()
        self.setSizeHint(QSize(200, 60))
    
    def _create_preview(self):
        """Create a preview pixmap of the gradient."""
        pixmap = QPixmap(150, 25)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create gradient
        gradient = QLinearGradient(0, 0, pixmap.width(), 0)
        for position, color in self.gradient.get_color_stops():
            gradient.setColorAt(position, QColor(*color))
        
        painter.fillRect(pixmap.rect(), gradient)
        painter.setPen(QColor(80, 80, 80))
        painter.drawRect(pixmap.rect())
        painter.end()
        
        self.setIcon(QIcon(pixmap))
    
    def set_weight(self, weight):
        """Set the gradient weight."""
        self.weight = weight
        self.setText(f"{self.name} (weight: {self.weight:.2f})")


class BlendParameterWidget(QWidget):
    """Widget for adjusting a single blend parameter."""
    
    parameter_changed = pyqtSignal(str, float)
    
    def __init__(self, param, parent=None):
        super().__init__(parent)
        self.param = param
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(f"{self.param.label}:")
        layout.addWidget(self.label)
        
        # Create appropriate control based on parameter type
        if self.param.step >= 1.0:
            self._create_discrete_control(layout)
        else:
            self._create_continuous_control(layout)
        
        self.setToolTip(self.param.description)
    
    def _create_discrete_control(self, layout):
        """Create discrete parameter control (combo box)."""
        self.control = QComboBox()
        
        if ":" in self.param.description:
            options_str = self.param.description.split(":", 1)[1]
            options = [opt.strip() for opt in options_str.split(",")]
            self.control.addItems(options)
            
            index = int(self.param.value)
            if 0 <= index < len(options):
                self.control.setCurrentIndex(index)
        else:
            for i in range(int(self.param.min_value), int(self.param.max_value) + 1):
                self.control.addItem(str(i))
            self.control.setCurrentIndex(int(self.param.value - self.param.min_value))
        
        self.control.currentIndexChanged.connect(self._on_combo_changed)
        layout.addWidget(self.control)
    
    def _create_continuous_control(self, layout):
        """Create continuous parameter control (slider)."""
        self.control = QSlider(Qt.Horizontal)
        
        # Convert to integer range for slider
        min_val_int = int(self.param.min_value * 100)
        max_val_int = int(self.param.max_value * 100)
        val_int = int(self.param.value * 100)
        step_int = max(1, int(self.param.step * 100))
        
        self.control.setRange(min_val_int, max_val_int)
        self.control.setValue(val_int)
        self.control.setSingleStep(step_int)
        
        self.value_label = QLabel(f"{self.param.value:.2f}")
        self.value_label.setFixedWidth(50)
        layout.addWidget(self.value_label)
        
        self.control.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.control)
    
    def _on_slider_changed(self, value_int):
        """Handle slider value change."""
        value = value_int / 100.0
        self.value_label.setText(f"{value:.2f}")
        self.parameter_changed.emit(self.param.name, value)
    
    def _on_combo_changed(self, index):
        """Handle combo box selection change."""
        value = float(index + self.param.min_value)
        self.parameter_changed.emit(self.param.name, value)
    
    def update_value(self, value):
        """Update the control to reflect a new parameter value."""
        if isinstance(self.control, QSlider):
            self.control.setValue(int(value * 100))
            self.value_label.setText(f"{value:.2f}")
        elif isinstance(self.control, QComboBox):
            index = int(value - self.param.min_value)
            if 0 <= index < self.control.count():
                self.control.setCurrentIndex(index)


class BlendMethodPanel(QWidget):
    """Panel for a specific blend method with its parameters."""
    
    parameters_changed = pyqtSignal()
    
    def __init__(self, blender, parent=None):
        super().__init__(parent)
        self.blender = blender
        self.param_widgets = {}
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Method description
        desc_label = QLabel(self.blender.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #aaa; font-style: italic;")
        desc_label.setFixedHeight(60)
        layout.addWidget(desc_label)
        
        # Parameters group
        param_group = QGroupBox("Parameters")
        param_layout = QFormLayout(param_group)
        
        for param in self.blender.get_parameter_list():
            widget = BlendParameterWidget(param)
            widget.parameter_changed.connect(self._on_parameter_changed)
            param_layout.addRow(widget)
            self.param_widgets[param.name] = widget
        
        layout.addWidget(param_group)
        layout.addStretch()
    
    def _on_parameter_changed(self, param_name, value):
        """Handle parameter change."""
        self.blender.set_parameter_value(param_name, value)
        self.parameters_changed.emit()
    
    def update_from_blender(self):
        """Update controls from the blender parameters."""
        for name, widget in self.param_widgets.items():
            param = self.blender.get_parameter(name)
            if param:
                widget.update_value(param.value)


class GradientBlendingWidget(QWidget):
    """Main widget for gradient blending functionality."""
    
    gradient_blended = pyqtSignal(object)
    gradients_added = pyqtSignal()
    
    def __init__(self, gradient_model):
        super().__init__()
        self.gradient_model = gradient_model
        self.merge_list = []
        self.blender_panels = {}
        self.current_blender = None
        
        self._init_ui()
        self._init_blenders()
    
    def _init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: Gradient selection
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel: Blend options and preview
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 600])
        main_layout.addWidget(splitter)
    
    def _create_left_panel(self):
        """Create the left panel for gradient selection."""
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Source selection group
        source_group = QGroupBox("Source Gradients")
        source_layout = QVBoxLayout(source_group)
        
        # Add buttons
        buttons = [
            ("Add Current Gradient", self._add_current_gradient),
            ("Add All From List", self._add_from_gradient_list),
            ("Add Selected From List", self._add_selected_from_gradient_list)
        ]
        
        for text, handler in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            if "Selected" in text:
                btn.setToolTip("Add only the selected gradients from the gradient list")
            source_layout.addWidget(btn)
        
        left_layout.addWidget(source_group)
        
        # Merge list group
        merge_list_group = QGroupBox("Gradients to Blend")
        merge_list_layout = QVBoxLayout(merge_list_group)
        
        # List widget
        self.merge_list_widget = QListWidget()
        self.merge_list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        self.merge_list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.merge_list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        merge_list_layout.addWidget(self.merge_list_widget)
        
        # Weight control
        weight_layout = QHBoxLayout()
        weight_layout.addWidget(QLabel("Weight:"))
        
        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0.0, 10.0)
        self.weight_spin.setSingleStep(0.1)
        self.weight_spin.setValue(1.0)
        self.weight_spin.valueChanged.connect(self._on_weight_changed)
        self.weight_spin.setEnabled(False)
        weight_layout.addWidget(self.weight_spin)
        merge_list_layout.addLayout(weight_layout)
        
        # Button row
        button_layout = QHBoxLayout()
        
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self._remove_selected)
        self.remove_button.setEnabled(False)
        button_layout.addWidget(self.remove_button)
        
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self._clear_merge_list)
        button_layout.addWidget(self.clear_button)
        
        merge_list_layout.addLayout(button_layout)
        left_layout.addWidget(merge_list_group)
        
        return left_panel
    
    def _create_right_panel(self):
        """Create the right panel for blend options and preview."""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Blend method selection
        method_group = QGroupBox("Blend Method")
        method_layout = QVBoxLayout(method_group)
        
        self.method_combo = QComboBox()
        self.method_combo.currentTextChanged.connect(self._on_method_changed)
        method_layout.addWidget(self.method_combo)
        
        # Stacked widget for method-specific parameters
        self.method_stack = QStackedWidget()
        method_layout.addWidget(self.method_stack)
        
        right_layout.addWidget(method_group)
        
        # Preview group
        preview_group = QGroupBox("Preview")
        preview_group.setFixedHeight(180)
        preview_layout = QVBoxLayout(preview_group)
        
        self.merged_preview = GradientPreviewWidget(None, "Blended Gradient")
        preview_layout.addWidget(self.merged_preview)
        
        self.blend_button = QPushButton("Apply Blended Gradient")
        self.blend_button.clicked.connect(self._apply_blended_gradient)
        self.blend_button.setEnabled(False)
        preview_layout.addWidget(self.blend_button)
        
        right_layout.addWidget(preview_group)
        
        # Method details
        details_group = QGroupBox("Method Description")
        details_layout = QVBoxLayout(details_group)
        
        self.details_label = QLabel()
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet("color: #aaa; font-style: italic;")
        details_layout.addWidget(self.details_label)
        
        details_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        right_layout.addWidget(details_group)
        
        return right_panel
    
    def _init_blenders(self):
        """Initialize blend method panels."""
        self.method_combo.clear()
        blenders = BlendRegistry.get_all_blenders() if BLENDING_AVAILABLE else []
        
        if not blenders:
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_label = QLabel("No blend methods available.\nPlease check your installation.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_layout.addWidget(empty_label)
            self.method_stack.addWidget(empty_widget)
            self.method_combo.addItem("None")
            return
        
        for blender in blenders:
            panel = BlendMethodPanel(blender)
            panel.parameters_changed.connect(self._update_blend_preview)
            
            self.method_stack.addWidget(panel)
            self.method_combo.addItem(blender.name)
            self.blender_panels[blender.name] = panel
        
        if blenders:
            self.method_combo.setCurrentText(blenders[0].name)
            self.current_blender = blenders[0]
    
    def _add_current_gradient(self):
        """Add the current gradient to the merge list."""
        gradient_copy = self.gradient_model.clone()
        name = gradient_copy.get_name() or "Current Gradient"
        self._add_gradient_to_list(gradient_copy, name, 1.0)
        self.gradients_added.emit()
    
    def _add_from_gradient_list(self):
        """Add ALL gradients from the main gradient list panel."""
        main_window = self.window()
        
        if hasattr(main_window, 'gradient_list_panel'):
            gradients = main_window.gradient_list_panel.gradients
            
            if not gradients:
                QMessageBox.information(self, "No Gradients", 
                    "No gradients found in the list panel. Add some gradients first.")
                return
            
            for gradient, name in gradients:
                gradient_copy = gradient.clone()
                self._add_gradient_to_list(gradient_copy, name, 1.0)
                
            self._update_blend_preview()
            self.gradients_added.emit()
        else:
            QMessageBox.warning(self, "Error", "Could not access the gradient list panel.")
    
    def _add_selected_from_gradient_list(self):
        """Add only SELECTED gradients from the main gradient list panel."""
        main_window = self.window()
        
        if hasattr(main_window, 'gradient_list_panel'):
            gradient_list_panel = main_window.gradient_list_panel
            selected_items = gradient_list_panel.list_widget.selectedItems()
            
            if not selected_items:
                QMessageBox.information(self, "No Selection", 
                    "No gradients selected in the list panel. Please select gradients first.")
                return
            
            if not gradient_list_panel.gradients:
                QMessageBox.information(self, "No Gradients", 
                    "No gradients found in the list panel. Add some gradients first.")
                return
            
            added_count = 0
            for item in selected_items:
                index = gradient_list_panel.list_widget.row(item)
                
                if 0 <= index < len(gradient_list_panel.gradients):
                    gradient, name = gradient_list_panel.gradients[index]
                    gradient_copy = gradient.clone()
                    self._add_gradient_to_list(gradient_copy, name, 1.0)
                    added_count += 1
            
            if added_count > 0:
                self._update_blend_preview()
                QMessageBox.information(self, "Gradients Added", 
                    f"Added {added_count} selected gradient(s) to the blend list.")
                self.gradients_added.emit()
            else:
                QMessageBox.warning(self, "Error", 
                    "Failed to add selected gradients. Please try again.")
        else:
            QMessageBox.warning(self, "Error", "Could not access the gradient list panel.")
    
    def _add_gradient_to_list(self, gradient, name, weight):
        """Add a gradient to the merge list."""
        item = GradientListItem(gradient, name, weight)
        self.merge_list_widget.addItem(item)
        self.merge_list.append((gradient, weight))
        self._update_blend_preview()
    
    def _remove_selected(self):
        """Remove the selected gradients from the merge list."""
        selected_items = self.merge_list_widget.selectedItems()
        
        if not selected_items:
            return
            
        for item in selected_items:
            index = self.merge_list_widget.row(item)
            self.merge_list_widget.takeItem(index)
            if 0 <= index < len(self.merge_list):
                self.merge_list.pop(index)
        
        self._update_blend_preview()
        self._on_selection_changed()
    
    def _clear_merge_list(self):
        """Clear the merge list."""
        if not self.merge_list:
            return
            
        self.merge_list_widget.clear()
        self.merge_list = []
        self._update_blend_preview()
        self._on_selection_changed()
    
    def _on_selection_changed(self):
        """Handle selection change in the merge list."""
        selected_items = self.merge_list_widget.selectedItems()
        has_selection = len(selected_items) > 0
        
        self.remove_button.setEnabled(has_selection)
        self.weight_spin.setEnabled(len(selected_items) == 1)
        
        if len(selected_items) == 1:
            item = selected_items[0]
            self.weight_spin.setValue(item.weight)
    
    def _on_weight_changed(self, value):
        """Handle weight change."""
        selected_items = self.merge_list_widget.selectedItems()
        
        if len(selected_items) == 1:
            item = selected_items[0]
            item.set_weight(value)
            
            index = self.merge_list_widget.row(item)
            if 0 <= index < len(self.merge_list):
                gradient, _ = self.merge_list[index]
                self.merge_list[index] = (gradient, value)
            
            self._update_blend_preview()
    
    def _on_method_changed(self, method_name):
        """Handle method selection change."""
        blender = BlendRegistry.get_blender(method_name) if BLENDING_AVAILABLE else None
        
        if not blender:
            return
            
        self.current_blender = blender
        
        if method_name in self.blender_panels:
            panel = self.blender_panels[method_name]
            self.method_stack.setCurrentWidget(panel)
        
        self._update_blend_preview()
        self._update_method_description()
    
    def _update_method_description(self):
        """Update the method description based on the selected method."""
        if not self.current_blender:
            self.details_label.setText("")
            return
            
        self.details_label.setText(self.current_blender.description)
    
    def _update_blend_preview(self):
        """Update the merged gradient preview."""
        if not self.merge_list or not self.current_blender:
            self.merged_preview.set_gradient(None)
            self.blend_button.setEnabled(False)
            return
        
        merged_gradient = self.current_blender.blend_gradients(self.merge_list)
        self.merged_preview.set_gradient(merged_gradient)
        
        name = f"Blended Gradient ({self.current_blender.name})"
        merged_gradient.set_name(name)
        self.merged_preview.set_title(name)
        
        self.blend_button.setEnabled(True)
    
    def _apply_blended_gradient(self):
        """Apply the merged gradient to the current gradient model."""
        if not self.merge_list or not self.current_blender:
            return
            
        merged_gradient = self.current_blender.blend_gradients(self.merge_list)
        self.gradient_blended.emit(merged_gradient)