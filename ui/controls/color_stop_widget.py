#!/usr/bin/env python3
"""
Color Stop Widget Module for Gradient Generator

This module provides the UI widget for editing a single color stop in the gradient.
"""
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton, 
                           QLabel, QDoubleSpinBox, QColorDialog, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QColor


class ColorStopWidget(QWidget):
    """Widget for editing a single color stop in the gradient."""
    
    color_changed = pyqtSignal(int, object)  # index, (r, g, b)
    position_changed = pyqtSignal(int, float)  # index, position
    delete_requested = pyqtSignal(int)  # index
    
    def __init__(self, index, position, color, parent=None):
        super().__init__(parent)
        
        self.index = index
        self.position = position
        self.color = color  # (r, g, b)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Index label
        self.index_label = QLabel(f"#{self.index+1}")
        self.index_label.setFixedWidth(30)
        layout.addWidget(self.index_label)
        
        # Position control
        self.position_spin = QDoubleSpinBox()
        self.position_spin.setRange(0.0, 1.0)
        self.position_spin.setSingleStep(0.01)
        self.position_spin.setDecimals(3)
        self.position_spin.setValue(self.position)
        self.position_spin.valueChanged.connect(self.on_position_changed)
        layout.addWidget(self.position_spin)
        
        # Color button
        self.color_button = QPushButton()
        self.color_button.setFixedSize(QSize(24, 24))
        self.update_color_button()
        self.color_button.clicked.connect(self.on_color_button_clicked)
        layout.addWidget(self.color_button)
        
        # Color values
        r, g, b = self.color
        
        self.r_spin = QSpinBox()
        self.r_spin.setRange(0, 255)
        self.r_spin.setValue(r)
        self.r_spin.valueChanged.connect(self.on_r_changed)
        layout.addWidget(self.r_spin)
        
        self.g_spin = QSpinBox()
        self.g_spin.setRange(0, 255)
        self.g_spin.setValue(g)
        self.g_spin.valueChanged.connect(self.on_g_changed)
        layout.addWidget(self.g_spin)
        
        self.b_spin = QSpinBox()
        self.b_spin.setRange(0, 255)
        self.b_spin.setValue(b)
        self.b_spin.valueChanged.connect(self.on_b_changed)
        layout.addWidget(self.b_spin)
        
        # Delete button
        self.delete_button = QPushButton("×")
        self.delete_button.setFixedSize(QSize(24, 24))
        self.delete_button.clicked.connect(self.on_delete)
        layout.addWidget(self.delete_button)
    
    def update_color_button(self):
        """Update the color button to reflect the current color."""
        r, g, b = self.color
        color_style = f"background-color: rgb({r}, {g}, {b});"
        self.color_button.setStyleSheet(f"""
            QPushButton {{
                {color_style}
                border: 1px solid #888;
            }}
            QPushButton:hover {{
                border: 1px solid white;
            }}
        """)
    
    def on_color_button_clicked(self):
        """Handle color button click - open color dialog."""
        r, g, b = self.color
        color = QColorDialog.getColor(QColor(r, g, b), self, "Select Color")
        
        if color.isValid():
            self.color = (color.red(), color.green(), color.blue())
            self.update_color_button()
            
            # Update RGB spinners
            self.r_spin.blockSignals(True)
            self.g_spin.blockSignals(True)
            self.b_spin.blockSignals(True)
            
            self.r_spin.setValue(color.red())
            self.g_spin.setValue(color.green())
            self.b_spin.setValue(color.blue())
            
            self.r_spin.blockSignals(False)
            self.g_spin.blockSignals(False)
            self.b_spin.blockSignals(False)
            
            # Emit signal
            self.color_changed.emit(self.index, self.color)
    
    def on_position_changed(self, value):
        """Handle position change."""
        self.position = value
        self.position_changed.emit(self.index, value)
    
    def on_r_changed(self, value):
        """Handle red component change."""
        _, g, b = self.color
        self.color = (value, g, b)
        self.update_color_button()
        self.color_changed.emit(self.index, self.color)
    
    def on_g_changed(self, value):
        """Handle green component change."""
        r, _, b = self.color
        self.color = (r, value, b)
        self.update_color_button()
        self.color_changed.emit(self.index, self.color)
    
    def on_b_changed(self, value):
        """Handle blue component change."""
        r, g, _ = self.color
        self.color = (r, g, value)
        self.update_color_button()
        self.color_changed.emit(self.index, self.color)
    
    def on_delete(self):
        """Handle delete button click."""
        self.delete_requested.emit(self.index)
