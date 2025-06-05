#!/usr/bin/env python3
"""
UPDATED Mathematical Distribution Module - Phase Parameter Support

Key changes:
- Even distribution: UNCHANGED - keeps strength parameter for gradual blending
- All other distributions: UPDATED to use phase parameter instead of strength
- Phase controls the starting point/offset of wave patterns at full intensity
- No gradual blending for wave patterns - they apply at full intensity with phase variation
"""
import math
from abc import ABC, abstractmethod


class ColorStopDistribution(ABC):
    """Abstract base class for color stop distribution algorithms."""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    @abstractmethod
    def distribute(self, num_stops, params=None):
        """Generate positions for color stops according to the distribution pattern."""
        pass
    
    def _process_positions(self, positions, ensure_endpoints=True):
        """Process positions: clamp to [0,1], sort, and optionally ensure endpoints."""
        try:
            positions = [max(0.0, min(1.0, float(pos))) for pos in positions]
            positions = sorted(positions)
            if ensure_endpoints and len(positions) >= 2:
                positions[0] = 0.0
                positions[-1] = 1.0
            return positions
        except (TypeError, ValueError):
            return [i / max(1, num_stops - 1) for i in range(num_stops)]
    
    def _apply_strength(self, original_positions, target_positions, strength):
        """Apply strength to smoothly transition between original and target positions."""
        if strength <= 0.0:
            return original_positions
        elif strength >= 1.0:
            return target_positions
        
        # Smooth interpolation with easing function
        def ease_in_out(t):
            """Smooth step function for natural transitions."""
            return t * t * (3.0 - 2.0 * t)
        
        eased_strength = ease_in_out(strength)
        
        result = []
        for orig, target in zip(original_positions, target_positions):
            interpolated = orig + (target - orig) * eased_strength
            result.append(interpolated)
        
        return result


class EvenDistribution(ColorStopDistribution):
    """
    Even distribution creates perfectly even spacing.
    UNCHANGED - still uses strength parameter for gradual blending.
    """
    
    def __init__(self):
        super().__init__("Even Distribution", 
                        "Creates perfectly even spacing with gradual strength control")
    
    def distribute(self, num_stops, params=None):
        if num_stops <= 1:
            return [0.5]
        
        p = params or {}
        strength = max(0.0, min(1.0, p.get('strength', 1.0)))
        original_positions = p.get('original_positions', None)
        
        if original_positions is None or len(original_positions) != num_stops:
            original_positions = [i / (num_stops - 1) for i in range(num_stops)]
        
        # Generate perfect even spacing - this is the target
        target_positions = [i / (num_stops - 1) for i in range(num_stops)]
        
        # Apply strength to smoothly transition from original to even
        result_positions = self._apply_strength(original_positions, target_positions, strength)
        
        return self._process_positions(result_positions)


class PowerCurveDistribution(ColorStopDistribution):
    """
    UPDATED: Power curve with phase parameter instead of strength.
    Phase shifts the curve along the input domain.
    """
    
    def __init__(self):
        super().__init__("Power Curves", "Apply exponential curves with phase offset")
    
    def distribute(self, num_stops, params=None):
        if num_stops <= 2:
            return [0.0, 1.0] if num_stops == 2 else [0.5]
        
        try:
            p = params or {}
            power = max(0.1, min(10.0, p.get('power', 2.0)))
            phase = p.get('phase', 0.0)  # Phase in radians
            original_positions = p.get('original_positions', None)
            
            if original_positions is None or len(original_positions) != num_stops:
                original_positions = [i / (num_stops - 1) for i in range(num_stops)]
            
            # Apply power curve with phase offset to each position
            target_positions = []
            for i, pos in enumerate(original_positions):
                # Apply phase as a shift in the curve calculation
                # Phase affects how the curve is sampled
                phase_offset = (phase / (2 * math.pi)) * 0.5  # Convert to position offset
                shifted_pos = (pos + phase_offset) % 1.0
                
                # Apply power curve
                transformed = shifted_pos ** power
                target_positions.append(transformed)
            
            # Ensure endpoints are preserved
            if len(target_positions) >= 2:
                target_positions[0] = 0.0
                target_positions[-1] = 1.0
            
            return self._process_positions(target_positions)
        except Exception:
            return original_positions if original_positions else [i / (num_stops - 1) for i in range(num_stops)]


class SinusoidalWaveDistribution(ColorStopDistribution):
    """
    UPDATED: Sine wave with phase parameter (no strength).
    Phase controls the wave starting point at full intensity.
    """
    
    def __init__(self):
        super().__init__("Sine Wave", "Apply sinusoidal wave with phase control")
    
    def distribute(self, num_stops, params=None):
        if num_stops <= 2:
            return [0.0, 1.0] if num_stops == 2 else [0.5]
        
        try:
            p = params or {}
            frequency = max(0.1, min(8.0, p.get('frequency', 2.0)))
            amplitude = max(0.0, min(0.4, p.get('amplitude', 0.2)))
            phase = p.get('phase', 0.0)  # Phase in radians
            original_positions = p.get('original_positions', None)
            
            if original_positions is None or len(original_positions) != num_stops:
                original_positions = [i / (num_stops - 1) for i in range(num_stops)]
            
            # Apply sine wave with phase at full intensity
            target_positions = []
            for pos in original_positions:
                # Apply sine wave with phase offset
                wave = math.sin(2 * math.pi * frequency * pos + phase)
                distorted = pos + amplitude * wave
                target_positions.append(distorted)
            
            return self._process_positions(target_positions)
        except Exception:
            return original_positions if original_positions else [i / (num_stops - 1) for i in range(num_stops)]


