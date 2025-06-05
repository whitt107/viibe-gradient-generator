#!/usr/bin/env python3
"""
Simplified Random Gradient Generator Module for VIIBE Gradient Generator - Sorting Removed

This module provides functionality to generate random gradients with various 
color schemes and truly random positions AND colors, supporting up to 64 color stops.

Removed clustering, saturation and brightness controls for simplified operation.
Colors are now truly random within each scheme's color theory constraints.

FIXED: Default scheme changed to "random" instead of "harmonious"
FIXED: Removed all sorting to maintain true randomization
"""
import random
import math
import colorsys
from typing import List, Tuple, Optional

# Import with fallback mechanism
try:
    from gradient_generator.core.gradient import Gradient, ColorStop
    from gradient_generator.core.color_utils import rgb_to_hsv, hsv_to_rgb
except ImportError:
    try:
        from core.gradient import Gradient, ColorStop
        from core.color_utils import rgb_to_hsv, hsv_to_rgb
    except ImportError:
        import sys, os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
        from gradient_generator.core.gradient import Gradient, ColorStop
        from gradient_generator.core.color_utils import rgb_to_hsv, hsv_to_rgb


class RandomGradientGenerator:
    """Simplified class for generating random gradients with truly random positions and colors."""
    
    MAX_COLOR_STOPS = 64
    DEFAULT_STOPS = 10
    
    @staticmethod
    def generate_random_gradient(
        num_stops=DEFAULT_STOPS, 
        harmonious=False,  # CHANGED: Default to False instead of True
        monochromatic=False,
        analogous=False,
        complementary=False,
        triadic=False,
        name=None,
        random_seed=None,
        seed=None  # Backward compatibility
    ):
        """Generate a random gradient with truly random colors and positions."""
        num_stops = max(2, min(RandomGradientGenerator.MAX_COLOR_STOPS, num_stops))
        
        # Handle seed parameter for backward compatibility
        if random_seed is None and seed is not None:
            random_seed = seed
        rand_gen = random.Random(random_seed)
        
        # Determine scheme type
        scheme = RandomGradientGenerator._get_scheme_type(
            harmonious, monochromatic, analogous, complementary, triadic
        )
        
        # Generate random base hue for schemes that need it
        base_hue = rand_gen.uniform(0, 360)
        
        # Generate truly random colors based on scheme
        colors = RandomGradientGenerator._generate_random_colors(
            scheme, base_hue, num_stops, rand_gen
        )
        
        # Generate truly random positions
        positions = RandomGradientGenerator._generate_random_positions(num_stops, rand_gen)
        
        # Create gradient
        gradient = Gradient()
        gradient._color_stops = []
        
        # Add color stops WITHOUT SORTING - maintain random order
        for position, color in zip(positions, colors):
            gradient.add_color_stop(position, color)
        
        # Set metadata
        gradient_name = name or RandomGradientGenerator._generate_name(
            scheme, base_hue, num_stops, random_seed
        )
        gradient.set_name(gradient_name)
        gradient.set_description(f"Random {scheme} gradient with {num_stops} stops and random positions")
        
        return gradient
    
    @staticmethod
    def _get_scheme_type(harmonious, monochromatic, analogous, complementary, triadic):
        """Determine scheme type from boolean flags."""
        if monochromatic:
            return "monochromatic"
        elif analogous:
            return "analogous"
        elif complementary:
            return "complementary"
        elif triadic:
            return "triadic"
        elif harmonious:
            return "harmonious"
        else:
            return "random"  # This is now the true default when no flags are set
    
    @staticmethod
    def _generate_random_colors(scheme, base_hue, num_stops, rand_gen):
        """Generate truly random colors based on the specified scheme."""
        colors = []
        
        if scheme == "random":
            # Completely random colors across full spectrum
            for i in range(num_stops):
                hue = rand_gen.uniform(0, 360)
                saturation = rand_gen.uniform(0.3, 1.0)
                value = rand_gen.uniform(0.2, 1.0)
                color = hsv_to_rgb(hue, saturation, value)
                colors.append(color)
                
        elif scheme == "monochromatic":
            # Random variations of a single hue
            for i in range(num_stops):
                # Small random variation around base hue (±10 degrees)
                hue = (base_hue + rand_gen.uniform(-10, 10)) % 360
                # Random saturation and value for variety
                saturation = rand_gen.uniform(0.3, 0.9)
                value = rand_gen.uniform(0.2, 0.9)
                color = hsv_to_rgb(hue, saturation, value)
                colors.append(color)
                
        elif scheme == "analogous":
            # Random colors within 60° range around base hue
            for i in range(num_stops):
                # Random hue within ±30° of base
                hue = (base_hue + rand_gen.uniform(-30, 30)) % 360
                saturation = rand_gen.uniform(0.5, 0.9)
                value = rand_gen.uniform(0.3, 0.9)
                color = hsv_to_rgb(hue, saturation, value)
                colors.append(color)
                
        elif scheme == "complementary":
            # Random colors from base hue and its complement
            for i in range(num_stops):
                # Randomly choose base or complementary side
                if rand_gen.random() < 0.5:
                    # Base hue side (±30°)
                    hue = (base_hue + rand_gen.uniform(-30, 30)) % 360
                else:
                    # Complementary side (±30°)
                    complement_hue = (base_hue + 180) % 360
                    hue = (complement_hue + rand_gen.uniform(-30, 30)) % 360
                
                saturation = rand_gen.uniform(0.6, 1.0)
                value = rand_gen.uniform(0.3, 0.9)
                color = hsv_to_rgb(hue, saturation, value)
                colors.append(color)
                
        elif scheme == "triadic":
            # Random colors from three hues 120° apart
            triadic_hues = [
                base_hue,
                (base_hue + 120) % 360,
                (base_hue + 240) % 360
            ]
            
            for i in range(num_stops):
                # Randomly choose one of the three triadic hues
                chosen_hue = rand_gen.choice(triadic_hues)
                # Add small random variation (±15°)
                hue = (chosen_hue + rand_gen.uniform(-15, 15)) % 360
                saturation = rand_gen.uniform(0.5, 0.9)
                value = rand_gen.uniform(0.3, 0.9)
                color = hsv_to_rgb(hue, saturation, value)
                colors.append(color)
                
        elif scheme == "harmonious":
            # Random colors within a harmonious range (similar to analogous but wider)
            for i in range(num_stops):
                # Random hue within ±45° of base for more variety than analogous
                hue = (base_hue + rand_gen.uniform(-45, 45)) % 360
                saturation = rand_gen.uniform(0.5, 0.95)
                value = rand_gen.uniform(0.3, 0.9)
                color = hsv_to_rgb(hue, saturation, value)
                colors.append(color)
        
        # DO NOT shuffle the colors - maintain generation order for true randomness
        return colors
    
    @staticmethod
    def _generate_random_positions(num_stops, rand_gen):
        """Generate truly random positions for color stops."""
        if num_stops <= 2:
            # For 2 or fewer stops, use fixed positions
            if num_stops == 1:
                return [0.5]  # Single stop in middle
            else:
                return [0.0, 1.0]  # Start and end
        
        # Generate completely random positions
        positions = []
        
        # Always include start and end positions
        positions.append(0.0)
        positions.append(1.0)
        
        # Generate random intermediate positions
        for i in range(num_stops - 2):
            # Generate a random position between 0.01 and 0.99 to avoid edge overlap
            pos = rand_gen.uniform(0.01, 0.99)
            positions.append(pos)
        
        # DO NOT SORT positions - maintain random order for true randomization
        
        # Ensure no two positions are too close together (minimum 0.01 apart)
        # but without sorting - check and adjust in place
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                if abs(positions[i] - positions[j]) < 0.01:
                    # Adjust the second position slightly
                    if positions[j] < positions[i]:
                        positions[j] = max(0.0, positions[i] - 0.01)
                    else:
                        positions[j] = min(1.0, positions[i] + 0.01)
        
        return positions[:num_stops]
    
    @staticmethod
    def _generate_name(scheme, base_hue, num_stops, seed):
        """Generate descriptive gradient name."""
        hue_name = RandomGradientGenerator._get_hue_name(base_hue)
        scheme_name = scheme.capitalize()
        
        if scheme == "monochromatic":
            name = f"Random {scheme_name} {hue_name}"
        elif scheme == "random":
            name = f"Random Spectrum"
        else:
            name = f"Random {scheme_name} ({hue_name} Base)"
        
        name += f" ({num_stops} stops)"
        if seed is not None:
            name += f" [Seed: {seed}]"
        
        return name
    
    @staticmethod
    def _get_hue_name(hue):
        """Get descriptive name for hue value."""
        hue_ranges = [
            (0, 15, "Red"), (15, 45, "Orange"), (45, 75, "Yellow"),
            (75, 105, "Yellow-Green"), (105, 135, "Green"), (135, 165, "Teal"),
            (165, 195, "Cyan"), (195, 225, "Blue"), (225, 255, "Indigo"),
            (255, 285, "Purple"), (285, 315, "Magenta"), (315, 360, "Red")
        ]
        
        for h_min, h_max, name in hue_ranges:
            if h_min <= hue < h_max:
                return name
        return "Mixed"
    
    # Convenience methods for specific gradient types
    @staticmethod
    def generate_random_monochromatic(num_stops=DEFAULT_STOPS, name=None, 
                                    random_seed=None, seed=None):
        """Generate a random monochromatic gradient with random variations."""
        return RandomGradientGenerator.generate_random_gradient(
            num_stops=num_stops, monochromatic=True,
            name=name, random_seed=random_seed or seed
        )
    
    @staticmethod
    def generate_random_analogous(num_stops=DEFAULT_STOPS, name=None, 
                                random_seed=None, seed=None):
        """Generate a random analogous gradient with colors within 60° range."""
        return RandomGradientGenerator.generate_random_gradient(
            num_stops=num_stops, analogous=True,
            name=name, random_seed=random_seed or seed
        )
    
    @staticmethod
    def generate_random_complementary(num_stops=DEFAULT_STOPS, name=None, 
                                    random_seed=None, seed=None):
        """Generate a random complementary gradient with opposing hues."""
        return RandomGradientGenerator.generate_random_gradient(
            num_stops=num_stops, complementary=True,
            name=name, random_seed=random_seed or seed
        )
    
    @staticmethod
    def generate_random_triadic(num_stops=DEFAULT_STOPS, name=None, 
                              random_seed=None, seed=None):
        """Generate a random triadic gradient with three 120° spaced hues."""
        return RandomGradientGenerator.generate_random_gradient(
            num_stops=num_stops, triadic=True,
            name=name, random_seed=random_seed or seed
        )
    
    @staticmethod
    def generate_random_harmonious(num_stops=DEFAULT_STOPS, name=None, 
                                 random_seed=None, seed=None):
        """Generate a random harmonious gradient with pleasing color relationships."""
        return RandomGradientGenerator.generate_random_gradient(
            num_stops=num_stops, harmonious=True,
            name=name, random_seed=random_seed or seed
        )


