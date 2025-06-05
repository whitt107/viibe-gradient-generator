#!/usr/bin/env python3
"""
Gradient Blending Module Initialization - Updated without Fractal Blend

This module initializes the gradient blending functionality and imports all
the necessary components for use within the application, including the 
blend types: Waveform, Crystal, Layer, Chromatic, and Memory blenders.

REMOVED: Harmony, Procedural, Gravity, and Fractal blenders
"""
try:
    # Import the core components
    from .blend_core import (
        GradientBlender, BlendParameter, BlendRegistry,
        get_interpolated_color_at_position, create_blended_gradient, distribute_stops_evenly
    )
    
    # Import the original blending methods (registers them with BlendRegistry)
    from .interleave_blend import InterleaveBlender
    from .mix_blend import MixBlender
    from .crossfade_blend import CrossfadeBlender
    from .stack_blend import StackBlender
    
    # Import the NEW blending methods (registers them with BlendRegistry)
    from .new_blend_types import (
        WaveformBlender, CrystalBlender,
        LayerBlender, ChromaticBlender, MemoryBlender
    )
    
    # Import the UI components
    from .gradient_blending_ui import GradientBlendingWidget, GradientPreviewWidget
    
    # Import integration utilities
    from .blending_integration import integrate_blending, add_blending_tab
    
    # Define all exported symbols
    __all__ = [
        # Core classes
        'GradientBlender',
        'BlendParameter',
        'BlendRegistry',
        
        # Original blending methods
        'InterleaveBlender',
        'MixBlender',
        'CrossfadeBlender',
        'StackBlender',
        
        # NEW blending methods
        'WaveformBlender',
        'CrystalBlender',
        'LayerBlender',
        'ChromaticBlender',
        'MemoryBlender',
        
        # UI components
        'GradientBlendingWidget',
        'GradientPreviewWidget',
        
        # Integration utilities
        'integrate_blending',
        'add_blending_tab',
        
        # Helper functions
        'get_interpolated_color_at_position',
        'create_blended_gradient',
        'distribute_stops_evenly'
    ]

    # Print initialization success message with blend type count
    print("Gradient blending module initialized successfully!")
    print(f"Available blend types: {len(BlendRegistry.get_all_blenders())}")
    
    # List all available blenders for debugging/information
    available_blenders = BlendRegistry.get_blender_names()
    if available_blenders:
        print("Registered blenders:", ", ".join(available_blenders))

except ImportError as e:
    # Provide a detailed message but don't crash the whole import
    import warnings
    warnings.warn(f"Gradient blending module could not be fully imported: {e}")
    
    # Try to import at least the core components
    try:
        from .blend_core import GradientBlender, BlendParameter, BlendRegistry
        from .gradient_blending_ui import GradientBlendingWidget
        from .blending_integration import integrate_blending, add_blending_tab
        
        print("Partial gradient blending import successful - core components available")
        
        # Define minimal exports for partial functionality
        __all__ = [
            'GradientBlender',
            'BlendParameter', 
            'BlendRegistry',
            'GradientBlendingWidget',
            'integrate_blending',
            'add_blending_tab'
        ]
        
    except ImportError:
        # Define empty exports to prevent import errors elsewhere
        __all__ = []
        print("Warning: Gradient blending functionality unavailable")

except Exception as e:
    # Handle any other unexpected errors during initialization
    import warnings
    warnings.warn(f"Unexpected error initializing gradient blending: {e}")
    __all__ = []

# Package metadata
__version__ = '2.2.0'  # Updated version to reflect changes
__author__ = 'Gradient Generator Team'
__description__ = 'Enhanced gradient blending functionality with 9 blend types for JWildfire Gradient Generator'

# Blend type information for external reference (updated)
BLEND_TYPE_INFO = {
    # Original blend types
    'interleave': 'Preserves all color stops from input gradients',
    'mix': 'Mixes colors at each position by combining RGB components', 
    'crossfade': 'Creates sequential transitions between gradients',
    'stack': 'Divides range into segments for each gradient',
    
    # NEW blend types
    'waveform': 'Creates wave interference patterns between gradients',
    'crystal': 'Creates crystalline facet patterns with light refraction',
    'layer': 'Photoshop-style blend modes (multiply, screen, overlay, etc.)',
    'chromatic': 'Separates RGB channels for prismatic aberration effects', 
    'memory': 'Uses gradient memory for trailing echo effects'
}

def get_blend_type_info(blend_type: str = None) -> dict:
    """
    Get information about available blend types.
    
    Args:
        blend_type: Specific blend type to get info for, or None for all
        
    Returns:
        Dictionary with blend type information
    """
    if blend_type:
        return {blend_type: BLEND_TYPE_INFO.get(blend_type.lower(), 'Unknown blend type')}
    else:
        return BLEND_TYPE_INFO.copy()

def list_available_blenders() -> list:
    """
    Get a list of all available registered blenders.
    
    Returns:
        List of blender names
    """
    try:
        return BlendRegistry.get_blender_names()
    except (NameError, AttributeError):
        return []

def get_blender_count() -> int:
    """
    Get the total number of registered blenders.
    
    Returns:
        Number of available blenders
    """
    try:
        return len(BlendRegistry.get_all_blenders())
    except (NameError, AttributeError):
        return 0

# Module initialization status check
def is_fully_initialized() -> bool:
    """
    Check if the blending module is fully initialized with all components.
    
    Returns:
        True if all components loaded successfully, False otherwise
    """
    required_components = [
        'GradientBlender', 'BlendRegistry', 'GradientBlendingWidget',
        'WaveformBlender', 'CrystalBlender', 'LayerBlender',
        'ChromaticBlender', 'MemoryBlender'
    ]
    
    for component in required_components:
        if component not in __all__:
            return False
    
    return True

# Print module status on import
if __name__ != "__main__":
    try:
        if is_fully_initialized():
            print(f"✓ Gradient blending fully initialized - {get_blender_count()} blend types available")
        else:
            print("⚠ Gradient blending partially initialized - some features may be unavailable")
    except:
        pass  # Silent fail if status check has issues

# For testing/debugging
if __name__ == "__main__":
    print("Gradient Blending Module Information")
    print("=" * 50)
    print(f"Version: {__version__}")
    print(f"Description: {__description__}")
    print(f"Total exports: {len(__all__)}")
    print(f"Fully initialized: {is_fully_initialized()}")
    
    print("\nAvailable blend types:")
    for blend_type, description in BLEND_TYPE_INFO.items():
        print(f"  • {blend_type.capitalize()}: {description}")
    
    print(f"\nRegistered blenders: {get_blender_count()}")
    available = list_available_blenders()
    if available:
        print("  -", ", ".join(available))
    else:
        print("  - None (BlendRegistry not available)")
    
    print("\nREMOVED BLENDERS:")
    print("  - Harmony Blender (removed)")
    print("  - Procedural Blender (removed)")
    print("  - Gravity Blender (removed)")
    print("  - Fractal Blender (removed)")
    
    print("\nUI IMPROVEMENTS:")
    print("  + Binary parameters now use checkboxes")
    print("  + Sample density uses sliders")
    print("  + Phase shift uses smooth sliders with degree display")
    print("  + Prism angle uses sliders with degree display")
    print("  + Layer blend modes use descriptive Photoshop names")