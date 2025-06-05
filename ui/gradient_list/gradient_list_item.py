#!/usr/bin/env python3
"""
Gradient List Item Module for Gradient Generator

This module contains the GradientListItem class and related functionality
for managing individual items in the gradient list panel.
"""
from PyQt5.QtWidgets import QListWidgetItem, QLabel
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QPainter, QLinearGradient, QColor, QIcon


class GradientListItem(QListWidgetItem):
    """Custom list item that holds a gradient and displays its preview."""
    
    def __init__(self, gradient, name=None, weight=1.0):
        super().__init__()
        
        self.gradient = gradient
        self.name = name or gradient.get_name() or "Unnamed Gradient"
        self.weight = weight
        
        # Set text
        self.setText(self.name)
        
        # Create preview pixmap
        self.create_preview()
        
        # Set size hint - increased for larger previews
        self.setSizeHint(QSize(200, 80))
    
    def create_preview(self):
        """Create a preview pixmap of the gradient."""
        # Create pixmap - increased size for better visualization
        pixmap = QPixmap(180, 60)
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
        
        # Set icon - convert QPixmap to QIcon
        self.setIcon(QIcon(pixmap))
        
        # The DecorationSize should not be set directly, 
        # instead we'll rely on the list widget's setIconSize method
    
    def update_name(self, name):
        """Update the gradient name."""
        self.name = name
        self.setText(name)
        self.gradient.set_name(name)
    
    def set_weight(self, weight):
        """Set the gradient weight."""
        self.weight = weight
        self.setText(f"{self.name} (weight: {self.weight:.2f})")


def create_mini_preview(gradient, width=40, height=20):
    """
    Create a small preview widget for the strip.
    
    Args:
        gradient: The gradient to preview
        width: Preview width
        height: Preview height
        
    Returns:
        QLabel with the gradient preview
    """
    from PyQt5.QtWidgets import QLabel
    from PyQt5.QtCore import Qt
    
    preview = QLabel()
    preview.setFixedSize(width, height)
    
    # Create pixmap
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)
    
    # Create painter
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Create linear gradient
    qgradient = QLinearGradient(0, 0, pixmap.width(), 0)
    
    # Add color stops
    for position, color in gradient.get_color_stops():
        qgradient.setColorAt(position, QColor(*color))
    
    # Draw gradient
    painter.fillRect(pixmap.rect(), qgradient)
    
    painter.end()
    
    preview.setPixmap(pixmap)
    return preview
