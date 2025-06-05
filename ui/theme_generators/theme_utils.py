#!/usr/bin/env python3
"""
Theme Utilities Module for Gradient Generator - Fixed Version

This module provides common utility functions for theme-based gradient generators,
centralizing reusable algorithms for color generation, position distribution,
and value adjustment across different theme types.
"""
import random
import math
import colorsys
from typing import List, Tuple, Dict, Optional


def adjust_value(v: float, brightness_factor: float, contrast_factor: float, 
                value_range: Tuple[float, float]) -> float:
    """
    Adjust the value (brightness) component with brightness and contrast.
    
    Args:
        v: Original value component (0-1)
        brightness_factor: Brightness multiplier
        contrast_factor: Contrast multiplier
        value_range: (min, max) range for value component
        
    Returns:
        Adjusted value component (0-1)
    """
    # Apply brightness
    v_adjusted = v * brightness_factor
    
    # Apply contrast (pivot around middle of the value range)
    v_mid = (value_range[0] + value_range[1]) / 2
    v_contrast = v_mid + (v_adjusted - v_mid) * contrast_factor
    
    # Clamp to valid range
    return max(0.0, min(1.0, v_contrast))


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """
    Convert HSV to RGB.
    
    Args:
        h: Hue in degrees (0-360)
        s: Saturation (0-1)
        v: Value (0-1)
        
    Returns:
        RGB tuple with values in range 0-255
    """
    # Convert to 0-1 range for colorsys
    h_norm = h / 360.0
    
    # Get RGB in 0-1 range
    r, g, b = colorsys.hsv_to_rgb(h_norm, s, v)
    
    # Convert to 0-255 range
    return (
        int(round(r * 255)),
        int(round(g * 255)),
        int(round(b * 255))
    )


def generate_colors_in_range(
    hsv_ranges: List[Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]],
    count: int,
    color_richness: float,
    brightness_factor: float,
    contrast_factor: float,
    pattern_params: Dict[str, any],
    random_gen: random.Random
) -> List[Tuple[int, int, int]]:
    """
    Generate a list of colors within the specified HSV ranges.
    
    Args:
        hsv_ranges: List of (hue_range, saturation_range, value_range) tuples
        count: Number of colors to generate
        color_richness: Diversity and richness of colors (0-1)
        brightness_factor: Brightness adjustment
        contrast_factor: Contrast adjustment
        pattern_params: Pattern parameters including clusters
        random_gen: Random number generator instance
        
    Returns:
        List of RGB tuples
    """
    hue_range, saturation_range, value_range = hsv_ranges
    colors = []
    
    # Determine number of color clusters
    cluster_min, cluster_max = pattern_params["clusters"]
    
    # Ensure cluster_min is always less than cluster_max to avoid randrange error
    if cluster_min >= cluster_max:
        cluster_max = cluster_min + 1
        
    num_clusters = random_gen.randint(
        cluster_min, 
        min(cluster_max, count)  # Can't have more clusters than colors
    )
    
    # Generate cluster centers (in HSV space)
    cluster_centers = []
    for _ in range(num_clusters):
        h = random_gen.uniform(hue_range[0], hue_range[1])
        s = random_gen.uniform(saturation_range[0], saturation_range[1])
        v = random_gen.uniform(value_range[0], value_range[1])
        
        # Apply brightness and contrast adjustments to value component
        v = adjust_value(v, brightness_factor, contrast_factor, value_range)
        
        cluster_centers.append((h, s, v))
    
    # Distribute colors around cluster centers with natural variation
    for i in range(count):
        # Select a cluster, with preference for broader distribution 
        # when color_richness is high
        if color_richness > 0.5 and i < num_clusters:
            # Ensure we use each cluster at least once for high color richness
            cluster_idx = i
        else:
            # Otherwise select randomly, possibly weighted
            cluster_idx = random_gen.randint(0, num_clusters - 1)
        
        # Get the cluster center
        center_h, center_s, center_v = cluster_centers[cluster_idx]
        
        # Determine variation scales
        # More variation with higher color_richness
        hue_variation = (hue_range[1] - hue_range[0]) * 0.15 * color_richness
        sat_variation = (saturation_range[1] - saturation_range[0]) * 0.2 * color_richness
        val_variation = (value_range[1] - value_range[0]) * 0.15 * color_richness
        
        # Add controlled random variation
        h = (center_h + random_gen.uniform(-hue_variation, hue_variation)) % 360
        s = max(0.0, min(1.0, center_s + random_gen.uniform(-sat_variation, sat_variation)))
        v = max(0.0, min(1.0, center_v + random_gen.uniform(-val_variation, val_variation)))
        
        # Apply pattern-based micro-variation (variegation)
        if random_gen.random() < pattern_params["variegation"]:
            # Apply small random "spots" of color variation
            h = (h + random_gen.uniform(-10, 10)) % 360
            s = max(0.0, min(1.0, s + random_gen.uniform(-0.1, 0.1)))
        
        # Convert HSV to RGB
        rgb = hsv_to_rgb(h, s, v)
        colors.append(rgb)
    
    return colors