# For testing
if __name__ == "__main__":
    # Test gradient generation with truly random colors
    print("Testing truly random gradient generation:")
    
    # Test with same seed to show reproducibility
    print("\n=== Testing Reproducibility (same seed) ===")
    for i in range(2):
        gradient = RandomGradientGenerator.generate_random_gradient(5, random_seed=42)
        positions = [f'{pos:.3f}' for pos, _ in gradient.get_color_stops()]
        colors = [f'RGB{color}' for _, color in gradient.get_color_stops()]
        print(f"Run {i+1} (seed 42): Positions: {positions}")
        print(f"                Colors: {colors}")
    
    # Test different schemes with different seeds
    print("\n=== Testing Different Schemes ===")
    schemes = [
        ("random", False, False, False, False, False),
        ("harmonious", True, False, False, False, False), 
        ("monochromatic", False, True, False, False, False),
        ("analogous", False, False, True, False, False),
        ("complementary", False, False, False, True, False),
        ("triadic", False, False, False, False, True)
    ]
    
    for i, (scheme_name, harmonious, mono, analog, comp, triad) in enumerate(schemes):
        gradient = RandomGradientGenerator.generate_random_gradient(
            6, harmonious=harmonious, monochromatic=mono, analogous=analog,
            complementary=comp, triadic=triad, random_seed=i*100
        )
        print(f"\n{scheme_name.upper()}:")
        print(f"  Name: {gradient.get_name()}")
        positions = [f'{pos:.3f}' for pos, _ in gradient.get_color_stops()]
        print(f"  Positions: {positions}")
        
        # Show first 3 colors to verify randomness
        colors = gradient.get_color_stops()[:3]
        for j, (pos, color) in enumerate(colors):
            print(f"  Color {j+1}: RGB{color} at position {pos:.3f}")
    
    # Test multiple generations to verify true randomness
    print("\n=== Testing True Randomness (different seeds) ===")
    for seed in [1, 2, 3]:
        gradient = RandomGradientGenerator.generate_random_gradient(4, random_seed=seed)
        positions = [f'{pos:.3f}' for pos, _ in gradient.get_color_stops()]
        first_color = gradient.get_color_stops()[1][1]  # Get second color (first is always at 0.0)
        print(f"Seed {seed}: Positions {positions}, Sample color: RGB{first_color}")
