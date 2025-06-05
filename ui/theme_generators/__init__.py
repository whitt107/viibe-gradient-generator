"""
Theme Generators Package for Gradient Generator

This package contains theme-based gradient generators for creating
specialized gradients with natural themes. Updated to include the new
Metal & Stone theme generator replacing the old metals theme.
"""

# Import all theme generators and utilities
from .theme_gradient_generator import ThemeGradientGenerator, ThemeParameter
from .foliage_theme import FoliageThemeGenerator
from .flower_theme import FlowerThemeGenerator
from .cosmic_theme import CosmicThemeGenerator
from .fire_theme import FireThemeGenerator
from .mood_theme import MoodThemeGenerator
from .metal_stone_theme import MetalAndStoneThemeGenerator  # NEW: Metal & Stone theme
from .theme_generator_widget import ThemeGeneratorWidget, ThemePreviewWidget, ThemeControlsWidget
from .theme_generator_integration import integrate_theme_generator, add_theme_generator_tab

# Optional theme generators (may not be present in all installations)
try:
    from .sky_theme import SkyThemeGenerator
except ImportError:
    SkyThemeGenerator = None

try:
    from .artistic_style_theme import ArtisticStyleThemeGenerator
except ImportError:
    ArtisticStyleThemeGenerator = None

try:
    from .holiday_theme import HolidayThemeGenerator
except ImportError:
    HolidayThemeGenerator = None

# NOTE: Removed old MetalsThemeGenerator - replaced by MetalAndStoneThemeGenerator

# Make key classes and functions available at package level
__all__ = [
    'ThemeGradientGenerator',
    'ThemeParameter',
    'FoliageThemeGenerator',
    'FlowerThemeGenerator',
    'CosmicThemeGenerator',
    'FireThemeGenerator',
    'MoodThemeGenerator',
    'MetalAndStoneThemeGenerator',  # NEW: Metal & Stone theme
    'ThemeGeneratorWidget',
    'ThemePreviewWidget',
    'ThemeControlsWidget',
    'integrate_theme_generator',
    'add_theme_generator_tab'
]

# Add optional generators to __all__ if they're available
if SkyThemeGenerator is not None:
    __all__.append('SkyThemeGenerator')

if ArtisticStyleThemeGenerator is not None:
    __all__.append('ArtisticStyleThemeGenerator')

if HolidayThemeGenerator is not None:
    __all__.append('HolidayThemeGenerator')

# Package metadata
__version__ = '1.1.0'  # Updated version for Metal & Stone integration
__author__ = 'Theme Generator Team'
__description__ = 'Theme-based gradient generators for VIIBE Gradient Generator with Metal & Stone materials'

# Available theme generators registry
AVAILABLE_THEMES = {
    'foliage': FoliageThemeGenerator,
    'flowers': FlowerThemeGenerator,
    'cosmic': CosmicThemeGenerator,
    'fire': FireThemeGenerator,
    'mood': MoodThemeGenerator,
    'metal_stone': MetalAndStoneThemeGenerator,  # NEW
}

# Add optional themes to registry if available
if SkyThemeGenerator is not None:
    AVAILABLE_THEMES['sky'] = SkyThemeGenerator

if ArtisticStyleThemeGenerator is not None:
    AVAILABLE_THEMES['artistic'] = ArtisticStyleThemeGenerator

if HolidayThemeGenerator is not None:
    AVAILABLE_THEMES['holidays'] = HolidayThemeGenerator


def get_available_theme_names():
    """
    Get list of available theme names sorted alphabetically.
    
    Returns:
        List of theme names
    """
    return sorted(AVAILABLE_THEMES.keys())


def create_theme_generator(theme_name: str):
    """
    Create a theme generator instance by name.
    
    Args:
        theme_name: Name of the theme generator
        
    Returns:
        Theme generator instance or None if not available
    """
    if theme_name in AVAILABLE_THEMES:
        return AVAILABLE_THEMES[theme_name]()
    return None


def get_theme_display_names():
    """
    Get mapping of theme keys to display names.
    
    Returns:
        Dictionary mapping theme keys to display names
    """
    display_names = {
        'foliage': 'Foliage',
        'flowers': 'Flowers', 
        'cosmic': 'Cosmic',
        'fire': 'Fire',
        'mood': 'Mood',
        'metal_stone': 'Metal & Stone',
    }
    
    # Add optional themes
    if 'sky' in AVAILABLE_THEMES:
        display_names['sky'] = 'Sky'
    if 'artistic' in AVAILABLE_THEMES:
        display_names['artistic'] = 'Artistic Styles'
    if 'holidays' in AVAILABLE_THEMES:
        display_names['holidays'] = 'Holidays'
        
    return display_names