def apply_user_preferences_to_pattern(
    pattern_params: Dict[str, any], 
    variance: float, 
    texture_complexity: float, 
    position_clustering: float
) -> Dict[str, any]:
    """
    Modify pattern parameters based on user preferences.
    
    Args:
        pattern_params: Original pattern parameters
        variance: Amount of variance to apply (0-1)
        texture_complexity: Texture complexity level (0-1)
        position_clustering: Position clustering amount (0-1)
        
    Returns:
        Modified pattern parameters
    """
    # Clone the pattern parameters
    modified_pattern = pattern_params.copy()
    
    # Apply user preferences
    
    # Adjust clustering - more clusters for higher complexity
    base_clusters = pattern_params["clusters"]
    cluster_min, cluster_max = base_clusters
    
    # Scale clusters based on texture complexity (maintaining min-max relationship)
    cluster_scale = 1.0 + texture_complexity
    new_cluster_min = max(2, int(cluster_min * cluster_scale))
    new_cluster_max = max(new_cluster_min + 1, int(cluster_max * cluster_scale))  # Ensure max > min
    modified_pattern["clusters"] = (new_cluster_min, new_cluster_max)
    
    # Scale variegation based on user variance
    modified_pattern["variegation"] = pattern_params["variegation"] * (0.5 + variance)
    
    # Apply texture complexity to transition sharpness
    modified_pattern["transition_sharpness"] = pattern_params["transition_sharpness"] * texture_complexity
    
    # Apply user position clustering
    modified_pattern["position_clustering"] = (
        pattern_params["position_clustering"] * position_clustering
    )
    
    return modified_pattern


def generate_positions(
    start: float, 
    end: float, 
    count: int, 
    clustering_factor: float,
    random_gen: random.Random
) -> List[float]:
    """
    Generate naturalistic position distributions within a range.
    
    Args:
        start: Start position (0-1)
        end: End position (0-1)
        count: Number of positions to generate
        clustering_factor: How clustered the positions should be (0-1)
        random_gen: Random number generator instance
        
    Returns:
        List of positions sorted from start to end
    """
    if count <= 0:
        return []
        
    if count == 1:
        return [(start + end) / 2]
        
    positions = []
    range_size = end - start
    
    if clustering_factor < 0.2:
        # Very low clustering - use even distribution with minor variation
        for i in range(count):
            base_pos = start + range_size * i / (count - 1)
            # Add very minor variation
            variation = range_size * 0.02 * random_gen.random()
            pos = base_pos + variation
            positions.append(min(end, max(start, pos)))
    else:
        # Use clustering algorithm
        
        # First, determine number of clusters
        num_clusters = max(1, min(count - 1, int(count * clustering_factor * 0.5)))
        
        # Generate cluster centers
        cluster_centers = []
        for i in range(num_clusters):
            # Distribute cluster centers across range
            center = start + range_size * i / max(1, num_clusters - 1)
            cluster_centers.append(center)
        
        # Assign each position to a cluster
        positions_per_cluster = [0] * num_clusters
        for i in range(count):
            # Find least populated cluster
            min_cluster = positions_per_cluster.index(min(positions_per_cluster))
            positions_per_cluster[min_cluster] += 1
        
        # Generate positions for each cluster
        result = []
        for cluster_idx, center in enumerate(cluster_centers):
            cluster_count = positions_per_cluster[cluster_idx]
            if cluster_count == 0:
                continue
                
            # Determine this cluster's range
            cluster_range = range_size / num_clusters * 0.8  # 80% of even segment
            
            # Generate positions around this center
            for i in range(cluster_count):
                # Randomize position within cluster range
                offset = (random_gen.random() * 2 - 1) * cluster_range
                pos = center + offset
                
                # Ensure within overall range
                pos = min(end, max(start, pos))
                result.append(pos)
        
        positions = sorted(result)
    
    # Ensure no exact duplicates
    final_positions = []
    last_pos = None
    for pos in positions:
        if last_pos is None or abs(pos - last_pos) > 0.01:
            final_positions.append(pos)
            last_pos = pos
    
    # If we lost positions due to duplicates, add random ones
    while len(final_positions) < count:
        new_pos = start + range_size * random_gen.random()
        if all(abs(new_pos - pos) > 0.01 for pos in final_positions):
            final_positions.append(new_pos)
    
    # Sort final positions
    return sorted(final_positions)


