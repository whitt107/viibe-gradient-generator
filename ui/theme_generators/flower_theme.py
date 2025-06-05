#!/usr/bin/env python3
"""
Refactored Flower Theme Generator - Streamlined & Responsive

Features 15 research-backed flower types with improved UI responsiveness.
Removed excess debug code, improved slider names, and ensured leaf integration
automatically updates preview. No even distribution applied to maintain natural patterns.
"""
import time
import random
import colorsys
from typing import List, Tuple, Dict

# Import with fallback
try:
    from .theme_gradient_generator import ThemeGradientGenerator, ThemeParameter
except ImportError:
    try:
        from theme_gradient_generator import ThemeGradientGenerator, ThemeParameter
    except ImportError:
        class ThemeGradientGenerator:
            def __init__(self, name, description=""): 
                self.name, self.description, self.parameters = name, description, {}
        class ThemeParameter:
            def __init__(self, name, label, min_val, max_val, default, step, desc=""):
                self.name, self.label = name, label
                self.min_value, self.max_value, self.default_value = min_val, max_val, default
                self.value, self.step, self.description = default, step, desc
            def set_value(self, value): self.value = max(self.min_value, min(self.max_value, value))
            def reset(self): self.value = self.default_value


class FlowerThemeGenerator(ThemeGradientGenerator):
    """Streamlined flower generator with responsive leaf integration and natural patterns."""

    # 15 flower types based on botanical research
    FLOWER_TYPE_NAMES = [
        "Rose", "Tulip", "Sunflower", "Lavender", "Cherry Blossom", "Peony", 
        "Iris", "Hibiscus", "Daffodil", "Orchid", "Poppy", "Lily", 
        "Marigold", "Violet", "Chrysanthemum"
    ]
    
    # Research-based flower color definitions
    FLOWER_COLORS = {
        "rose": {
            "shadows": [(139, 0, 0), (165, 42, 42), (178, 34, 34), (128, 0, 0), (102, 51, 51)],
            "midtones": [(220, 20, 60), (255, 20, 147), (255, 105, 180), (255, 182, 193), (255, 192, 203)],
            "highlights": [(255, 228, 225), (255, 240, 245), (255, 248, 220), (255, 250, 240), (255, 255, 255)]
        },
        "tulip": {
            "shadows": [(128, 0, 128), (139, 0, 139), (148, 0, 211), (75, 0, 130), (102, 51, 153)],
            "midtones": [(255, 0, 255), (255, 20, 147), (255, 215, 0), (255, 255, 0), (238, 130, 238)],
            "highlights": [(255, 240, 245), (255, 255, 224), (255, 255, 240), (255, 248, 220), (255, 250, 250)]
        },
        "sunflower": {
            "shadows": [(184, 134, 11), (218, 165, 32), (205, 133, 63), (160, 82, 45), (139, 69, 19)],
            "midtones": [(255, 215, 0), (255, 255, 0), (255, 218, 185), (255, 228, 181), (255, 239, 213)],
            "highlights": [(255, 248, 220), (255, 250, 240), (255, 255, 224), (255, 255, 240), (255, 250, 205)]
        },
        "lavender": {
            "shadows": [(75, 0, 130), (106, 90, 205), (123, 104, 238), (72, 61, 139), (138, 43, 226)],
            "midtones": [(147, 112, 219), (216, 191, 216), (221, 160, 221), (230, 230, 250), (238, 130, 238)],
            "highlights": [(245, 245, 245), (248, 248, 255), (255, 240, 245), (255, 248, 220), (250, 240, 255)]
        },
        "cherry_blossom": {
            "shadows": [(255, 105, 180), (255, 182, 193), (255, 192, 203), (219, 112, 147), (199, 21, 133)],
            "midtones": [(255, 218, 185), (255, 228, 225), (255, 240, 245), (255, 228, 181), (255, 239, 213)],
            "highlights": [(255, 248, 220), (255, 250, 240), (255, 255, 224), (255, 255, 240), (255, 250, 250)]
        },
        "peony": {
            "shadows": [(205, 92, 92), (220, 20, 60), (255, 20, 147), (199, 21, 133), (219, 112, 147)],
            "midtones": [(255, 105, 180), (255, 182, 193), (255, 192, 203), (255, 160, 122), (255, 127, 80)],
            "highlights": [(255, 218, 185), (255, 228, 225), (255, 240, 245), (255, 248, 220), (255, 250, 240)]
        },
        "iris": {
            "shadows": [(25, 25, 112), (72, 61, 139), (75, 0, 130), (106, 90, 205), (123, 104, 238)],
            "midtones": [(147, 112, 219), (176, 196, 222), (135, 206, 235), (173, 216, 230), (216, 191, 216)],
            "highlights": [(230, 230, 250), (248, 248, 255), (240, 248, 255), (245, 245, 245), (255, 255, 255)]
        },
        "hibiscus": {
            "shadows": [(128, 0, 0), (139, 0, 0), (165, 42, 42), (178, 34, 34), (220, 20, 60)],
            "midtones": [(255, 0, 0), (255, 69, 0), (255, 99, 71), (255, 140, 0), (255, 165, 0)],
            "highlights": [(255, 215, 0), (255, 218, 185), (255, 228, 181), (255, 239, 213), (255, 248, 220)]
        },
        "daffodil": {
            "shadows": [(255, 140, 0), (255, 165, 0), (218, 165, 32), (184, 134, 11), (205, 133, 63)],
            "midtones": [(255, 215, 0), (255, 255, 0), (255, 218, 185), (255, 228, 181), (255, 239, 213)],
            "highlights": [(255, 248, 220), (255, 250, 240), (255, 255, 224), (255, 255, 240), (255, 255, 255)]
        },
        "orchid": {
            "shadows": [(153, 50, 204), (138, 43, 226), (148, 0, 211), (199, 21, 133), (219, 112, 147)],
            "midtones": [(218, 112, 214), (238, 130, 238), (255, 20, 147), (255, 105, 180), (221, 160, 221)],
            "highlights": [(255, 182, 193), (255, 192, 203), (255, 240, 245), (248, 248, 255), (255, 255, 255)]
        },
        "poppy": {
            "shadows": [(139, 0, 0), (165, 42, 42), (178, 34, 34), (128, 0, 0), (220, 20, 60)],
            "midtones": [(255, 0, 0), (255, 69, 0), (255, 99, 71), (255, 20, 147), (255, 140, 0)],
            "highlights": [(255, 165, 0), (255, 215, 0), (255, 218, 185), (255, 228, 181), (255, 239, 213)]
        },
        "lily": {
            "shadows": [(255, 140, 0), (255, 165, 0), (255, 105, 180), (219, 112, 147), (205, 92, 92)],
            "midtones": [(255, 182, 193), (255, 192, 203), (255, 218, 185), (255, 228, 181), (255, 239, 213)],
            "highlights": [(255, 240, 245), (255, 248, 220), (255, 250, 240), (255, 255, 224), (255, 255, 255)]
        },
        "marigold": {
            "shadows": [(184, 134, 11), (218, 165, 32), (205, 133, 63), (160, 82, 45), (255, 140, 0)],
            "midtones": [(255, 165, 0), (255, 215, 0), (255, 255, 0), (255, 218, 185), (255, 228, 181)],
            "highlights": [(255, 239, 213), (255, 248, 220), (255, 250, 240), (255, 255, 224), (255, 255, 240)]
        },
        "violet": {
            "shadows": [(75, 0, 130), (72, 61, 139), (106, 90, 205), (25, 25, 112), (123, 104, 238)],
            "midtones": [(147, 112, 219), (138, 43, 226), (216, 191, 216), (221, 160, 221), (230, 230, 250)],
            "highlights": [(238, 130, 238), (245, 245, 245), (248, 248, 255), (255, 240, 245), (255, 255, 255)]
        },
        "chrysanthemum": {
            "shadows": [(184, 134, 11), (139, 0, 139), (165, 42, 42), (128, 0, 128), (218, 165, 32)],
            "midtones": [(255, 215, 0), (255, 20, 147), (255, 182, 193), (238, 130, 238), (255, 218, 185)],
            "highlights": [(255, 228, 225), (255, 240, 245), (255, 248, 220), (255, 250, 240), (255, 255, 255)]
        }
    }
    
    # Research-based leaf/foliage colors
    LEAF_COLORS = {
        "shadows": [(0, 100, 0), (34, 139, 34), (0, 128, 0), (85, 107, 47), (107, 142, 35)],
        "midtones": [(50, 205, 50), (60, 179, 113), (102, 205, 170), (144, 238, 144), (152, 251, 152)],
        "highlights": [(173, 255, 47), (205, 255, 105), (240, 255, 240), (245, 255, 250), (248, 255, 240)]
    }
    
    def __init__(self):
        super().__init__("Botanical Flowers", "15 research-based flower types with natural color patterns")
        self.last_flower_type = -1
        self.base_structure = None
        self.random_gen = random.Random()
        self._current_seed = int(time.time() * 1000) % 999999

    def _create_parameters(self) -> Dict[str, ThemeParameter]:
        """Create streamlined parameters with better names."""
        return {
            "flower_type": ThemeParameter("flower_type", "Flower Species", 0, 14, 0, 1, "Select botanical flower species"),
            "color_vibrancy": ThemeParameter("color_vibrancy", "Color Vibrancy", 0, 1, 0.8, 0.01, "Intensity and saturation of flower colors"),
            "tonal_depth": ThemeParameter("tonal_depth", "Tonal Depth", 0, 1, 0.6, 0.01, "Range from light to dark tones"),
            "foliage_mix": ThemeParameter("foliage_mix", "Foliage Mix", 0, 1, 0.3, 0.01, "Amount of green leaf colors mixed with flowers"),
            "lighting_warmth": ThemeParameter("lighting_warmth", "Lighting Warmth", 0, 1, 0.7, 0.01, "Cool morning to warm afternoon light"),
            "natural_variance": ThemeParameter("natural_variance", "Natural Variance", 0, 1, 0.5, 0.01, "Color variation within the species"),
            "stops": ThemeParameter("stops", "Color Stops", 4, 32, 12, 1, "Number of gradient color stops")
        }

    def _rgb_to_hsv(self, r: int, g: int, b: int) -> Tuple[float, float, float]:
        """Convert RGB to HSV."""
        return colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB."""
        r, g, b = colorsys.hsv_to_rgb(h, max(0, min(1, s)), max(0, min(1, v)))
        return (int(r * 255), int(g * 255), int(b * 255))

    def _get_flower_key(self) -> str:
        """Get current flower key from type parameter."""
        flower_idx = int(self.parameters["flower_type"].value) % len(self.FLOWER_TYPE_NAMES)
        return self.FLOWER_TYPE_NAMES[flower_idx].lower().replace(" ", "_")

    def _select_flower_colors(self, flower_colors: Dict, num_colors: int) -> List[Tuple[int, int, int]]:
        """Select and blend colors from the flower palette."""
        all_colors = []
        
        # Calculate foliage integration
        foliage_amount = self.parameters["foliage_mix"].value
        num_leaf_colors = int(num_colors * foliage_amount)
        num_flower_colors = num_colors - num_leaf_colors
        
        # Distribute flower colors across tonal ranges
        depth = self.parameters["tonal_depth"].value
        
        if depth < 0.3:  # Light flowers - more highlights
            shadow_weight, midtone_weight, highlight_weight = 0.2, 0.3, 0.5
        elif depth > 0.7:  # Deep tones - more shadows
            shadow_weight, midtone_weight, highlight_weight = 0.5, 0.3, 0.2
        else:  # Balanced
            shadow_weight, midtone_weight, highlight_weight = 0.3, 0.4, 0.3
        
        # Select flower colors
        if num_flower_colors > 0:
            shadow_count = max(1, int(num_flower_colors * shadow_weight))
            midtone_count = max(1, int(num_flower_colors * midtone_weight))
            highlight_count = max(1, num_flower_colors - shadow_count - midtone_count)
            
            for _ in range(shadow_count):
                all_colors.append(self.random_gen.choice(flower_colors["shadows"]))
            for _ in range(midtone_count):
                all_colors.append(self.random_gen.choice(flower_colors["midtones"]))
            for _ in range(highlight_count):
                all_colors.append(self.random_gen.choice(flower_colors["highlights"]))
        
        # Add leaf colors
        if num_leaf_colors > 0:
            leaf_shadow_count = max(1, int(num_leaf_colors * 0.4))
            leaf_midtone_count = max(1, int(num_leaf_colors * 0.4))
            leaf_highlight_count = max(1, num_leaf_colors - leaf_shadow_count - leaf_midtone_count)
            
            for _ in range(leaf_shadow_count):
                all_colors.append(self.random_gen.choice(self.LEAF_COLORS["shadows"]))
            for _ in range(leaf_midtone_count):
                all_colors.append(self.random_gen.choice(self.LEAF_COLORS["midtones"]))
            for _ in range(leaf_highlight_count):
                all_colors.append(self.random_gen.choice(self.LEAF_COLORS["highlights"]))
        
        # Shuffle to mix naturally
        self.random_gen.shuffle(all_colors)
        return all_colors[:num_colors]

    def _generate_natural_positions(self, num_stops: int) -> List[float]:
        """Generate natural positions with organic spacing."""
        positions = []
        
        if num_stops <= 2:
            if num_stops == 1:
                return [0.5]
            else:
                return [0.0, 1.0]
        
        # Generate natural organic positions without even distribution
        # Start with endpoints
        positions = [0.0, 1.0]
        
        # Add intermediate positions with natural clustering
        for i in range(num_stops - 2):
            # Create natural clusters with some randomness
            cluster_position = self.random_gen.random()
            
            # Add some natural variation to avoid perfect spacing
            variation = 0.15 * (self.random_gen.random() - 0.5)
            pos = max(0.01, min(0.99, cluster_position + variation))
            positions.append(pos)
        
        # Sort and ensure minimum spacing
        positions.sort()
        for i in range(1, len(positions)):
            if positions[i] - positions[i-1] < 0.015:
                positions[i] = min(1.0, positions[i-1] + 0.015)
        
        return positions

    def _apply_botanical_adjustments(self, rgb_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Apply botanical and environmental adjustments."""
        r, g, b = rgb_color
        h, s, v = self._rgb_to_hsv(r, g, b)
        h *= 360
        
        # Get parameters
        vibrancy = self.parameters["color_vibrancy"].value
        warmth = self.parameters["lighting_warmth"].value
        variance = self.parameters["natural_variance"].value
        
        # Apply vibrancy
        s = s * (0.4 + vibrancy * 0.6)
        v = v * (0.5 + vibrancy * 0.3)
        
        # Apply lighting warmth
        if warmth > 0.5:  # Warm light
            warm_factor = (warmth - 0.5) * 2
            if h > 180:  # Cool colors
                h = max(0, h - warm_factor * 15)
            v = v * (1 + warm_factor * 0.15)
        else:  # Cool light
            cool_factor = (0.5 - warmth) * 2
            if h < 180:  # Warm colors
                h = min(360, h + cool_factor * 15)
            v = v * (1 - cool_factor * 0.1)
        
        # Natural variance
        if variance > 0.1:
            hue_var = variance * 15 * (self.random_gen.random() - 0.5)
            sat_var = variance * 0.15 * (self.random_gen.random() - 0.5)
            val_var = variance * 0.1 * (self.random_gen.random() - 0.5)
            
            h = (h + hue_var) % 360
            s = max(0.0, min(1.0, s + sat_var))
            v = max(0.0, min(1.0, v + val_var))
        
        return self._hsv_to_rgb(h / 360, s, v)

    def _should_regenerate_base(self) -> bool:
        """Check if base structure needs regeneration."""
        current_flower = int(self.parameters["flower_type"].value)
        current_stops = int(self.parameters["stops"].value)
        
        flower_changed = current_flower != self.last_flower_type
        stops_changed = (self.base_structure and len(self.base_structure) != current_stops)
        
        return flower_changed or stops_changed or not self.base_structure

    def generate_gradient(self):
        """Generate streamlined botanical flower gradient."""
        # Generate new seed if needed
        if self._should_regenerate_base():
            self._current_seed = int(time.time() * 1000) % 999999
            self.random_gen.seed(self._current_seed)
            
            # Get colors and generate base structure
            flower_key = self._get_flower_key()
            flower_colors = self.FLOWER_COLORS.get(flower_key, self.FLOWER_COLORS["rose"])
            stops = int(self.parameters["stops"].value)
            
            selected_colors = self._select_flower_colors(flower_colors, stops)
            positions = self._generate_natural_positions(stops)
            
            self.base_structure = list(zip(positions, selected_colors))
            self.last_flower_type = int(self.parameters["flower_type"].value)
        
        # Create gradient
        try:
            from gradient_generator.core.gradient import Gradient
        except ImportError:
            class Gradient:
                def __init__(self):
                    self._color_stops, self.name, self.description = [], "", ""
                    self.author, self.ugr_category = "", ""
                def add_color_stop(self, pos, color): self._color_stops.append((pos, color))
                def set_name(self, name): self.name = name
                def set_description(self, desc): self.description = desc
                def set_author(self, author): self.author = author
                def set_ugr_category(self, cat): self.ugr_category = cat
        
        gradient = Gradient()
        gradient._color_stops = []
        
        # Apply adjustments to base colors
        for pos, base_color in self.base_structure:
            adjusted_color = self._apply_botanical_adjustments(base_color)
            gradient.add_color_stop(pos, adjusted_color)
        
        # Generate name
        flower_name = self.FLOWER_TYPE_NAMES[int(self.parameters["flower_type"].value)]
        foliage_desc = " & Foliage" if self.parameters["foliage_mix"].value > 0.3 else ""
        
        gradient.set_name(f"{flower_name} Garden{foliage_desc}")
        gradient.set_description(
            f"Botanical {flower_name.lower()} gradient with natural color patterns. "
            f"Vibrancy: {self.parameters['color_vibrancy'].value:.2f}, "
            f"Foliage: {self.parameters['foliage_mix'].value:.2f}."
        )
        gradient.set_author("VIIBE Botanical Generator")
        gradient.set_ugr_category("Natural Botanical")
        
        return gradient

    def reset_parameters(self):
        """Reset parameters except flower type."""
        current_flower = self.parameters["flower_type"].value
        
        for name, param in self.parameters.items():
            if name != "flower_type":
                param.reset()
        
        self.parameters["flower_type"].value = current_flower
        self.base_structure = None  # Force regeneration