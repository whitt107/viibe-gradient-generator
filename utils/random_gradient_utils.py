#!/usr/bin/env python3
"""
Gradient Utilities Module for Enhanced Random Gradient Generator - Sorting Removed

This module provides utility functions for generating gradients with natural
patterns and distributions, shared between the theme generator and random
gradient generator.

FIXED: Removed sorting to maintain true randomization
"""
import random
import math
import colorsys
from typing import List, Tuple, Dict, Any


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """
    Convert HSV to RGB color space.
    
    Args:
        h: Hue value in degrees (0-360)
        s: Saturation value (0-1)
        v: Value/brightness value (0-1)
        
    Returns:
        RGB tuple with values in range 0-255
    """
    # Convert to 0-1 range for colorsys
    h_norm = h / 360.0
    
    # Convert to RGB in 0-1 range
    r, g, b = colorsys.hsv_to_rgb(h_norm, s, v)
    
    # Convert to 0-255 range and round to integers
    return (
        max(0, min(255, int(round(r * 255)))),
        max(0, min(255, int(round(g * 255)))),
        max(0, min(255, int(round(b * 255))))
    )


def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """
    Convert RGB to HSV color space.
    
    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)
        
    Returns:
        HSV tuple (hue in degrees 0-360, saturation 0-1, value 0-1)
    """
    # Convert to 0-1 range for colorsys
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0
    
    # Convert to HSV
    h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
    
    # Convert hue to degrees
    h_degrees = h * 360.0
    
    return (h_degrees, s, v)


def adjust_value(value: float, brightness: float, contrast: float, 
                value_range: Tuple[float, float]) -> float:
    """
    Adjust a value (brightness) component based on brightness and contrast factors.
    
    Args:
        value: Original value (0-1)
        brightness: Brightness multiplier
        contrast: Contrast multiplier
        value_range: (min, max) range for the value
        
    Returns:
        Adjusted value component (0-1)
    """
    # Apply brightness
    adjusted = value * brightness
    
    # Apply contrast - pivot around middle of range
    mid_point = (value_range[0] + value_range[1]) / 2
    contrasted = mid_point + (adjusted - mid_point) * contrast
    
    # Clamp to valid range
    return max(0.0, min(1.0, contrasted))


