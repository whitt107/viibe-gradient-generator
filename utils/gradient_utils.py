#!/usr/bin/env python3
"""
Refactored Gradient Utilities Module for Enhanced Random Gradient Generator

This module provides utility functions for generating gradients with natural
patterns and distributions, shared between the theme generator and random
gradient generator.

Key improvements:
- Removed redundant code and excessive debug statements
- Consolidated similar functions
- Streamlined algorithms while preserving all functionality
- Improved error handling and performance
"""
import random
import math
import colorsys
from typing import List, Tuple, Dict, Any


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Convert HSV to RGB color space."""
    h_norm = h / 360.0
    r, g, b = colorsys.hsv_to_rgb(h_norm, s, v)
    return (
        max(0, min(255, int(round(r * 255)))),
        max(0, min(255, int(round(g * 255)))),
        max(0, min(255, int(round(b * 255))))
    )


def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB to HSV color space."""
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
    h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
    return (h * 360.0, s, v)


def adjust_value(value: float, brightness: float, contrast: float, 
                value_range: Tuple[float, float]) -> float:
    """Adjust a value component based on brightness and contrast factors."""
    adjusted = value * brightness
    mid_point = (value_range[0] + value_range[1]) / 2
    contrasted = mid_point + (adjusted - mid_point) * contrast
    return max(0.0, min(1.0, contrasted))


