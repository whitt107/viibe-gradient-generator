#!/usr/bin/env python3
"""
Refactored Fire Theme Generator - FIXED VERSION

Creates realistic fire-themed gradients with proper temperature effects,
improved smoke blending, and streamlined parameters.

FIXES:
- Temperature slider now properly affects fire color temperature
- Smoke blend adds realistic grey/white/black smoke colors
- Removed unnecessary random seed slider
- Fixed high/low value handling to prevent errors
- Improved color temperature accuracy
"""
import time
import random
import math
import colorsys
from typing import List, Tuple, Dict

# Import with fallback mechanism
try:
    from gradient_generator.core.gradient import Gradient
    from gradient_generator.core.color_utils import rgb_to_hsv, hsv_to_rgb
except ImportError:
    try:
        from core.gradient import Gradient
        from core.color_utils import rgb_to_hsv, hsv_to_rgb
    except ImportError:
        class Gradient:
            def __init__(self):
                self._color_stops = []
                self._name = ""
                self._description = ""
                self._author = ""
                self._ugr_category = ""
            
            def add_color_stop(self, position, color):
                self._color_stops.append((position, color))
            
            def set_name(self, name): self._name = name
            def set_description(self, desc): self._description = desc
            def set_author(self, author): self._author = author
            def set_ugr_category(self, category): self._ugr_category = category
            def get_name(self): return self._name
            def get_description(self): return self._description
        
        def rgb_to_hsv(r, g, b):
            r, g, b = r/255.0, g/255.0, b/255.0
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            return h * 360, s, v
        
        def hsv_to_rgb(h, s, v):
            h = h / 360.0
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            return int(r * 255), int(g * 255), int(b * 255)


class ThemeParameter:
    """Theme parameter class."""
    def __init__(self, name: str, label: str, min_value: float, max_value: float, 
                default_value: float, step: float = 0.1, description: str = ""):
        self.name = name
        self.label = label
        self.min_value = min_value
        self.max_value = max_value
        self.default_value = default_value
        self.value = default_value
        self.step = step
        self.description = description
    
    def set_value(self, value: float):
        self.value = max(self.min_value, min(self.max_value, value))
    
    def reset(self):
        self.value = self.default_value


class ThemeGradientGeneratorBase:
    """Base class for theme generators."""
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.parameters = self._create_parameters()
    
    def _create_parameters(self) -> Dict[str, ThemeParameter]:
        return {}
    
    def get_parameter(self, name: str) -> ThemeParameter:
        return self.parameters.get(name)
    
    def set_parameter_value(self, name: str, value: float):
        if name in self.parameters:
            self.parameters[name].set_value(value)
    
    def get_parameter_value(self, name: str) -> float:
        if name in self.parameters:
            return self.parameters[name].value
        return 0.0
    
    def reset_parameters(self):
        for param in self.parameters.values():
            param.reset()
    
    def get_parameter_list(self) -> List[ThemeParameter]:
        return list(self.parameters.values())
    
    def _create_gradient_with_name(self) -> Gradient:
        gradient = Gradient()
        gradient._color_stops = []
        gradient.set_name(f"{self.name} Theme Gradient")
        return gradient


