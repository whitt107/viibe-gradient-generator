#!/usr/bin/env python3
"""
Enhanced Animation Module Package Initialization

This package provides animation functionality for gradient transitions
in the VIIBE Gradient Generator application with full interactive features
including right-click delete and left-click add functionality.
"""

# Import core animation components
from .animated_gradient_preview import AnimatedGradientPreview
from .animated_gradient_drawing import AnimatedGradientDrawingArea
from .startup_integration import initialize_animation

# Export all public classes and functions
__all__ = [
    'AnimatedGradientPreview',
    'AnimatedGradientDrawingArea', 
    'initialize_animation'
]

# Version information
__version__ = "2.0.0"
__author__ = "VIIBE Gradient Generator Team"

# Feature flags
FEATURES = {
    'interactive_stops': True,      # Right-click delete, left-click add
    'context_menus': True,          # Context menu support
    'visual_hints': True,           # Visual hints for adding stops
    'color_interpolation': True,    # Smart color interpolation
    'status_feedback': True,        # Status bar integration
    'animation_effects': True,      # Smooth animations
    'safety_checks': True,          # Prevent invalid operations
    'drag_and_drop': True,          # Drag stops to move
    'color_picker': True,           # Integrated color picker
    'keyboard_shortcuts': True     # Keyboard support
}

# Configuration constants
CONFIG = {
    'MAX_COLOR_STOPS': 64,
    'MIN_COLOR_STOPS': 1,
    'DEFAULT_HITBOX_RADIUS': 10,
    'ANIMATION_FPS': 60,
    'DEBOUNCE_DELAY_MS': 50,
    'DOUBLE_CLICK_THRESHOLD_MS': 300,
    'STATUS_MESSAGE_TIMEOUT_MS': 3000
}

def get_feature_info():
    """
    Get information about available features.
    
    Returns:
        dict: Dictionary of feature flags and their status
    """
    return FEATURES.copy()

def get_config():
    """
    Get configuration constants.
    
    Returns:
        dict: Dictionary of configuration values
    """
    return CONFIG.copy()

def is_feature_enabled(feature_name):
    """
    Check if a specific feature is enabled.
    
    Args:
        feature_name (str): Name of the feature to check
        
    Returns:
        bool: True if feature is enabled, False otherwise
    """
    return FEATURES.get(feature_name, False)

def get_version():
    """
    Get the version of the animation module.
    
    Returns:
        str: Version string
    """
    return __version__

def print_features():
    """Print all available features and their status."""
    print("Enhanced Animation Module Features:")
    print("=" * 40)
    for feature, enabled in FEATURES.items():
        status = "✓ Enabled" if enabled else "✗ Disabled"
        print(f"{feature:20} : {status}")
    print("=" * 40)

# Initialization message with feature summary
def _print_init_message():
    """Print initialization message with feature summary."""
    enabled_features = [name for name, enabled in FEATURES.items() if enabled]
    feature_count = len(enabled_features)
    
    print(f"Enhanced Animation Module v{__version__} initialized")
    print(f"✓ {feature_count} interactive features enabled")
    
    # Print key features
    key_features = [
        'interactive_stops', 'context_menus', 'visual_hints', 
        'color_interpolation', 'animation_effects'
    ]
    
    active_key_features = [f for f in key_features if FEATURES.get(f, False)]
    if active_key_features:
        print(f"🎯 Key features: {', '.join(active_key_features)}")
    
    print("🎨 Ready for interactive gradient editing!")

# Auto-initialization check
try:
    # Only print initialization message if we're in a proper application context
    from PyQt5.QtWidgets import QApplication
    if QApplication.instance():
        _print_init_message()
    else:
        # Delay message until QApplication is available
        def delayed_message():
            if QApplication.instance():
                _print_init_message()
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, delayed_message)
        
except ImportError:
    # PyQt5 not available, just print basic message
    print(f"Enhanced Animation Module v{__version__} loaded")

