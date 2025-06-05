#!/usr/bin/env python3
"""
Color Utilities Module

This module provides utility functions for color manipulation, conversion
between different color spaces, and related operations.
"""
import math


def clamp(value, min_val=0, max_val=255):
    """
    Clamp a value to the specified range.
    
    Args:
        value: The value to clamp
        min_val: Minimum value (default: 0)
        max_val: Maximum value (default: 255)
        
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def rgb_to_hsv(r, g, b):
    """
    Convert RGB color to HSV.
    
    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)
        
    Returns:
        Tuple (h, s, v) with h in degrees (0-360) and s, v in range 0-1
    """
    # Normalize RGB values to 0-1
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0
    
    c_max = max(r_norm, g_norm, b_norm)
    c_min = min(r_norm, g_norm, b_norm)
    delta = c_max - c_min
    
    # Calculate hue
    if delta == 0:
        h = 0  # Undefined, use 0
    elif c_max == r_norm:
        h = 60 * ((g_norm - b_norm) / delta % 6)
    elif c_max == g_norm:
        h = 60 * ((b_norm - r_norm) / delta + 2)
    else:  # c_max == b_norm
        h = 60 * ((r_norm - g_norm) / delta + 4)
    
    # Calculate saturation
    s = 0 if c_max == 0 else delta / c_max
    
    # Value is the maximum component
    v = c_max
    
    return (h, s, v)


def hsv_to_rgb(h, s, v):
    """
    Convert HSV color to RGB.
    
    Args:
        h: Hue in degrees (0-360)
        s: Saturation (0-1)
        v: Value (0-1)
        
    Returns:
        Tuple (r, g, b) with values in range 0-255
    """
    # Handle edge cases
    if s == 0:
        # Achromatic (gray)
        r = g = b = v
    else:
        # Normalize hue to segment
        h_segment = h / 60
        i = math.floor(h_segment)
        f = h_segment - i  # Fractional part
        
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))
        
        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:  # i == 5
            r, g, b = v, p, q
    
    # Convert to 0-255 range
    return (
        int(clamp(r * 255)),
        int(clamp(g * 255)),
        int(clamp(b * 255))
    )


def rgb_to_hex(r, g, b):
    """
    Convert RGB color to hex string.
    
    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)
        
    Returns:
        Hex color string (e.g., "#FF0000" for red)
    """
    return f"#{r:02X}{g:02X}{b:02X}"


def hex_to_rgb(hex_color):
    """
    Convert hex color string to RGB.
    
    Args:
        hex_color: Hex color string (e.g., "#FF0000" or "FF0000" for red)
        
    Returns:
        Tuple (r, g, b) with values in range 0-255
    """
    # Remove leading # if present
    if hex_color.startswith("#"):
        hex_color = hex_color[1:]
    
    # Parse RGB components
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return (r, g, b)


def blend_colors(color1, color2, blend_factor):
    """
    Blend two RGB colors.
    
    Args:
        color1: First RGB tuple (r, g, b)
        color2: Second RGB tuple (r, g, b)
        blend_factor: Blend factor (0-1), where 0 is color1 and 1 is color2
        
    Returns:
        Blended RGB tuple (r, g, b)
    """
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    
    # Linear interpolation
    r = int(r1 * (1 - blend_factor) + r2 * blend_factor)
    g = int(g1 * (1 - blend_factor) + g2 * blend_factor)
    b = int(b1 * (1 - blend_factor) + b2 * blend_factor)
    
    return (r, g, b)


def interpolate_colors(color1, color2, steps):
    """
    Interpolate between two colors to create a gradient.
    
    Args:
        color1: First RGB tuple (r, g, b)
        color2: Second RGB tuple (r, g, b)
        steps: Number of color steps to generate (including first and last)
        
    Returns:
        List of RGB tuples representing the gradient
    """
    result = []
    
    for i in range(steps):
        blend_factor = i / (steps - 1) if steps > 1 else 0
        result.append(blend_colors(color1, color2, blend_factor))
    
    return result


def adjust_brightness(color, factor):
    """
    Adjust the brightness of a color.
    
    Args:
        color: RGB tuple (r, g, b)
        factor: Brightness factor (0-infinite, 1 is unchanged)
        
    Returns:
        Adjusted RGB tuple (r, g, b)
    """
    r, g, b = color
    
    # Convert to HSV, adjust V, convert back
    h, s, v = rgb_to_hsv(r, g, b)
    v = clamp(v * factor, 0, 1)
    
    return hsv_to_rgb(h, s, v)


def adjust_saturation(color, factor):
    """
    Adjust the saturation of a color.
    
    Args:
        color: RGB tuple (r, g, b)
        factor: Saturation factor (0-infinite, 1 is unchanged)
        
    Returns:
        Adjusted RGB tuple (r, g, b)
    """
    r, g, b = color
    
    # Convert to HSV, adjust S, convert back
    h, s, v = rgb_to_hsv(r, g, b)
    s = clamp(s * factor, 0, 1)
    
    return hsv_to_rgb(h, s, v)


def rotate_hue(color, degrees):
    """
    Rotate the hue of a color.
    
    Args:
        color: RGB tuple (r, g, b)
        degrees: Rotation in degrees (0-360)
        
    Returns:
        Color with rotated hue as RGB tuple (r, g, b)
    """
    r, g, b = color
    
    # Convert to HSV, adjust H, convert back
    h, s, v = rgb_to_hsv(r, g, b)
    h = (h + degrees) % 360
    
    return hsv_to_rgb(h, s, v)


def complementary_color(color):
    """
    Get the complementary color (opposite on the color wheel).
    
    Args:
        color: RGB tuple (r, g, b)
        
    Returns:
        Complementary color as RGB tuple (r, g, b)
    """
    return rotate_hue(color, 180)


def triadic_colors(color):
    """
    Get triadic colors (three colors evenly spaced on the color wheel).
    
    Args:
        color: RGB tuple (r, g, b)
        
    Returns:
        Tuple of three RGB tuples including the original color
    """
    color2 = rotate_hue(color, 120)
    color3 = rotate_hue(color, 240)
    
    return (color, color2, color3)


def analogous_colors(color, angle=30):
    """
    Get analogous colors (colors adjacent on the color wheel).
    
    Args:
        color: RGB tuple (r, g, b)
        angle: Angle between colors (default: 30 degrees)
        
    Returns:
        Tuple of three RGB tuples with the original in the middle
    """
    color1 = rotate_hue(color, -angle)
    color3 = rotate_hue(color, angle)
    
    return (color1, color, color3)
