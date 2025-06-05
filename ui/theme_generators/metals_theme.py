#!/usr/bin/env python3
"""
Enhanced Metals Theme Generator Module

Creates rich, naturalistic gradients resembling various types of metals 
through algorithmic color generation and natural variation patterns.
"""
import time
import random
import os
import uuid
import math
from typing import List, Tuple, Dict

# Try multiple import paths to handle different execution contexts
try:
    from theme_gradient_generator import ThemeGradientGenerator, ThemeParameter
    from theme_utils import apply_user_preferences_to_pattern, generate_color_palette, create_naturalistic_stops
except ImportError:
    try:
        from gradient_generator.ui.theme_generators.theme_gradient_generator import ThemeGradientGenerator, ThemeParameter
        from gradient_generator.ui.theme_generators.theme_utils import apply_user_preferences_to_pattern, generate_color_palette, create_naturalistic_stops
    except ImportError:
        import sys, os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
        from gradient_generator.ui.theme_generators.theme_gradient_generator import ThemeGradientGenerator, ThemeParameter
        from gradient_generator.ui.theme_generators.theme_utils import apply_user_preferences_to_pattern, generate_color_palette, create_naturalistic_stops


class MetalsThemeGenerator(ThemeGradientGenerator):
    """Generates gradients based on metal themes with algorithmic color ranges."""

    # Metal type names for UI display
    METAL_TYPE_NAMES = [
        "Steel", "Copper", "Gold", "Silver", "Bronze", "Iron",
        "Titanium", "Aluminum", "Brass", "Pewter", "Chrome", "Platinum",
        "Weathered Steel", "Oxidized Copper", "Tarnished Silver", "Rusted Iron"
    ]
    
    # Map from UI names to internal type keys
    METAL_TYPE_MAP = {
        "Steel": "steel", "Copper": "copper", "Gold": "gold", "Silver": "silver",
        "Bronze": "bronze", "Iron": "iron", "Titanium": "titanium", "Aluminum": "aluminum",
        "Brass": "brass", "Pewter": "pewter", "Chrome": "chrome", "Platinum": "platinum",
        "Weathered Steel": "weathered_steel", "Oxidized Copper": "oxidized_copper",
        "Tarnished Silver": "tarnished_silver", "Rusted Iron": "rusted_iron"
    }

    # Base metal color range definitions
    # Format: [shadows (h,s,v min/max), midtones (h,s,v min/max), highlights (h,s,v min/max)]
    METAL_COLOR_RANGES = {
        "steel": [
            [(220, 240), (0.05, 0.15), (0.1, 0.25)],  # Shadows - cool blue-grays
            [(210, 230), (0.08, 0.20), (0.3, 0.5)],   # Midtones - neutral grays
            [(200, 220), (0.05, 0.12), (0.6, 0.9)]    # Highlights - bright cool grays
        ],
        "copper": [
            [(15, 35), (0.6, 0.8), (0.1, 0.3)],       # Shadows - deep copper
            [(10, 30), (0.7, 0.9), (0.4, 0.6)],       # Midtones - rich copper
            [(20, 40), (0.5, 0.7), (0.7, 0.95)]       # Highlights - bright copper
        ],
        "gold": [
            [(45, 55), (0.7, 0.9), (0.2, 0.4)],       # Shadows - deep gold
            [(40, 50), (0.8, 1.0), (0.5, 0.7)],       # Midtones - rich gold
            [(35, 45), (0.6, 0.8), (0.8, 1.0)]        # Highlights - bright gold
        ],
        "silver": [
            [(210, 230), (0.02, 0.08), (0.15, 0.3)],  # Shadows - cool grays
            [(200, 220), (0.03, 0.10), (0.4, 0.6)],   # Midtones - neutral silvers
            [(190, 210), (0.02, 0.08), (0.75, 0.95)]  # Highlights - bright silvers
        ],
        "bronze": [
            [(25, 45), (0.5, 0.7), (0.15, 0.3)],      # Shadows - dark bronze
            [(20, 40), (0.6, 0.8), (0.35, 0.55)],     # Midtones - medium bronze
            [(15, 35), (0.4, 0.6), (0.6, 0.8)]        # Highlights - bright bronze
        ],
        "iron": [
            [(240, 260), (0.1, 0.25), (0.05, 0.2)],   # Shadows - dark blue-grays
            [(230, 250), (0.15, 0.3), (0.2, 0.4)],    # Midtones - medium grays
            [(220, 240), (0.1, 0.2), (0.5, 0.7)]      # Highlights - lighter grays
        ],
        "titanium": [
            [(240, 280), (0.1, 0.2), (0.2, 0.35)],    # Shadows - cool grays with purple
            [(250, 270), (0.05, 0.15), (0.4, 0.6)],   # Midtones - neutral titanium
            [(260, 280), (0.03, 0.1), (0.7, 0.9)]     # Highlights - bright titanium
        ],
        "aluminum": [
            [(200, 220), (0.03, 0.12), (0.2, 0.35)],  # Shadows - cool aluminum
            [(190, 210), (0.05, 0.15), (0.45, 0.65)], # Midtones - medium aluminum
            [(180, 200), (0.02, 0.1), (0.75, 0.95)]   # Highlights - bright aluminum
        ],
        "brass": [
            [(50, 70), (0.6, 0.8), (0.2, 0.35)],      # Shadows - deep brass
            [(45, 65), (0.7, 0.9), (0.4, 0.6)],       # Midtones - rich brass
            [(40, 60), (0.5, 0.7), (0.7, 0.9)]        # Highlights - bright brass
        ],
        "pewter": [
            [(220, 240), (0.08, 0.18), (0.15, 0.3)],  # Shadows - dark pewter
            [(210, 230), (0.1, 0.2), (0.35, 0.55)],   # Midtones - medium pewter
            [(200, 220), (0.06, 0.15), (0.6, 0.8)]    # Highlights - bright pewter
        ],
        "chrome": [
            [(200, 220), (0.02, 0.08), (0.1, 0.25)],  # Shadows - very dark chrome
            [(190, 210), (0.03, 0.1), (0.3, 0.5)],    # Midtones - medium chrome
            [(180, 200), (0.01, 0.05), (0.8, 1.0)]    # Highlights - brilliant chrome
        ],
        "platinum": [
            [(210, 230), (0.01, 0.05), (0.2, 0.35)],  # Shadows - cool platinum
            [(200, 220), (0.02, 0.08), (0.45, 0.65)], # Midtones - neutral platinum
            [(190, 210), (0.01, 0.06), (0.8, 0.98)]   # Highlights - bright platinum
        ],
        "weathered_steel": [
            [(20, 40), (0.3, 0.5), (0.1, 0.25)],      # Shadows - rust tinged
            [(220, 240), (0.2, 0.4), (0.25, 0.45)],   # Midtones - weathered grays
            [(200, 220), (0.1, 0.3), (0.5, 0.7)]      # Highlights - varied grays
        ],
        "oxidized_copper": [
            [(150, 170), (0.4, 0.6), (0.15, 0.3)],    # Shadows - green patina
            [(160, 180), (0.5, 0.7), (0.3, 0.5)],     # Midtones - blue-green patina
            [(140, 160), (0.3, 0.5), (0.6, 0.8)]      # Highlights - bright patina
        ],
        "tarnished_silver": [
            [(40, 60), (0.3, 0.5), (0.1, 0.25)],      # Shadows - yellow tarnish
            [(210, 230), (0.1, 0.25), (0.3, 0.5)],    # Midtones - mixed silver/tarnish
            [(190, 210), (0.05, 0.15), (0.6, 0.8)]    # Highlights - remaining silver
        ],
        "rusted_iron": [
            [(10, 30), (0.7, 0.9), (0.15, 0.3)],      # Shadows - deep rust
            [(15, 35), (0.6, 0.8), (0.35, 0.55)],     # Midtones - medium rust
            [(20, 40), (0.5, 0.7), (0.6, 0.8)]        # Highlights - bright rust
        ]
    }
    
    # Texture/pattern definitions to create naturalistic variations
    METAL_PATTERNS = {
        "steel":           {"clusters": (2, 4), "variegation": 0.1, "transition_sharpness": 0.4, "position_clustering": 0.2},
        "copper":          {"clusters": (3, 5), "variegation": 0.2, "transition_sharpness": 0.3, "position_clustering": 0.3},
        "gold":            {"clusters": (2, 4), "variegation": 0.15, "transition_sharpness": 0.2, "position_clustering": 0.25},
        "silver":          {"clusters": (2, 3), "variegation": 0.05, "transition_sharpness": 0.5, "position_clustering": 0.15},
        "bronze":          {"clusters": (3, 5), "variegation": 0.25, "transition_sharpness": 0.3, "position_clustering": 0.3},
        "iron":            {"clusters": (2, 4), "variegation": 0.2, "transition_sharpness": 0.4, "position_clustering": 0.25},
        "titanium":        {"clusters": (2, 3), "variegation": 0.08, "transition_sharpness": 0.4, "position_clustering": 0.2},
        "aluminum":        {"clusters": (2, 3), "variegation": 0.1, "transition_sharpness": 0.5, "position_clustering": 0.15},
        "brass":           {"clusters": (3, 5), "variegation": 0.2, "transition_sharpness": 0.25, "position_clustering": 0.3},
        "pewter":          {"clusters": (2, 4), "variegation": 0.15, "transition_sharpness": 0.3, "position_clustering": 0.25},
        "chrome":          {"clusters": (2, 3), "variegation": 0.05, "transition_sharpness": 0.6, "position_clustering": 0.1},
        "platinum":        {"clusters": (2, 3), "variegation": 0.03, "transition_sharpness": 0.5, "position_clustering": 0.1},
        "weathered_steel": {"clusters": (4, 7), "variegation": 0.4, "transition_sharpness": 0.2, "position_clustering": 0.5},
        "oxidized_copper": {"clusters": (3, 6), "variegation": 0.35, "transition_sharpness": 0.25, "position_clustering": 0.4},
        "tarnished_silver":{"clusters": (3, 5), "variegation": 0.3, "transition_sharpness": 0.3, "position_clustering": 0.35},
        "rusted_iron":     {"clusters": (4, 8), "variegation": 0.45, "transition_sharpness": 0.2, "position_clustering": 0.6}
    }
    
    def __init__(self):
        """Initialize the metals theme generator."""
        super().__init__(
            name="Enhanced Metals",
            description="Generate rich, naturalistic gradients resembling various types of metals and their surfaces"
        )
        self.metal_type = "steel"  # Default metal type
        self.random_gen = random.Random()
        self.last_used_seed = None
        self.should_generate_new_seed = True
        self.generation_counter = 0
    
    def request_new_seed(self):
        """Request a new seed for the next gradient generation."""
        self.should_generate_new_seed = True
        self.generation_counter += 1
        if "random_seed" in self.parameters:
            self.parameters["random_seed"].value = 0.0

    def _create_parameters(self) -> Dict[str, ThemeParameter]:
        """Create metals-specific parameters with improved dropdown support."""
        return {
            "metal_type": ThemeParameter("metal_type", "Metal Type", 0.0, 15.0, 0.0, 1.0,
                                        "Type of metal surface to generate"),
            "surface_finish": ThemeParameter("surface_finish", "Surface Finish", 0.0, 1.0, 0.5, 0.05,
                                            "Surface finish quality - rough to mirror polish (0.0-1.0)"),
            "oxidation_level": ThemeParameter("oxidation_level", "Oxidation Level", 0.0, 1.0, 0.2, 0.05,
                                             "Amount of oxidation/tarnish/patina (0.0-1.0)"),
            "reflectivity": ThemeParameter("reflectivity", "Reflectivity", 0.0, 1.0, 0.7, 0.05,
                                          "Surface reflectivity and shine (0.0-1.0)"),
            "brightness": ThemeParameter("brightness", "Brightness", 0.5, 1.5, 1.0, 0.05,
                                        "Overall brightness adjustment (0.5-1.5)"),
            "contrast": ThemeParameter("contrast", "Contrast", 0.5, 1.5, 1.1, 0.05,
                                      "Contrast between light and dark areas (0.5-1.5)"),
            "shadow_depth": ThemeParameter("shadow_depth", "Shadow Depth", 0.0, 1.0, 0.6, 0.05,
                                          "Darkness of shadow areas (0.0-1.0)"),
            "highlight_intensity": ThemeParameter("highlight_intensity", "Highlight Intensity", 0.0, 1.0, 0.8, 0.05,
                                                 "Intensity of metallic highlights (0.0-1.0)"),
            "texture_variation": ThemeParameter("texture_variation", "Texture Variation", 0.0, 1.0, 0.4, 0.05,
                                               "Surface texture and imperfection variation (0.0-1.0)"),
            "color_temperature": ThemeParameter("color_temperature", "Color Temperature", 0.0, 1.0, 0.5, 0.05,
                                               "Cool to warm color temperature (0.0=cool, 1.0=warm)"),
            "stop_count": ThemeParameter("stop_count", "Color Stops", 12.0, 64.0, 32.0, 2.0,
                                        "Number of color stops to generate (12-64)"),
            "position_clustering": ThemeParameter("position_clustering", "Position Clustering", 0.0, 1.0, 0.3, 0.05,
                                                "Tendency of color stops to cluster in patterns (0.0-1.0)"),
            "random_seed": ThemeParameter("random_seed", "Random Seed", 0.0, 1000.0, 0.0, 1.0,
                                         "Seed for randomization (0=auto-generate)")
        }
    
    def _generate_unique_seed(self):
        """Generate a guaranteed unique seed value"""
        time_component = int(time.time() * 1000) & 0xFFFFFFFF
        counter_component = self.generation_counter & 0xFFFF
        random_component = random.randint(1, 0xFFFF)
        pid_component = os.getpid() & 0xFFFF
        uuid_int = int(uuid.uuid4().hex[-8:], 16)
        
        seed = ((time_component & 0xFFFFFFFF) ^ 
                (counter_component << 16) ^ 
                (random_component << 8) ^ 
                (pid_component << 24) ^ 
                (uuid_int & 0xFFFFFFFF))
        
        return abs(seed) % 1000000
    
    def _adjust_color_ranges_for_parameters(self, base_ranges, params):
        """Adjust base color ranges based on user parameters."""
        adjusted_ranges = []
        
        for i, (hue_range, sat_range, val_range) in enumerate(base_ranges):
            # Apply oxidation level - increases saturation and shifts colors
            oxidation = params["oxidation_level"]
            
            # Apply surface finish - affects value range and saturation
            finish = params["surface_finish"]
            
            # Apply color temperature - shifts hue
            temperature = params["color_temperature"]
            
            # Apply reflectivity - affects value range
            reflectivity = params["reflectivity"]
            
            # Adjust hue range based on color temperature
            temp_shift = (temperature - 0.5) * 20  # ±10 degree shift
            new_hue_range = (
                (hue_range[0] + temp_shift) % 360,
                (hue_range[1] + temp_shift) % 360
            )
            
            # Adjust saturation based on oxidation and finish
            sat_multiplier = 1.0 + oxidation * 0.5  # More saturation with oxidation
            finish_sat_adjust = (1.0 - finish) * 0.3  # Rough surfaces have more color variation
            new_sat_range = (
                min(1.0, sat_range[0] * sat_multiplier + finish_sat_adjust),
                min(1.0, sat_range[1] * sat_multiplier + finish_sat_adjust)
            )
            
            # Adjust value range based on reflectivity and finish
            if i == 2:  # Highlights
                val_multiplier = 0.5 + reflectivity * 0.5  # More reflective = brighter highlights
                finish_adjustment = finish * 0.2  # Polished surfaces have brighter highlights
            elif i == 0:  # Shadows
                val_multiplier = 1.0 - oxidation * 0.3  # Oxidation darkens shadows
                finish_adjustment = (1.0 - finish) * 0.1  # Rough surfaces have darker shadows
            else:  # Midtones
                val_multiplier = 1.0
                finish_adjustment = 0
            
            new_val_range = (
                max(0.0, val_range[0] * val_multiplier + finish_adjustment),
                min(1.0, val_range[1] * val_multiplier + finish_adjustment)
            )
            
            # Ensure valid ranges
            if new_hue_range[0] > new_hue_range[1]:
                new_hue_range = (new_hue_range[1], new_hue_range[0])
            if new_sat_range[0] > new_sat_range[1]:
                new_sat_range = (new_sat_range[1], new_sat_range[0])
            if new_val_range[0] > new_val_range[1]:
                new_val_range = (new_val_range[1], new_val_range[0])
            
            adjusted_ranges.append((new_hue_range, new_sat_range, new_val_range))
        
        return adjusted_ranges
    
    def generate_gradient(self):
        """Generate a metals-themed gradient with algorithmic color ranges."""
        # Handle seed generation
        seed_param = int(self.parameters["random_seed"].value)
        if seed_param > 0 and not self.should_generate_new_seed:
            seed = seed_param
        else:
            seed = self._generate_unique_seed()
            self.parameters["random_seed"].value = float(seed)
        
        self.last_used_seed = seed
        self.should_generate_new_seed = False
        self.random_gen.seed(seed)
        
        # Create gradient and get parameters
        gradient = self._create_gradient_with_name()
        metal_type_idx = min(max(0, int(self.parameters["metal_type"].value)), len(self.METAL_TYPE_NAMES)-1)
        
        # Get parameter values
        params = {name: self.parameters[name].value for name in [
            "surface_finish", "oxidation_level", "reflectivity", "brightness", "contrast", 
            "shadow_depth", "highlight_intensity", "texture_variation", "color_temperature",
            "stop_count", "position_clustering"
        ]}
        
        # Get metal type and associated data
        metal_name = self.METAL_TYPE_NAMES[metal_type_idx]
        self.metal_type = self.METAL_TYPE_MAP.get(metal_name, "steel")
        base_color_ranges = self.METAL_COLOR_RANGES[self.metal_type]
        pattern_params = self.METAL_PATTERNS.get(self.metal_type, self.METAL_PATTERNS["steel"])
        
        # Adjust color ranges based on user parameters
        adjusted_color_ranges = self._adjust_color_ranges_for_parameters(base_color_ranges, params)
        
        # Apply user parameters to modify pattern
        modified_pattern = apply_user_preferences_to_pattern(
            pattern_params, params["texture_variation"], params["texture_variation"], params["position_clustering"]
        )
        
        # Adjust pattern based on surface finish
        finish_factor = params["surface_finish"]
        modified_pattern["variegation"] *= (1.0 + (1.0 - finish_factor) * 0.5)  # Rough surfaces = more variation
        modified_pattern["transition_sharpness"] *= (0.5 + finish_factor * 0.5)  # Polished = sharper transitions
        
        # Fix any invalid cluster values
        cluster_min, cluster_max = modified_pattern["clusters"]
        if cluster_min >= cluster_max:
            modified_pattern["clusters"] = (cluster_min, cluster_min + 1)
        
        # Generate color palette
        color_palette = generate_color_palette(
            adjusted_color_ranges,
            params["reflectivity"],  # Use reflectivity as color richness for metals
            params["brightness"],
            params["contrast"],
            params["shadow_depth"],
            params["highlight_intensity"],
            modified_pattern,
            int(params["stop_count"]),
            self.metal_type,
            self.random_gen
        )
        
        # Create color stops with naturalistic distribution
        color_stops = create_naturalistic_stops(
            color_palette, modified_pattern, int(params["stop_count"]), self.random_gen
        )
        
        # Add color stops and metadata
        for position, color in color_stops:
            gradient.add_color_stop(position, color)
        
        # Create descriptive name with key characteristics
        finish_desc = "Polished" if params["surface_finish"] > 0.7 else "Brushed" if params["surface_finish"] > 0.3 else "Rough"
        oxidation_desc = ""
        if params["oxidation_level"] > 0.5:
            oxidation_desc = " Aged" if self.metal_type in ["steel", "iron"] else " Patinated" if self.metal_type == "copper" else " Tarnished"
        
        gradient.set_name(f"Enhanced Metals - {finish_desc} {metal_name}{oxidation_desc} (Seed: {seed})")
        
        # Create detailed description
        description_parts = [
            f"Algorithmically generated {metal_name.lower()} gradient",
            f"Surface: {finish_desc.lower()}",
            f"Reflectivity: {params['reflectivity']:.1f}",
            f"{int(params['stop_count'])} color stops"
        ]
        if params["oxidation_level"] > 0.3:
            description_parts.append(f"oxidation level: {params['oxidation_level']:.1f}")
        
        gradient.set_description(" | ".join(description_parts))
        gradient.set_author("VIIBE Gradient Generator")
        gradient.set_ugr_category("Enhanced Metals")
        
        return gradient