# Module-level convenience functions
def create_animated_preview(gradient_model, **kwargs):
    """
    Convenience function to create an AnimatedGradientPreview.
    
    Args:
        gradient_model: The gradient model to preview
        **kwargs: Additional arguments passed to AnimatedGradientPreview
        
    Returns:
        AnimatedGradientPreview: Configured preview widget
    """
    preview = AnimatedGradientPreview(gradient_model)
    
    # Apply any configuration from kwargs
    for key, value in kwargs.items():
        if hasattr(preview, key):
            setattr(preview, key, value)
    
    return preview

def create_drawing_area(gradient_model, **kwargs):
    """
    Convenience function to create an AnimatedGradientDrawingArea.
    
    Args:
        gradient_model: The gradient model to draw
        **kwargs: Additional arguments for configuration
        
    Returns:
        AnimatedGradientDrawingArea: Configured drawing area widget
    """
    drawing_area = AnimatedGradientDrawingArea(gradient_model)
    
    # Apply any configuration from kwargs
    for key, value in kwargs.items():
        if hasattr(drawing_area, key):
            setattr(drawing_area, key, value)
    
    return drawing_area

def initialize_enhanced_animation():
    """
    Initialize the enhanced animation system with full features.
    
    This is an alias for initialize_animation() with additional
    feature verification.
    
    Returns:
        bool: True if initialization successful
    """
    try:
        success = initialize_animation()
        
        if success:
            print("✓ Enhanced animation system initialized successfully")
            print("✓ Interactive gradient editing is now available")
            
            # Verify key features are available
            if is_feature_enabled('interactive_stops'):
                print("✓ Right-click delete and left-click add features ready")
            
            if is_feature_enabled('context_menus'):
                print("✓ Context menu support enabled")
            
            if is_feature_enabled('visual_hints'):
                print("✓ Visual hints and feedback enabled")
        
        return success
        
    except Exception as e:
        print(f"✗ Enhanced animation initialization failed: {e}")
        return False

# Error handling for import issues
def safe_import_check():
    """
    Check if all required modules can be imported safely.
    
    Returns:
        tuple: (success: bool, missing_modules: list)
    """
    missing_modules = []
    
    try:
        from PyQt5.QtWidgets import QWidget, QMenu, QColorDialog
    except ImportError as e:
        missing_modules.append(f"PyQt5.QtWidgets: {e}")
    
    try:
        from PyQt5.QtCore import Qt, pyqtSignal, QTimer
    except ImportError as e:
        missing_modules.append(f"PyQt5.QtCore: {e}")
    
    try:
        from PyQt5.QtGui import QPainter, QColor, QCursor
    except ImportError as e:
        missing_modules.append(f"PyQt5.QtGui: {e}")
    
    success = len(missing_modules) == 0
    return success, missing_modules

# Perform import check on module load
_import_success, _missing_modules = safe_import_check()

if not _import_success:
    print("⚠️  Warning: Some required modules are missing:")
    for module in _missing_modules:
        print(f"   - {module}")
    print("   Enhanced animation features may not work properly.")

# Export additional utilities
__all__.extend([
    'get_feature_info',
    'get_config', 
    'is_feature_enabled',
    'get_version',
    'print_features',
    'create_animated_preview',
    'create_drawing_area',
    'initialize_enhanced_animation',
    'safe_import_check',
    'FEATURES',
    'CONFIG'
])

# Module documentation
__doc__ += """

Enhanced Features:
- Right-click color stops to delete or edit
- Left-click gradient area to add new stops  
- Visual hints showing where stops can be added
- Context menus for quick operations
- Smart color interpolation for new stops
- Status bar integration for user feedback
- Safety checks preventing invalid operations
- Smooth animations and transitions
- Full integration with existing gradient editor

Usage:
    from gradient_generator.ui.animation import AnimatedGradientPreview
    
    # Create enhanced preview
    preview = AnimatedGradientPreview(gradient_model)
    
    # Connect signals for interaction feedback
    preview.stop_added.connect(handle_stop_added)
    preview.stop_deleted.connect(handle_stop_deleted)
    
    # Initialize the enhanced system
    from gradient_generator.ui.animation import initialize_enhanced_animation
    initialize_enhanced_animation()

For more information, see the individual module documentation.
"""