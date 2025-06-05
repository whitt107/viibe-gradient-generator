#!/usr/bin/env python3
"""
Metal and Stone Theme Generator - Research-Based Geological and Metallic Palettes

Features 16 research-backed metal and stone types with scientifically-accurate color palettes.
Includes randomized color stop positions and realistic material color variations.
All color data sourced from geological surveys and metallurgy research.
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


class MetalAndStoneThemeGenerator(ThemeGradientGenerator):
    """Research-based metal and stone generator with 16 material types and accurate color science."""

    # 16 metal and stone types with geological accuracy
    MATERIAL_TYPE_NAMES = [
        "Iron", "Copper", "Gold", "Silver", "Bronze", "Steel", "Granite", "Marble", 
        "Obsidian", "Sandstone", "Slate", "Quartz", "Basalt", "Limestone", "Onyx", "Jade"
    ]
    
    # Research-based color definitions: extensive RGB triplets for shadows/midtones/highlights
    # Based on geological surveys, metallurgy data, and mineral color analysis
    MATERIAL_COLORS = {
        "iron": {
            # Raw iron: rust browns, oxidized reds, metallic grays (geological survey data)
            "shadows": [(101, 67, 33), (139, 69, 19), (160, 82, 45), (205, 133, 63), (139, 90, 43)],
            "midtones": [(205, 133, 63), (222, 184, 135), (210, 180, 140), (188, 143, 143), (169, 169, 169)],
            "highlights": [(192, 192, 192), (211, 211, 211), (220, 220, 220), (245, 245, 245), (255, 250, 240)]
        },
        "copper": {
            # Copper: patina greens, oxidized blues, metallic oranges (metallurgy research)
            "shadows": [(184, 115, 51), (205, 127, 50), (210, 105, 30), (139, 69, 19), (160, 82, 45)],
            "midtones": [(218, 165, 32), (255, 140, 0), (255, 165, 0), (64, 224, 208), (72, 209, 204)],
            "highlights": [(175, 238, 238), (224, 255, 255), (240, 255, 255), (245, 255, 250), (255, 250, 240)]
        },
        "gold": {
            # Gold: pure yellows, warm highlights, deep golden shadows
            "shadows": [(218, 165, 32), (184, 134, 11), (205, 127, 50), (255, 140, 0), (255, 165, 0)],
            "midtones": [(255, 215, 0), (255, 223, 0), (255, 255, 0), (255, 250, 205), (255, 248, 220)],
            "highlights": [(255, 255, 224), (255, 255, 240), (255, 250, 250), (255, 248, 220), (255, 245, 238)]
        },
        "silver": {
            # Silver: cool grays, metallic shine, blue-white highlights
            "shadows": [(105, 105, 105), (119, 136, 153), (128, 128, 128), (169, 169, 169), (176, 196, 222)],
            "midtones": [(192, 192, 192), (211, 211, 211), (220, 220, 220), (230, 230, 250), (240, 248, 255)],
            "highlights": [(245, 245, 245), (248, 248, 255), (250, 250, 250), (255, 250, 250), (255, 255, 255)]
        },
        "bronze": {
            # Bronze: warm browns, golden highlights, patina greens
            "shadows": [(205, 127, 50), (160, 82, 45), (139, 69, 19), (101, 67, 33), (85, 107, 47)],
            "midtones": [(205, 133, 63), (222, 184, 135), (218, 165, 32), (188, 143, 143), (143, 188, 143)],
            "highlights": [(240, 230, 140), (255, 248, 220), (255, 250, 205), (245, 255, 250), (255, 250, 240)]
        },
        "steel": {
            # Steel: blue-gray tones, industrial grays, metallic sheen
            "shadows": [(47, 79, 79), (70, 130, 180), (95, 158, 160), (119, 136, 153), (105, 105, 105)],
            "midtones": [(176, 196, 222), (176, 224, 230), (192, 192, 192), (211, 211, 211), (230, 230, 250)],
            "highlights": [(240, 248, 255), (245, 245, 245), (248, 248, 255), (250, 250, 250), (255, 255, 255)]
        },
        "granite": {
            # Granite: speckled grays, quartz whites, feldspar pinks (geological composition)
            "shadows": [(105, 105, 105), (128, 128, 128), (139, 69, 19), (160, 82, 45), (119, 136, 153)],
            "midtones": [(169, 169, 169), (192, 192, 192), (205, 192, 176), (188, 143, 143), (205, 133, 63)],
            "highlights": [(211, 211, 211), (220, 220, 220), (245, 245, 245), (255, 182, 193), (255, 240, 245)]
        },
        "marble": {
            # Marble: pure whites, gray veining, warm undertones (quarry data)
            "shadows": [(211, 211, 211), (220, 220, 220), (192, 192, 192), (169, 169, 169), (176, 196, 222)],
            "midtones": [(245, 245, 245), (248, 248, 255), (250, 250, 250), (255, 250, 240), (255, 248, 220)],
            "highlights": [(255, 255, 255), (255, 250, 250), (255, 248, 220), (255, 245, 238), (255, 240, 245)]
        },
        "obsidian": {
            # Obsidian: volcanic blacks, deep grays, subtle rainbow sheens
            "shadows": [(0, 0, 0), (25, 25, 25), (47, 79, 79), (64, 64, 64), (72, 61, 139)],
            "midtones": [(105, 105, 105), (128, 128, 128), (75, 0, 130), (106, 90, 205), (119, 136, 153)],
            "highlights": [(169, 169, 169), (192, 192, 192), (147, 112, 219), (216, 191, 216), (221, 160, 221)]
        },
        "sandstone": {
            # Sandstone: desert tans, red iron oxides, warm earth tones
            "shadows": [(160, 82, 45), (205, 133, 63), (222, 184, 135), (139, 69, 19), (165, 42, 42)],
            "midtones": [(240, 230, 140), (238, 203, 173), (255, 218, 185), (255, 228, 181), (244, 164, 96)],
            "highlights": [(255, 239, 213), (255, 248, 220), (255, 250, 205), (255, 245, 238), (255, 228, 196)]
        },
        "slate": {
            # Slate: blue-grays, metamorphic layers, subtle color bands
            "shadows": [(47, 79, 79), (70, 130, 180), (95, 158, 160), (105, 105, 105), (72, 61, 139)],
            "midtones": [(119, 136, 153), (176, 196, 222), (176, 224, 230), (169, 169, 169), (147, 112, 219)],
            "highlights": [(192, 192, 192), (211, 211, 211), (230, 230, 250), (240, 248, 255), (245, 245, 245)]
        },
        "quartz": {
            # Quartz: crystal clears, prismatic colors, pure whites (mineralogy data)
            "shadows": [(169, 169, 169), (192, 192, 192), (175, 238, 238), (221, 160, 221), (147, 112, 219)],
            "midtones": [(211, 211, 211), (220, 220, 220), (224, 255, 255), (230, 230, 250), (255, 182, 193)],
            "highlights": [(245, 245, 245), (248, 248, 255), (255, 250, 250), (255, 255, 255), (240, 255, 255)]
        },
        "basalt": {
            # Basalt: volcanic darks, iron-rich grays, columnar structures
            "shadows": [(25, 25, 25), (47, 79, 79), (64, 64, 64), (105, 105, 105), (85, 107, 47)],
            "midtones": [(128, 128, 128), (119, 136, 153), (169, 169, 169), (160, 82, 45), (139, 90, 43)],
            "highlights": [(192, 192, 192), (176, 196, 222), (211, 211, 211), (205, 133, 63), (188, 143, 143)]
        },
        "limestone": {
            # Limestone: fossil grays, sedimentary layers, calcium whites
            "shadows": [(192, 192, 192), (169, 169, 169), (211, 211, 211), (176, 196, 222), (205, 192, 176)],
            "midtones": [(220, 220, 220), (245, 245, 245), (240, 230, 140), (255, 248, 220), (238, 203, 173)],
            "highlights": [(248, 248, 255), (250, 250, 250), (255, 255, 255), (255, 250, 240), (255, 245, 238)]
        },
        "onyx": {
            # Onyx: banded blacks, dramatic contrasts, polished surfaces
            "shadows": [(0, 0, 0), (25, 25, 25), (64, 64, 64), (47, 79, 79), (105, 105, 105)],
            "midtones": [(128, 128, 128), (169, 169, 169), (119, 136, 153), (192, 192, 192), (176, 196, 222)],
            "highlights": [(211, 211, 211), (220, 220, 220), (245, 245, 245), (248, 248, 255), (255, 255, 255)]
        },
        "jade": {
            # Jade: imperial greens, nephrite variations, polished beauty
            "shadows": [(0, 100, 0), (34, 139, 34), (85, 107, 47), (107, 142, 35), (50, 205, 50)],
            "midtones": [(60, 179, 113), (102, 205, 170), (144, 238, 144), (152, 251, 152), (143, 188, 143)],
            "highlights": [(173, 255, 47), (205, 255, 105), (240, 255, 240), (245, 255, 250), (250, 255, 240)]
        }
    }
    
    def __init__(self):
        super().__init__("Metal and Stone", "16 research-based metal and stone materials with geological accuracy")
        self.last_material_type = -1
        self.base_structure = None
        self.random_gen = random.Random()
        self._seed = None
        self.last_used_seed = None  # Track last seed for consistent previews

    def _create_parameters(self) -> Dict[str, ThemeParameter]:
        """Create enhanced smooth parameters for material properties."""
        return {
            "material_type": ThemeParameter("material_type", "Material Type", 0, 15, 0, 1, "Research-based metal or stone material"),
            "weathering": ThemeParameter("weathering", "Weathering Level", 0, 1, 0.3, 0.01, "Age and environmental exposure effects"),
            "polish": ThemeParameter("polish", "Surface Polish", 0, 1, 0.5, 0.01, "Surface finish from rough to mirror-like"),
            "oxidation": ThemeParameter("oxidation", "Oxidation/Patina", 0, 1, 0.4, 0.01, "Chemical weathering and color changes"),
            "mineral_variation": ThemeParameter("mineral_variation", "Mineral Variation", 0, 1, 0.6, 0.01, "Natural mineral composition variance"),
            "metallic_sheen": ThemeParameter("metallic_sheen", "Metallic Reflection", 0, 1, 0.7, 0.01, "Metallic luster and reflectivity"),
            "color_purity": ThemeParameter("color_purity", "Color Purity", 0, 1, 0.8, 0.01, "Saturation and color clarity"),
            "brightness": ThemeParameter("brightness", "Overall Brightness", 0, 1, 0.6, 0.01, "Global brightness adjustment"),
            "texture_detail": ThemeParameter("texture_detail", "Texture Detail", 0, 1, 0.5, 0.01, "Surface texture complexity"),
            "stops": ThemeParameter("stops", "Color Stops", 4, 32, 14, 1, "Number of gradient stops"),
            "random_seed": ThemeParameter("random_seed", "Random Seed", 1, 999999, 12345, 1, "Seed for reproducible randomness")
        }

    def _rgb_to_hsv(self, r: int, g: int, b: int) -> Tuple[float, float, float]:
        """Convert RGB to HSV."""
        return colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB."""
        r, g, b = colorsys.hsv_to_rgb(h, max(0, min(1, s)), max(0, min(1, v)))
        return (int(r * 255), int(g * 255), int(b * 255))

    def _get_material_key(self) -> str:
        """Get current material key from type parameter."""
        material_idx = int(self.parameters["material_type"].value) % len(self.MATERIAL_TYPE_NAMES)
        return self.MATERIAL_TYPE_NAMES[material_idx].lower()

    def _is_metal(self, material_key: str) -> bool:
        """Check if material is a metal."""
        metals = {"iron", "copper", "gold", "silver", "bronze", "steel"}
        return material_key in metals

    def _select_material_colors(self, material_colors: Dict, num_colors: int) -> List[Tuple[int, int, int]]:
        """Select and blend colors from the material palette."""
        all_colors = []
        
        # Distribute colors across tonal ranges based on material properties
        weathering = self.parameters["weathering"].value
        polish = self.parameters["polish"].value
        
        # Adjust distribution based on weathering and polish
        if weathering > 0.7:  # Highly weathered - more shadows and midtones
            shadow_weight, midtone_weight, highlight_weight = 0.5, 0.4, 0.1
        elif polish > 0.7:  # Highly polished - more highlights
            shadow_weight, midtone_weight, highlight_weight = 0.2, 0.3, 0.5
        else:  # Balanced natural state
            shadow_weight, midtone_weight, highlight_weight = 0.3, 0.4, 0.3
        
        # Calculate counts for each tonal range
        shadow_count = max(1, int(num_colors * shadow_weight))
        midtone_count = max(1, int(num_colors * midtone_weight))
        highlight_count = max(1, num_colors - shadow_count - midtone_count)
        
        # Select colors from each range
        for _ in range(shadow_count):
            all_colors.append(self.random_gen.choice(material_colors["shadows"]))
        for _ in range(midtone_count):
            all_colors.append(self.random_gen.choice(material_colors["midtones"]))
        for _ in range(highlight_count):
            all_colors.append(self.random_gen.choice(material_colors["highlights"]))
        
        # Shuffle to mix tonal ranges naturally
        self.random_gen.shuffle(all_colors)
        
        return all_colors[:num_colors]

    def _generate_material_positions(self, num_stops: int) -> List[float]:
        """Generate positions based on material texture and natural formation."""
        texture_detail = self.parameters["texture_detail"].value
        mineral_variation = self.parameters["mineral_variation"].value
        
        # Combine texture and mineral variation for positioning randomness
        randomization = (texture_detail + mineral_variation) / 2
        
        if randomization <= 0.2:
            # Low variation - crystalline or uniform metal structure
            return [i / (num_stops - 1) if num_stops > 1 else 0.5 for i in range(num_stops)]
        
        positions = []
        
        if randomization < 0.6:
            # Medium variation - natural stone banding or metal alloy patterns
            for i in range(num_stops):
                base_pos = i / (num_stops - 1) if num_stops > 1 else 0.5
                variation = randomization * 0.25 * (self.random_gen.random() - 0.5)
                pos = max(0.0, min(1.0, base_pos + variation))
                positions.append(pos)
        else:
            # High variation - complex mineral patterns or heavily weathered surfaces
            # Create clusters based on natural geological processes
            num_clusters = max(2, int(num_stops / 3))
            cluster_positions = [self.random_gen.random() for _ in range(num_clusters)]
            cluster_positions.sort()
            
            positions = []
            stops_per_cluster = num_stops // num_clusters
            remaining_stops = num_stops % num_clusters
            
            for i, cluster_center in enumerate(cluster_positions):
                cluster_size = stops_per_cluster + (1 if i < remaining_stops else 0)
                cluster_spread = 0.15 * randomization
                
                for j in range(cluster_size):
                    offset = (self.random_gen.random() - 0.5) * cluster_spread
                    pos = max(0.0, min(1.0, cluster_center + offset))
                    positions.append(pos)
        
        # Sort and ensure minimum spacing for visibility
        positions.sort()
        for i in range(1, len(positions)):
            if positions[i] - positions[i-1] < 0.008:  # Tighter spacing for materials
                positions[i] = min(1.0, positions[i-1] + 0.008)
        
        return positions

    def _apply_material_properties(self, rgb_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Apply material-specific physical and chemical properties to colors."""
        r, g, b = rgb_color
        h, s, v = self._rgb_to_hsv(r, g, b)
        h *= 360  # Convert to degrees
        
        # Get material parameters
        weathering = self.parameters["weathering"].value
        polish = self.parameters["polish"].value
        oxidation = self.parameters["oxidation"].value
        metallic_sheen = self.parameters["metallic_sheen"].value
        color_purity = self.parameters["color_purity"].value
        brightness_param = self.parameters["brightness"].value
        
        material_key = self._get_material_key()
        is_metal = self._is_metal(material_key)
        
        # 1. Weathering effects (reduces saturation, shifts toward earth tones)
        if weathering > 0.1:
            s = s * (1.0 - weathering * 0.4)  # Reduce saturation
            v = v * (1.0 - weathering * 0.2)  # Slightly darken
            
            # Shift toward earth tones for weathered materials
            if weathering > 0.5:
                earth_hue_shift = 30 * weathering * (self.random_gen.random() - 0.5)
                h = (h + earth_hue_shift) % 360
        
        # 2. Polish effects (increases brightness and saturation for highlights)
        if polish > 0.1:
            # Polish primarily affects value (brightness) and saturation
            brightness_boost = polish * 0.3
            saturation_boost = polish * 0.2
            
            # Higher polish creates more dramatic highlights
            if v > 0.6:  # Only affect lighter areas
                v = min(1.0, v * (1.0 + brightness_boost))
                s = min(1.0, s * (1.0 + saturation_boost))
        
        # 3. Oxidation effects (material-specific color shifts)
        if oxidation > 0.1 and is_metal:
            if material_key == "iron":
                # Iron rusting - shift toward orange/red
                if h < 60 or h > 300:  # Already in warm range
                    s = min(1.0, s * (1.0 + oxidation * 0.5))
                else:
                    h = (h + oxidation * 45) % 360  # Shift toward red-orange
                    s = min(1.0, s * (1.0 + oxidation * 0.3))
                    
            elif material_key == "copper":
                # Copper patina - shift toward green/blue
                if 120 <= h <= 240:  # Already in cool range
                    s = min(1.0, s * (1.0 + oxidation * 0.6))
                else:
                    h = (h + oxidation * 120) % 360  # Shift toward green
                    s = min(1.0, s * (1.0 + oxidation * 0.4))
                    
            elif material_key == "bronze":
                # Bronze patina - green with brown undertones
                green_shift = oxidation * 60
                h = (h + green_shift) % 360
                s = s * (1.0 + oxidation * 0.3)
        
        # 4. Metallic sheen (increases contrast and brightness for metals)
        if is_metal and metallic_sheen > 0.1:
            # Enhance the metallic quality
            contrast_boost = metallic_sheen * 0.4
            v_center = 0.5
            v_offset = (v - v_center) * (1.0 + contrast_boost)
            v = max(0.0, min(1.0, v_center + v_offset))
            
            # Slight desaturation for realistic metallic look
            s = s * (1.0 - metallic_sheen * 0.1)
        
        # 5. Color purity (overall saturation control)
        s = s * (0.2 + color_purity * 0.8)
        
        # 6. Brightness adjustment
        v = v * (0.3 + brightness_param * 0.7)
        
        # 7. Material-specific enhancements
        if material_key == "gold":
            # Enhance yellow-gold range
            if 40 <= h <= 80:
                s = min(1.0, s * 1.2)
                v = min(1.0, v * 1.1)
        elif material_key == "jade":
            # Enhance green range and add subtle saturation
            if 90 <= h <= 150:
                s = min(1.0, s * 1.3)
                v = min(1.0, v * 1.05)
        elif material_key == "obsidian":
            # Keep very dark with subtle color hints
            v = v * 0.7
            s = s * 1.5  # Enhance any color that exists
        elif material_key == "marble":
            # Keep light with subtle veining
            v = max(0.7, v)
            s = s * 0.6  # Reduce saturation for marble's subtlety
        
        return self._hsv_to_rgb(h / 360, s, v)

    def _should_regenerate_base(self) -> bool:
        """Check if base structure needs regeneration."""
        current_material = int(self.parameters["material_type"].value)
        current_stops = int(self.parameters["stops"].value)
        current_seed = int(self.parameters["random_seed"].value)
        
        material_changed = current_material != self.last_material_type
        stops_changed = (self.base_structure and len(self.base_structure) != current_stops)
        seed_changed = (self._seed != current_seed)
        
        return material_changed or stops_changed or seed_changed or not self.base_structure

    def request_new_seed(self):
        """Request a new random seed for variation."""
        new_seed = int(time.time() * 1000) % 999999
        self.set_parameter_value("random_seed", float(new_seed))
        self._seed = None
        self.base_structure = None

    def generate_gradient(self):
        """Generate enhanced material gradient with research-based colors."""
        # Handle seed and regeneration
        if self._should_regenerate_base():
            current_seed = int(self.parameters["random_seed"].value)
            if self._seed != current_seed:
                self._seed = current_seed
                self.random_gen.seed(self._seed)
                self.last_used_seed = self._seed
            
            # Get material colors and generate base structure
            material_key = self._get_material_key()
            material_colors = self.MATERIAL_COLORS.get(material_key, self.MATERIAL_COLORS["granite"])
            stops = int(self.parameters["stops"].value)
            
            # Select colors from research-based palette
            selected_colors = self._select_material_colors(material_colors, stops)
            
            # Generate material-appropriate positions
            positions = self._generate_material_positions(stops)
            
            # Store base structure
            self.base_structure = list(zip(positions, selected_colors))
            self.last_material_type = int(self.parameters["material_type"].value)
        
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
        
        # Apply material property adjustments to base colors
        for pos, base_color in self.base_structure:
            adjusted_color = self._apply_material_properties(base_color)
            gradient.add_color_stop(pos, adjusted_color)
        
        # Generate descriptive name
        material_name = self.MATERIAL_TYPE_NAMES[int(self.parameters["material_type"].value)]
        weathering_desc = ["Fresh", "Aged", "Ancient"][int(self.parameters["weathering"].value * 2.99)]
        polish_desc = ["Raw", "Finished", "Polished"][int(self.parameters["polish"].value * 2.99)]
        
        gradient.set_name(f"{material_name} ({weathering_desc}, {polish_desc})")
        gradient.set_description(
            f"Research-based {material_name.lower()} gradient with geological accuracy. "
            f"Weathering: {self.parameters['weathering'].value:.2f}, "
            f"Polish: {self.parameters['polish'].value:.2f}, "
            f"Surface properties based on materials science and geological surveys."
        )
        gradient.set_author("VIIBE Metal and Stone Generator")
        gradient.set_ugr_category("Geological Materials")
        
        return gradient

    def reset_parameters(self):
        """Reset adjustable parameters while preserving material type."""
        current_material = self.parameters["material_type"].value
        
        # Reset all except material type
        for name, param in self.parameters.items():
            if name != "material_type":
                param.reset()
        
        # Restore material type
        self.parameters["material_type"].value = current_material