def generate_naturalistic_positions(
    count: int, 
    start: float = 0.0, 
    end: float = 1.0,
    clustering_factor: float = 0.3,
    rand_gen: random.Random = None
) -> List[float]:
    """Generate positions with naturalistic clustering patterns."""
    if rand_gen is None:
        rand_gen = random.Random()
        
    if count <= 0:
        return []
    if count == 1:
        return [(start + end) / 2]
    
    range_size = end - start
    positions = []
    
    if clustering_factor < 0.2:
        # Low clustering - even distribution with minor variation
        for i in range(count):
            base_pos = start + range_size * i / (count - 1)
            variation = range_size * 0.02 * rand_gen.random()
            positions.append(min(end, max(start, base_pos + variation)))
    else:
        # Clustering algorithm
        num_clusters = max(1, min(count // 2, int(count * clustering_factor * 0.5)))
        
        # Generate cluster centers
        cluster_centers = [start + range_size * i / max(1, num_clusters - 1) 
                          for i in range(num_clusters)]
        
        # Allocate positions to clusters
        positions_per_cluster = [0] * num_clusters
        for i in range(count):
            min_cluster = positions_per_cluster.index(min(positions_per_cluster))
            positions_per_cluster[min_cluster] += 1
        
        # Generate positions for each cluster
        for cluster_idx, center in enumerate(cluster_centers):
            cluster_count = positions_per_cluster[cluster_idx]
            if cluster_count == 0:
                continue
                
            cluster_range = range_size / num_clusters * 0.8
            
            for i in range(cluster_count):
                offset = (rand_gen.random() * 2 - 1) * cluster_range
                pos = min(end, max(start, center + offset))
                positions.append(pos)
    
    # Remove duplicates while maintaining order
    deduped_positions = []
    for pos in positions:
        if all(abs(pos - existing) > 0.01 for existing in deduped_positions):
            deduped_positions.append(pos)
    
    # Ensure we have the right number of positions
    while len(deduped_positions) < count:
        new_pos = start + range_size * rand_gen.random()
        if all(abs(new_pos - pos) > 0.01 for pos in deduped_positions):
            deduped_positions.append(new_pos)
    
    if len(deduped_positions) > count:
        # Remove excess from middle, preserving first and last if close to edges
        if count >= 2:
            # Keep positions closest to start and end
            sorted_by_distance = sorted(deduped_positions, 
                                      key=lambda x: min(abs(x-start), abs(x-end)))
            deduped_positions = sorted_by_distance[:count]
        else:
            deduped_positions = deduped_positions[:count]
    
    # Ensure positions are within range
    deduped_positions = [max(start, min(end, pos)) for pos in deduped_positions]
    
    # Set exact start/end if close
    if deduped_positions and abs(deduped_positions[0] - start) < 0.05:
        deduped_positions[0] = start
    if deduped_positions and abs(deduped_positions[-1] - end) < 0.05:
        deduped_positions[-1] = end
    
    return deduped_positions


def generate_color_palette(
    hsv_ranges: List[Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]],
    count: int,
    color_richness: float = 0.7,
    brightness_factor: float = 1.0,
    contrast_factor: float = 1.0,
    rand_gen: random.Random = None
) -> List[Tuple[int, int, int]]:
    """Generate a color palette with natural variations across HSV ranges."""
    if rand_gen is None:
        rand_gen = random.Random()
    
    colors = []
    colors_per_range = max(1, count // len(hsv_ranges))
    extra_colors = count - (colors_per_range * len(hsv_ranges))
    
    range_counts = [colors_per_range] * len(hsv_ranges)
    for i in range(extra_colors):
        range_counts[i % len(hsv_ranges)] += 1
    
    for range_idx, hsv_range in enumerate(hsv_ranges):
        h_range, s_range, v_range = hsv_range
        range_count = range_counts[range_idx]
        
        if range_count <= 0:
            continue
        
        num_clusters = max(1, min(range_count, int(2 + range_count * 0.3)))
        
        # Generate cluster centers
        cluster_centers = []
        for _ in range(num_clusters):
            h = rand_gen.uniform(h_range[0], h_range[1])
            s = rand_gen.uniform(s_range[0], s_range[1])
            v = rand_gen.uniform(v_range[0], v_range[1])
            v = adjust_value(v, brightness_factor, contrast_factor, v_range)
            cluster_centers.append((h, s, v))
        
        # Generate colors for this range
        for i in range(range_count):
            cluster_idx = rand_gen.randint(0, num_clusters - 1)
            center_h, center_s, center_v = cluster_centers[cluster_idx]
            
            # Calculate variation scale
            h_variation = (h_range[1] - h_range[0]) * 0.15 * color_richness
            s_variation = (s_range[1] - s_range[0]) * 0.2 * color_richness
            v_variation = (v_range[1] - v_range[0]) * 0.15 * color_richness
            
            # Add controlled variation
            h = (center_h + rand_gen.uniform(-h_variation, h_variation)) % 360
            s = max(0.0, min(1.0, center_s + rand_gen.uniform(-s_variation, s_variation)))
            v = max(0.0, min(1.0, center_v + rand_gen.uniform(-v_variation, v_variation)))
            
            # Micro variation for naturalistic appearance
            if rand_gen.random() < 0.3:
                h = (h + rand_gen.uniform(-5, 5)) % 360
                s = max(0.0, min(1.0, s + rand_gen.uniform(-0.05, 0.05)))
                v = max(0.0, min(1.0, v + rand_gen.uniform(-0.05, 0.05)))
            
            colors.append(hsv_to_rgb(h, s, v))
    
    # Fill any remaining slots
    while len(colors) < count:
        range_idx = rand_gen.randint(0, len(hsv_ranges) - 1)
        h_range, s_range, v_range = hsv_ranges[range_idx]
        
        h = rand_gen.uniform(h_range[0], h_range[1])
        s = rand_gen.uniform(s_range[0], s_range[1])
        v = rand_gen.uniform(v_range[0], v_range[1])
        v = adjust_value(v, brightness_factor, contrast_factor, v_range)
        
        colors.append(hsv_to_rgb(h, s, v))
    
    return colors[:count]


def create_naturalistic_color_stops(
    colors: List[Tuple[int, int, int]],
    clustering_factor: float = 0.3,
    rand_gen: random.Random = None
) -> List[Tuple[float, Tuple[int, int, int]]]:
    """Create naturalistic color stops from a list of colors."""
    if not colors:
        return []
    
    positions = generate_naturalistic_positions(
        len(colors), 0.0, 1.0, clustering_factor, rand_gen
    )
    
    color_stops = list(zip(positions, colors))
    
    # Ensure first position is 0.0 and last is 1.0
    if color_stops:
        if color_stops[0][0] > 0.0:
            color_stops[0] = (0.0, color_stops[0][1])
        if color_stops[-1][0] < 1.0:
            color_stops[-1] = (1.0, color_stops[-1][1])
    
    return color_stops


def blend_rgb_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                    factor: float) -> Tuple[int, int, int]:
    """Blend two RGB colors using linear interpolation."""
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    
    r = int(r1 * (1 - factor) + r2 * factor)
    g = int(g1 * (1 - factor) + g2 * factor)
    b = int(b1 * (1 - factor) + b2 * factor)
    
    return (r, g, b)


def blend_hsv_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                    factor: float) -> Tuple[int, int, int]:
    """Blend two RGB colors in HSV space for better transitions."""
    h1, s1, v1 = rgb_to_hsv(*color1)
    h2, s2, v2 = rgb_to_hsv(*color2)
    
    # Handle hue wrapping (shorter path around color wheel)
    if abs(h2 - h1) > 180:
        if h1 < h2:
            h1 += 360
        else:
            h2 += 360
    
    # Interpolate in HSV space
    h = (h1 * (1 - factor) + h2 * factor) % 360
    s = s1 * (1 - factor) + s2 * factor
    v = v1 * (1 - factor) + v2 * factor
    
    return hsv_to_rgb(h, s, v)