def generate_naturalistic_positions(
    count: int, 
    start: float = 0.0, 
    end: float = 1.0,
    clustering_factor: float = 0.3,
    rand_gen: random.Random = None
) -> List[float]:
    """
    Generate positions with naturalistic clustering patterns.
    
    Args:
        count: Number of positions to generate
        start: Start position in range (default: 0.0)
        end: End position in range (default: 1.0)
        clustering_factor: How clustered positions should be (0-1)
        rand_gen: Random generator instance
        
    Returns:
        List of positions - NO LONGER SORTED to maintain randomness
    """
    if rand_gen is None:
        rand_gen = random.Random()
        
    if count <= 0:
        return []
        
    if count == 1:
        return [(start + end) / 2]
    
    # Initialize positions list
    positions = []
    range_size = end - start
    
    if clustering_factor < 0.2:
        # Low clustering - use even distribution with minor variation
        for i in range(count):
            base_pos = start + range_size * i / (count - 1)
            variation = range_size * 0.02 * rand_gen.random()
            pos = base_pos + variation
            positions.append(min(end, max(start, pos)))
    else:
        # Use clustering algorithm
        # Determine number of clusters based on clustering factor
        # More clusters with higher clustering factor
        num_clusters = max(1, min(count // 2, int(count * clustering_factor * 0.5)))
        
        # Generate cluster centers
        cluster_centers = []
        for i in range(num_clusters):
            # Distribute cluster centers evenly across range
            center = start + range_size * i / max(1, num_clusters - 1)
            cluster_centers.append(center)
        
        # Allocate positions to clusters
        positions_per_cluster = [0] * num_clusters
        for i in range(count):
            # Find least populated cluster
            min_cluster = positions_per_cluster.index(min(positions_per_cluster))
            positions_per_cluster[min_cluster] += 1
        
        # Generate positions for each cluster
        for cluster_idx, center in enumerate(cluster_centers):
            cluster_count = positions_per_cluster[cluster_idx]
            if cluster_count == 0:
                continue
                
            # Determine cluster range (spread)
            cluster_range = range_size / num_clusters * 0.8
            
            # Generate positions around this center
            for i in range(cluster_count):
                # Randomize within cluster range
                offset = (rand_gen.random() * 2 - 1) * cluster_range
                pos = center + offset
                
                # Ensure within overall range
                pos = min(end, max(start, pos))
                positions.append(pos)
    
    # Ensure no exact duplicates but maintain random order
    deduped_positions = []
    
    for pos in positions:
        # Check if position is too close to existing ones
        too_close = False
        for existing_pos in deduped_positions:
            if abs(pos - existing_pos) <= 0.01:
                too_close = True
                break
        
        if not too_close:
            deduped_positions.append(pos)
    
    # If we lost positions due to deduplication, add random ones
    while len(deduped_positions) < count:
        new_pos = start + range_size * rand_gen.random()
        too_close = False
        for existing_pos in deduped_positions:
            if abs(new_pos - existing_pos) <= 0.01:
                too_close = True
                break
        
        if not too_close:
            deduped_positions.append(new_pos)
    
    # Ensure we have exactly the right number of positions
    if len(deduped_positions) > count:
        # If too many, remove some (preserving first and last if they exist)
        extras = len(deduped_positions) - count
        if extras > 0:
            # Remove from middle randomly
            middle_indices = list(range(1, len(deduped_positions) - 1)) if len(deduped_positions) > 2 else list(range(len(deduped_positions)))
            if middle_indices and len(middle_indices) >= extras:
                to_remove = rand_gen.sample(middle_indices, extras)
                # Remove in reverse order to maintain indices
                for idx in reversed(to_remove):
                    deduped_positions.pop(idx)
            else:
                # Just truncate
                deduped_positions = deduped_positions[:count]
    
    # Ensure positions are within range
    deduped_positions = [max(start, min(end, pos)) for pos in deduped_positions]
    
    # Explicitly set first and last positions to start and end if close
    if deduped_positions and abs(deduped_positions[0] - start) < 0.05:
        deduped_positions[0] = start
    if deduped_positions and abs(deduped_positions[-1] - end) < 0.05:
        deduped_positions[-1] = end
    
    # DO NOT SORT - return positions in random order for true randomization
    return deduped_positions


def generate_color_palette(
    hsv_ranges: List[Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]],
    count: int,
    color_richness: float = 0.7,
    brightness_factor: float = 1.0,
    contrast_factor: float = 1.0,
    rand_gen: random.Random = None
) -> List[Tuple[int, int, int]]:
    """
    Generate a color palette with natural variations across HSV ranges.
    
    Args:
        hsv_ranges: List of HSV range tuples ((h_min, h_max), (s_min, s_max), (v_min, v_max))
        count: Number of colors to generate
        color_richness: Amount of color variation (0-1)
        brightness_factor: Overall brightness adjustment
        contrast_factor: Overall contrast adjustment
        rand_gen: Random generator instance
        
    Returns:
        List of RGB color tuples - maintains generation order (no sorting)
    """
    if rand_gen is None:
        rand_gen = random.Random()
    
    # Colors to generate
    colors = []
    
    # Number of colors per range
    colors_per_range = max(1, count // len(hsv_ranges))
    extra_colors = count - (colors_per_range * len(hsv_ranges))
    
    # Track range assignments for color distribution
    range_counts = [colors_per_range] * len(hsv_ranges)
    
    # Distribute extra colors to ranges
    for i in range(extra_colors):
        range_counts[i % len(hsv_ranges)] += 1
    
    # Generate clusters in each range
    for range_idx, hsv_range in enumerate(hsv_ranges):
        h_range, s_range, v_range = hsv_range
        range_count = range_counts[range_idx]
        
        # Skip if no colors assigned to this range
        if range_count <= 0:
            continue
        
        # Determine number of clusters for this range
        num_clusters = max(1, min(range_count, int(2 + range_count * 0.3)))
        
        # Generate cluster centers
        cluster_centers = []
        for _ in range(num_clusters):
            h = rand_gen.uniform(h_range[0], h_range[1])
            s = rand_gen.uniform(s_range[0], s_range[1])
            v = rand_gen.uniform(v_range[0], v_range[1])
            
            # Apply brightness and contrast adjustments
            v = adjust_value(v, brightness_factor, contrast_factor, v_range)
            
            cluster_centers.append((h, s, v))
        
        # Assign colors to clusters
        for i in range(range_count):
            # Choose a cluster, with some preference for less used clusters
            cluster_idx = rand_gen.randint(0, num_clusters - 1)
            
            # Get cluster center
            center_h, center_s, center_v = cluster_centers[cluster_idx]
            
            # Calculate variation scale based on color richness
            h_variation = (h_range[1] - h_range[0]) * 0.15 * color_richness
            s_variation = (s_range[1] - s_range[0]) * 0.2 * color_richness
            v_variation = (v_range[1] - v_range[0]) * 0.15 * color_richness
            
            # Add controlled variation
            h = (center_h + rand_gen.uniform(-h_variation, h_variation)) % 360
            s = max(0.0, min(1.0, center_s + rand_gen.uniform(-s_variation, s_variation)))
            v = max(0.0, min(1.0, center_v + rand_gen.uniform(-v_variation, v_variation)))
            
            # Apply random "micro variation" for naturalistic appearance
            if rand_gen.random() < 0.3:
                h = (h + rand_gen.uniform(-5, 5)) % 360
                s = max(0.0, min(1.0, s + rand_gen.uniform(-0.05, 0.05)))
                v = max(0.0, min(1.0, v + rand_gen.uniform(-0.05, 0.05)))
            
            # Convert to RGB
            color = hsv_to_rgb(h, s, v)
            colors.append(color)
    
    # If we didn't generate enough colors, add some random ones
    while len(colors) < count:
        # Choose a random range
        range_idx = rand_gen.randint(0, len(hsv_ranges) - 1)
        h_range, s_range, v_range = hsv_ranges[range_idx]
        
        # Generate a color within that range
        h = rand_gen.uniform(h_range[0], h_range[1])
        s = rand_gen.uniform(s_range[0], s_range[1])
        v = rand_gen.uniform(v_range[0], v_range[1])
        v = adjust_value(v, brightness_factor, contrast_factor, v_range)
        
        # Convert to RGB
        color = hsv_to_rgb(h, s, v)
        colors.append(color)
    
    # If we generated too many colors, truncate the list
    if len(colors) > count:
        colors = colors[:count]
    
    # DO NOT shuffle to mix range distributions - maintain generation order for randomness
    
    return colors


def create_naturalistic_color_stops(
    colors: List[Tuple[int, int, int]],
    clustering_factor: float = 0.3,
    rand_gen: random.Random = None
) -> List[Tuple[float, Tuple[int, int, int]]]:
    """
    Create naturalistic color stops from a list of colors.
    
    Args:
        colors: List of RGB color tuples
        clustering_factor: How clustered positions should be (0-1)
        rand_gen: Random generator instance
        
    Returns:
        List of (position, color) tuples - maintains original order (no sorting)
    """
    if not colors:
        return []
    
    # Generate positions with clustering
    positions = generate_naturalistic_positions(
        len(colors), 0.0, 1.0, clustering_factor, rand_gen
    )
    
    # Match positions with colors
    color_stops = list(zip(positions, colors))
    
    # Ensure first position is 0.0 and last is 1.0
    if color_stops and color_stops[0][0] > 0.0:
        color_stops[0] = (0.0, color_stops[0][1])
    
    if color_stops and color_stops[-1][0] < 1.0:
        color_stops[-1] = (1.0, color_stops[-1][1])
    
    # DO NOT SORT by position - maintain original order for randomness
    return color_stops


def blend_rgb_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                    factor: float) -> Tuple[int, int, int]:
    """
    Blend two RGB colors using linear interpolation.
    
    Args:
        color1: First RGB color tuple
        color2: Second RGB color tuple
        factor: Blend factor (0 = color1, 1 = color2)
        
    Returns:
        Blended RGB color tuple
    """
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    
    # Linear interpolation
    r = int(r1 * (1 - factor) + r2 * factor)
    g = int(g1 * (1 - factor) + g2 * factor)
    b = int(b1 * (1 - factor) + b2 * factor)
    
    return (r, g, b)


def blend_hsv_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                    factor: float) -> Tuple[int, int, int]:
    """
    Blend two RGB colors in HSV space for better transitions.
    
    Args:
        color1: First RGB color tuple
        color2: Second RGB color tuple
        factor: Blend factor (0 = color1, 1 = color2)
        
    Returns:
        Blended RGB color tuple
    """
    # Convert colors to HSV
    h1, s1, v1 = rgb_to_hsv(*color1)
    h2, s2, v2 = rgb_to_hsv(*color2)
    
    # Handle hue wrapping (go the shorter way around the color wheel)
    if abs(h2 - h1) > 180:
        if h1 < h2:
            h1 += 360
        else:
            h2 += 360
    
    # Interpolate in HSV space
    h = (h1 * (1 - factor) + h2 * factor) % 360
    s = s1 * (1 - factor) + s2 * factor
    v = v1 * (1 - factor) + v2 * factor
    
    # Convert back to RGB
    return hsv_to_rgb(h, s, v)


