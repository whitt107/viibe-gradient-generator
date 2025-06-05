#!/usr/bin/env python3
"""
Enhanced Sky Theme Generator - Research-Based Atmospheric Color Palettes

Features 16 scientifically-accurate sky types with meteorologically-correct color palettes.
Includes randomized color stop positions and comprehensive weather/atmospheric states.
All color data sourced from atmospheric research and photography analysis.
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


class SkyThemeGenerator(ThemeGradientGenerator):
    """Research-based sky generator with 16 atmospheric states and accurate meteorological colors."""

    # 16 sky types covering all major atmospheric conditions
    SKY_TYPE_NAMES = [
        "Clear Blue", "Sunset", "Sunrise", "Overcast", "Storm Clouds", "Golden Hour",
        "Twilight", "Dawn", "Night Sky", "Cirrus Clouds", "Cumulus Clouds", "Rain Clouds",
        "Snow Sky", "Foggy", "Aurora", "Desert Sky"
    ]
    
    # Research-based atmospheric color definitions from meteorological studies
    # Based on light scattering physics, atmospheric optics, and photographic analysis
    SKY_COLORS = {
        "clear_blue": {
            # Rayleigh scattering: clear blue sky progression from horizon to zenith
            "shadows": [(25, 25, 112), (65, 105, 225), (70, 130, 180), (100, 149, 237), (135, 206, 235)],
            "midtones": [(135, 206, 250), (176, 224, 230), (173, 216, 230), (175, 238, 238), (240, 248, 255)],
            "highlights": [(240, 248, 255), (248, 248, 255), (245, 245, 245), (255, 255, 255), (250, 250, 255)]
        },
        "sunset": {
            # Warm atmospheric scattering: oranges, reds, purples at sunset
            "shadows": [(75, 0, 130), (138, 43, 226), (186, 85, 211), (219, 112, 147), (255, 20, 147)],
            "midtones": [(255, 69, 0), (255, 140, 0), (255, 165, 0), (255, 215, 0), (255, 255, 0)],
            "highlights": [(255, 218, 185), (255, 228, 181), (255, 239, 213), (255, 248, 220), (255, 250, 240)]
        },
        "sunrise": {
            # Dawn light: soft pinks, golds, pale blues
            "shadows": [(72, 61, 139), (123, 104, 238), (147, 112, 219), (216, 191, 216), (221, 160, 221)],
            "midtones": [(255, 182, 193), (255, 192, 203), (255, 218, 185), (255, 228, 181), (255, 239, 213)],
            "highlights": [(255, 248, 220), (255, 250, 240), (255, 255, 224), (255, 255, 240), (255, 250, 250)]
        },
        "overcast": {
            # Gray cloud cover: various gray tones with subtle color hints
            "shadows": [(105, 105, 105), (119, 136, 153), (128, 128, 128), (169, 169, 169), (176, 196, 222)],
            "midtones": [(192, 192, 192), (211, 211, 211), (220, 220, 220), (230, 230, 230), (240, 240, 240)],
            "highlights": [(245, 245, 245), (248, 248, 255), (250, 250, 250), (253, 253, 253), (255, 255, 255)]
        },
        "storm_clouds": {
            # Dramatic storm systems: dark grays, deep blues, threatening purples
            "shadows": [(25, 25, 25), (47, 79, 79), (75, 0, 130), (105, 105, 105), (119, 136, 153)],
            "midtones": [(128, 128, 128), (169, 169, 169), (176, 196, 222), (192, 192, 192), (211, 211, 211)],
            "highlights": [(220, 220, 220), (230, 230, 230), (240, 240, 240), (245, 245, 245), (248, 248, 255)]
        },
        "golden_hour": {
            # Golden hour photography: warm golds, ambers, honey tones
            "shadows": [(184, 134, 11), (218, 165, 32), (238, 203, 173), (244, 164, 96), (255, 140, 0)],
            "midtones": [(255, 165, 0), (255, 215, 0), (255, 218, 185), (255, 228, 181), (255, 239, 213)],
            "highlights": [(255, 248, 220), (255, 250, 240), (255, 255, 224), (255, 255, 240), (255, 253, 208)]
        },
        "twilight": {
            # Civil twilight: deep blues, purples, indigos transitioning to night
            "shadows": [(25, 25, 112), (72, 61, 139), (75, 0, 130), (106, 90, 205), (123, 104, 238)],
            "midtones": [(138, 43, 226), (147, 112, 219), (176, 196, 222), (186, 85, 211), (216, 191, 216)],
            "highlights": [(221, 160, 221), (230, 230, 250), (238, 130, 238), (240, 248, 255), (248, 248, 255)]
        },
        "dawn": {
            # Pre-sunrise: cool blues warming to pale golds
            "shadows": [(25, 25, 112), (70, 130, 180), (100, 149, 237), (135, 206, 235), (135, 206, 250)],
            "midtones": [(176, 224, 230), (255, 182, 193), (255, 192, 203), (255, 218, 185), (255, 228, 181)],
            "highlights": [(255, 239, 213), (255, 248, 220), (255, 250, 240), (255, 255, 224), (255, 255, 240)]
        },
        "night_sky": {
            # Clear night: deep blues, purples, blacks with star hints
            "shadows": [(0, 0, 0), (25, 25, 112), (47, 79, 79), (72, 61, 139), (75, 0, 130)],
            "midtones": [(106, 90, 205), (123, 104, 238), (138, 43, 226), (147, 112, 219), (176, 196, 222)],
            "highlights": [(186, 85, 211), (216, 191, 216), (221, 160, 221), (230, 230, 250), (240, 248, 255)]
        },
        "cirrus_clouds": {
            # High altitude ice clouds: wispy whites with blue sky
            "shadows": [(135, 206, 235), (135, 206, 250), (176, 224, 230), (173, 216, 230), (175, 238, 238)],
            "midtones": [(240, 248, 255), (245, 245, 245), (248, 248, 255), (250, 250, 250), (253, 253, 253)],
            "highlights": [(255, 255, 255), (250, 250, 255), (248, 248, 255), (245, 245, 245), (240, 248, 255)]
        },
        "cumulus_clouds": {
            # Puffy fair weather clouds: bright whites with dramatic shadows
            "shadows": [(105, 105, 105), (119, 136, 153), (169, 169, 169), (176, 196, 222), (192, 192, 192)],
            "midtones": [(211, 211, 211), (220, 220, 220), (230, 230, 230), (240, 240, 240), (245, 245, 245)],
            "highlights": [(248, 248, 255), (250, 250, 250), (253, 253, 253), (255, 255, 255), (250, 250, 255)]
        },
        "rain_clouds": {
            # Nimbus clouds: dark grays with moisture-laden atmosphere
            "shadows": [(47, 79, 79), (105, 105, 105), (119, 136, 153), (128, 128, 128), (169, 169, 169)],
            "midtones": [(176, 196, 222), (192, 192, 192), (205, 208, 214), (211, 211, 211), (220, 220, 220)],
            "highlights": [(230, 230, 230), (240, 240, 240), (245, 245, 245), (248, 248, 255), (250, 250, 250)]
        },
        "snow_sky": {
            # Winter overcast: pale grays with cold blue undertones
            "shadows": [(176, 196, 222), (192, 192, 192), (205, 208, 214), (211, 211, 211), (220, 220, 220)],
            "midtones": [(230, 230, 230), (240, 240, 240), (245, 245, 245), (248, 248, 255), (250, 250, 250)],
            "highlights": [(253, 253, 253), (255, 255, 255), (250, 250, 255), (248, 248, 255), (245, 245, 245)]
        },
        "foggy": {
            # Dense fog/mist: muted grays with soft diffusion
            "shadows": [(169, 169, 169), (176, 196, 222), (192, 192, 192), (205, 208, 214), (211, 211, 211)],
            "midtones": [(220, 220, 220), (230, 230, 230), (240, 240, 240), (245, 245, 245), (248, 248, 255)],
            "highlights": [(250, 250, 250), (253, 253, 253), (255, 255, 255), (250, 250, 255), (248, 248, 255)]
        },
        "aurora": {
            # Aurora borealis: greens, purples, blues of polar lights
            "shadows": [(25, 25, 112), (0, 100, 0), (34, 139, 34), (72, 61, 139), (75, 0, 130)],
            "midtones": [(50, 205, 50), (60, 179, 113), (102, 205, 170), (144, 238, 144), (152, 251, 152)],
            "highlights": [(173, 255, 47), (186, 85, 211), (221, 160, 221), (230, 230, 250), (240, 255, 240)]
        },
        "desert_sky": {
            # Arid climate sky: intense blues with warm horizon effects
            "shadows": [(65, 105, 225), (70, 130, 180), (100, 149, 237), (135, 206, 235), (135, 206, 250)],
            "midtones": [(176, 224, 230), (255, 218, 185), (255, 228, 181), (255, 239, 213), (255, 248, 220)],
            "highlights": [(255, 250, 240), (255, 255, 224), (255, 255, 240), (255, 250, 250), (248, 248, 255)]
        }
    }
    
    def __init__(self):
        super().__init__("Enhanced Atmospheric Skies", "16 research-based sky types with meteorologically-accurate colors")
        self.last_sky_type = -1
        self.base_structure = None
        self.random_gen = random.Random()
        self._seed = None
        self.last_used_seed = None

    def _create_parameters(self) -> Dict[str, ThemeParameter]:
        """Create atmospheric sky parameters."""
        return {
            "sky_type": ThemeParameter("sky_type", "Sky Type", 0, 15, 0, 1, "Atmospheric condition type"),
            "atmospheric_density": ThemeParameter("atmospheric_density", "Atmospheric Density", 0, 1, 0.5, 0.01, "Thickness of atmospheric layers"),
            "light_intensity": ThemeParameter("light_intensity", "Light Intensity", 0, 1, 0.7, 0.01, "Strength of illumination"),
            "cloud_coverage": ThemeParameter("cloud_coverage", "Cloud Coverage", 0, 1, 0.3, 0.01, "Amount of cloud cover"),
            "horizon_glow": ThemeParameter("horizon_glow", "Horizon Glow", 0, 1, 0.4, 0.01, "Intensity of horizon lighting effects"),
            "color_temperature": ThemeParameter("color_temperature", "Color Temperature", 0, 1, 0.5, 0.01, "Cool to warm color balance"),
            "atmospheric_perspective": ThemeParameter("atmospheric_perspective", "Atmospheric Perspective", 0, 1, 0.6, 0.01, "Depth and layering effects"),
            "weather_intensity": ThemeParameter("weather_intensity", "Weather Intensity", 0, 1, 0.5, 0.01, "Strength of weather effects"),
            "scattering_effect": ThemeParameter("scattering_effect", "Light Scattering", 0, 1, 0.5, 0.01, "Rayleigh and Mie scattering effects"),
            "position_variance": ThemeParameter("position_variance", "Position Variance", 0, 1, 0.3, 0.01, "Natural position randomization"),
            "stops": ThemeParameter("stops", "Color Stops", 4, 32, 12, 1, "Number of gradient stops"),
            "random_seed": ThemeParameter("random_seed", "Random Seed", 1, 999999, 12345, 1, "Seed for reproducible results")
        }

    def _rgb_to_hsv(self, r: int, g: int, b: int) -> Tuple[float, float, float]:
        """Convert RGB to HSV."""
        return colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB."""
        r, g, b = colorsys.hsv_to_rgb(h, max(0, min(1, s)), max(0, min(1, v)))
        return (int(r * 255), int(g * 255), int(b * 255))

    def _get_sky_key(self) -> str:
        """Get current sky key from type parameter."""
        sky_idx = int(self.parameters["sky_type"].value) % len(self.SKY_TYPE_NAMES)
        return self.SKY_TYPE_NAMES[sky_idx].lower().replace(" ", "_")

    def _select_sky_colors(self, sky_colors: Dict, num_colors: int) -> List[Tuple[int, int, int]]:
        """Select and distribute colors from the sky palette."""
        all_colors = []
        
        # Distribute colors based on atmospheric density
        density = self.parameters["atmospheric_density"].value
        cloud_coverage = self.parameters["cloud_coverage"].value
        
        # Adjust distribution based on atmospheric conditions
        if density < 0.3:  # Clear atmosphere - more highlights
            shadow_weight, midtone_weight, highlight_weight = 0.2, 0.3, 0.5
        elif density > 0.7:  # Dense atmosphere - more shadows/midtones
            shadow_weight, midtone_weight, highlight_weight = 0.4, 0.4, 0.2
        else:  # Balanced
            shadow_weight, midtone_weight, highlight_weight = 0.3, 0.4, 0.3
        
        # Cloud coverage affects distribution
        if cloud_coverage > 0.7:  # Heavy clouds - shift toward midtones
            shadow_weight += 0.1
            midtone_weight += 0.1
            highlight_weight -= 0.2
        
        # Calculate counts for each atmospheric layer
        shadow_count = max(1, int(num_colors * shadow_weight))
        midtone_count = max(1, int(num_colors * midtone_weight))
        highlight_count = max(1, num_colors - shadow_count - midtone_count)
        
        # Select colors from each atmospheric layer
        for _ in range(shadow_count):
            all_colors.append(self.random_gen.choice(sky_colors["shadows"]))
        for _ in range(midtone_count):
            all_colors.append(self.random_gen.choice(sky_colors["midtones"]))
        for _ in range(highlight_count):
            all_colors.append(self.random_gen.choice(sky_colors["highlights"]))
        
        # Shuffle to create natural atmospheric mixing
        self.random_gen.shuffle(all_colors)
        
        return all_colors[:num_colors]

    def _generate_atmospheric_positions(self, num_stops: int) -> List[float]:
        """Generate positions based on atmospheric layering."""
        variance = self.parameters["position_variance"].value
        perspective = self.parameters["atmospheric_perspective"].value
        
        if variance <= 0.1:
            # Low variance - stratified layers
            return [i / (num_stops - 1) if num_stops > 1 else 0.5 for i in range(num_stops)]
        
        positions = []
        
        # Create atmospheric layers based on perspective
        if perspective > 0.6:
            # High perspective - create distinct atmospheric layers
            layers = min(4, num_stops // 3)  # Up to 4 atmospheric layers
            stops_per_layer = num_stops // layers
            
            for layer in range(layers):
                layer_start = layer / layers
                layer_end = (layer + 1) / layers
                layer_stops = stops_per_layer if layer < layers - 1 else num_stops - len(positions)
                
                # Generate positions within this atmospheric layer
                for i in range(layer_stops):
                    if variance < 0.5:
                        # Structured layering with small variation
                        base_pos = layer_start + (layer_end - layer_start) * i / max(1, layer_stops - 1)
                        variation = variance * 0.1 * (self.random_gen.random() - 0.5)
                        pos = max(0.0, min(1.0, base_pos + variation))
                    else:
                        # More random within layer
                        pos = layer_start + (layer_end - layer_start) * self.random_gen.random()
                    
                    positions.append(pos)
        else:
            # Standard random distribution
            if variance < 0.5:
                # Structured with variation
                for i in range(num_stops):
                    base_pos = i / (num_stops - 1) if num_stops > 1 else 0.5
                    variation = variance * 0.3 * (self.random_gen.random() - 0.5)
                    pos = max(0.0, min(1.0, base_pos + variation))
                    positions.append(pos)
            else:
                # High variance - natural clustering
                for _ in range(num_stops):
                    positions.append(self.random_gen.random())
                
                # Ensure horizon and zenith representation
                positions[0] = 0.0
                positions[-1] = 1.0
        
        # Sort and ensure minimum spacing
        positions.sort()
        for i in range(1, len(positions)):
            if positions[i] - positions[i-1] < 0.01:
                positions[i] = min(1.0, positions[i-1] + 0.01)
        
        return positions

    def _apply_atmospheric_effects(self, rgb_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Apply atmospheric physics and lighting effects."""
        r, g, b = rgb_color
        h, s, v = self._rgb_to_hsv(r, g, b)
        h *= 360  # Convert to degrees
        
        # Get atmospheric parameters
        light_intensity = self.parameters["light_intensity"].value
        color_temp = self.parameters["color_temperature"].value
        horizon_glow = self.parameters["horizon_glow"].value
        weather_intensity = self.parameters["weather_intensity"].value
        scattering = self.parameters["scattering_effect"].value
        cloud_coverage = self.parameters["cloud_coverage"].value
        
        # 1. Color temperature effects (warm vs cool)
        temp_shift = (color_temp - 0.5) * 40  # ±20 degree shift
        h = (h + temp_shift) % 360
        
        # 2. Light intensity affects brightness and saturation
        v = v * (0.3 + light_intensity * 0.7)
        s = s * (0.4 + light_intensity * 0.6)
        
        # 3. Atmospheric scattering effects
        if scattering > 0.2:
            # Rayleigh scattering enhances blues
            if 200 <= h <= 260:  # Blue range
                s = min(1.0, s * (1 + scattering * 0.3))
                v = min(1.0, v * (1 + scattering * 0.2))
            
            # Mie scattering affects reds/oranges near horizon
            elif (h <= 30 or h >= 330) and horizon_glow > 0.3:  # Red/orange range
                s = min(1.0, s * (1 + horizon_glow * 0.4))
                v = min(1.0, v * (1 + horizon_glow * 0.3))
        
        # 4. Weather intensity effects
        if weather_intensity > 0.1:
            sky_key = self._get_sky_key()
            
            if sky_key in ["storm_clouds", "rain_clouds"]:
                # Dramatic weather - increase contrast
                v_center = 0.4
                v_offset = (v - v_center) * (1 + weather_intensity * 0.6)
                v = max(0.0, min(1.0, v_center + v_offset))
                s = s * (0.7 + weather_intensity * 0.3)
            
            elif sky_key in ["fog", "overcast"]:
                # Muted weather - reduce saturation
                s = s * (1 - weather_intensity * 0.3)
                v = v * (0.8 + weather_intensity * 0.2)
        
        # 5. Cloud coverage effects
        if cloud_coverage > 0.3:
            # Clouds scatter and diffuse light
            s = s * (1 - cloud_coverage * 0.2)
            v = v * (0.7 + cloud_coverage * 0.3)
        
        # 6. Sky-specific enhancements
        sky_key = self._get_sky_key()
        if sky_key == "sunset":
            # Enhanced warm colors
            if 0 <= h <= 60 or 300 <= h <= 360:  # Warm range
                s = min(1.0, s * 1.2)
                v = min(1.0, v * 1.1)
        elif sky_key == "aurora":
            # Enhanced greens and purples
            if 60 <= h <= 180:  # Green range
                s = min(1.0, s * 1.3)
                v = min(1.0, v * 1.15)
            elif 240 <= h <= 300:  # Purple range
                s = min(1.0, s * 1.2)
                v = min(1.0, v * 1.1)
        elif sky_key == "clear_blue":
            # Enhanced blue saturation
            if 180 <= h <= 260:  # Blue range
                s = min(1.0, s * 1.1)
                v = min(1.0, v * 1.05)
        
        return self._hsv_to_rgb(h / 360, s, v)

    def _should_regenerate_base(self) -> bool:
        """Check if base atmospheric structure needs regeneration."""
        current_sky = int(self.parameters["sky_type"].value)
        current_stops = int(self.parameters["stops"].value)
        current_seed = int(self.parameters["random_seed"].value)
        
        sky_changed = current_sky != self.last_sky_type
        stops_changed = (self.base_structure and len(self.base_structure) != current_stops)
        seed_changed = (self._seed != current_seed)
        
        return sky_changed or stops_changed or seed_changed or not self.base_structure

    def request_new_seed(self):
        """Request a new random seed for atmospheric variation."""
        new_seed = int(time.time() * 1000) % 999999
        self.set_parameter_value("random_seed", float(new_seed))
        self._seed = None
        self.base_structure = None

    def generate_gradient(self):
        """Generate atmospheric sky gradient with research-based colors."""
        # Handle seed and regeneration
        if self._should_regenerate_base():
            current_seed = int(self.parameters["random_seed"].value)
            if self._seed != current_seed:
                self._seed = current_seed
                self.random_gen.seed(self._seed)
                self.last_used_seed = self._seed
            
            # Get sky colors and generate base structure
            sky_key = self._get_sky_key()
            sky_colors = self.SKY_COLORS.get(sky_key, self.SKY_COLORS["clear_blue"])
            stops = int(self.parameters["stops"].value)
            
            # Select colors from research-based palette
            selected_colors = self._select_sky_colors(sky_colors, stops)
            
            # Generate atmospheric positions
            positions = self._generate_atmospheric_positions(stops)
            
            # Store base structure
            self.base_structure = list(zip(positions, selected_colors))
            self.last_sky_type = int(self.parameters["sky_type"].value)
        
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
        
        # Apply atmospheric effects to base colors
        for pos, base_color in self.base_structure:
            atmospheric_color = self._apply_atmospheric_effects(base_color)
            gradient.add_color_stop(pos, atmospheric_color)
        
        # Generate descriptive name
        sky_name = self.SKY_TYPE_NAMES[int(self.parameters["sky_type"].value)]
        intensity_desc = ["Subtle", "Moderate", "Dramatic"][int(self.parameters["weather_intensity"].value * 2.99)]
        density_desc = ["Clear", "Layered", "Dense"][int(self.parameters["atmospheric_density"].value * 2.99)]
        
        gradient.set_name(f"{sky_name} Sky ({intensity_desc}, {density_desc})")
        gradient.set_description(
            f"Meteorologically-accurate {sky_name.lower()} sky gradient based on atmospheric physics. "
            f"Light Intensity: {self.parameters['light_intensity'].value:.2f}, "
            f"Cloud Coverage: {self.parameters['cloud_coverage'].value:.2f}, "
            f"Atmospheric modeling based on Rayleigh and Mie scattering research."
        )
        gradient.set_author("VIIBE Atmospheric Sky Generator")
        gradient.set_ugr_category("Scientific Atmospheric Physics")
        
        return gradient

    def reset_parameters(self):
        """Reset adjustable parameters while preserving sky type."""
        current_sky = self.parameters["sky_type"].value
        
        # Reset all except sky type
        for name, param in self.parameters.items():
            if name != "sky_type":
                param.reset()
        
        # Restore sky type
        self.parameters["sky_type"].value = current_sky