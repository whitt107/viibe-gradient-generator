#!/usr/bin/env python3
"""
Gradient Metadata Module

This module handles gradient metadata including name, author, description,
and JWildfire-specific settings.
"""


class GradientMetadata:
    """Class for managing gradient metadata."""
    
    def __init__(self):
        """Initialize metadata with default values."""
        self.name = "New Gradient"
        self.author = ""
        self.description = ""
        self.ugr_category = "Custom"
        self.combine_gradients = False
    
    def reset(self):
        """Reset metadata to default values."""
        self.__init__()
    
    def is_default(self) -> bool:
        """Check if metadata has only default values."""
        return (
            self.name == "New Gradient" and
            self.author == "" and
            self.description == "" and
            self.ugr_category == "Custom" and
            not self.combine_gradients
        )
    
    def copy(self) -> 'GradientMetadata':
        """Create a copy of this metadata."""
        metadata = GradientMetadata()
        metadata.name = self.name
        metadata.author = self.author
        metadata.description = self.description
        metadata.ugr_category = self.ugr_category
        metadata.combine_gradients = self.combine_gradients
        return metadata
    
    def __repr__(self):
        """String representation of metadata."""
        return (f"GradientMetadata(name='{self.name}', author='{self.author}', "
                f"category='{self.ugr_category}', combine={self.combine_gradients})")
