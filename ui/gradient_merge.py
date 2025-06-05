#!/usr/bin/env python3
"""
Refactored Gradient Merge Module for Gradient Generator

Streamlined version that maintains all functionality while reducing code size.
Supports merging multiple gradients with various methods and weighting options.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QListWidget, QListWidgetItem, QComboBox,
                           QDoubleSpinBox, QGroupBox, QFormLayout, QSplitter,
                           QMessageBox, QCheckBox, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QPainter, QLinearGradient, QColor, QIcon

import copy
import bisect
from ..core.gradient import Gradient
from ..core.color_utils import rgb_to_hsv, hsv_to_rgb


class GradientPreviewWidget(QWidget):
    """Compact widget for displaying gradient previews."""
    
    def __init__(self, gradient, title="Preview"):
        super().__init__()
        self.gradient = gradient
        self.title = title
        self.setMinimumHeight(80)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        self.preview_area = QLabel()
        self.preview_area.setMinimumHeight(60)
        self.preview_area.setStyleSheet("border: 1px solid #555;")
        layout.addWidget(self.preview_area)
        
        self.update_preview()
    
    def update_preview(self):
        if not self.gradient:
            return
            
        width, height = self.preview_area.width() or 300, 60
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        qgradient = QLinearGradient(0, 0, width, 0)
        for position, color in self.gradient.get_color_stops():
            qgradient.setColorAt(position, QColor(*color))
        
        painter.fillRect(0, 0, width, height, qgradient)
        painter.setPen(QColor(80, 80, 80))
        painter.drawRect(0, 0, width-1, height-1)
        painter.end()
        
        self.preview_area.setPixmap(pixmap)
    
    def set_gradient(self, gradient):
        self.gradient = gradient
        self.update_preview()
    
    def set_title(self, title):
        self.title = title
        self.title_label.setText(title)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_preview()


class GradientListItem(QListWidgetItem):
    """Compact list item with gradient preview."""
    
    def __init__(self, gradient, name=None, weight=1.0):
        super().__init__()
        self.gradient = gradient
        self.name = name or gradient.get_name() or "Unnamed Gradient"
        self.weight = weight
        
        self.setText(f"{self.name} (weight: {self.weight:.2f})")
        self._create_preview()
        self.setSizeHint(QSize(200, 60))
    
    def _create_preview(self):
        pixmap = QPixmap(150, 25)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        gradient = QLinearGradient(0, 0, pixmap.width(), 0)
        for position, color in self.gradient.get_color_stops():
            gradient.setColorAt(position, QColor(*color))
        
        painter.fillRect(pixmap.rect(), gradient)
        painter.setPen(QColor(80, 80, 80))
        painter.drawRect(pixmap.rect())
        painter.end()
        
        self.setIcon(QIcon(pixmap))
    
    def set_weight(self, weight):
        self.weight = weight
        self.setText(f"{self.name} (weight: {self.weight:.2f})")


class GradientMerger:
    """Handles gradient merging with multiple algorithms."""
    
    @staticmethod
    def merge_gradients(gradients_with_weights, method="interleave", use_weights=True):
        if not gradients_with_weights:
            return Gradient()
        if len(gradients_with_weights) == 1:
            return gradients_with_weights[0][0].clone()
        
        methods = {
            "interleave": GradientMerger._merge_interleave,
            "blend": GradientMerger._merge_blend,
            "crossfade": GradientMerger._merge_crossfade,
            "stack": GradientMerger._merge_stack
        }
        
        merge_func = methods.get(method, GradientMerger._merge_interleave)
        return merge_func(gradients_with_weights, use_weights)
    
    @staticmethod
    def _merge_interleave(gradients_with_weights, use_weights):
        merged_gradient = Gradient()
        merged_gradient._color_stops = []
        
        all_stops = []
        for gradient, weight in gradients_with_weights:
            if use_weights and weight <= 0:
                continue
            stops = gradient.get_color_stops()
            weighted_stops = [(pos, color, weight if use_weights else 1.0) for pos, color in stops]
            all_stops.extend(weighted_stops)
        
        all_stops.sort(key=lambda s: s[0])
        
        # Group stops by position with tolerance
        grouped_stops = []
        current_group = []
        epsilon = 0.001
        
        for pos, color, weight in all_stops:
            if not current_group or abs(pos - current_group[0][0]) <= epsilon:
                current_group.append((pos, color, weight))
            else:
                grouped_stops.append(current_group)
                current_group = [(pos, color, weight)]
        
        if current_group:
            grouped_stops.append(current_group)
        
        # Process groups
        for group in grouped_stops:
            avg_pos = sum(pos for pos, _, _ in group) / len(group)
            
            if use_weights:
                max_weight_color = max(group, key=lambda s: s[2])[1]
                merged_gradient.add_color_stop(avg_pos, max_weight_color)
            else:
                for i, (_, color, _) in enumerate(group):
                    offset_pos = avg_pos + (i * epsilon)
                    merged_gradient.add_color_stop(min(offset_pos, 1.0), color)
        
        merged_gradient.set_name("Merged Gradient (Interleave)")
        return merged_gradient
    
    @staticmethod
    def _merge_blend(gradients_with_weights, use_weights):
        merged_gradient = Gradient()
        merged_gradient._color_stops = []
        
        # Get unique positions
        unique_positions = set()
        for gradient, _ in gradients_with_weights:
            for pos, _ in gradient.get_color_stops():
                unique_positions.add(pos)
        
        for pos in sorted(unique_positions):
            blended_color = [0, 0, 0]
            total_weight = 0
            
            for gradient, weight in gradients_with_weights:
                if use_weights and weight <= 0:
                    continue
                
                color = gradient.get_interpolated_color(pos)
                factor = weight if use_weights else 1.0
                total_weight += factor
                
                for i in range(3):
                    blended_color[i] += color[i] * factor
            
            if total_weight > 0:
                blended_color = tuple(min(255, max(0, int(c / total_weight))) for c in blended_color)
                merged_gradient.add_color_stop(pos, blended_color)
        
        merged_gradient.set_name("Merged Gradient (Blend)")
        return merged_gradient
    
    @staticmethod
    def _merge_crossfade(gradients_with_weights, use_weights):
        merged_gradient = Gradient()
        merged_gradient._color_stops = []
        
        if use_weights:
            gradients_with_weights = [(g, w) for g, w in gradients_with_weights if w > 0]
        
        if not gradients_with_weights:
            return merged_gradient
        
        # Normalize weights
        if use_weights:
            total_weight = sum(weight for _, weight in gradients_with_weights)
            normalized_weights = [weight / total_weight for _, weight in gradients_with_weights]
        else:
            normalized_weights = [1.0 / len(gradients_with_weights)] * len(gradients_with_weights)
        
        num_samples = max(2, min(100, len(gradients_with_weights) * 10))
        
        for i in range(num_samples):
            pos = i / (num_samples - 1) if num_samples > 1 else 0
            
            # Calculate which gradient is active
            weight_sum = 0
            active_gradient_index = 0
            
            for idx, weight in enumerate(normalized_weights):
                weight_sum += weight
                if pos <= weight_sum:
                    active_gradient_index = idx
                    break
            
            gradient, _ = gradients_with_weights[active_gradient_index]
            color = gradient.get_interpolated_color(pos)
            merged_gradient.add_color_stop(pos, color)
        
        merged_gradient.set_name("Merged Gradient (Crossfade)")
        return merged_gradient
    
    @staticmethod
    def _merge_stack(gradients_with_weights, use_weights):
        merged_gradient = Gradient()
        merged_gradient._color_stops = []
        
        if use_weights:
            gradients_with_weights = [(g, w) for g, w in gradients_with_weights if w > 0]
        
        if not gradients_with_weights:
            return merged_gradient
        
        # Calculate segment sizes
        if use_weights:
            total_weight = sum(weight for _, weight in gradients_with_weights)
            segment_sizes = [weight / total_weight for _, weight in gradients_with_weights]
        else:
            segment_sizes = [1.0 / len(gradients_with_weights)] * len(gradients_with_weights)
        
        start_pos = 0
        for i, (gradient, _) in enumerate(gradients_with_weights):
            segment_size = segment_sizes[i]
            end_pos = min(1.0, start_pos + segment_size)
            
            stops = gradient.get_color_stops()
            if not stops:
                start_pos = end_pos
                continue
            
            for original_pos, color in stops:
                mapped_pos = start_pos + original_pos * (end_pos - start_pos)
                merged_gradient.add_color_stop(mapped_pos, color)
            
            start_pos = end_pos
        
        merged_gradient.set_name("Merged Gradient (Stack)")
        return merged_gradient


class GradientMergeWidget(QWidget):
    """Streamlined widget for merging gradients."""
    
    gradient_merged = pyqtSignal(object)
    
    def __init__(self, gradient_model, parent=None):
        super().__init__(parent)
        self.gradient_model = gradient_model
        self.merge_list = []
        self._init_ui()
    
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 600])
        main_layout.addWidget(splitter)
    
    def _create_left_panel(self):
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Source gradients
        source_group = QGroupBox("Source Gradients")
        source_layout = QVBoxLayout(source_group)
        
        buttons = [
            ("Add Current Gradient", self._add_current_gradient),
            ("Add From Gradient List", self._add_from_gradient_list)
        ]
        
        for text, handler in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            source_layout.addWidget(btn)
        
        left_layout.addWidget(source_group)
        
        # Merge list
        merge_list_group = QGroupBox("Gradients to Merge")
        merge_list_layout = QVBoxLayout(merge_list_group)
        
        self.merge_list_widget = QListWidget()
        self.merge_list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        self.merge_list_widget.itemSelectionChanged.connect(self._on_selection_changed)
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
        
        # Buttons
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
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Merge options
        options_group = QGroupBox("Merge Options")
        options_layout = QFormLayout(options_group)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Interleave (Alternate Stops)",
            "Blend (Color Mixing)",
            "Crossfade (Sequential Transition)",
            "Stack (Sequential Segments)"
        ])
        self.method_combo.currentTextChanged.connect(self._on_options_changed)
        options_layout.addRow("Merge Method:", self.method_combo)
        
        self.use_weights_check = QCheckBox("Use Weights")
        self.use_weights_check.setChecked(True)
        self.use_weights_check.stateChanged.connect(self._on_options_changed)
        options_layout.addRow("", self.use_weights_check)
        
        right_layout.addWidget(options_group)
        
        # Preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.merged_preview = GradientPreviewWidget(None, "Merged Gradient")
        preview_layout.addWidget(self.merged_preview)
        
        self.merge_button = QPushButton("Apply Merged Gradient")
        self.merge_button.clicked.connect(self._apply_merged_gradient)
        self.merge_button.setEnabled(False)
        preview_layout.addWidget(self.merge_button)
        
        right_layout.addWidget(preview_group)
        
        # Method details
        details_group = QGroupBox("Method Description")
        details_layout = QVBoxLayout(details_group)
        
        self.details_label = QLabel()
        self.details_label.setWordWrap(True)
        self._update_method_description()
        details_layout.addWidget(self.details_label)
        
        right_layout.addWidget(details_group)
        
        return right_panel
    
    def _add_current_gradient(self):
        gradient_copy = self.gradient_model.clone()
        name = gradient_copy.get_name() or "Current Gradient"
        self._add_gradient_to_list(gradient_copy, name, 1.0)
    
    def _add_from_gradient_list(self):
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
                
            self._update_merge_preview()
        else:
            QMessageBox.warning(self, "Error", "Could not access the gradient list panel.")
    
    def _add_gradient_to_list(self, gradient, name, weight):
        item = GradientListItem(gradient, name, weight)
        self.merge_list_widget.addItem(item)
        self.merge_list.append((gradient, weight))
        self._update_merge_preview()
    
    def _remove_selected(self):
        selected_items = self.merge_list_widget.selectedItems()
        
        for item in selected_items:
            index = self.merge_list_widget.row(item)
            self.merge_list_widget.takeItem(index)
            if 0 <= index < len(self.merge_list):
                self.merge_list.pop(index)
        
        self._update_merge_preview()
        self._on_selection_changed()
    
    def _clear_merge_list(self):
        if not self.merge_list:
            return
        
        self.merge_list_widget.clear()
        self.merge_list = []
        self._update_merge_preview()
        self._on_selection_changed()
    
    def _on_selection_changed(self):
        selected_items = self.merge_list_widget.selectedItems()
        has_selection = len(selected_items) > 0
        
        self.remove_button.setEnabled(has_selection)
        self.weight_spin.setEnabled(len(selected_items) == 1)
        
        if len(selected_items) == 1:
            item = selected_items[0]
            self.weight_spin.setValue(item.weight)
    
    def _on_weight_changed(self, value):
        selected_items = self.merge_list_widget.selectedItems()
        
        if len(selected_items) == 1:
            item = selected_items[0]
            item.set_weight(value)
            
            index = self.merge_list_widget.row(item)
            if 0 <= index < len(self.merge_list):
                gradient, _ = self.merge_list[index]
                self.merge_list[index] = (gradient, value)
            
            self._update_merge_preview()
    
    def _on_options_changed(self):
        self._update_method_description()
        self._update_merge_preview()
    
    def _update_method_description(self):
        method = self.method_combo.currentText().split(" ")[0].lower()
        
        descriptions = {
            "interleave": "Preserves all color stops from all gradients, keeping their "
                         "original positions. If multiple stops have the same position, the highest "
                         "weighted gradient's color is used (if weights are enabled).",
            "blend": "Mixes colors at each position by combining RGB components from all "
                    "gradients. The contribution of each gradient is determined by its weight. "
                    "This creates smooth transitions between all contributing gradients.",
            "crossfade": "Creates a sequential transition between gradients, similar to a "
                        "crossfade in audio. Each gradient is allocated a portion of the range based "
                        "on its weight. This method maintains the original appearance of each gradient.",
            "stack": "Divides the gradient range into segments, with each gradient occupying "
                    "a portion proportional to its weight. This preserves each gradient's appearance "
                    "but compresses it to fit in its segment of the range."
        }
        
        self.details_label.setText(descriptions.get(method, ""))
    
    def _update_merge_preview(self):
        if not self.merge_list:
            self.merged_preview.set_gradient(None)
            self.merge_button.setEnabled(False)
            return
        
        method_text = self.method_combo.currentText().split(" ")[0].lower()
        use_weights = self.use_weights_check.isChecked()
        
        merged_gradient = GradientMerger.merge_gradients(
            self.merge_list, method_text, use_weights
        )
        
        self.merged_preview.set_gradient(merged_gradient)
        
        name = f"Merged Gradient ({method_text.capitalize()})"
        merged_gradient.set_name(name)
        self.merged_preview.set_title(name)
        
        self.merge_button.setEnabled(True)
    
    def _apply_merged_gradient(self):
        if not self.merge_list:
            return
            
        method_text = self.method_combo.currentText().split(" ")[0].lower()
        use_weights = self.use_weights_check.isChecked()
        
        merged_gradient = GradientMerger.merge_gradients(
            self.merge_list, method_text, use_weights
        )
        
        self.gradient_merged.emit(merged_gradient)
