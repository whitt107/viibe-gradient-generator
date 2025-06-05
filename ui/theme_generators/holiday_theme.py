#!/usr/bin/env python3
"""
Streamlined Holiday Theme Generator for Gradient Generator

Features 17 holiday types with culturally-accurate and research-backed color palettes.
Simplified controls and reduced debug code for better user experience.
All color data sourced from cultural research and traditional holiday symbolism.
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


class HolidayThemeGenerator(ThemeGradientGenerator):
    """Streamlined holiday generator with 17 global celebrations and accurate cultural colors."""

    # 17 holiday types covering major global celebrations
    HOLIDAY_TYPE_NAMES = [
        "Christmas", "Halloween", "Easter", "Thanksgiving", "Valentine's Day", "New Year's Eve",
        "4th of July", "Celebratory Fireworks", "St. Patrick's Day", "Hanukkah", "Diwali", 
        "Chinese New Year", "Mardi Gras", "Day of the Dead", "Autumn Harvest", "Winter Solstice", 
        "Spring Equinox"
    ]
    
    # Research-based holiday color definitions with cultural accuracy
    HOLIDAY_COLORS = {
        "christmas": {
            "shadows": [(139, 0, 0), (0, 100, 0), (184, 134, 11), (128, 0, 0), (34, 139, 34)],
            "midtones": [(220, 20, 60), (34, 139, 34), (255, 215, 0), (178, 34, 34), (50, 205, 50)],
            "highlights": [(255, 192, 203), (144, 238, 144), (255, 255, 224), (255, 228, 225), (240, 255, 240)]
        },
        "halloween": {
            "shadows": [(0, 0, 0), (75, 0, 130), (139, 69, 19), (128, 0, 128), (64, 64, 64)],
            "midtones": [(255, 140, 0), (138, 43, 226), (255, 165, 0), (147, 112, 219), (105, 105, 105)],
            "highlights": [(255, 218, 185), (221, 160, 221), (255, 228, 181), (238, 130, 238), (211, 211, 211)]
        },
        "easter": {
            "shadows": [(221, 160, 221), (173, 216, 230), (255, 182, 193), (144, 238, 144), (255, 218, 185)],
            "midtones": [(238, 130, 238), (176, 224, 230), (255, 192, 203), (152, 251, 152), (255, 228, 181)],
            "highlights": [(255, 240, 245), (240, 248, 255), (255, 228, 225), (240, 255, 240), (255, 248, 220)]
        },
        "thanksgiving": {
            "shadows": [(139, 69, 19), (184, 134, 11), (128, 0, 0), (255, 140, 0), (160, 82, 45)],
            "midtones": [(218, 165, 32), (255, 165, 0), (220, 20, 60), (255, 215, 0), (210, 180, 140)],
            "highlights": [(255, 218, 185), (255, 228, 181), (255, 239, 213), (255, 248, 220), (255, 250, 240)]
        },
        "valentines": {
            "shadows": [(139, 0, 0), (199, 21, 133), (128, 0, 128), (165, 42, 42), (178, 34, 34)],
            "midtones": [(220, 20, 60), (255, 20, 147), (255, 105, 180), (255, 182, 193), (255, 192, 203)],
            "highlights": [(255, 182, 193), (255, 192, 203), (255, 228, 225), (255, 240, 245), (255, 248, 220)]
        },
        "new_years": {
            "shadows": [(0, 0, 0), (25, 25, 25), (128, 128, 128), (64, 64, 64), (105, 105, 105)],
            "midtones": [(255, 215, 0), (192, 192, 192), (255, 255, 0), (211, 211, 211), (220, 220, 220)],
            "highlights": [(255, 255, 224), (245, 245, 245), (255, 255, 240), (248, 248, 255), (255, 250, 250)]
        },
        "fourth_july": {
            "shadows": [(25, 25, 112), (139, 0, 0), (128, 0, 0), (0, 0, 139), (72, 61, 139)],
            "midtones": [(220, 20, 60), (70, 130, 180), (255, 0, 0), (135, 206, 235), (178, 34, 34)],
            "highlights": [(255, 255, 255), (255, 255, 224), (255, 240, 245), (240, 248, 255), (255, 250, 250)]
        },
        "celebratory_fireworks": {
            # Multi-colored explosive celebration: brilliant golds, electric blues, hot pinks, emerald greens
            "shadows": [(25, 25, 112), (139, 0, 139), (0, 100, 0), (184, 134, 11), (128, 0, 128)],
            "midtones": [(255, 215, 0), (255, 20, 147), (0, 255, 127), (255, 165, 0), (138, 43, 226)],
            "highlights": [(255, 255, 224), (255, 192, 203), (144, 238, 144), (255, 218, 185), (221, 160, 221)]
        },
        "st_patricks": {
            "shadows": [(0, 100, 0), (34, 139, 34), (0, 128, 0), (46, 125, 50), (85, 107, 47)],
            "midtones": [(50, 205, 50), (60, 179, 113), (144, 238, 144), (152, 251, 152), (102, 205, 170)],
            "highlights": [(173, 255, 47), (205, 255, 105), (240, 255, 240), (245, 255, 250), (248, 255, 240)]
        },
        "hanukkah": {
            "shadows": [(25, 25, 112), (0, 0, 139), (70, 130, 180), (72, 61, 139), (105, 105, 105)],
            "midtones": [(100, 149, 237), (135, 206, 235), (176, 196, 222), (192, 192, 192), (211, 211, 211)],
            "highlights": [(173, 216, 230), (240, 248, 255), (245, 245, 245), (248, 248, 255), (255, 255, 255)]
        },
        "diwali": {
            "shadows": [(139, 69, 19), (184, 134, 11), (178, 34, 34), (139, 0, 0), (128, 0, 128)],
            "midtones": [(255, 215, 0), (255, 140, 0), (220, 20, 60), (255, 165, 0), (218, 165, 32)],
            "highlights": [(255, 255, 224), (255, 218, 185), (255, 228, 181), (255, 239, 213), (255, 248, 220)]
        },
        "chinese_new_year": {
            "shadows": [(139, 0, 0), (184, 134, 11), (128, 0, 0), (165, 42, 42), (178, 34, 34)],
            "midtones": [(220, 20, 60), (255, 215, 0), (255, 0, 0), (218, 165, 32), (255, 140, 0)],
            "highlights": [(255, 218, 185), (255, 255, 224), (255, 228, 181), (255, 239, 213), (255, 248, 220)]
        },
        "mardi_gras": {
            "shadows": [(75, 0, 130), (184, 134, 11), (0, 100, 0), (128, 0, 128), (34, 139, 34)],
            "midtones": [(138, 43, 226), (255, 215, 0), (50, 205, 50), (147, 112, 219), (144, 238, 144)],
            "highlights": [(221, 160, 221), (255, 255, 224), (173, 255, 47), (238, 130, 238), (240, 255, 240)]
        },
        "day_of_the_dead": {
            "shadows": [(139, 69, 19), (75, 0, 130), (139, 0, 0), (128, 0, 128), (165, 42, 42)],
            "midtones": [(255, 140, 0), (138, 43, 226), (255, 20, 147), (255, 165, 0), (220, 20, 60)],
            "highlights": [(255, 218, 185), (221, 160, 221), (255, 182, 193), (255, 228, 181), (255, 240, 245)]
        },
        "autumn_harvest": {
            "shadows": [(139, 69, 19), (160, 82, 45), (184, 134, 11), (128, 0, 0), (85, 107, 47)],
            "midtones": [(218, 165, 32), (210, 180, 140), (255, 140, 0), (244, 164, 96), (255, 165, 0)],
            "highlights": [(255, 218, 185), (255, 228, 181), (255, 239, 213), (255, 248, 220), (255, 250, 240)]
        },
        "winter_solstice": {
            "shadows": [(25, 25, 112), (72, 61, 139), (105, 105, 105), (70, 130, 180), (128, 128, 128)],
            "midtones": [(135, 206, 235), (176, 196, 222), (192, 192, 192), (211, 211, 211), (220, 220, 220)],
            "highlights": [(240, 248, 255), (245, 245, 245), (248, 248, 255), (255, 255, 255), (250, 250, 250)]
        },
        "spring_equinox": {
            "shadows": [(34, 139, 34), (85, 107, 47), (255, 215, 0), (46, 125, 50), (184, 134, 11)],
            "midtones": [(50, 205, 50), (173, 255, 47), (255, 255, 0), (152, 251, 152), (218, 165, 32)],
            "highlights": [(240, 255, 240), (255, 255, 224), (245, 255, 250), (248, 255, 240), (255, 250, 240)]
        }
    }
    
    def __init__(self):
        super().__init__("Global Holiday Celebrations", "17 research-based holiday themes with culturally-accurate color palettes")
        self.last_holiday_type = -1
        self.base_structure = None
        self.random_gen = random.Random()
        self._seed = None

    def _create_parameters(self) -> Dict[str, ThemeParameter]:
        """Create simplified holiday-specific parameters."""
        return {
            "holiday_type": ThemeParameter("holiday_type", "Holiday Type", 0, 16, 0, 1, "Global holiday celebration"),
            "celebration_intensity": ThemeParameter("celebration_intensity", "Celebration Intensity", 0, 1, 0.8, 0.01, "Energy and vibrancy of the celebration"),
            "traditional_colors": ThemeParameter("traditional_colors", "Traditional Colors", 0, 1, 0.7, 0.01, "Adherence to traditional holiday colors"),
            "seasonal_warmth": ThemeParameter("seasonal_warmth", "Seasonal Warmth", 0, 1, 0.5, 0.01, "Cool to warm seasonal color shift"),
            "color_depth": ThemeParameter("color_depth", "Color Depth", 0, 1, 0.6, 0.01, "Depth and richness of colors"),
            "festive_sparkle": ThemeParameter("festive_sparkle", "Festive Sparkle", 0, 1, 0.4, 0.01, "Bright highlights and shimmer"),
            "mood_contrast": ThemeParameter("mood_contrast", "Mood Contrast", 0, 1, 0.5, 0.01, "Light/dark celebration dynamics"),
            "color_intensity": ThemeParameter("color_intensity", "Color Intensity", 0, 1, 0.7, 0.01, "Overall color saturation"),
            "overall_brightness": ThemeParameter("overall_brightness", "Overall Brightness", 0, 1, 0.6, 0.01, "Global brightness level"),
            "color_stops": ThemeParameter("color_stops", "Color Stops", 4, 32, 12, 1, "Number of gradient stops"),
            "auto_seed": ThemeParameter("auto_seed", "Auto Seed", 1, 999999, 12345, 1, "Automatic randomization seed")
        }

    def _rgb_to_hsv(self, r: int, g: int, b: int) -> Tuple[float, float, float]:
        """Convert RGB to HSV."""
        return colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB."""
        r, g, b = colorsys.hsv_to_rgb(h, max(0, min(1, s)), max(0, min(1, v)))
        return (int(r * 255), int(g * 255), int(b * 255))

    def _get_holiday_key(self) -> str:
        """Get current holiday key from type parameter."""
        holiday_idx = int(self.parameters["holiday_type"].value) % len(self.HOLIDAY_TYPE_NAMES)
        holiday_name = self.HOLIDAY_TYPE_NAMES[holiday_idx]
        
        # Map display names to color keys
        key_mapping = {
            "Christmas": "christmas",
            "Halloween": "halloween", 
            "Easter": "easter",
            "Thanksgiving": "thanksgiving",
            "Valentine's Day": "valentines",
            "New Year's Eve": "new_years",
            "4th of July": "fourth_july",
            "Celebratory Fireworks": "celebratory_fireworks",
            "St. Patrick's Day": "st_patricks",
            "Hanukkah": "hanukkah",
            "Diwali": "diwali",
            "Chinese New Year": "chinese_new_year",
            "Mardi Gras": "mardi_gras",
            "Day of the Dead": "day_of_the_dead",
            "Autumn Harvest": "autumn_harvest",
            "Winter Solstice": "winter_solstice",
            "Spring Equinox": "spring_equinox"
        }
        
        return key_mapping.get(holiday_name, "christmas")

    def _select_holiday_colors(self, holiday_colors: Dict, num_colors: int) -> List[Tuple[int, int, int]]:
        """Select and distribute colors from the holiday palette."""
        all_colors = []
        
        # Get parameters
        color_depth = self.parameters["color_depth"].value
        traditional_colors = self.parameters["traditional_colors"].value
        
        # Adjust distribution based on color depth
        if color_depth < 0.3:
            shadow_weight, midtone_weight, highlight_weight = 0.2, 0.3, 0.5
        elif color_depth > 0.7:
            shadow_weight, midtone_weight, highlight_weight = 0.4, 0.4, 0.2
        else:
            shadow_weight, midtone_weight, highlight_weight = 0.3, 0.4, 0.3
        
        # Calculate counts for each tonal range
        shadow_count = max(1, int(num_colors * shadow_weight))
        midtone_count = max(1, int(num_colors * midtone_weight))
        highlight_count = max(1, num_colors - shadow_count - midtone_count)
        
        # Select colors from each range
        for _ in range(shadow_count):
            all_colors.append(self.random_gen.choice(holiday_colors["shadows"]))
        for _ in range(midtone_count):
            all_colors.append(self.random_gen.choice(holiday_colors["midtones"]))
        for _ in range(highlight_count):
            all_colors.append(self.random_gen.choice(holiday_colors["highlights"]))
        
        # Shuffle unless very traditional
        if traditional_colors < 0.8:
            self.random_gen.shuffle(all_colors)
        
        return all_colors[:num_colors]

    def _generate_random_positions(self, num_stops: int) -> List[float]:
        """Generate random positions for color stops."""
        if num_stops <= 1:
            return [0.5]
        if num_stops == 2:
            return [0.0, 1.0]
        
        positions = [0.0, 1.0]  # Always include start and end
        
        # Generate random intermediate positions
        for _ in range(num_stops - 2):
            pos = self.random_gen.uniform(0.01, 0.99)
            positions.append(pos)
        
        # Sort and ensure minimum spacing
        positions.sort()
        for i in range(1, len(positions)):
            if positions[i] - positions[i-1] < 0.01:
                positions[i] = min(1.0, positions[i-1] + 0.01)
        
        return positions

    def _apply_holiday_adjustments(self, rgb_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Apply holiday-specific color adjustments."""
        r, g, b = rgb_color
        h, s, v = self._rgb_to_hsv(r, g, b)
        h *= 360
        
        # Get parameters
        celebration_intensity = self.parameters["celebration_intensity"].value
        traditional_colors = self.parameters["traditional_colors"].value
        seasonal_warmth = self.parameters["seasonal_warmth"].value
        festive_sparkle = self.parameters["festive_sparkle"].value
        mood_contrast = self.parameters["mood_contrast"].value
        color_intensity = self.parameters["color_intensity"].value
        overall_brightness = self.parameters["overall_brightness"].value
        
        # Seasonal warmth adjustment
        warm_shift = (seasonal_warmth - 0.5) * 40
        h = (h + warm_shift) % 360
        
        # Celebration intensity affects saturation and brightness
        s = s * (0.5 + celebration_intensity * 0.5) * (0.5 + color_intensity * 0.5)
        v = v * (0.6 + celebration_intensity * 0.3) * (0.6 + overall_brightness * 0.4)
        
        # Festive sparkle for bright colors
        if festive_sparkle > 0.1 and v > 0.6:
            sparkle_boost = festive_sparkle * 0.3
            v = min(1.0, v + sparkle_boost)
            s = min(1.0, s + sparkle_boost * 0.5)
        
        # Mood contrast
        if mood_contrast > 0.1:
            v_center = 0.5
            v_offset = (v - v_center) * (1 + mood_contrast * 0.6)
            v = max(0.0, min(1.0, v_center + v_offset))
        
        # Holiday-specific enhancements
        holiday_key = self._get_holiday_key()
        
        if holiday_key in ["fourth_july", "celebratory_fireworks"]:
            # Enhance firework colors
            if 0 <= h <= 15 or 345 <= h <= 360:  # Red
                s = min(1.0, s * 1.3)
                v = min(1.0, v * 1.2)
            elif 210 <= h <= 250:  # Blue
                s = min(1.0, s * 1.2)
                v = min(1.0, v * 1.1)
            # Add explosive sparkle
            if self.random_gen.random() < festive_sparkle * 0.3:
                v = min(1.0, v * 1.4)
                
        elif holiday_key == "christmas":
            # Enhance red and green
            if 0 <= h <= 20 or 340 <= h <= 360:  # Red
                s = min(1.0, s * 1.2)
            elif 100 <= h <= 140:  # Green
                s = min(1.0, s * 1.15)
                
        elif holiday_key == "halloween":
            # Enhance orange and purple
            if 20 <= h <= 40:  # Orange
                s = min(1.0, s * 1.3)
                v = min(1.0, v * 1.1)
            elif 270 <= h <= 300:  # Purple
                s = min(1.0, s * 1.2)
                
        elif holiday_key == "diwali":
            # Enhance golds and warm colors
            if 40 <= h <= 80:  # Gold/yellow
                s = min(1.0, s * 1.3)
                v = min(1.0, v * 1.2)
            if 0 <= h <= 40:  # Orange/red
                v = min(1.0, v * 1.1)
        
        return self._hsv_to_rgb(h / 360, s, v)

    def _should_regenerate_base(self) -> bool:
        """Check if base structure needs regeneration."""
        current_holiday = int(self.parameters["holiday_type"].value)
        current_stops = int(self.parameters["color_stops"].value)
        current_seed = int(self.parameters["auto_seed"].value)
        
        holiday_changed = current_holiday != self.last_holiday_type
        stops_changed = (self.base_structure and len(self.base_structure) != current_stops)
        seed_changed = (self._seed != current_seed)
        
        return holiday_changed or stops_changed or seed_changed or not self.base_structure

    def request_new_seed(self):
        """Request a new random seed for variation."""
        new_seed = int(time.time() * 1000) % 999999
        self.set_parameter_value("auto_seed", float(new_seed))
        self._seed = None
        self.base_structure = None

    def generate_gradient(self):
        """Generate holiday gradient with culturally-accurate colors."""
        # Handle regeneration
        if self._should_regenerate_base():
            current_seed = int(self.parameters["auto_seed"].value)
            if self._seed != current_seed:
                self._seed = current_seed
                self.random_gen.seed(self._seed)
            
            # Get holiday colors and generate base structure
            holiday_key = self._get_holiday_key()
            holiday_colors = self.HOLIDAY_COLORS.get(holiday_key, self.HOLIDAY_COLORS["christmas"])
            stops = int(self.parameters["color_stops"].value)
            
            # Select colors from palette
            selected_colors = self._select_holiday_colors(holiday_colors, stops)
            
            # Generate random positions
            positions = self._generate_random_positions(stops)
            
            # Store base structure
            self.base_structure = list(zip(positions, selected_colors))
            self.last_holiday_type = int(self.parameters["holiday_type"].value)
        
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
            adjusted_color = self._apply_holiday_adjustments(base_color)
            gradient.add_color_stop(pos, adjusted_color)
        
        # Generate name
        holiday_name = self.HOLIDAY_TYPE_NAMES[int(self.parameters["holiday_type"].value)]
        intensity_desc = ["Subtle", "Traditional", "Festive"][int(self.parameters["celebration_intensity"].value * 2.99)]
        traditional_desc = ["Modern", "Classic", "Traditional"][int(self.parameters["traditional_colors"].value * 2.99)]
        
        gradient.set_name(f"{holiday_name} ({intensity_desc}, {traditional_desc})")
        gradient.set_description(
            f"Research-based {holiday_name} gradient with culturally-accurate colors. "
            f"Celebration intensity: {self.parameters['celebration_intensity'].value:.2f}, "
            f"Traditional adherence: {self.parameters['traditional_colors'].value:.2f}"
        )
        gradient.set_author("VIIBE Holiday Theme Generator")
        gradient.set_ugr_category("Cultural Holiday Themes")
        
        return gradient

    def reset_parameters(self):
        """Reset adjustable parameters while preserving holiday type."""
        current_holiday = self.parameters["holiday_type"].value
        
        # Reset all except holiday type
        for name, param in self.parameters.items():
            if name != "holiday_type":
                param.reset()
        
        # Restore holiday type
        self.parameters["holiday_type"].value = current_holiday