class HarmonicWaveDistribution(ColorStopDistribution):
    """
    UPDATED: Harmonic wave with phase parameter (no strength).
    Phase controls the wave starting point at full intensity.
    """
    
    def __init__(self):
        super().__init__("Harmonic Wave", "Apply multiple harmonics with phase control")
    
    def distribute(self, num_stops, params=None):
        if num_stops <= 2:
            return [0.0, 1.0] if num_stops == 2 else [0.5]
        
        try:
            p = params or {}
            frequency = max(0.5, min(6.0, p.get('frequency', 2.0)))
            amplitude = max(0.0, min(0.3, p.get('amplitude', 0.15)))
            harmonics = max(2, min(6, p.get('harmonics', 4)))
            phase = p.get('phase', 0.0)  # Phase in radians
            original_positions = p.get('original_positions', None)
            
            if original_positions is None or len(original_positions) != num_stops:
                original_positions = [i / (num_stops - 1) for i in range(num_stops)]
            
            # Apply harmonic wave with phase at full intensity
            target_positions = []
            for pos in original_positions:
                # Sum multiple harmonics with phase offset
                wave = 0
                for h in range(1, harmonics + 1):
                    decay = 1.0 / h
                    wave += decay * math.sin(2 * math.pi * h * frequency * pos + phase)
                
                wave *= 0.5 / harmonics
                distorted = pos + amplitude * wave
                target_positions.append(distorted)
            
            return self._process_positions(target_positions)
        except Exception:
            return original_positions if original_positions else [i / (num_stops - 1) for i in range(num_stops)]


class SpirographDistribution(ColorStopDistribution):
    """
    UPDATED: Spirograph with phase parameter (no strength).
    Phase controls the pattern starting point at full intensity.
    """
    
    def __init__(self):
        super().__init__("Spirograph", "Apply complex cycloid patterns with phase control")
    
    def distribute(self, num_stops, params=None):
        if num_stops <= 2:
            return [0.0, 1.0] if num_stops == 2 else [0.5]
        
        try:
            p = params or {}
            R = p.get('outer_radius', 5.0)
            r = p.get('inner_radius', 3.0)
            d = p.get('pen_distance', 2.0)
            amplitude = max(0.0, min(0.3, p.get('amplitude', 0.2)))
            phase = p.get('phase', 0.0)  # Phase in radians
            original_positions = p.get('original_positions', None)
            
            if original_positions is None or len(original_positions) != num_stops:
                original_positions = [i / (num_stops - 1) for i in range(num_stops)]
            
            # Apply spirograph with phase at full intensity
            target_positions = []
            for pos in original_positions:
                # Use position as parameter for spirograph with phase offset
                theta = pos * 4 * math.pi + phase
                
                # Spirograph equations
                x = (R - r) * math.cos(theta) + d * math.cos((R - r) / r * theta)
                
                # Normalize and apply as offset
                x_normalized = x / (R + d)
                distorted = pos + amplitude * x_normalized
                target_positions.append(distorted)
            
            return self._process_positions(target_positions)
        except Exception:
            return original_positions if original_positions else [i / (num_stops - 1) for i in range(num_stops)]


