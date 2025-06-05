#!/usr/bin/env python3
"""
Image Analyzer Module for Gradient Generator

This module provides functionality to analyze images and extract dominant colors
for creating gradients from images.
"""
import os
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from collections import Counter

from ..core.gradient import Gradient
from ..utils.logger import get_logger

# Get logger
logger = get_logger()


class ImageAnalyzer:
    """Class for analyzing images and extracting color information."""
    
    def __init__(self):
        """Initialize the image analyzer."""
        self.image = None
        self.image_path = None
        self.dominant_colors = []
    
    def load_image(self, image_path):
        """
        Load an image for analysis.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if the image was loaded successfully, False otherwise
        """
        try:
            # Check if the file exists
            if not os.path.isfile(image_path):
                logger.error(f"Image file not found: {image_path}")
                return False
            
            # Open the image
            self.image = Image.open(image_path)
            self.image_path = image_path
            
            # Convert to RGB if needed
            if self.image.mode != 'RGB':
                self.image = self.image.convert('RGB')
            
            logger.info(f"Successfully loaded image: {image_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading image: {e}", exc_info=True)
            return False
    
    def extract_dominant_colors(self, num_colors=5, resize_factor=0.25):
        """
        Extract dominant colors from the loaded image using K-means clustering.
        
        Args:
            num_colors: Number of dominant colors to extract (default: 5)
            resize_factor: Factor to resize image for faster processing (default: 0.25)
            
        Returns:
            List of dominant colors as (r, g, b) tuples
        """
        if self.image is None:
            logger.error("No image loaded")
            return []
        
        try:
            # Resize image for faster processing
            width, height = self.image.size
            new_width = max(1, int(width * resize_factor))
            new_height = max(1, int(height * resize_factor))
            resized_image = self.image.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert image to numpy array
            pixels = np.array(resized_image)
            reshaped_pixels = pixels.reshape((-1, 3))
            
            # Perform K-means clustering
            kmeans = KMeans(n_clusters=num_colors, n_init=10)
            kmeans.fit(reshaped_pixels)
            
            # Get the dominant colors
            colors = kmeans.cluster_centers_
            
            # Count pixel occurrences for each cluster
            labels = kmeans.labels_
            counter = Counter(labels)
            
            # Sort colors by frequency
            color_ranks = {}
            for i in range(num_colors):
                color_ranks[i] = counter[i]
            
            # Sort colors by frequency (most frequent first)
            sorted_colors = sorted(color_ranks.items(), key=lambda x: x[1], reverse=True)
            sorted_indices = [idx for idx, _ in sorted_colors]
            
            # Get the dominant colors in RGB format
            self.dominant_colors = []
            for idx in sorted_indices:
                r, g, b = [int(val) for val in colors[idx]]
                self.dominant_colors.append((r, g, b))
            
            logger.info(f"Extracted {len(self.dominant_colors)} dominant colors from image")
            return self.dominant_colors
            
        except Exception as e:
            logger.error(f"Error extracting dominant colors: {e}", exc_info=True)
            return []
    
    def create_gradient_from_image(self, num_colors=5, distribute_evenly=True):
        """
        Create a gradient from the loaded image.
        
        Args:
            num_colors: Number of dominant colors to extract (default: 5)
            distribute_evenly: Whether to distribute stops evenly (default: True)
            
        Returns:
            Gradient object with colors from the image
        """
        if self.image is None:
            logger.error("No image loaded")
            return None
        
        # Extract dominant colors if not already done
        if not self.dominant_colors:
            self.extract_dominant_colors(num_colors)
        
        if not self.dominant_colors:
            logger.error("Failed to extract dominant colors")
            return None
        
        try:
            # Create a new gradient
            gradient = Gradient()
            
            # Clear default stops
            gradient._color_stops = []
            
            # Add color stops
            if distribute_evenly:
                # Distribute colors evenly along the gradient
                for i, color in enumerate(self.dominant_colors):
                    position = i / (len(self.dominant_colors) - 1) if len(self.dominant_colors) > 1 else 0
                    gradient.add_color_stop(position, color)
            else:
                # Distribute colors based on image analysis
                # This is a simple implementation; more sophisticated algorithms could be used
                for i, color in enumerate(self.dominant_colors):
                    position = i / (len(self.dominant_colors) - 1) if len(self.dominant_colors) > 1 else 0
                    gradient.add_color_stop(position, color)
            
            # Set metadata
            if self.image_path:
                image_name = os.path.basename(self.image_path)
                gradient.set_name(f"Gradient from {image_name}")
                gradient.set_description(f"Generated from image: {image_name}")
                
            logger.info(f"Successfully created gradient from image with {len(self.dominant_colors)} colors")
            return gradient
            
        except Exception as e:
            logger.error(f"Error creating gradient from image: {e}", exc_info=True)
            return None


def create_gradient_from_image_path(image_path, num_colors=5, distribute_evenly=True):
    """
    Utility function to create a gradient from an image path.
    
    Args:
        image_path: Path to the image file
        num_colors: Number of dominant colors to extract (default: 5)
        distribute_evenly: Whether to distribute stops evenly (default: True)
        
    Returns:
        Gradient object with colors from the image or None if failed
    """
    analyzer = ImageAnalyzer()
    
    if analyzer.load_image(image_path):
        return analyzer.create_gradient_from_image(num_colors, distribute_evenly)
    
    return None
