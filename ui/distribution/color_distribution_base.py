#!/usr/bin/env python3
"""
Fixed Color Distribution Base Module for VIIBE Gradient Generator

This module contains the corrected base classes and algorithms for color distribution
functionality. FIXED: Now reorders only colors while preserving original positions.
"""
import math
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

# Import with fallback mechanism
try:
    from gradient_generator.core.color_utils import rgb_to_hsv, hsv_to_rgb
except ImportError:
    try:
        from core.color_utils import rgb_to_hsv, hsv_to_rgb
    except ImportError:
        import colorsys
        
        def rgb_to_hsv(r, g, b):
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            return (h * 360, s, v)
        
        def hsv_to_rgb(h, s, v):
            r, g, b = colorsys.hsv_to_rgb(h/360.0, s, v)
            return (int(r*255), int(g*255), int(b*255))


class ColorDistribution(ABC):
    """Abstract base class for color distribution algorithms."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def sort_key(self, color_stop: Tuple[float, Tuple[int, int, int]]) -> float:
        """Generate a sort key for a color stop."""
        pass
    
    def distribute(self, color_stops: List[Tuple[float, Tuple[int, int, int]]], 
                  reverse: bool = False, preserve_endpoints: bool = True) -> List[Tuple[float, Tuple[int, int, int]]]:
        """
        Reorder colors while preserving original positions.
        
        This is the key fix: we extract colors, sort them, then map them back 
        to the original positions instead of creating new evenly-spaced positions.
        """
        if len(color_stops) <= 1:
            return color_stops.copy()
        
        try:
            # Extract original positions and colors
            original_positions = [pos for pos, _ in color_stops]
            colors_with_indices = [(i, color, self.sort_key((pos, color))) 
                                 for i, (pos, color) in enumerate(color_stops)]
            
            # Sort colors by the algorithm's criteria
            colors_with_indices.sort(key=lambda x: x[2], reverse=reverse)
            
            # Extract just the sorted colors
            sorted_colors = [color for _, color, _ in colors_with_indices]
            
            # Handle endpoint preservation
            if preserve_endpoints and len(sorted_colors) >= 2:
                # Find original first and last colors
                first_color = color_stops[0][1]
                last_color = color_stops[-1][1]
                
                # Remove these colors from sorted list if they exist
                if first_color in sorted_colors:
                    sorted_colors.remove(first_color)
                if last_color in sorted_colors and last_color != first_color:
                    sorted_colors.remove(last_color)
                
                # Create final color list with preserved endpoints
                final_colors = [first_color] + sorted_colors + [last_color]
                
                # Trim to original length if needed
                final_colors = final_colors[:len(original_positions)]
                
                # Pad if needed (shouldn't happen, but safety check)
                while len(final_colors) < len(original_positions):
                    final_colors.append(color_stops[-1][1])
            else:
                final_colors = sorted_colors
            
            # Create result with original positions but reordered colors
            result = []
            for i, position in enumerate(original_positions):
                if i < len(final_colors):
                    result.append((position, final_colors[i]))
                else:
                    # Safety fallback
                    result.append((position, color_stops[i][1]))
            
            return result
            
        except Exception as e:
            print(f"Error in distribute: {e}")
            return color_stops.copy()


class BrightnessDistribution(ColorDistribution):
    """Distribute color stops by brightness (HSV value)."""
    
    def __init__(self):
        super().__init__("Brightness", "Reorder colors by HSV brightness from dark to light")
    
    def sort_key(self, color_stop: Tuple[float, Tuple[int, int, int]]) -> float:
        try:
            _, (r, g, b) = color_stop
            _, _, v = rgb_to_hsv(r, g, b)
            return v
        except Exception:
            return 0.5


class LuminanceDistribution(ColorDistribution):
    """Distribute color stops by perceived luminance."""
    
    def __init__(self):
        super().__init__("Luminance", "Reorder colors by perceived brightness using ITU-R BT.709 luminance")
    
    def sort_key(self, color_stop: Tuple[float, Tuple[int, int, int]]) -> float:
        try:
            _, (r, g, b) = color_stop
            return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
        except Exception:
            return 0.5


class HueDistribution(ColorDistribution):
    """Distribute color stops by hue around the color wheel."""
    
    def __init__(self):
        super().__init__("Hue", "Reorder colors by hue position around the color wheel (0-360°)")
    
    def sort_key(self, color_stop: Tuple[float, Tuple[int, int, int]]) -> float:
        try:
            _, (r, g, b) = color_stop
            h, _, _ = rgb_to_hsv(r, g, b)
            return h / 360.0  # Normalize to 0-1 for consistent sorting
        except Exception:
            return 0.5


class SaturationDistribution(ColorDistribution):
    """Distribute color stops by saturation level."""
    
    def __init__(self):
        super().__init__("Saturation", "Reorder colors by saturation from grayscale to vivid")
    
    def sort_key(self, color_stop: Tuple[float, Tuple[int, int, int]]) -> float:
        try:
            _, (r, g, b) = color_stop
            _, s, _ = rgb_to_hsv(r, g, b)
            return s
        except Exception:
            return 0.5


class ChannelDistribution(ColorDistribution):
    """Base class for RGB channel distributions."""
    
    def __init__(self, channel: str, index: int):
        super().__init__(f"{channel} Channel", f"Reorder colors by {channel.lower()} color channel intensity (0-255)")
        self.index = index
    
    def sort_key(self, color_stop: Tuple[float, Tuple[int, int, int]]) -> float:
        try:
            _, color = color_stop
            return color[self.index] / 255.0
        except Exception:
            return 0.5


class RedChannelDistribution(ChannelDistribution):
    def __init__(self):
        super().__init__("Red", 0)


class GreenChannelDistribution(ChannelDistribution):
    def __init__(self):
        super().__init__("Green", 1)


class BlueChannelDistribution(ChannelDistribution):
    def __init__(self):
        super().__init__("Blue", 2)


class DistanceFromColorDistribution(ColorDistribution):
    """Distribute color stops by distance from a reference color."""
    
    def __init__(self, reference_color: Tuple[int, int, int] = (128, 128, 128)):
        self.reference_color = reference_color
        super().__init__(
            f"Distance from Color", 
            f"Reorder colors by Euclidean distance from RGB{reference_color}"
        )
    
    def sort_key(self, color_stop: Tuple[float, Tuple[int, int, int]]) -> float:
        try:
            _, (r, g, b) = color_stop
            ref_r, ref_g, ref_b = self.reference_color
            distance = math.sqrt((r - ref_r) ** 2 + (g - ref_g) ** 2 + (b - ref_b) ** 2)
            return distance / 441.67  # Normalize to 0-1 (max distance is sqrt(255^2 * 3))
        except Exception:
            return 0.5


class WarmCoolDistribution(ColorDistribution):
    """Distribute color stops from cool to warm colors."""
    
    def __init__(self):
        super().__init__("Warm-Cool", "Reorder colors from cool (blues/greens) to warm (reds/oranges)")
    
    def sort_key(self, color_stop: Tuple[float, Tuple[int, int, int]]) -> float:
        try:
            _, (r, g, b) = color_stop
            h, s, v = rgb_to_hsv(r, g, b)
            
            # Cool colors: 120-300 degrees (blue, cyan, green)
            # Warm colors: 300-360, 0-120 degrees (red, orange, yellow)
            
            if 120 <= h <= 300:
                # Cool colors: map to 0.0-0.4 range
                cool_position = (h - 120) / 180  # 0-1 within cool range
                return 0.4 * cool_position
            else:
                # Warm colors: map to 0.4-1.0 range
                if h >= 300:
                    warm_position = (h - 300) / 60  # Red side: 300-360
                else:
                    warm_position = (60 - h) / 60   # Yellow side: 0-60 (inverted)
                return 0.4 + 0.6 * warm_position
        except Exception:
            return 0.5


class ChromaDistribution(ColorDistribution):
    """Distribute color stops by chroma (color intensity)."""
    
    def __init__(self):
        super().__init__("Chroma", "Reorder colors by chroma (saturation × brightness)")
    
    def sort_key(self, color_stop: Tuple[float, Tuple[int, int, int]]) -> float:
        try:
            _, (r, g, b) = color_stop
            _, s, v = rgb_to_hsv(r, g, b)
            return s * v
        except Exception:
            return 0.5


class ContrastDistribution(ColorDistribution):
    """Distribute color stops by contrast from average."""
    
    def __init__(self):
        super().__init__("Contrast", "Reorder colors by contrast difference from average gray")
        self.average_gray = 128  # Default fallback
    
    def distribute(self, color_stops: List[Tuple[float, Tuple[int, int, int]]], 
                  reverse: bool = False, preserve_endpoints: bool = True) -> List[Tuple[float, Tuple[int, int, int]]]:
        """Override to calculate average first."""
        if not color_stops:
            return color_stops
        
        try:
            # Calculate average gray value
            total_gray = sum((0.299 * r + 0.587 * g + 0.114 * b) for _, (r, g, b) in color_stops)
            self.average_gray = total_gray / len(color_stops)
        except Exception:
            self.average_gray = 128  # Fallback
        
        return super().distribute(color_stops, reverse, preserve_endpoints)
    
    def sort_key(self, color_stop: Tuple[float, Tuple[int, int, int]]) -> float:
        try:
            _, (r, g, b) = color_stop
            gray_value = 0.299 * r + 0.587 * g + 0.114 * b
            return abs(gray_value - self.average_gray) / 255.0
        except Exception:
            return 0.5


class ComplementaryDistribution(ColorDistribution):
    """Distribute color stops by complementary relationships."""
    
    def __init__(self):
        super().__init__("Complementary", "Reorder colors by complementary color relationships")
        self.primary_hue = 0  # Default fallback
    
    def distribute(self, color_stops: List[Tuple[float, Tuple[int, int, int]]], 
                  reverse: bool = False, preserve_endpoints: bool = True) -> List[Tuple[float, Tuple[int, int, int]]]:
        """Override to find primary hue first."""
        if not color_stops:
            return color_stops
        
        try:
            # Find the most saturated color as primary
            max_saturation = 0
            for _, (r, g, b) in color_stops:
                h, s, v = rgb_to_hsv(r, g, b)
                if s > max_saturation:
                    max_saturation = s
                    self.primary_hue = h
        except Exception:
            self.primary_hue = 0  # Fallback
        
        return super().distribute(color_stops, reverse, preserve_endpoints)
    
    def sort_key(self, color_stop: Tuple[float, Tuple[int, int, int]]) -> float:
        try:
            _, (r, g, b) = color_stop
            h, s, v = rgb_to_hsv(r, g, b)
            
            # Calculate distance from primary hue and its complement
            complement_hue = (self.primary_hue + 180) % 360
            
            # Distance to primary (shortest path around circle)
            dist_to_primary = min(abs(h - self.primary_hue), 360 - abs(h - self.primary_hue))
            # Distance to complement (shortest path around circle)
            dist_to_complement = min(abs(h - complement_hue), 360 - abs(h - complement_hue))
            
            # Sort by minimum distance to either primary or complement
            return min(dist_to_primary, dist_to_complement) / 180.0  # Normalize to 0-1
        except Exception:
            return 0.5


class RandomDistribution(ColorDistribution):
    """Randomly redistribute color stops."""
    
    def __init__(self, seed: int = None):
        super().__init__("Random", "Randomly shuffle the colors at existing positions")
        self.seed = seed
    
    def distribute(self, color_stops: List[Tuple[float, Tuple[int, int, int]]], 
                  reverse: bool = False, preserve_endpoints: bool = True) -> List[Tuple[float, Tuple[int, int, int]]]:
        """Override to use random shuffling of colors only."""
        if len(color_stops) <= 1:
            return color_stops.copy()
        
        try:
            import random
            if self.seed is not None:
                random.seed(self.seed)
            
            # Extract original positions and colors
            original_positions = [pos for pos, _ in color_stops]
            colors = [color for _, color in color_stops]
            
            # Handle endpoint preservation
            if preserve_endpoints and len(colors) >= 2:
                # Remove first and last colors from shuffle list
                first_color = colors[0]
                last_color = colors[-1]
                middle_colors = colors[1:-1]
                
                # Shuffle only the middle colors
                random.shuffle(middle_colors)
                
                # Reconstruct color list
                shuffled_colors = [first_color] + middle_colors + [last_color]
            else:
                # Shuffle all colors
                shuffled_colors = colors.copy()
                random.shuffle(shuffled_colors)
            
            # Create result with original positions and shuffled colors
            result = []
            for position, color in zip(original_positions, shuffled_colors):
                result.append((position, color))
            
            if reverse:
                # Reverse only the color order, keep positions the same
                colors_only = [color for _, color in result]
                colors_only.reverse()
                result = [(pos, color) for (pos, _), color in zip(result, colors_only)]
            
            return result
        except Exception as e:
            print(f"Error in random distribution: {e}")
            return color_stops.copy()
    
    def sort_key(self, color_stop: Tuple[float, Tuple[int, int, int]]) -> float:
        # Not used in random distribution
        return 0.0


# Simple brightness-only fallback for when advanced distributions fail
class SimpleBrightnessDistribution(ColorDistribution):
    """Simple fallback brightness distribution."""
    
    def __init__(self):
        super().__init__("Simple Brightness", "Simple brightness reordering (fallback)")
    
    def sort_key(self, color_stop: Tuple[float, Tuple[int, int, int]]) -> float:
        try:
            _, (r, g, b) = color_stop
            # Simple brightness calculation
            return (r + g + b) / (3 * 255.0)
        except Exception:
            return 0.5


# Registry with error handling
def create_distribution_registry():
    """Create the distribution registry with error handling."""
    registry = {}
    
    # Try to add each distribution, skip if it fails
    distributions_to_add = [
        ("brightness", BrightnessDistribution),
        ("luminance", LuminanceDistribution),
        ("hue", HueDistribution),
        ("saturation", SaturationDistribution),
        ("red_channel", RedChannelDistribution),
        ("green_channel", GreenChannelDistribution),
        ("blue_channel", BlueChannelDistribution),
        ("warm_cool", WarmCoolDistribution),
        ("chroma", ChromaDistribution),
        ("contrast", ContrastDistribution),
        ("complementary", ComplementaryDistribution),
        ("random", RandomDistribution),
        ("simple_brightness", SimpleBrightnessDistribution),  # Always works fallback
    ]
    
    for key, distribution_class in distributions_to_add:
        try:
            registry[key] = distribution_class()
        except Exception as e:
            print(f"Warning: Could not create {key} distribution: {e}")
    
    # Ensure we have at least one working distribution
    if not registry:
        print("Warning: No distributions available, creating minimal fallback")
        registry["fallback"] = SimpleBrightnessDistribution()
    
    return registry


# Create the registry
DISTRIBUTION_REGISTRY = create_distribution_registry()


def get_distribution(name: str) -> Optional[ColorDistribution]:
    """Get a distribution algorithm by name."""
    distribution = DISTRIBUTION_REGISTRY.get(name.lower())
    if distribution is None:
        # Fallback to simple brightness if requested distribution doesn't exist
        print(f"Warning: Distribution '{name}' not found, using simple brightness fallback")
        return DISTRIBUTION_REGISTRY.get("simple_brightness") or DISTRIBUTION_REGISTRY.get("brightness")
    return distribution


def get_available_distributions() -> List[Tuple[str, str, str]]:
    """Get list of available distributions with enhanced descriptions."""
    return [(key, dist.name, dist.description) for key, dist in DISTRIBUTION_REGISTRY.items()]


def create_distance_distribution(reference_color: Tuple[int, int, int]) -> ColorDistribution:
    """Create a distance-based distribution with a custom reference color."""
    try:
        return DistanceFromColorDistribution(reference_color)
    except Exception as e:
        print(f"Error creating distance distribution: {e}")
        # Return a fallback
        return DISTRIBUTION_REGISTRY.get("simple_brightness", SimpleBrightnessDistribution())


def create_random_distribution(seed: int = None) -> ColorDistribution:
    """Create a random distribution with optional seed."""
    try:
        return RandomDistribution(seed)
    except Exception as e:
        print(f"Error creating random distribution: {e}")
        return DISTRIBUTION_REGISTRY.get("simple_brightness", SimpleBrightnessDistribution())


def blend_distributions(original_stops: List[Tuple[float, Tuple[int, int, int]]],
                       distributed_stops: List[Tuple[float, Tuple[int, int, int]]],
                       strength: float) -> List[Tuple[float, Tuple[int, int, int]]]:
    """
    Blend between original and distributed stops based on strength.
    
    Since we're only reordering colors (not positions), we blend the color assignments.
    """
    try:
        # Clamp strength to valid range
        strength = max(0.0, min(1.0, strength))
        
        if strength <= 0.0:
            return original_stops.copy()
        if strength >= 1.0:
            return distributed_stops.copy()
        
        if len(original_stops) != len(distributed_stops):
            print("Warning: Mismatched stop counts, returning distributed stops")
            return distributed_stops.copy()
        
        # For color reordering, we need to blend the color assignments
        # This is complex since we're dealing with discrete color mappings
        # For simplicity, we'll use a threshold approach
        
        if strength >= 0.5:
            return distributed_stops.copy()
        else:
            return original_stops.copy()
            
    except Exception as e:
        print(f"Error in blend_distributions: {e}")
        return original_stops.copy()


def safe_distribute(distribution_name: str, color_stops: List[Tuple[float, Tuple[int, int, int]]], 
                   reverse: bool = False, preserve_endpoints: bool = True) -> List[Tuple[float, Tuple[int, int, int]]]:
    """Safely distribute color stops with error handling."""
    try:
        distribution = get_distribution(distribution_name)
        if distribution:
            return distribution.distribute(color_stops, reverse, preserve_endpoints)
        else:
            print(f"Distribution '{distribution_name}' not available")
            return color_stops.copy()
    except Exception as e:
        print(f"Error in safe_distribute: {e}")
        return color_stops.copy()


# Utility functions for testing and validation
def test_distribution(distribution_name: str, test_stops: List[Tuple[float, Tuple[int, int, int]]]) -> dict:
    """Test a distribution algorithm with sample data."""
    try:
        distribution = get_distribution(distribution_name)
        if not distribution:
            return {"error": f"Distribution '{distribution_name}' not found", "success": False}
        
        result = distribution.distribute(test_stops)
        
        # Verify positions are preserved
        original_positions = [pos for pos, _ in test_stops]
        result_positions = [pos for pos, _ in result]
        positions_preserved = original_positions == result_positions
        
        return {
            "distribution": distribution_name,
            "original_stops": len(test_stops),
            "result_stops": len(result),
            "positions_preserved": positions_preserved,
            "success": True,
            "result": result
        }
    except Exception as e:
        return {"error": str(e), "success": False}


if __name__ == "__main__":
    # Test the fixed distribution system
    print("Fixed Color Distribution System - Colors Only Reordering")
    print("=" * 60)
    
    # Show available distributions
    print("\nAvailable Distributions:")
    distributions = get_available_distributions()
    for key, name, description in distributions:
        print(f"  {name}: {description}")
    
    print(f"\nTotal distributions available: {len(distributions)}")
    
    # Test with sample data
    test_stops = [
        (0.0, (255, 0, 0)),    # Red at start
        (0.25, (255, 255, 0)), # Yellow 
        (0.5, (0, 255, 0)),    # Green in middle
        (0.75, (0, 255, 255)), # Cyan
        (1.0, (0, 0, 255))     # Blue at end
    ]
    
    print(f"\nTesting with sample stops: {len(test_stops)} colors")
    print("Original positions:", [pos for pos, _ in test_stops])
    print("Original colors:", [color for _, color in test_stops])
    
    # Test key distributions
    test_distributions = ["brightness", "hue", "warm_cool", "random"]
    
    for dist_name in test_distributions:
        result = test_distribution(dist_name, test_stops)
        if result.get("success"):
            positions_ok = "✓" if result.get("positions_preserved") else "✗"
            print(f"\n{dist_name.upper()} distribution:")
            print(f"  Success: ✓")
            print(f"  Positions preserved: {positions_ok}")
            if result.get("result"):
                result_positions = [pos for pos, _ in result["result"]]
                result_colors = [color for _, color in result["result"]]
                print(f"  Result positions: {result_positions}")
                print(f"  Result colors: {result_colors}")
        else:
            print(f"✗ {dist_name} failed: {result.get('error')}")
    
    print("\n" + "=" * 60)
    print("KEY FIX: Colors are now reordered while positions stay the same!")
    print("- Original positions are preserved exactly")
    print("- Only the color values are redistributed according to sorting criteria")
    print("- This maintains the gradient's structure while reorganizing color flow")
