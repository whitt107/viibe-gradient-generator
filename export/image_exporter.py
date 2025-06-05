#!/usr/bin/env python3
"""
Image Exporter Module for Gradient Generator

This module implements functionality to export gradients as image files
in various formats, including PNG and JPG.
"""
import os
from PyQt5.QtGui import QImage, QPainter, QLinearGradient, QRadialGradient, QConicalGradient, QColor, QPen
from PyQt5.QtCore import Qt, QRect


class ImageExporter:
    """Class for exporting gradients as image files."""
    
    def __init__(self):
        """Initialize the exporter with default settings."""
        self.quality = 100  # For JPEG compression (0-100)
        self.size = 512     # Default size for exported images
        self.gradient_type = "linear"  # linear, radial, conical
        self.draw_points = False  # Whether to draw color stop points
    
    def set_quality(self, quality):
        """Set the image quality (for JPEG)."""
        self.quality = max(1, min(100, quality))
    
    def set_size(self, size):
        """Set the image size."""
        self.size = max(64, min(4096, size))
    
    def set_gradient_type(self, gradient_type):
        """Set the gradient type."""
        if gradient_type in ["linear", "radial", "conical"]:
            self.gradient_type = gradient_type
    
    def set_draw_points(self, draw_points):
        """Set whether to draw color stop points."""
        self.draw_points = draw_points
    
    def export(self, gradient, file_path):
        """
        Export gradient as an image file.
        
        Args:
            gradient: Gradient object to export
            file_path: Path where the image will be saved
        
        Returns:
            True if export was successful, False otherwise
        """
        # Create a QImage with the specified size
        image = QImage(self.size, self.size, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        
        # Create painter
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get color stops
        color_stops = gradient.get_color_stops()
        
        # Draw the gradient based on type
        rect = QRect(0, 0, self.size, self.size)
        
        if self.gradient_type == "linear":
            self._draw_linear_gradient(painter, rect, color_stops)
        elif self.gradient_type == "radial":
            self._draw_radial_gradient(painter, rect, color_stops)
        elif self.gradient_type == "conical":
            self._draw_conical_gradient(painter, rect, color_stops)
        
        # Draw color stop points if enabled
        if self.draw_points:
            self._draw_color_points(painter, rect, color_stops)
        
        # End painting
        painter.end()
        
        # Determine file format based on extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Save the image
        success = False
        
        if ext == ".png":
            success = image.save(file_path, "PNG")
        elif ext == ".jpg" or ext == ".jpeg":
            success = image.save(file_path, "JPEG", self.quality)
        else:
            # Default to PNG
            success = image.save(file_path, "PNG")
        
        return success
    
    def _draw_linear_gradient(self, painter, rect, color_stops):
        """Draw a linear gradient."""
        # Create gradient
        gradient = QLinearGradient(
            rect.left(), rect.top(), 
            rect.right(), rect.top()
        )
        
        # Add color stops
        for position, color in color_stops:
            gradient.setColorAt(position, QColor(*color))
        
        # Draw gradient
        painter.fillRect(rect, gradient)
        
        # Draw border
        painter.setPen(QColor(80, 80, 80))
        painter.drawRect(rect)
    
    def _draw_radial_gradient(self, painter, rect, color_stops):
        """Draw a radial gradient."""
        # Create gradient
        center_x = rect.left() + rect.width() // 2
        center_y = rect.top() + rect.height() // 2
        radius = rect.width() // 2
        
        gradient = QRadialGradient(
            center_x, center_y, radius,
            center_x, center_y
        )
        
        # Add color stops
        for position, color in color_stops:
            gradient.setColorAt(position, QColor(*color))
        
        # Draw gradient
        painter.fillRect(rect, gradient)
        
        # Draw border
        painter.setPen(QColor(80, 80, 80))
        painter.drawRect(rect)
    
    def _draw_conical_gradient(self, painter, rect, color_stops):
        """Draw a conical gradient."""
        # Create gradient
        center_x = rect.left() + rect.width() // 2
        center_y = rect.top() + rect.height() // 2
        
        gradient = QConicalGradient(
            center_x, center_y, 0
        )
        
        # Add color stops
        for position, color in color_stops:
            gradient.setColorAt(position, QColor(*color))
        
        # Draw gradient
        painter.fillRect(rect, gradient)
        
        # Draw border
        painter.setPen(QColor(80, 80, 80))
        painter.drawRect(rect)
    
    def _draw_color_points(self, painter, rect, color_stops):
        """Draw color stop points."""
        # Linear gradient points are drawn along the top edge
        if self.gradient_type == "linear":
            y = rect.top()
            for position, color in color_stops:
                x = rect.left() + int(position * rect.width())
                
                # Draw outer circle
                painter.setPen(QColor(220, 220, 220))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(x - 6, y - 6, 12, 12)
                
                # Draw inner circle with the color
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(*color))
                painter.drawEllipse(x - 4, y - 4, 8, 8)
        
        # Radial gradient points are drawn along a line from center to right
        elif self.gradient_type == "radial":
            center_x = rect.left() + rect.width() // 2
            center_y = rect.top() + rect.height() // 2
            
            for position, color in color_stops:
                x = center_x + int(position * (rect.width() // 2))
                
                # Draw outer circle
                painter.setPen(QColor(220, 220, 220))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(x - 6, center_y - 6, 12, 12)
                
                # Draw inner circle with the color
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(*color))
                painter.drawEllipse(x - 4, center_y - 4, 8, 8)
        
        # Conical gradient points are drawn in a circle around the center
        elif self.gradient_type == "conical":
            center_x = rect.left() + rect.width() // 2
            center_y = rect.top() + rect.height() // 2
            radius = rect.width() // 2 - 10
            
            for position, color in color_stops:
                # Convert position (0-1) to angle (0-360)
                angle = position * 360
                
                # Convert angle to radians and calculate point position
                import math
                rad = math.radians(angle)
                x = center_x + int(radius * math.cos(rad))
                y = center_y - int(radius * math.sin(rad))
                
                # Draw outer circle
                painter.setPen(QColor(220, 220, 220))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(x - 6, y - 6, 12, 12)
                
                # Draw inner circle with the color
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(*color))
                painter.drawEllipse(x - 4, y - 4, 8, 8)