#!/usr/bin/env python3
"""
Refactored Foliage Theme Generator - Streamlined Implementation

Features 16 scientifically-accurate foliage types with real-world color palettes.
Streamlined with better parameter names, reduced debug code, and simplified controls.
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


class FoliageThemeGenerator(ThemeGradientGenerator):
    """Streamlined foliage generator with 16 plant types and accurate botanical colors."""

    FOLIAGE_TYPE_NAMES = [
        "Spring Oak", "Summer Maple", "Autumn Mixed", "Winter Pine", "Tropical Palm",
        "Desert Sage", "Forest Fern", "Bamboo Grove", "Eucalyptus", "Japanese Maple",
        "Redwood", "Birch", "Willow", "Moss & Lichen", "Alpine Conifers", "Rainforest Canopy"
    ]
    
    # Research-based color definitions (preserved from original)
    FOLIAGE_COLORS = {
        "spring_oak": {
            "shadows": [(34, 79, 23), (45, 95, 35), (56, 111, 47), (67, 127, 59), (78, 143, 71)],
            "midtones": [(89, 159, 83), (100, 175, 95), (124, 191, 107), (148, 207, 119), (172, 223, 131)],
            "highlights": [(196, 239, 143), (220, 255, 155), (235, 255, 180), (245, 255, 200), (250, 255, 220)]
        },
        "summer_maple": {
            "shadows": [(15, 51, 24), (25, 67, 34), (35, 83, 44), (45, 99, 54), (55, 115, 64)],
            "midtones": [(65, 131, 74), (75, 147, 84), (95, 163, 104), (115, 179, 124), (135, 195, 144)],
            "highlights": [(155, 211, 164), (175, 227, 184), (195, 243, 204), (215, 255, 224), (235, 255, 244)]
        },
        "autumn_mixed": {
            "shadows": [(101, 67, 33), (139, 69, 19), (160, 82, 45), (205, 133, 63), (222, 184, 135)],
            "midtones": [(255, 140, 0), (255, 165, 0), (255, 215, 0), (218, 165, 32), (184, 134, 11)],
            "highlights": [(255, 218, 185), (255, 228, 196), (255, 239, 213), (255, 245, 238), (255, 250, 240)]
        },
        "winter_pine": {
            "shadows": [(19, 36, 23), (29, 46, 33), (39, 56, 43), (49, 66, 53), (59, 76, 63)],
            "midtones": [(69, 86, 73), (79, 96, 83), (89, 106, 93), (99, 116, 103), (119, 136, 123)],
            "highlights": [(139, 156, 143), (159, 176, 163), (179, 196, 183), (199, 216, 203), (219, 236, 223)]
        },
        "tropical_palm": {
            "shadows": [(0, 100, 0), (34, 139, 34), (46, 125, 50), (60, 179, 113), (85, 107, 47)],
            "midtones": [(102, 205, 170), (124, 252, 0), (144, 238, 144), (152, 251, 152), (173, 255, 47)],
            "highlights": [(205, 255, 105), (240, 255, 240), (245, 255, 250), (250, 255, 240), (255, 255, 255)]
        },
        "desert_sage": {
            "shadows": [(85, 107, 47), (105, 105, 105), (119, 136, 153), (128, 128, 128), (169, 169, 169)],
            "midtones": [(192, 192, 192), (175, 238, 238), (176, 224, 230), (135, 206, 235), (173, 216, 230)],
            "highlights": [(230, 230, 250), (240, 248, 255), (245, 245, 245), (248, 248, 255), (255, 255, 255)]
        },
        "forest_fern": {
            "shadows": [(34, 49, 34), (46, 79, 46), (62, 98, 62), (78, 117, 78), (94, 136, 94)],
            "midtones": [(110, 155, 110), (126, 174, 126), (142, 193, 142), (158, 212, 158), (174, 231, 174)],
            "highlights": [(190, 250, 190), (206, 255, 206), (222, 255, 222), (238, 255, 238), (250, 255, 250)]
        },
        "bamboo_grove": {
            "shadows": [(85, 107, 47), (107, 142, 35), (124, 158, 52), (141, 174, 69), (158, 190, 86)],
            "midtones": [(175, 206, 103), (192, 222, 120), (209, 238, 137), (226, 254, 154), (243, 255, 171)],
            "highlights": [(255, 255, 224), (255, 255, 240), (255, 250, 205), (255, 248, 220), (255, 255, 255)]
        },
        "eucalyptus": {
            "shadows": [(47, 79, 79), (95, 158, 160), (102, 153, 153), (119, 181, 183), (136, 209, 213)],
            "midtones": [(153, 218, 242), (175, 238, 238), (176, 224, 230), (192, 192, 192), (211, 211, 211)],
            "highlights": [(230, 230, 250), (240, 248, 255), (245, 245, 245), (248, 248, 255), (255, 255, 255)]
        },
        "japanese_maple": {
            "shadows": [(85, 26, 26), (105, 26, 26), (125, 26, 26), (139, 0, 0), (165, 42, 42)],
            "midtones": [(178, 34, 34), (205, 92, 92), (220, 20, 60), (233, 150, 122), (250, 128, 114)],
            "highlights": [(255, 160, 122), (255, 182, 193), (255, 192, 203), (255, 218, 185), (255, 228, 225)]
        },
        "redwood": {
            "shadows": [(59, 26, 26), (79, 46, 46), (99, 66, 66), (119, 86, 86), (139, 106, 106)],
            "midtones": [(34, 79, 34), (54, 99, 54), (74, 119, 74), (94, 139, 94), (114, 159, 114)],
            "highlights": [(134, 179, 134), (154, 199, 154), (174, 219, 174), (194, 239, 194), (214, 255, 214)]
        },
        "birch": {
            "shadows": [(60, 179, 113), (85, 155, 85), (110, 171, 110), (135, 187, 135), (160, 203, 160)],
            "midtones": [(185, 219, 185), (200, 235, 200), (215, 251, 215), (230, 255, 230), (240, 255, 240)],
            "highlights": [(245, 255, 245), (248, 255, 248), (250, 255, 250), (253, 255, 253), (255, 255, 255)]
        },
        "willow": {
            "shadows": [(107, 142, 35), (124, 158, 52), (141, 174, 69), (158, 190, 86), (175, 206, 103)],
            "midtones": [(192, 222, 120), (209, 238, 137), (226, 254, 154), (240, 255, 240), (245, 255, 250)],
            "highlights": [(250, 255, 240), (253, 255, 243), (255, 255, 224), (255, 255, 240), (255, 255, 255)]
        },
        "moss_lichen": {
            "shadows": [(46, 79, 46), (62, 95, 62), (78, 111, 78), (94, 127, 94), (110, 143, 110)],
            "midtones": [(126, 159, 126), (142, 175, 142), (158, 191, 158), (174, 207, 174), (190, 223, 190)],
            "highlights": [(206, 239, 206), (222, 255, 222), (238, 255, 238), (246, 255, 246), (250, 255, 250)]
        },
        "alpine_conifers": {
            "shadows": [(25, 25, 112), (47, 79, 79), (70, 130, 180), (95, 158, 160), (119, 136, 153)],
            "midtones": [(135, 206, 235), (176, 196, 222), (176, 224, 230), (192, 192, 192), (211, 211, 211)],
            "highlights": [(230, 230, 250), (240, 248, 255), (245, 245, 245), (248, 248, 255), (255, 255, 255)]
        },
        "rainforest_canopy": {
            "shadows": [(0, 100, 0), (0, 128, 0), (34, 139, 34), (46, 125, 50), (60, 179, 113)],
            "midtones": [(102, 205, 170), (144, 238, 144), (152, 251, 152), (173, 255, 47), (205, 255, 105)],
            "highlights": [(240, 255, 240), (245, 255, 250), (250, 255, 240), (253, 255, 253), (255, 255, 255)]
        }
    }
    
    def __init__(self):
        super().__init__("Foliage Collection", "16 research-based foliage types with accurate botanical colors")
        self.last_foliage_type = -1
        self.base_structure = None
        self.random_gen = random.Random()
        self._internal_seed = int(time.time() * 1000) % 999999  # Internal seed management

    def _create_parameters(self) -> Dict[str, ThemeParameter]:
        """Create streamlined botanical parameters with better names."""
        return {
            "foliage_type": ThemeParameter(
                "foliage_type", "Plant Type", 0, 15, 0, 1, 
                "Select foliage type from 16 research-based plant varieties"
            ),
            "seasonal_shift": ThemeParameter(
                "seasonal_shift", "Season", 0, 1, 0.5, 0.01, 
                "Seasonal color variation: spring (0) to autumn (1)"
            ),
            "plant_health": ThemeParameter(
                "plant_health", "Plant Health", 0, 1, 0.8, 0.01, 
                "Plant vitality: affects color saturation and vibrancy"
            ),
            "sunlight": ThemeParameter(
                "sunlight", "Sunlight Exposure", 0, 1, 0.6, 0.01, 
                "Sun/shade adaptation: shade (0) to full sun (1)"
            ),
            "maturity": ThemeParameter(
                "maturity", "Growth Stage", 0, 1, 0.5, 0.01, 
                "Leaf maturity: young growth (0) to mature foliage (1)"
            ),
            "hydration": ThemeParameter(
                "hydration", "Water Level", 0, 1, 0.5, 0.01, 
                "Plant hydration: affects color depth and intensity"
            ),
            "chlorophyll": ThemeParameter(
                "chlorophyll", "Green Intensity", 0, 1, 0.7, 0.01, 
                "Chlorophyll density: affects green pigment strength"
            ),
            "stress_level": ThemeParameter(
                "stress_level", "Environmental Stress", 0, 1, 0.2, 0.01, 
                "Environmental stress: adds browns and yellows"
            ),
            "stops": ThemeParameter(
                "stops", "Color Stops", 4, 32, 14, 1, 
                "Number of gradient color stops"
            )
        }

    def _rgb_to_hsv(self, r: int, g: int, b: int) -> Tuple[float, float, float]:
        """Convert RGB to HSV."""
        return colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB."""
        r, g, b = colorsys.hsv_to_rgb(h, max(0, min(1, s)), max(0, min(1, v)))
        return (int(r * 255), int(g * 255), int(b * 255))

    def _get_foliage_key(self) -> str:
        """Get current foliage key from type parameter."""
        foliage_idx = int(self.parameters["foliage_type"].value) % len(self.FOLIAGE_TYPE_NAMES)
        return self.FOLIAGE_TYPE_NAMES[foliage_idx].lower().replace(" ", "_")

    def _select_foliage_colors(self, foliage_colors: Dict, num_colors: int) -> List[Tuple[int, int, int]]:
        """Select and blend colors from the foliage palette."""
        all_colors = []
        
        # Distribute colors based on maturity and sunlight
        maturity = self.parameters["maturity"].value
        sunlight = self.parameters["sunlight"].value
        
        # Adjust distribution based on parameters
        if maturity < 0.3:  # Young growth - more highlights
            shadow_weight, midtone_weight, highlight_weight = 0.2, 0.3, 0.5
        elif maturity > 0.7:  # Mature growth - more shadows and midtones
            shadow_weight, midtone_weight, highlight_weight = 0.4, 0.4, 0.2
        else:  # Balanced mature foliage
            shadow_weight, midtone_weight, highlight_weight = 0.3, 0.4, 0.3
        
        # Sunlight affects highlight distribution
        if sunlight > 0.7:  # High light - more highlights
            highlight_weight *= 1.3
            shadow_weight *= 0.8
        elif sunlight < 0.3:  # Low light - more shadows
            shadow_weight *= 1.3
            highlight_weight *= 0.8
        
        # Calculate counts for each tonal range
        shadow_count = max(1, int(num_colors * shadow_weight))
        midtone_count = max(1, int(num_colors * midtone_weight))
        highlight_count = max(1, num_colors - shadow_count - midtone_count)
        
        # Select colors from each range
        for _ in range(shadow_count):
            all_colors.append(self.random_gen.choice(foliage_colors["shadows"]))
        for _ in range(midtone_count):
            all_colors.append(self.random_gen.choice(foliage_colors["midtones"]))
        for _ in range(highlight_count):
            all_colors.append(self.random_gen.choice(foliage_colors["highlights"]))
        
        # Shuffle to mix tonal ranges naturally
        self.random_gen.shuffle(all_colors)
        
        return all_colors[:num_colors]

    def _generate_naturalistic_positions(self, num_stops: int) -> List[float]:
        """Generate naturalistic leaf distribution positions."""
        # Simple naturalistic distribution without texture variation parameter
        positions = []
        
        # Create natural clustering patterns
        num_clusters = max(2, min(num_stops // 3, 4))
        
        # Generate cluster centers
        cluster_centers = []
        for i in range(num_clusters):
            center = i / (num_clusters - 1) if num_clusters > 1 else 0.5
            # Add some randomness to cluster centers
            center += (self.random_gen.random() - 0.5) * 0.2
            center = max(0.1, min(0.9, center))
            cluster_centers.append(center)
        
        # Distribute positions around clusters
        for i in range(num_stops):
            cluster_idx = i % num_clusters
            center = cluster_centers[cluster_idx]
            
            # Random position around cluster center
            cluster_spread = 0.15
            offset = (self.random_gen.random() - 0.5) * cluster_spread
            pos = max(0.0, min(1.0, center + offset))
            positions.append(pos)
        
        # Sort and ensure minimum spacing
        positions.sort()
        for i in range(1, len(positions)):
            if positions[i] - positions[i-1] < 0.008:
                positions[i] = min(1.0, positions[i-1] + 0.008)
        
        return positions

    def _apply_botanical_adjustments(self, rgb_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Apply botanical and environmental adjustments to colors."""
        r, g, b = rgb_color
        h, s, v = self._rgb_to_hsv(r, g, b)
        h *= 360  # Convert to degrees
        
        # Get parameters with new names
        seasonal_shift = self.parameters["seasonal_shift"].value
        plant_health = self.parameters["plant_health"].value
        sunlight = self.parameters["sunlight"].value
        maturity = self.parameters["maturity"].value
        hydration = self.parameters["hydration"].value
        chlorophyll = self.parameters["chlorophyll"].value
        stress_level = self.parameters["stress_level"].value
        
        # 1. Seasonal color shift
        if seasonal_shift > 0.6:  # Autumn colors
            if 60 <= h <= 180:  # Green range
                seasonal_hue_shift = (seasonal_shift - 0.6) * 100
                s *= 1.2
            else:
                seasonal_hue_shift = 0
        elif seasonal_shift < 0.4:  # Spring colors
            if 60 <= h <= 180:
                seasonal_hue_shift = (0.4 - seasonal_shift) * -20
                v *= 1.1
            else:
                seasonal_hue_shift = 0
        else:
            seasonal_hue_shift = 0
        
        h = (h + seasonal_hue_shift) % 360
        
        # 2. Plant health affects saturation and brightness
        health_factor = 0.5 + plant_health * 0.5
        s *= health_factor
        v *= health_factor
        
        # 3. Sunlight exposure affects color temperature
        light_temp_shift = (sunlight - 0.5) * 30
        h = (h + light_temp_shift) % 360
        
        if sunlight > 0.6:
            v *= 1 + (sunlight - 0.6) * 0.5
        
        # 4. Maturity affects color intensity
        if maturity < 0.4:  # Young foliage
            if 60 <= h <= 180:
                h += 15
                s *= 1.1
                v *= 1.1
        elif maturity > 0.7:  # Mature foliage
            s *= 1.05
            v *= 0.95
        
        # 5. Hydration affects color depth
        moisture_factor = 0.7 + hydration * 0.3
        s *= moisture_factor
        if hydration > 0.7:
            v *= 1.05
        elif hydration < 0.3:
            if 60 <= h <= 180:
                h += 20
            s *= 0.8
            v *= 0.9
        
        # 6. Chlorophyll density
        if 60 <= h <= 180:  # Green range
            s *= 0.8 + chlorophyll * 0.4
            if chlorophyll > 0.6:
                h += (chlorophyll - 0.6) * -10
        
        # 7. Environmental stress
        if stress_level > 0.3:
            stress_factor = stress_level - 0.3
            
            if 60 <= h <= 180:  # Green range
                stress_hue_shift = stress_factor * 60
                h = (h + stress_hue_shift) % 360
                s *= 1 - stress_factor * 0.3
                v *= 1 - stress_factor * 0.2
        
        # 8. Foliage-specific enhancements
        foliage_key = self._get_foliage_key()
        
        if foliage_key == "autumn_mixed":
            if 30 <= h <= 60:
                s = min(1.0, s * 1.3)
                v = min(1.0, v * 1.1)
        elif foliage_key == "tropical_palm":
            if 60 <= h <= 180:
                s = min(1.0, s * 1.2)
                v = min(1.0, v * 1.1)
        elif foliage_key == "desert_sage":
            s *= 0.7
            if 60 <= h <= 180:
                h = (h + 180) % 360
                h = (h * 0.3 + 210 * 0.7) % 360
        elif foliage_key == "winter_pine":
            if 60 <= h <= 180:
                h = (h * 0.7 + 150 * 0.3) % 360
                s *= 0.9
                v *= 0.95
        
        return self._hsv_to_rgb(h / 360, s, v)

    def _should_regenerate_base(self) -> bool:
        """Check if base structure needs regeneration."""
        current_foliage = int(self.parameters["foliage_type"].value)
        current_stops = int(self.parameters["stops"].value)
        
        foliage_changed = current_foliage != self.last_foliage_type
        stops_changed = (self.base_structure and len(self.base_structure) != current_stops)
        
        return foliage_changed or stops_changed or not self.base_structure

    def request_new_seed(self):
        """Request a new random seed for variation."""
        self._internal_seed = int(time.time() * 1000) % 999999
        self.random_gen.seed(self._internal_seed)
        self.base_structure = None

    def generate_gradient(self):
        """Generate foliage gradient with streamlined implementation."""
        # Handle regeneration
        if self._should_regenerate_base():
            self.random_gen.seed(self._internal_seed)
            
            # Get foliage colors and generate base structure
            foliage_key = self._get_foliage_key()
            foliage_colors = self.FOLIAGE_COLORS.get(foliage_key, self.FOLIAGE_COLORS["summer_maple"])
            stops = int(self.parameters["stops"].value)
            
            # Select colors from research-based palette
            selected_colors = self._select_foliage_colors(foliage_colors, stops)
            
            # Generate naturalistic positions
            positions = self._generate_naturalistic_positions(stops)
            
            # Store base structure
            self.base_structure = list(zip(positions, selected_colors))
            self.last_foliage_type = int(self.parameters["foliage_type"].value)
        
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
        
        # Apply botanical adjustments to base colors
        for pos, base_color in self.base_structure:
            adjusted_color = self._apply_botanical_adjustments(base_color)
            gradient.add_color_stop(pos, adjusted_color)
        
        # Generate descriptive name
        foliage_name = self.FOLIAGE_TYPE_NAMES[int(self.parameters["foliage_type"].value)]
        
        # Create descriptive qualifiers
        health_desc = ["Stressed", "Healthy", "Vigorous"][int(self.parameters["plant_health"].value * 2.99)]
        seasonal_desc = ["Spring", "Summer", "Autumn"][int(self.parameters["seasonal_shift"].value * 2.99)]
        light_desc = ["Shade", "Partial Sun", "Full Sun"][int(self.parameters["sunlight"].value * 2.99)]
        
        gradient.set_name(f"{foliage_name} ({health_desc}, {seasonal_desc}, {light_desc})")
        gradient.set_description(
            f"Research-based {foliage_name.lower()} foliage gradient with accurate botanical coloration."
        )
        gradient.set_author("VIIBE Foliage Generator")
        gradient.set_ugr_category("Botanical")
        
        return gradient

    def reset_parameters(self):
        """Reset adjustable parameters while preserving foliage type."""
        current_foliage = self.parameters["foliage_type"].value
        
        # Reset all except foliage type
        for name, param in self.parameters.items():
            if name != "foliage_type":
                param.reset()
        
        # Restore foliage type
        self.parameters["foliage_type"].value = current_foliage

    def get_foliage_info(self) -> Dict[str, str]:
        """Get information about the current foliage type."""
        foliage_key = self._get_foliage_key()
        foliage_name = self.FOLIAGE_TYPE_NAMES[int(self.parameters["foliage_type"].value)]
        
        # Basic info without excessive detail
        return {
            "common_name": foliage_name,
            "foliage_type": foliage_key,
            "description": f"Research-based {foliage_name.lower()} with accurate botanical coloration"
        }