def hsv_to_rgb_util(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Convert HSV to RGB with proper 0-255 range and bounds checking."""
    # Ensure valid input ranges
    h = max(0.0, min(360.0, h))
    s = max(0.0, min(1.0, s))
    v = max(0.0, min(1.0, v))
    
    h_norm = h / 360.0
    r, g, b = colorsys.hsv_to_rgb(h_norm, s, v)
    return (
        max(0, min(255, int(round(r * 255)))),
        max(0, min(255, int(round(g * 255)))),
        max(0, min(255, int(round(b * 255))))
    )


def apply_temperature_effect(base_ranges: List, temperature: float) -> List:
    """Apply realistic temperature effect to fire colors."""
    # Clamp temperature to valid range
    temperature = max(0.0, min(1.0, temperature))
    
    adjusted_ranges = []
    
    for hue_range, sat_range, val_range in base_ranges:
        # Temperature effect on fire colors:
        # 0.0 = Cool fire (more red/orange, lower temp ~800-1200K)
        # 0.5 = Normal fire (orange/yellow, ~1200-1500K) 
        # 1.0 = Hot fire (white/blue, >1500K)
        
        if temperature > 0.8:
            # Very hot - white/blue hot (>1800K)
            hot_factor = (temperature - 0.8) / 0.2
            
            # Shift toward blue-white
            new_hue_min = max(0, hue_range[0] + hot_factor * 180)  # Toward blue
            new_hue_max = min(360, hue_range[1] + hot_factor * 180)
            
            # Drastically reduce saturation for white-hot effect
            sat_reduction = hot_factor * 0.8
            new_sat_min = max(0.0, sat_range[0] - sat_reduction)
            new_sat_max = max(0.1, sat_range[1] - sat_reduction)
            
            # Increase brightness significantly
            brightness_boost = 1.0 + hot_factor * 0.5
            new_val_min = min(1.0, val_range[0] * brightness_boost)
            new_val_max = min(1.0, val_range[1] * brightness_boost)
            
        elif temperature > 0.6:
            # Hot fire - yellow/white (1200-1800K)
            hot_factor = (temperature - 0.6) / 0.2
            
            # Shift toward yellow/white
            hue_shift = hot_factor * 20  # Toward yellow
            new_hue_min = min(60, hue_range[0] + hue_shift)
            new_hue_max = min(60, hue_range[1] + hue_shift)
            
            # Moderate saturation reduction
            sat_reduction = hot_factor * 0.3
            new_sat_min = max(0.2, sat_range[0] - sat_reduction)
            new_sat_max = max(0.4, sat_range[1] - sat_reduction)
            
            # Increase brightness
            brightness_boost = 1.0 + hot_factor * 0.3
            new_val_min = min(1.0, val_range[0] * brightness_boost)
            new_val_max = min(1.0, val_range[1] * brightness_boost)
            
        elif temperature < 0.4:
            # Cool fire - red/orange (800-1200K)
            cool_factor = (0.4 - temperature) / 0.4
            
            # Shift toward deep red
            hue_shift = cool_factor * 15
            new_hue_min = max(0, hue_range[0] - hue_shift)
            new_hue_max = max(10, hue_range[1] - hue_shift)
            
            # Increase saturation for deeper colors
            sat_boost = cool_factor * 0.2
            new_sat_min = min(1.0, sat_range[0] + sat_boost)
            new_sat_max = min(1.0, sat_range[1] + sat_boost)
            
            # Reduce brightness for cooler appearance
            brightness_reduction = 1.0 - cool_factor * 0.2
            new_val_min = max(0.1, val_range[0] * brightness_reduction)
            new_val_max = max(0.2, val_range[1] * brightness_reduction)
            
        else:
            # Normal temperature range (0.4-0.6)
            new_hue_min, new_hue_max = hue_range
            new_sat_min, new_sat_max = sat_range
            new_val_min, new_val_max = val_range
        
        # Ensure valid ranges
        if new_hue_min > new_hue_max:
            new_hue_min, new_hue_max = new_hue_max, new_hue_min
        if new_sat_min > new_sat_max:
            new_sat_min, new_sat_max = new_sat_max, new_sat_min
        if new_val_min > new_val_max:
            new_val_min, new_val_max = new_val_max, new_val_min
        
        adjusted_ranges.append([
            (new_hue_min, new_hue_max),
            (new_sat_min, new_sat_max),
            (new_val_min, new_val_max)
        ])
    
    return adjusted_ranges


def add_smoke_colors(color_palette: Dict, smoke_amount: float, 
                    random_gen: random.Random) -> Dict:
    """Add realistic smoke colors - greys, whites, and blacks."""
    # Clamp smoke amount
    smoke_amount = max(0.0, min(1.0, smoke_amount))
    
    if smoke_amount < 0.05:
        return color_palette
    
    # Number of smoke colors to add based on amount
    smoke_count = max(1, int(smoke_amount * 8))
    
    smoke_colors = []
    
    for _ in range(smoke_count):
        smoke_type = random_gen.random()
        
        if smoke_type < 0.3:
            # Dark smoke/ash (blacks and dark greys)
            h = random_gen.uniform(0, 30)  # Slight warm tint
            s = random_gen.uniform(0.05, 0.2) * smoke_amount
            v = random_gen.uniform(0.05, 0.25) * (1.0 + smoke_amount * 0.3)
            
        elif smoke_type < 0.6:
            # Medium smoke (greys)
            h = random_gen.uniform(0, 60)  # Warm grey tint
            s = random_gen.uniform(0.1, 0.3) * smoke_amount
            v = random_gen.uniform(0.3, 0.6)
            
        else:
            # Light smoke/steam (light greys and whites)
            h = random_gen.uniform(200, 220)  # Slight cool tint
            s = random_gen.uniform(0.02, 0.15) * smoke_amount
            v = random_gen.uniform(0.7, 0.95)
        
        smoke_color = hsv_to_rgb_util(h, s, v)
        smoke_colors.append(smoke_color)
    
    # Distribute smoke colors across all tonal ranges for realism
    smoke_per_range = len(smoke_colors) // 3
    remainder = len(smoke_colors) % 3
    
    # Add to shadows (dark smoke)
    color_palette["shadows"].extend(smoke_colors[:smoke_per_range + (1 if remainder > 0 else 0)])
    
    # Add to midtones (medium smoke)
    start_idx = smoke_per_range + (1 if remainder > 0 else 0)
    end_idx = start_idx + smoke_per_range + (1 if remainder > 1 else 0)
    color_palette["midtones"].extend(smoke_colors[start_idx:end_idx])
    
    # Add to highlights (light smoke)
    color_palette["highlights"].extend(smoke_colors[end_idx:])
    
    return color_palette


def generate_positions(start: float, end: float, count: int, 
                      clustering_factor: float, random_gen: random.Random) -> List[float]:
    """Generate naturalistic position distributions with bounds checking."""
    # Input validation
    start = max(0.0, min(1.0, start))
    end = max(start, min(1.0, end))
    count = max(1, count)
    clustering_factor = max(0.0, min(1.0, clustering_factor))
    
    if count <= 0:
        return []
    if count == 1:
        return [(start + end) / 2]
    
    positions = []
    range_size = end - start
    
    if clustering_factor < 0.2 or range_size < 0.01:
        # Even distribution
        for i in range(count):
            base_pos = start + range_size * i / (count - 1)
            variation = range_size * 0.02 * random_gen.random()
            pos = base_pos + variation
            positions.append(min(end, max(start, pos)))
    else:
        # Clustering algorithm with bounds checking
        num_clusters = max(1, min(count, int(count * clustering_factor * 0.5)))
        
        cluster_centers = []
        for i in range(num_clusters):
            center = start + range_size * i / max(1, num_clusters - 1)
            cluster_centers.append(center)
        
        positions_per_cluster = [0] * num_clusters
        for i in range(count):
            min_cluster = positions_per_cluster.index(min(positions_per_cluster))
            positions_per_cluster[min_cluster] += 1
        
        result = []
        for cluster_idx, center in enumerate(cluster_centers):
            cluster_count = positions_per_cluster[cluster_idx]
            if cluster_count == 0:
                continue
                
            cluster_range = min(range_size / num_clusters * 0.8, range_size * 0.3)
            
            for i in range(cluster_count):
                offset = (random_gen.random() * 2 - 1) * cluster_range
                pos = center + offset
                pos = min(end, max(start, pos))
                result.append(pos)
        
        positions = sorted(result)
    
    # Remove duplicates with bounds checking
    final_positions = []
    last_pos = None
    for pos in positions:
        pos = max(start, min(end, pos))
        if last_pos is None or abs(pos - last_pos) > 0.01:
            final_positions.append(pos)
            last_pos = pos
    
    # Ensure we have enough positions
    while len(final_positions) < count and len(final_positions) < 100:  # Prevent infinite loop
        new_pos = start + range_size * random_gen.random()
        if all(abs(new_pos - pos) > 0.01 for pos in final_positions):
            final_positions.append(new_pos)
    
    return sorted(final_positions[:count])  # Ensure exact count


class FireThemeGenerator(ThemeGradientGeneratorBase):
    """Enhanced Fire Theme Generator with proper temperature effects and smoke blending."""

    FIRE_TYPE_NAMES = [
        "Candle Flame", "Wood Fire", "Gas Flame", "Coal Fire", 
        "Inferno", "Dragon Fire", "Blue Flame", "White Hot",
        "Ember Glow", "Wildfire", "Forge Fire", "Plasma Fire"
    ]
    
    FIRE_TYPE_MAP = {
        "Candle Flame": "candle", "Wood Fire": "wood", "Gas Flame": "gas", 
        "Coal Fire": "coal", "Inferno": "inferno", "Dragon Fire": "dragon",
        "Blue Flame": "blue", "White Hot": "white_hot", "Ember Glow": "ember", 
        "Wildfire": "wildfire", "Forge Fire": "forge", "Plasma Fire": "plasma"
    }

    # Base fire color ranges (before temperature modification)
    FIRE_COLOR_RANGES = {
        "candle": [
            [(0, 15), (0.6, 0.8), (0.1, 0.25)],    # Deep red base
            [(15, 35), (0.7, 0.9), (0.3, 0.6)],    # Orange core
            [(35, 60), (0.5, 0.8), (0.7, 0.95)]    # Yellow tips
        ],
        "wood": [
            [(0, 20), (0.7, 0.9), (0.15, 0.3)],
            [(10, 40), (0.8, 1.0), (0.4, 0.7)],
            [(30, 60), (0.6, 0.9), (0.6, 0.9)]
        ],
        "gas": [
            [(220, 250), (0.4, 0.7), (0.2, 0.4)],  # Blue base
            [(200, 240), (0.5, 0.8), (0.4, 0.7)],
            [(45, 60), (0.3, 0.6), (0.8, 1.0)]
        ],
        "coal": [
            [(350, 15), (0.8, 1.0), (0.1, 0.2)],
            [(0, 25), (0.6, 0.8), (0.3, 0.5)],
            [(20, 45), (0.7, 0.9), (0.5, 0.7)]
        ],
        "inferno": [
            [(350, 20), (0.9, 1.0), (0.05, 0.2)],
            [(0, 30), (0.8, 1.0), (0.3, 0.6)],
            [(25, 55), (0.7, 0.9), (0.7, 1.0)]
        ],
        "dragon": [
            [(0, 30), (0.7, 0.9), (0.2, 0.4)],
            [(15, 45), (0.8, 1.0), (0.4, 0.7)],
            [(40, 70), (0.6, 0.8), (0.6, 0.9)]
        ],
        "blue": [
            [(200, 250), (0.6, 0.9), (0.2, 0.4)],
            [(210, 260), (0.4, 0.7), (0.5, 0.8)],
            [(220, 280), (0.2, 0.5), (0.8, 1.0)]
        ],
        "white_hot": [
            [(20, 60), (0.1, 0.3), (0.3, 0.5)],
            [(30, 70), (0.05, 0.2), (0.6, 0.8)],
            [(40, 80), (0.0, 0.1), (0.9, 1.0)]
        ],
        "ember": [
            [(350, 20), (0.7, 0.9), (0.1, 0.3)],
            [(0, 30), (0.5, 0.7), (0.2, 0.5)],
            [(15, 45), (0.6, 0.8), (0.4, 0.7)]
        ],
        "wildfire": [
            [(340, 25), (0.8, 1.0), (0.1, 0.25)],
            [(5, 35), (0.7, 0.9), (0.3, 0.6)],
            [(25, 65), (0.6, 0.8), (0.6, 0.9)]
        ],
        "forge": [
            [(350, 20), (0.8, 1.0), (0.2, 0.4)],
            [(10, 40), (0.7, 0.9), (0.4, 0.7)],
            [(30, 60), (0.5, 0.7), (0.7, 0.9)]
        ],
        "plasma": [
            [(270, 320), (0.3, 0.6), (0.3, 0.5)],
            [(200, 280), (0.4, 0.7), (0.5, 0.8)],
            [(180, 240), (0.5, 0.8), (0.8, 1.0)]
        ]
    }
    
    def __init__(self):
        super().__init__(
            name="Fire",
            description="Generate realistic fire gradients with temperature and smoke effects"
        )
        self.fire_type = "wood"
        self.random_gen = random.Random()
        self.generation_counter = 0
    
    def request_new_seed(self):
        """Request a new seed for the next gradient generation."""
        self.generation_counter += 1

    def _create_parameters(self) -> Dict[str, ThemeParameter]:
        """Create fire-specific parameters."""
        return {
            "fire_type": ThemeParameter("fire_type", "Fire Type", 0.0, 11.0, 1.0, 1.0,
                                       "Type of fire to generate"),
            "flame_intensity": ThemeParameter("flame_intensity", "Flame Intensity", 0.0, 1.0, 0.7, 0.05,
                                            "Energy and wildness of flames"),
            "temperature": ThemeParameter("temperature", "Temperature", 0.0, 1.0, 0.5, 0.05,
                                        "Fire temperature: 0=cool red/orange, 0.5=normal, 1=white/blue hot"),
            "flame_height": ThemeParameter("flame_height", "Flame Height", 0.0, 1.0, 0.5, 0.05,
                                         "Height affects hue distribution"),
            "smoke_blend": ThemeParameter("smoke_blend", "Smoke Blend", 0.0, 1.0, 0.2, 0.05,
                                        "Amount of smoke colors (greys/whites/blacks)"),
            "core_brightness": ThemeParameter("core_brightness", "Core Brightness", 0.5, 2.0, 1.2, 0.05,
                                            "Brightness of flame core"),
            "color_saturation": ThemeParameter("color_saturation", "Color Saturation", 0.3, 1.5, 1.0, 0.05,
                                             "Overall color intensity"),
            "flame_spread": ThemeParameter("flame_spread", "Flame Spread", 0.0, 1.0, 0.5, 0.05,
                                         "Spread of flame positions"),
            "stop_count": ThemeParameter("stop_count", "Color Stops", 8.0, 64.0, 20.0, 2.0,
                                        "Number of color stops (8-64)")
        }
    
    def generate_gradient(self):
        """Generate fire-themed gradient with proper temperature and smoke effects."""
        # Generate unique seed
        seed = int(time.time() * 1000) % 1000000 + self.generation_counter
        self.random_gen.seed(seed)
        
        gradient = self._create_gradient_with_name()
        
        # Get parameters with bounds checking
        fire_type_idx = max(0, min(len(self.FIRE_TYPE_NAMES)-1, int(self.parameters["fire_type"].value)))
        fire_name = self.FIRE_TYPE_NAMES[fire_type_idx]
        self.fire_type = self.FIRE_TYPE_MAP.get(fire_name, "wood")
        
        params = {
            "flame_intensity": max(0.0, min(1.0, self.parameters["flame_intensity"].value)),
            "temperature": max(0.0, min(1.0, self.parameters["temperature"].value)),
            "flame_height": max(0.0, min(1.0, self.parameters["flame_height"].value)),
            "smoke_blend": max(0.0, min(1.0, self.parameters["smoke_blend"].value)),
            "core_brightness": max(0.5, min(2.0, self.parameters["core_brightness"].value)),
            "color_saturation": max(0.3, min(1.5, self.parameters["color_saturation"].value)),
            "flame_spread": max(0.0, min(1.0, self.parameters["flame_spread"].value)),
            "stop_count": max(8, min(64, int(self.parameters["stop_count"].value)))
        }
        
        # Get base color ranges and apply temperature effect
        base_ranges = self.FIRE_COLOR_RANGES[self.fire_type]
        temp_adjusted_ranges = apply_temperature_effect(base_ranges, params["temperature"])
        
        # Generate color palette
        color_palette = self._generate_color_palette(temp_adjusted_ranges, params)
        
        # Add smoke colors
        color_palette = add_smoke_colors(color_palette, params["smoke_blend"], self.random_gen)
        
        # Create color stops
        color_stops = self._create_color_stops(color_palette, params)
        
        # Add to gradient
        for position, color in color_stops:
            gradient.add_color_stop(position, color)
        
        # Set metadata
        temp_desc = ("Cool" if params["temperature"] < 0.3 else 
                    "Hot" if params["temperature"] < 0.7 else "White-Hot")
        gradient.set_name(f"Fire - {fire_name} ({temp_desc}) [Seed: {seed}]")
        gradient.set_description(
            f"{fire_name.lower()} fire gradient. "
            f"Temp: {params['temperature']:.2f}, "
            f"Intensity: {params['flame_intensity']:.2f}, "
            f"Smoke: {params['smoke_blend']:.2f}"
        )
        gradient.set_author("VIIBE Gradient Generator")
        gradient.set_ugr_category("Fire Themes")
        
        return gradient
    
    def _generate_color_palette(self, color_ranges, params) -> Dict:
        """Generate color palette from ranges."""
        stop_count = params["stop_count"]
        shadow_count = max(3, int(stop_count * 0.3))
        midtone_count = max(4, int(stop_count * 0.4))
        highlight_count = max(3, int(stop_count * 0.3))
        
        # Adjust counts to match target
        total = shadow_count + midtone_count + highlight_count
        if total != stop_count:
            midtone_count += (stop_count - total)
        
        def generate_colors_in_range(hsv_range, count, brightness_adj):
            hue_range, sat_range, val_range = hsv_range
            colors = []
            
            for i in range(count):
                h = self.random_gen.uniform(hue_range[0], hue_range[1])
                s = self.random_gen.uniform(sat_range[0], sat_range[1]) * params["color_saturation"]
                v = self.random_gen.uniform(val_range[0], val_range[1]) * brightness_adj
                
                # Apply bounds checking
                s = max(0.0, min(1.0, s))
                v = max(0.0, min(1.0, v))
                
                color = hsv_to_rgb_util(h, s, v)
                colors.append(color)
            
            return colors
        
        return {
            "shadows": generate_colors_in_range(color_ranges[0], shadow_count, 
                                              params["core_brightness"] * 0.7),
            "midtones": generate_colors_in_range(color_ranges[1], midtone_count, 
                                               params["core_brightness"]),
            "highlights": generate_colors_in_range(color_ranges[2], highlight_count, 
                                                 params["core_brightness"] * 1.3)
        }
    
    def _create_color_stops(self, color_palette, params) -> List:
        """Create color stops with flame spread positioning."""
        all_colors = (color_palette["shadows"] + 
                     color_palette["midtones"] + 
                     color_palette["highlights"])
        
        self.random_gen.shuffle(all_colors)
        
        if len(all_colors) > params["stop_count"]:
            all_colors = all_colors[:params["stop_count"]]
        
        positions = generate_positions(
            0.0, 1.0, len(all_colors),
            0.3 + params["flame_spread"] * 0.4,
            self.random_gen
        )
        
        color_stops = list(zip(positions, all_colors))
        color_stops.sort(key=lambda x: x[0])
        
        # Ensure proper endpoints
        if color_stops and color_stops[0][0] > 0.01:
            color_stops[0] = (0.0, color_stops[0][1])
        if color_stops and color_stops[-1][0] < 0.99:
            color_stops[-1] = (1.0, color_stops[-1][1])
        
        return color_stops