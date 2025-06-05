#!/usr/bin/env python3
"""
Gradient Serializer Module for Gradient Generator

This module handles gradient serialization and deserialization.
"""
from ...core.gradient import Gradient


class GradientSerializer:
    """Handles gradient serialization and deserialization."""
    
    def serialize_gradient(self, gradient):
        """Serialize a gradient to dict."""
        return {
            "color_stops": gradient.get_color_stops(),
            "name": gradient.get_name(),
            "author": gradient.get_author(),
            "description": gradient.get_description(),
            "ugr_category": gradient.get_ugr_category(),
            "combine_gradients": gradient.get_combine_gradients(),
            "seamless_blend": gradient.get_seamless_blend(),
            "blend_region": gradient.get_blend_region()
        }
    
    def deserialize_gradient(self, data):
        """Deserialize gradient from dict."""
        gradient = Gradient()
        gradient._color_stops = []
        
        for position, color in data.get("color_stops", []):
            gradient.add_color_stop(position, color)
        
        gradient.set_name(data.get("name", ""))
        gradient.set_author(data.get("author", ""))
        gradient.set_description(data.get("description", ""))
        gradient.set_ugr_category(data.get("ugr_category", "Custom"))
        gradient.set_combine_gradients(data.get("combine_gradients", False))
        gradient.set_seamless_blend(data.get("seamless_blend", False))
        gradient.set_blend_region(data.get("blend_region", 0.1))
        
        return gradient