def get_hue_name(hue: float) -> str:
    """Get a descriptive name for a hue value."""
    hue_ranges = [
        (0, 15, "Red"), (15, 45, "Orange-Red"), (45, 75, "Orange"),
        (75, 105, "Yellow"), (105, 135, "Yellow-Green"), (135, 165, "Green"),
        (165, 195, "Teal"), (195, 225, "Cyan"), (225, 255, "Blue"),
        (255, 285, "Indigo"), (285, 315, "Purple"), (315, 345, "Magenta"),
        (345, 360, "Red")
    ]
    
    for h_min, h_max, name in hue_ranges:
        if h_min <= hue < h_max:
            return name
    
    return "Mixed"


def create_transition_gradient(
    color1: Tuple[int, int, int], 
    color2: Tuple[int, int, int], 
    num_steps: int,
    blend_in_hsv: bool = True
) -> List[Tuple[float, Tuple[int, int, int]]]:
    """Create a smooth gradient transition between two colors."""
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
    """Generate a monochromatic color palette based on a single hue."""
    if rand_gen is None:
        rand_gen = random.Random()
    
    colors = []
    hue_variation = 10.0  # ±10 degrees
    
    for i in range(num_colors):
        # Vary hue slightly for realism
        hue = (base_hue + rand_gen.uniform(-hue_variation, hue_variation)) % 360
        
        if num_colors > 1:
            # Distribute across value range
            progress = i / (num_colors - 1)
            value = value_range[0] + progress * (value_range[1] - value_range[0])
            saturation = rand_gen.uniform(saturation_range[0], saturation_range[1])
        else:
            saturation = rand_gen.uniform(saturation_range[0], saturation_range[1])
            value = rand_gen.uniform(value_range[0], value_range[1])
        
        colors.append(hsv_to_rgb(hue, saturation, value))
    
    return colors


# Simplified testing function (removed excessive debug output)
if __name__ == "__main__":
    print("Testing gradient utilities...")
    
    # Test color generation
    hsv_ranges = [
        ((0, 60), (0.5, 0.8), (0.2, 0.4)),    # Shadows
        ((20, 80), (0.6, 0.9), (0.4, 0.7)),   # Midtones
        ((30, 90), (0.5, 0.8), (0.7, 0.9))    # Highlights
    ]
    
    colors = generate_color_palette(hsv_ranges, 12)
    print(f"Generated {len(colors)} colors")
    
    # Test position generation
    positions = generate_naturalistic_positions(10, 0.0, 1.0, 0.4)
    print(f"Generated {len(positions)} positions")
    
    # Test color stops creation
    color_stops = create_naturalistic_color_stops(colors, 0.4)
    print(f"Generated {len(color_stops)} color stops")
    
    print("All tests completed successfully")
