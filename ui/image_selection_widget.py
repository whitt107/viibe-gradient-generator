#!/usr/bin/env python3
"""
Fixed Image Selection Widget Module for Gradient Generator

This module provides the image selection widget and color preview components
for the image-to-gradient functionality with proper coordinate handling.
"""
from PyQt5.QtWidgets import QLabel, QFrame
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRect, QPoint
from PyQt5.QtGui import QPixmap, QColor, QPainter, QPen, QBrush, QCursor


class SelectableImageWidget(QLabel):
    """Widget for displaying an image with region/point selection capabilities."""
    
    # Signals
    region_selected = pyqtSignal(QRect)  # Emitted when a region is selected
    point_selected = pyqtSignal(QPoint)  # Emitted when a point is selected
    selection_cleared = pyqtSignal()     # Emitted when selection is cleared
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Selection mode
        self.selection_mode = "rectangle"  # "rectangle", "point"
        self.selection_active = False
        
        # Selection state
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.current_selection = QRect()
        self.selected_points = []
        self.is_drawing = False
        
        # Image data
        self.original_pixmap = None
        self.scaled_pixmap = None
        self.scale_factor = 1.0
        self.image_offset = QPoint(0, 0)  # Offset of scaled image within widget
        
        # Visual settings
        self.selection_color = QColor(255, 0, 0, 128)  # Semi-transparent red
        self.selection_border_color = QColor(255, 0, 0, 255)  # Solid red border
        
        # Setup widget
        self.setMinimumSize(400, 300)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 2px solid #555; background-color: #333;")
        self.setMouseTracking(True)
        
        # Default message
        self.setText("Click 'Browse...' to load an image")
    
    def set_image(self, pixmap):
        """Set the image to display and enable selection."""
        self.original_pixmap = pixmap
        self.update_display()
        self.selection_active = True
        self.clear_selection()
    
    def set_selection_mode(self, mode):
        """Set the selection mode."""
        if mode in ["rectangle", "point"]:
            self.selection_mode = mode
            self.clear_selection()
            self.update_cursor()
    
    def clear_selection(self):
        """Clear the current selection."""
        self.current_selection = QRect()
        self.selected_points.clear()
        self.update_display()
        self.selection_cleared.emit()
    
    def get_selection_region(self):
        """Get the current selection as a rectangle in original image coordinates."""
        if not self.original_pixmap or self.current_selection.isEmpty():
            return None
        
        # Convert from widget coordinates to original image coordinates
        rect = self.current_selection
        
        # Adjust for image offset within widget
        adjusted_rect = QRect(
            rect.x() - self.image_offset.x(),
            rect.y() - self.image_offset.y(),
            rect.width(),
            rect.height()
        )
        
        # Scale back to original image size
        if self.scale_factor > 0:
            orig_rect = QRect(
                int(adjusted_rect.x() / self.scale_factor),
                int(adjusted_rect.y() / self.scale_factor),
                int(adjusted_rect.width() / self.scale_factor),
                int(adjusted_rect.height() / self.scale_factor)
            )
        else:
            orig_rect = adjusted_rect
        
        # Ensure the rectangle is within image bounds
        if self.original_pixmap:
            image_rect = QRect(0, 0, self.original_pixmap.width(), self.original_pixmap.height())
            return orig_rect.intersected(image_rect)
        
        return orig_rect
    
    def get_selection_points(self):
        """Get selected points in original image coordinates."""
        if not self.original_pixmap or not self.selected_points:
            return []
        
        # Convert from widget coordinates to original image coordinates
        original_points = []
        for point in self.selected_points:
            # Adjust for image offset
            adjusted_point = QPoint(
                point.x() - self.image_offset.x(),
                point.y() - self.image_offset.y()
            )
            
            # Scale back to original image coordinates
            if self.scale_factor > 0:
                orig_point = QPoint(
                    int(adjusted_point.x() / self.scale_factor),
                    int(adjusted_point.y() / self.scale_factor)
                )
            else:
                orig_point = adjusted_point
            
            # Ensure point is within image bounds
            if self.original_pixmap:
                if (0 <= orig_point.x() < self.original_pixmap.width() and
                    0 <= orig_point.y() < self.original_pixmap.height()):
                    original_points.append(orig_point)
        
        return original_points
    
    def update_display(self):
        """Update the displayed image with selection overlay."""
        if not self.original_pixmap:
            return
        
        # Scale image to fit widget while maintaining aspect ratio
        widget_size = self.size()
        scaled_pixmap = self.original_pixmap.scaled(
            widget_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        
        # Calculate scale factor and image offset
        self.scale_factor = min(
            widget_size.width() / self.original_pixmap.width(),
            widget_size.height() / self.original_pixmap.height()
        )
        
        # Calculate offset to center the image
        self.image_offset = QPoint(
            (widget_size.width() - scaled_pixmap.width()) // 2,
            (widget_size.height() - scaled_pixmap.height()) // 2
        )
        
        # Create a display pixmap with transparent background
        display_pixmap = QPixmap(widget_size)
        display_pixmap.fill(Qt.transparent)
        
        painter = QPainter(display_pixmap)
        
        # Draw the scaled image at the calculated offset
        painter.drawPixmap(self.image_offset, scaled_pixmap)
        
        # Draw selection overlay
        self.draw_selection_overlay(painter)
        
        painter.end()
        
        self.scaled_pixmap = display_pixmap
        self.setPixmap(display_pixmap)
    
    def draw_selection_overlay(self, painter):
        """Draw the selection overlay on the image."""
        if not self.selection_active:
            return
        
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.selection_mode == "rectangle" and not self.current_selection.isEmpty():
            # Draw rectangle selection
            painter.setPen(QPen(self.selection_border_color, 2))
            painter.setBrush(QBrush(self.selection_color))
            
            # Draw the selection rectangle (already in widget coordinates)
            painter.drawRect(self.current_selection)
            
        elif self.selection_mode == "point" and self.selected_points:
            # Draw point selections
            painter.setPen(QPen(self.selection_border_color, 3))
            painter.setBrush(QBrush(Qt.red))
            
            for point in self.selected_points:
                # Draw circle at each point (already in widget coordinates)
                painter.drawEllipse(point, 5, 5)
    
    def update_cursor(self):
        """Update the cursor based on selection mode."""
        if not self.selection_active:
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.CrossCursor)
    
    def mousePressEvent(self, event):
        """Handle mouse press for starting selection."""
        if not self.selection_active or not self.original_pixmap:
            return
        
        # Check if click is within the image area
        if not self.is_point_in_image(event.pos()):
            return
        
        if event.button() == Qt.LeftButton:
            if self.selection_mode == "rectangle":
                self.start_point = event.pos()
                self.end_point = event.pos()
                self.is_drawing = True
                
            elif self.selection_mode == "point":
                # Add point to selection
                self.selected_points.append(event.pos())
                self.point_selected.emit(event.pos())
                self.update_display()
        
        elif event.button() == Qt.RightButton:
            # Right click to clear selection
            self.clear_selection()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for updating selection."""
        if not self.selection_active or not self.original_pixmap:
            return
        
        if self.is_drawing and self.selection_mode == "rectangle":
            # Update selection rectangle
            self.end_point = event.pos()
            self.update_selection_rect()
            self.update_display()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release for completing selection."""
        if not self.selection_active or not self.original_pixmap:
            return
        
        if event.button() == Qt.LeftButton and self.is_drawing:
            if self.selection_mode == "rectangle":
                self.is_drawing = False
                if not self.current_selection.isEmpty():
                    # Ensure selection is within image bounds
                    image_bounds = QRect(
                        self.image_offset.x(),
                        self.image_offset.y(),
                        int(self.original_pixmap.width() * self.scale_factor),
                        int(self.original_pixmap.height() * self.scale_factor)
                    )
                    
                    # Intersect with image bounds
                    bounded_selection = self.current_selection.intersected(image_bounds)
                    if not bounded_selection.isEmpty():
                        self.current_selection = bounded_selection
                        self.region_selected.emit(self.current_selection)
                        self.update_display()
    
    def is_point_in_image(self, point):
        """Check if a point is within the displayed image area."""
        if not self.original_pixmap:
            return False
        
        image_rect = QRect(
            self.image_offset.x(),
            self.image_offset.y(),
            int(self.original_pixmap.width() * self.scale_factor),
            int(self.original_pixmap.height() * self.scale_factor)
        )
        
        return image_rect.contains(point)
    
    def update_selection_rect(self):
        """Update the current selection rectangle."""
        if self.start_point.isNull() or self.end_point.isNull():
            return
        
        # Create rectangle from start and end points
        self.current_selection = QRect(
            min(self.start_point.x(), self.end_point.x()),
            min(self.start_point.y(), self.end_point.y()),
            abs(self.end_point.x() - self.start_point.x()),
            abs(self.end_point.y() - self.start_point.y())
        )
    
    def resizeEvent(self, event):
        """Handle resize event."""
        super().resizeEvent(event)
        if self.original_pixmap:
            self.update_display()


class ColorPreviewWidget(QFrame):
    """Widget to display a color swatch."""
    
    def __init__(self, color, parent=None):
        """Initialize with the given RGB color."""
        super().__init__(parent)
        
        self.color = color  # (r, g, b)
        
        # Set fixed size
        self.setFixedSize(QSize(40, 40))
        
        # Set style
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        # Set background color
        self.update_color()
    
    def update_color(self):
        """Update the background color."""
        r, g, b = self.color
        self.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border: 1px solid #888;")