def get_hue_name(hue: float) -> str:
    """
    Get a descriptive name for a hue value.
    
    Args:
        hue: Hue value in degrees (0-360)
        
    Returns:
        String name of the hue
    """
    hue_names = {
        (0, 15): "Red",
        (15, 45): "Orange-Red",
        (45, 75): "Orange",
        (75, 105): "Yellow",
        (105, 135): "Yellow-Green",
        (135, 165): "Green",
        (165, 195): "Teal",
        (195, 225): "Cyan",
        (225, 255): "Blue",
        (255, 285): "Indigo",
        (285, 315): "Purple",
        (315, 345): "Magenta",
        (345, 360): "Red"
    }
    
    for (h_min, h_max), name in hue_names.items():
        if h_min <= hue < h_max:
            return name
    
    return "Mixed"


def create_transition_gradient(
    color1: Tuple[int, int, int], 
    color2: Tuple[int, int, int], 
    num_steps: int,
    blend_in_hsv: bool = True
) -> List[Tuple[float, Tuple[int, int, int]]]:
    """
    Create a smooth gradient transition between two colors.
    
    Args:
        color1: Start color as RGB tuple
        color2: End color as RGB tuple
        num_steps: Number of color stops to generate
        blend_in_hsv: Whether to blend in HSV space (better for most colors)
        
    Returns:
        List of (position, color) tuples for the gradient
    """
    gradient_stops = []
    
    blend_func = blend_hsv_colors if blend_in_hsv else blend_rgb_colors
    
    for i in range(num_steps):
        position = i / (num_steps - 1) if num_steps > 1 else 0.5
        if i == 0:
            color = color1
        elif i == num_steps - 1:
            color = color2
        else:
            factor = i / (num_steps - 1)
            color = blend_func(color1, color2, factor)
        
        gradient_stops.append((position, color))
    
    return gradient_stops


