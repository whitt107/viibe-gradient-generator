#!/usr/bin/env python3
"""
Gradient Comparison Dialog for Gradient Generator

This module provides a dialog for comparing multiple gradients side by side.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QSplitter, QWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QPainter, QLinearGradient, QColor


class GradientComparisonWidget(QWidget):
    """Widget showing a single gradient for comparison."""
    
    def __init__(self, gradient, name):
        super().__init__()
        
        self.gradient = gradient
        self.name = name
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Name label
        name_label = QLabel(self.name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(name_label)
        
        # Gradient preview
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(200, 100)
        layout.addWidget(self.preview_label)
        
        # Gradient info
        info_text = f"Stops: {len(self.gradient.get_color_stops())}"
        if self.gradient.get_seamless_blend():
            info_text += "\nSeamless: Yes"
        if self.gradient.get_author():
            info_text += f"\nAuthor: {self.gradient.get_author()}"
        
        info_label = QLabel(info_text)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #888;")
        layout.addWidget(info_label)
        
        # Update preview
        self.update_preview()
    
    def update_preview(self):
        """Update the gradient preview."""
        width = 200
        height = 100
        
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create linear gradient
        gradient = QLinearGradient(0, 0, width, 0)
        
        # Add color stops
        for position, color in self.gradient.get_color_stops():
            gradient.setColorAt(position, QColor(*color))
        
        # Draw gradient
        painter.fillRect(pixmap.rect(), gradient)
        
        # Draw border
        painter.setPen(QColor(80, 80, 80))
        painter.drawRect(pixmap.rect())
        
        painter.end()
        
        self.preview_label.setPixmap(pixmap)
    
    def resizeEvent(self, event):
        """Handle resize event."""
        super().resizeEvent(event)
        self.update_preview()


class GradientComparisonDialog(QDialog):
    """Dialog for comparing multiple gradients."""
    
    def __init__(self, gradients, parent=None):
        super().__init__(parent)
        
        self.gradients = gradients  # List of (gradient, name) tuples
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Gradient Comparison")
        self.setModal(True)
        self.resize(800, 400)
        
        main_layout = QVBoxLayout(self)
        
        # Create splitter for gradient comparisons
        splitter = QSplitter(Qt.Horizontal)
        
        # Create comparison widgets
        for gradient, name in self.gradients:
            widget = GradientComparisonWidget(gradient, name)
            splitter.addWidget(widget)
        
        # Make all sections equal size
        sizes = [1] * len(self.gradients)
        splitter.setSizes(sizes)
        
        main_layout.addWidget(splitter)
        
        # Button row
        button_layout = QHBoxLayout()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