class ComplexWaveDistribution(ColorStopDistribution):
    """
    UPDATED: Complex wave with phase parameter (no strength).
    Phase controls the wave starting point at full intensity.
    """
    
    def __init__(self):
        super().__init__("Complex Wave", "Apply multi-wave combination with phase control")
    
    def distribute(self, num_stops, params=None):
        if num_stops <= 2:
            return [0.0, 1.0] if num_stops == 2 else [0.5]
        
        try:
            p = params or {}
            frequency = max(0.5, min(6.0, p.get('frequency', 2.0)))
            amplitude = max(0.0, min(0.3, p.get('amplitude', 0.2)))
            complexity = max(1, min(4, p.get('complexity', 2)))
            phase = p.get('phase', 0.0)  # Phase in radians
            original_positions = p.get('original_positions', None)
            
            if original_positions is None or len(original_positions) != num_stops:
                original_positions = [i / (num_stops - 1) for i in range(num_stops)]
            
            # Apply complex wave with phase at full intensity
            target_positions = []
            for pos in original_positions:
                wave = 0
                
                if complexity >= 1:
                    wave += math.sin(2 * math.pi * frequency * pos + phase)
                
                if complexity >= 2:
                    golden = 1.618
                    wave += 0.6 * math.sin(2 * math.pi * frequency * golden * pos + phase)
                
                if complexity >= 3:
                    triangle = 0
                    for n in range(1, 8, 2):
                        triangle += ((-1)**((n-1)//2) / (n*n)) * math.sin(n * 2 * math.pi * frequency * pos + phase)
                    wave += 0.4 * triangle
                
                if complexity >= 4:
                    square = 0
                    for n in range(1, 6, 2):
                        square += (1/n) * math.sin(n * 2 * math.pi * frequency * pos + phase)
                    wave += 0.3 * square
                
                wave /= complexity
                distorted = pos + amplitude * wave
                target_positions.append(distorted)
            
            return self._process_positions(target_positions)
        except Exception:
            return original_positions if original_positions else [i / (num_stops - 1) for i in range(num_stops)]


class GoldenRatioDistribution(ColorStopDistribution):
    """
    UPDATED: Golden ratio with phase parameter (no strength).
    Phase controls the pattern offset at full intensity.
    """
    
    def __init__(self):
        super().__init__("Golden Ratio", "Apply natural golden ratio spacing with phase control")
    
    def distribute(self, num_stops, params=None):
        if num_stops <= 1:
            return [0.5]
        
        try:
            p = params or {}
            phase = p.get('phase', 0.0)  # Phase in radians
            original_positions = p.get('original_positions', None)
            
            if original_positions is None or len(original_positions) != num_stops:
                original_positions = [i / (num_stops - 1) for i in range(num_stops)]
            
            # Generate golden ratio influenced positions with phase
            phi = (1 + math.sqrt(5)) / 2
            target_positions = []
            
            # Convert phase to a position offset
            phase_offset = (phase / (2 * math.pi))
            
            for i, original_pos in enumerate(original_positions):
                if i == 0:
                    target_positions.append(0.0)
                elif i == len(original_positions) - 1:
                    target_positions.append(1.0)
                else:
                    # Use golden ratio with phase offset
                    golden_angle = 2 * math.pi / (phi * phi)
                    position = ((i * golden_angle) + phase) % (2 * math.pi)
                    normalized = position / (2 * math.pi)
                    
                    # Apply at full intensity (no strength blending)
                    target_positions.append(normalized)
            
            # Sort to maintain gradient order
            target_positions = sorted(target_positions)
            target_positions[0] = 0.0
            target_positions[-1] = 1.0
            
            return self._process_positions(target_positions)
        except Exception:
            return original_positions if original_positions else [i / (num_stops - 1) for i in range(num_stops)]


def create_distributions():
    """Create the updated distribution registry with phase support."""
    return {
        "even": EvenDistribution(),
        "power_curves": PowerCurveDistribution(),
        "sine_wave": SinusoidalWaveDistribution(),
        "harmonic_wave": HarmonicWaveDistribution(),
        "spirograph": SpirographDistribution(),
        "complex_wave": ComplexWaveDistribution(),
        "golden_ratio": GoldenRatioDistribution(),
    }


# Global distributions registry
DISTRIBUTIONS = create_distributions()


def get_distribution(name):
    """Get a distribution by name."""
    return DISTRIBUTIONS.get(name.lower())


def get_available_distributions():
    """Get list of available distribution names and descriptions."""
    result = []
    for key, dist in DISTRIBUTIONS.items():
        result.append((key, dist.name, dist.description))
    return result


def test_phase_distributions():
    """Test that distributions use phase parameter correctly."""
    print("Testing UPDATED Mathematical Distributions - Phase Parameters")
    print("=" * 70)
    
    # Test with uneven original positions
    original_positions = [0.0, 0.1, 0.15, 0.7, 1.0]
    print(f"Original positions: {[f'{p:.3f}' for p in original_positions]}")
    print()
    
    # Test phase parameter for each distribution
    for dist_name, dist in DISTRIBUTIONS.items():
        print(f"{dist.name.upper()}:")
        
        if dist_name == "even":
            # Even distribution uses strength
            params = {'strength': 1.0, 'original_positions': original_positions}
            result = dist.distribute(len(original_positions), params)
            print(f"  With strength 100%: {[f'{p:.3f}' for p in result]}")
        else:
            # Other distributions use phase
            # Test with 0° phase
            params = {'phase': 0.0, 'original_positions': original_positions}
            result_0 = dist.distribute(len(original_positions), params)
            print(f"  Phase 0°:   {[f'{p:.3f}' for p in result_0]}")
            
            # Test with 90° phase (π/2 radians)
            params = {'phase': math.pi/2, 'original_positions': original_positions}
            result_90 = dist.distribute(len(original_positions), params)
            print(f"  Phase 90°:  {[f'{p:.3f}' for p in result_90]}")
        
        print()
    
    print("=" * 70)
    print("UPDATED BEHAVIOR:")
    print("✅ Even Distribution: Uses strength (0-100%) for gradual blending")
    print("✅ All Other Patterns: Use phase (0-360°) for wave offset control")
    print("✅ Phase controls starting point of wave patterns at full intensity")
    print("✅ No gradual blending for wave patterns - they apply at full effect")


if __name__ == "__main__":
    test_phase_distributions()