def generate_monochromatic_palette(
    base_hue: float, 
    saturation_range: Tuple[float, float],
    value_range: Tuple[float, float],
    num_colors: int,
    rand_gen: random.Random = None
) -> List[Tuple[int, int, int]]:
    """
    Generate a monochromatic color palette based on a single hue.
    
    Args:
        base_hue: Base hue in degrees (0-360)
        saturation_range: (min, max) range for saturation
        value_range: (min, max) range for value/brightness
        num_colors: Number of colors to generate
        rand_gen: Random generator instance
        
    Returns:
        List of RGB color tuples - maintains generation order (no sorting)
    """
    if rand_gen is None:
        rand_gen = random.Random()
    
    colors = []
    
    # Adjust hue slightly for each color to avoid flatness
    hue_variation = 10.0  # ±10 degrees
    
    # Generate colors
    for i in range(num_colors):
        # Vary hue slightly for realism
        hue = (base_hue + rand_gen.uniform(-hue_variation, hue_variation)) % 360
        
        # Distribute saturation and value across their ranges
        if num_colors > 1:
            # Gradually transition across the range
            progress = i / (num_colors - 1)
            # Map progress (0-1) to value range (low to high)
            value = value_range[0] + progress * (value_range[1] - value_range[0])
            # Saturation varies in a more random pattern
            saturation = rand_gen.uniform(saturation_range[0], saturation_range[1])
        else:
            # Single color case
            saturation = rand_gen.uniform(saturation_range[0], saturation_range[1])
            value = rand_gen.uniform(value_range[0], value_range[1])
        
        # Convert to RGB
        color = hsv_to_rgb(hue, saturation, value)
        colors.append(color)
    
    # DO NOT shuffle to avoid monotonous progression - maintain generation order for randomness
    
    return colors


# Testing functions
if __name__ == "__main__":
    # Test color generation
    hsv_ranges = [
        ((0, 60), (0.5, 0.8), (0.2, 0.4)),  # Shadows
        ((20, 80), (0.6, 0.9), (0.4, 0.7)),  # Midtones
        ((30, 90), (0.5, 0.8), (0.7, 0.9))   # Highlights
    ]
    
    colors = generate_color_palette(hsv_ranges, 12)
    print(f"Generated {len(colors)} colors")
    
    # Test position generation
    positions = generate_naturalistic_positions(10, 0.0, 1.0, 0.4)
    print(f"Positions: {positions}")
    
    # Test color stops creation
    color_stops = create_naturalistic_color_stops(colors, 0.4)
    print(f"Generated {len(color_stops)} color stops")
    for pos, color in color_stops:
        print(f"Position: {pos:.2f}, Color: {color}")