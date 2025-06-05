#!/usr/bin/env python3
"""
Fixed Image-to-Gradient Dialog Module for Gradient Generator

This module implements a dialog for creating gradients from images by
extracting dominant colors with proper mode switching functionality.
Enhanced colors display area to accommodate up to 64 colors with stacking.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QSpinBox, QFileDialog, QGroupBox, 
                           QFormLayout, QCheckBox, QFrame, QScrollArea,
                           QMessageBox, QButtonGroup, QRadioButton,
                           QSlider, QWidget, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage

import os
import numpy as np
from PIL import Image

from ..core.gradient import Gradient
from ..utils.logger import get_logger
from .image_selection_widget import SelectableImageWidget, ColorPreviewWidget

# Get logger
logger = get_logger()


class ImageToGradientDialog(QDialog):
    """Dialog for creating gradients from images with region selection."""
    
    gradient_created = pyqtSignal(object)
    
    def __init__(self, parent=None):
        """Initialize the dialog."""
        super().__init__(parent)
        
        self.init_ui()
        
        # Initialize data
        self.image_path = None
        self.dominant_colors = []
        self.pil_image = None
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Create Gradient from Image")
        self.setMinimumSize(900, 600)
        
        main_layout = QHBoxLayout(self)
        
        # === Left Panel: Image and Selection ===
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel, 2)
        
        # === Right Panel: Options and Results ===
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel, 1)
    
    def _create_left_panel(self):
        """Create the left panel with image display and selection controls."""
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Image selection group
        image_group = QGroupBox("Image Selection and Region")
        image_layout = QVBoxLayout(image_group)
        
        # File path and browse
        path_layout = QHBoxLayout()
        self.path_label = QLabel("No image selected")
        self.path_label.setWordWrap(True)
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_image)
        
        path_layout.addWidget(self.path_label, 1)
        path_layout.addWidget(self.browse_button)
        image_layout.addLayout(path_layout)
        
        # Selection mode controls
        self.selection_group = self._create_selection_mode_group()
        image_layout.addWidget(self.selection_group)
        
        # Image widget
        self.image_widget = SelectableImageWidget()
        self.image_widget.region_selected.connect(self._on_region_selected)
        self.image_widget.point_selected.connect(self._on_point_selected)
        self.image_widget.selection_cleared.connect(self._on_selection_cleared)
        image_layout.addWidget(self.image_widget, 1)
        
        # Selection controls
        controls_layout = QHBoxLayout()
        self.clear_selection_button = QPushButton("Clear Selection")
        self.clear_selection_button.clicked.connect(self._clear_selection)
        self.clear_selection_button.setEnabled(False)
        
        self.selection_info_label = QLabel("No selection")
        self.selection_info_label.setStyleSheet("color: #888; font-style: italic;")
        
        controls_layout.addWidget(self.clear_selection_button)
        controls_layout.addWidget(self.selection_info_label)
        controls_layout.addStretch()
        image_layout.addLayout(controls_layout)
        
        left_layout.addWidget(image_group)
        return left_panel
    
    def _create_selection_mode_group(self):
        """Create the selection mode radio button group."""
        selection_group = QGroupBox("Selection Mode")
        selection_layout = QHBoxLayout(selection_group)
        
        self.selection_button_group = QButtonGroup()
        
        self.rectangle_radio = QRadioButton("Rectangle")
        self.point_radio = QRadioButton("Points")
        self.whole_image_radio = QRadioButton("Whole Image")
        
        self.rectangle_radio.setChecked(True)
        
        self.selection_button_group.addButton(self.rectangle_radio, 0)
        self.selection_button_group.addButton(self.point_radio, 1)
        self.selection_button_group.addButton(self.whole_image_radio, 2)
        
        self.selection_button_group.buttonClicked.connect(self._on_selection_mode_changed)
        
        selection_layout.addWidget(self.rectangle_radio)
        selection_layout.addWidget(self.point_radio)
        selection_layout.addWidget(self.whole_image_radio)
        
        return selection_group
    
    def _create_right_panel(self):
        """Create the right panel with options and results."""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Options group
        options_group = self._create_options_group()
        right_layout.addWidget(options_group)
        
        # Colors group - ENHANCED for 64 colors
        colors_group = self._create_colors_group()
        right_layout.addWidget(colors_group)
        
        # Buttons
        button_layout = self._create_button_layout()
        right_layout.addLayout(button_layout)
        
        right_layout.addStretch()
        return right_panel
    
    def _create_options_group(self):
        """Create the extraction options group."""
        options_group = QGroupBox("Extraction Options")
        options_layout = QFormLayout(options_group)
        
        # Number of colors - increased max to 64
        self.color_count_spin = QSpinBox()
        self.color_count_spin.setRange(2, 64)  # Increased from 15 to 64
        self.color_count_spin.setValue(5)
        self.color_count_spin.valueChanged.connect(self._on_options_changed)
        options_layout.addRow("Number of colors:", self.color_count_spin)
        
        # Similarity radius
        self.similarity_slider = QSlider(Qt.Horizontal)
        self.similarity_slider.setRange(1, 50)
        self.similarity_slider.setValue(10)
        self.similarity_slider.valueChanged.connect(self._update_similarity_label)
        
        self.similarity_label = QLabel("Similarity radius: 10px")
        similarity_layout = QVBoxLayout()
        similarity_layout.addWidget(self.similarity_slider)
        similarity_layout.addWidget(self.similarity_label)
        options_layout.addRow("Point similarity:", similarity_layout)
        
        # Distribute evenly
        self.distribute_evenly_check = QCheckBox("Distribute colors evenly")
        self.distribute_evenly_check.setChecked(True)
        options_layout.addRow("", self.distribute_evenly_check)
        
        return options_group
    
    def _create_colors_group(self):
        """Create the extracted colors display group - ENHANCED for 64 colors."""
        colors_group = QGroupBox("Extracted Colors")
        colors_layout = QVBoxLayout(colors_group)
        
        # Enhanced scrollable colors container with grid layout
        self.colors_container = QWidget()
        self.colors_layout = QGridLayout(self.colors_container)
        self.colors_layout.setSpacing(2)  # Tight spacing for more colors
        
        # Scrollable area with increased height for multiple rows
        colors_scroll = QScrollArea()
        colors_scroll.setWidgetResizable(True)
        colors_scroll.setWidget(self.colors_container)
        colors_scroll.setMinimumHeight(200)  # Increased from 70 to 200
        colors_scroll.setMaximumHeight(300)  # Set maximum height
        colors_layout.addWidget(colors_scroll)
        
        # Info label
        self.extraction_info_label = QLabel("Select an image and region to extract colors")
        self.extraction_info_label.setStyleSheet("color: #888; font-style: italic;")
        colors_layout.addWidget(self.extraction_info_label)
        
        return colors_group
    
    def _create_button_layout(self):
        """Create the button layout."""
        button_layout = QHBoxLayout()
        
        self.extract_button = QPushButton("Extract Colors")
        self.extract_button.clicked.connect(self.extract_colors)
        self.extract_button.setEnabled(False)
        
        self.create_button = QPushButton("Create Gradient")
        self.create_button.clicked.connect(self.create_gradient)
        self.create_button.setEnabled(False)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.extract_button)
        button_layout.addWidget(self.create_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        
        return button_layout
    
    def browse_image(self):
        """Open file dialog to select an image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff);;All Files (*)"
        )
        
        if file_path:
            self.image_path = file_path
            self.path_label.setText(file_path)
            
            if self._load_image_preview(file_path):
                self.extract_button.setEnabled(True)
                self._reset_extraction_state()
            else:
                self._reset_image_state()
    
    def _load_image_preview(self, file_path):
        """Load and display image preview."""
        try:
            logger.info(f"Loading image: {file_path}")
            
            # Load with PIL
            self.pil_image = Image.open(file_path)
            if self.pil_image.mode != 'RGB':
                self.pil_image = self.pil_image.convert('RGB')
            
            # Convert to QPixmap
            img_array = np.array(self.pil_image)
            if not img_array.flags['C_CONTIGUOUS']:
                img_array = np.ascontiguousarray(img_array)
            
            height, width, channels = img_array.shape
            if channels != 3:
                raise ValueError(f"Expected 3 channels (RGB), got {channels}")
            
            bytes_per_line = width * channels
            qimg = QImage(img_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            
            if pixmap.isNull():
                raise ValueError("Failed to create QPixmap")
            
            self.image_widget.set_image(pixmap)
            logger.info(f"Successfully loaded image: {width}x{height}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load image: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
            return False
    
    def _reset_image_state(self):
        """Reset state when image loading fails."""
        self.image_path = None
        self.path_label.setText("Failed to load image")
        self.extract_button.setEnabled(False)
        self._reset_extraction_state()
    
    def _reset_extraction_state(self):
        """Reset extraction-related state."""
        self._clear_selection()
        self._update_color_preview([])
        self.create_button.setEnabled(False)
        self.extraction_info_label.setText("Select an image and region to extract colors")
    
    def _on_selection_mode_changed(self, button):
        """Handle selection mode change with proper state management."""
        button_id = self.selection_button_group.id(button)
        
        if button_id == 2:  # Whole image
            # Disable interactive selection but keep widget responsive
            self.image_widget.selection_active = False
            self.image_widget.clear_selection()
            self.selection_info_label.setText("Whole image selected")
            self.clear_selection_button.setEnabled(False)
        else:
            # Enable interactive selection
            mode = "rectangle" if button_id == 0 else "point"
            self.image_widget.set_selection_mode(mode)
            # Ensure selection is properly enabled
            if self.image_widget.original_pixmap:
                self.image_widget.selection_active = True
            self._clear_selection()
    
    def _on_region_selected(self, region):
        """Handle region selection."""
        region_rect = self.image_widget.get_selection_region()
        if region_rect:
            self.selection_info_label.setText(
                f"Region: {region_rect.width()}×{region_rect.height()}px"
            )
            self.clear_selection_button.setEnabled(True)
    
    def _on_point_selected(self, point):
        """Handle point selection."""
        points = self.image_widget.get_selection_points()
        if points:
            self.selection_info_label.setText(f"{len(points)} point(s) selected")
            self.clear_selection_button.setEnabled(True)
    
    def _on_selection_cleared(self):
        """Handle selection clearing."""
        self.selection_info_label.setText("No selection")
        self.clear_selection_button.setEnabled(False)
    
    def _clear_selection(self):
        """Clear current selection."""
        self.image_widget.clear_selection()
        self._on_selection_cleared()
    
    def _on_options_changed(self):
        """Handle options changes."""
        if self.dominant_colors:
            self._update_color_preview([])
            self.create_button.setEnabled(False)
            self.extraction_info_label.setText("Options changed - re-extract colors")
    
    def _update_similarity_label(self, value):
        """Update similarity radius label."""
        self.similarity_label.setText(f"Similarity radius: {value}px")
    
    def extract_colors(self):
        """Extract dominant colors based on current selection mode."""
        if not self.image_path or not self.pil_image:
            QMessageBox.warning(self, "No Image", "Please select an image first.")
            return
        
        try:
            logger.info("Starting color extraction...")
            num_colors = self.color_count_spin.value()
            
            if self.whole_image_radio.isChecked():
                self.dominant_colors = self._extract_from_whole_image(num_colors)
                self.extraction_info_label.setText("Extracted colors from entire image")
                
            elif self.rectangle_radio.isChecked():
                region = self.image_widget.get_selection_region()
                if region and not region.isEmpty():
                    self.dominant_colors = self._extract_from_region(region, num_colors)
                    self.extraction_info_label.setText(
                        f"Extracted colors from {region.width()}×{region.height()}px region"
                    )
                else:
                    QMessageBox.warning(self, "No Selection", "Please select a region first.")
                    return
                    
            elif self.point_radio.isChecked():
                points = self.image_widget.get_selection_points()
                if points:
                    self.dominant_colors = self._extract_from_points(points, num_colors)
                    self.extraction_info_label.setText(
                        f"Extracted colors from {len(points)} selected point(s)"
                    )
                else:
                    QMessageBox.warning(self, "No Selection", "Please select some points first.")
                    return
            
            if not self.dominant_colors:
                QMessageBox.critical(self, "Error", "Failed to extract colors from selection.")
                return
            
            self._update_color_preview(self.dominant_colors)
            self.create_button.setEnabled(True)
            logger.info(f"Successfully extracted {len(self.dominant_colors)} colors")
            
        except Exception as e:
            logger.error(f"Error extracting colors: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Color extraction failed: {str(e)}")
    
    def _extract_from_whole_image(self, num_colors):
        """Extract colors from entire image."""
        try:
            img_array = np.array(self.pil_image)
            return self._perform_clustering(img_array, num_colors)
        except Exception as e:
            logger.error(f"Error extracting from whole image: {e}")
            return []
    
    def _extract_from_region(self, region, num_colors):
        """Extract colors from selected region."""
        try:
            img_width, img_height = self.pil_image.size
            
            # Clamp region to image bounds
            x = max(0, min(region.x(), img_width - 1))
            y = max(0, min(region.y(), img_height - 1))
            width = max(1, min(region.width(), img_width - x))
            height = max(1, min(region.height(), img_height - y))
            
            crop_box = (x, y, x + width, y + height)
            cropped_image = self.pil_image.crop(crop_box)
            img_array = np.array(cropped_image)
            
            return self._perform_clustering(img_array, num_colors)
        except Exception as e:
            logger.error(f"Error extracting from region: {e}")
            return []
    
    def _extract_from_points(self, points, num_colors):
        """Extract colors from around selected points."""
        try:
            img_array = np.array(self.pil_image)
            height, width = img_array.shape[:2]
            radius = self.similarity_slider.value()
            
            collected_pixels = []
            for point in points:
                x, y = point.x(), point.y()
                if 0 <= x < width and 0 <= y < height:
                    # Sample circular region around point
                    x_min, x_max = max(0, x - radius), min(width, x + radius + 1)
                    y_min, y_max = max(0, y - radius), min(height, y + radius + 1)
                    
                    for py in range(y_min, y_max):
                        for px in range(x_min, x_max):
                            # Check if pixel is within circular radius
                            dist = ((px - x) ** 2 + (py - y) ** 2) ** 0.5
                            if dist <= radius:
                                collected_pixels.append(img_array[py, px])
            
            if not collected_pixels:
                return []
            
            pixels_array = np.array(collected_pixels)
            return self._perform_clustering(pixels_array, num_colors)
        except Exception as e:
            logger.error(f"Error extracting from points: {e}")
            return []
    
    def _perform_clustering(self, pixels, num_colors):
        """Perform k-means clustering on pixel data."""
        try:
            from sklearn.cluster import KMeans
            from collections import Counter
        except ImportError:
            QMessageBox.critical(self, "Missing Dependency", 
                "scikit-learn is required. Install with: pip install scikit-learn")
            return []
        
        try:
            # Reshape pixels for clustering
            if len(pixels.shape) == 3:
                reshaped_pixels = pixels.reshape((-1, 3))
            else:
                reshaped_pixels = pixels
            
            if len(reshaped_pixels) == 0:
                return []
            
            # Limit colors to available unique pixels
            unique_pixels = np.unique(reshaped_pixels, axis=0)
            actual_num_colors = min(num_colors, len(unique_pixels))
            
            if actual_num_colors < 2:
                return [tuple(pixel) for pixel in unique_pixels]
            
            # Perform clustering
            kmeans = KMeans(n_clusters=actual_num_colors, n_init=10, random_state=42, max_iter=300)
            kmeans.fit(reshaped_pixels)
            
            # Get colors sorted by frequency
            colors = kmeans.cluster_centers_
            labels = kmeans.labels_
            counter = Counter(labels)
            
            # Sort by frequency and convert to RGB tuples
            dominant_colors = []
            for i in sorted(range(actual_num_colors), key=lambda x: counter.get(x, 0), reverse=True):
                r, g, b = colors[i]
                r = max(0, min(255, int(round(r))))
                g = max(0, min(255, int(round(g))))
                b = max(0, min(255, int(round(b))))
                dominant_colors.append((r, g, b))
            
            return dominant_colors
        except Exception as e:
            logger.error(f"Error in clustering: {e}")
            return []
    
    def _update_color_preview(self, colors):
        """Update the color preview display with grid layout for up to 64 colors."""
        # Clear existing widgets
        for i in reversed(range(self.colors_layout.count())):
            child = self.colors_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        # Add color widgets in a grid layout
        if colors:
            # Calculate grid dimensions based on number of colors
            num_colors = len(colors)
            
            # Determine columns based on available space and color count
            if num_colors <= 8:
                cols = min(8, num_colors)  # Single row for 8 or fewer
            elif num_colors <= 16:
                cols = 8  # 2 rows for 9-16 colors
            elif num_colors <= 32:
                cols = 8  # Up to 4 rows for 17-32 colors
            else:
                cols = 8  # More rows as needed for 33-64 colors
            
            # Add color widgets to grid
            for i, color in enumerate(colors):
                row = i // cols
                col = i % cols
                
                color_widget = ColorPreviewWidget(color)
                color_widget.setToolTip(f"RGB: {color[0]}, {color[1]}, {color[2]}")
                color_widget.setFixedSize(30, 30)  # Slightly smaller for more colors
                
                self.colors_layout.addWidget(color_widget, row, col)
        
        # Add stretch to fill remaining space
        self.colors_layout.setRowStretch(self.colors_layout.rowCount(), 1)
        self.colors_layout.setColumnStretch(self.colors_layout.columnCount(), 1)
    
    def create_gradient(self):
        """Create gradient from extracted colors."""
        if not self.dominant_colors:
            QMessageBox.warning(self, "Warning", "No colors extracted. Please extract colors first.")
            return
        
        try:
            # Create gradient
            gradient = Gradient()
            gradient._color_stops = []
            
            # Add color stops
            distribute_evenly = self.distribute_evenly_check.isChecked()
            for i, color in enumerate(self.dominant_colors):
                if distribute_evenly:
                    position = i / (len(self.dominant_colors) - 1) if len(self.dominant_colors) > 1 else 0.5
                else:
                    # For now, same as evenly distributed
                    position = i / (len(self.dominant_colors) - 1) if len(self.dominant_colors) > 1 else 0.5
                
                gradient.add_color_stop(position, color)
            
            # Set metadata
            if self.image_path:
                image_name = os.path.basename(self.image_path)
                
                if self.whole_image_radio.isChecked():
                    gradient_name = f"Gradient from {image_name}"
                    description = f"Generated from entire image: {image_name}"
                elif self.rectangle_radio.isChecked():
                    gradient_name = f"Gradient from {image_name} (Region)"
                    region = self.image_widget.get_selection_region()
                    description = f"Generated from {image_name} region: {region.width()}×{region.height()}px"
                else:  # Points
                    points = self.image_widget.get_selection_points()
                    gradient_name = f"Gradient from {image_name} ({len(points)} Points)"
                    description = f"Generated from {image_name} using {len(points)} selected points"
                
                gradient.set_name(gradient_name)
                gradient.set_description(f"{description} | Colors extracted: {len(self.dominant_colors)}")
            
            # Emit signal and close
            self.gradient_created.emit(gradient)
            self.accept()
            
        except Exception as e:
            logger.error(f"Failed to create gradient: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create gradient: {str(e)}")