def create_naturalistic_stops(
    color_palette: Dict[str, List[Tuple[int, int, int]]],
    pattern_params: Dict[str, any],
    stop_count: int,
    random_gen: random.Random
) -> List[Tuple[float, Tuple[int, int, int]]]:
    """
    Create color stops with naturalistic distributions.
    
    Args:
        color_palette: Dictionary with 'shadows', 'midtones', 'highlights' lists of RGB tuples
        pattern_params: Pattern parameters 
        stop_count: Number of color stops to create
        random_gen: Random number generator instance
        
    Returns:
        List of (position, color) tuples sorted by position
    """
    # Combine all colors from the palette into a single list
    all_colors = []
    all_colors.extend(color_palette["shadows"])
    all_colors.extend(color_palette["midtones"])
    all_colors.extend(color_palette["highlights"])
    
    # Shuffle the colors to mix the tonal ranges
    random_gen.shuffle(all_colors)
    
    # If we have more colors than needed, trim the list
    if len(all_colors) > stop_count:
        all_colors = all_colors[:stop_count]
    
    # Generate positions across the full 0-1 range
    positions = generate_positions(
        0.0, 1.0,  # Full range
        len(all_colors),
        pattern_params["position_clustering"],
        random_gen
    )
    
    # Combine positions and colors
    color_stops = []
    for i, color in enumerate(all_colors):
        color_stops.append((positions[i], color))
    
    # Sort by position
    color_stops.sort(key=lambda x: x[0])
    
    # Ensure we start at position 0.0 and end at 1.0 exactly
    if color_stops[0][0] > 0.01:
        color_stops.insert(0, (0.0, color_stops[0][1]))
    else:
        color_stops[0] = (0.0, color_stops[0][1])
        
    if color_stops[-1][0] < 0.99:
        color_stops.append((1.0, color_stops[-1][1]))
    else:
        color_stops[-1] = (1.0, color_stops[-1][1])
    
    return color_stops


def calculate_tonal_counts(
    stop_count: int,
    theme_type: str = None
) -> Tuple[int, int, int]:
    """
    Calculate appropriate counts for shadows, midtones, and highlights based on theme type.
    
    Args:
        stop_count: Total number of color stops
        theme_type: Optional theme type string to adjust distribution
        
    Returns:
        Tuple of (shadow_count, midtone_count, highlight_count)
    """
    # Default distribution
    shadow_count = max(3, int(stop_count * 0.3))
    midtone_count = max(3, int(stop_count * 0.4))
    highlight_count = max(3, int(stop_count * 0.3))
    
    # Adjust based on theme type if provided
    if theme_type:
        if theme_type in ["winter", "pine", "blue_spruce"]:
            # More midtones and highlights for these types
            midtone_count = int(midtone_count * 1.2)
            highlight_count = int(highlight_count * 1.2)
            shadow_count = stop_count - midtone_count - highlight_count
        elif theme_type in ["autumn", "autumn_mixed", "red_maple"]:
            # More highlights for these vibrant types
            highlight_count = int(highlight_count * 1.3)
            shadow_count = int(shadow_count * 0.9)
            midtone_count = stop_count - highlight_count - shadow_count
    
    # Ensure minimum counts
    shadow_count = max(2, shadow_count)
    midtone_count = max(3, midtone_count)
    highlight_count = max(2, highlight_count)
    
    # Adjust counts to match target stop count
    total = shadow_count + midtone_count + highlight_count
    if total < stop_count:
        # Add the difference to midtones
        midtone_count += (stop_count - total)
    elif total > stop_count:
        # Reduce counts proportionally
        factor = stop_count / total
        shadow_count = max(2, int(shadow_count * factor))
        midtone_count = max(3, int(midtone_count * factor))
        highlight_count = max(2, int(highlight_count * factor))
    
    return shadow_count, midtone_count, highlight_count


def generate_color_palette(
    base_color_ranges: List[Tuple],
    color_richness: float,
    brightness: float,
    contrast: float,
    shadow_depth: float,
    highlight_vibrance: float,
    pattern_params: Dict[str, any],
    stop_count: int,
    theme_type: str,
    random_gen: random.Random
) -> Dict[str, List[Tuple[int, int, int]]]:
    """
    Generate a rich color palette from HSV ranges.
    
    Args:
        base_color_ranges: List of HSV range tuples for shadows, midtones, highlights
        color_richness: Color richness factor (0-1)
        brightness: Overall brightness adjustment
        contrast: Overall contrast adjustment
        shadow_depth: Shadow depth factor (0-1)
        highlight_vibrance: Highlight vibrance factor (0-1)
        pattern_params: Pattern parameters
        stop_count: Total number of color stops
        theme_type: Type of theme (affects color distribution)
        random_gen: Random number generator
        
    Returns:
        Dictionary with 'shadows', 'midtones', 'highlights' lists of RGB tuples
    """
    # Calculate appropriate counts for each tonal range
    shadow_count, midtone_count, highlight_count = calculate_tonal_counts(
        stop_count, theme_type
    )
    
    # Generate colors for each tonal range
    shadows = generate_colors_in_range(
        base_color_ranges[0],  # Shadow HSV ranges
        shadow_count,
        color_richness,
        brightness * (1.0 - shadow_depth * 0.5),  # Darker shadows
        contrast,
        pattern_params,
        random_gen
    )
    
    midtones = generate_colors_in_range(
        base_color_ranges[1],  # Midtone HSV ranges
        midtone_count,
        color_richness,
        brightness,  # Standard brightness
        contrast,
        pattern_params,
        random_gen
    )
    
    highlights = generate_colors_in_range(
        base_color_ranges[2],  # Highlight HSV ranges
        highlight_count,
        color_richness,
        brightness * (1.0 + highlight_vibrance * 0.3),  # Brighter highlights
        contrast,
        pattern_params,
        random_gen
    )
    
    return {
        "shadows": shadows,
        "midtones": midtones,
        "highlights": highlights
    }
