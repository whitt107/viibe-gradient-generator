#!/usr/bin/env python3
"""
Complete Distribution Package for VIIBE Gradient Generator

This package provides unified mathematical and color-based distribution functionality
with shared real-time preview system for distributing gradient color stops.
"""

# Core system imports with comprehensive error handling
print("Loading VIIBE Distribution System...")

# Import shared preview system
try:
    from .shared_distribution_preview import (
        create_distribution_preview_system, SharedGradientPreviewWidget, 
        PreviewController, GradientPreviewLabel
    )
    SHARED_PREVIEW_AVAILABLE = True
    print("✓ Shared preview system loaded")
except ImportError as e:
    print(f"⚠ Shared preview system not available: {e}")
    SHARED_PREVIEW_AVAILABLE = False
    
    # Create fallback functions
    def create_distribution_preview_system(gradient_model):
        from PyQt5.QtWidgets import QLabel
        return QLabel("Preview not available"), None
    
    SharedGradientPreviewWidget = None
    PreviewController = None
    GradientPreviewLabel = None

# Import mathematical distributions
try:
    from .base_distributions import DISTRIBUTIONS, ColorStopDistribution
    from .distribution_widget import ColorStopDistributionWidget
    MATH_DISTRIBUTIONS_AVAILABLE = True
    print(f"✓ Mathematical distributions loaded ({len(DISTRIBUTIONS)} algorithms)")
except ImportError as e:
    print(f"⚠ Mathematical distributions not available: {e}")
    MATH_DISTRIBUTIONS_AVAILABLE = False
    DISTRIBUTIONS = {}
    ColorStopDistribution = None
    ColorStopDistributionWidget = None

# Import color distributions
try:
    from .color_distribution_base import (
        get_distribution, get_available_distributions, 
        create_distance_distribution, DISTRIBUTION_REGISTRY
    )
    from .color_distribution_widget import ColorDistributionWidget
    COLOR_DISTRIBUTIONS_AVAILABLE = True
    print(f"✓ Color distributions loaded ({len(DISTRIBUTION_REGISTRY)} algorithms)")
except ImportError as e:
    print(f"⚠ Color distributions not available: {e}")
    COLOR_DISTRIBUTIONS_AVAILABLE = False
    
    # Create fallbacks
    def get_distribution(name): return None
    def get_available_distributions(): return []
    def create_distance_distribution(color): return None
    DISTRIBUTION_REGISTRY = {}
    ColorDistributionWidget = None

# Import unified integration system
try:
    from .unified_distribution_integration import (
        integrate_unified_distribution, create_unified_distribution_widget,
        find_application_components
    )
    UNIFIED_INTEGRATION_AVAILABLE = True
    print("✓ Unified integration system loaded")
except ImportError as e:
    print(f"⚠ Unified integration not available: {e}")
    UNIFIED_INTEGRATION_AVAILABLE = False
    
    # Create fallbacks
    def integrate_unified_distribution(): return False
    def create_unified_distribution_widget(gradient_model): return None
    def find_application_components(): return None, None, None

# Import auto-integration module
try:
    from .distribution_integration_module import (
        ensure_distribution_integration, check_integration_status,
        manual_integrate
    )
    AUTO_INTEGRATION_AVAILABLE = True
    print("✓ Auto-integration system loaded")
except ImportError as e:
    print(f"⚠ Auto-integration not available: {e}")
    AUTO_INTEGRATION_AVAILABLE = False
    
    # Create fallbacks
    def ensure_distribution_integration(): return False
    def check_integration_status(): return {'attempted': False, 'successful': False}
    def manual_integrate(): return False

# Package metadata
__version__ = "2.0.0"
__author__ = "VIIBE Gradient Generator Team"
__description__ = "Unified distribution system with shared real-time preview"

# Main exports
__all__ = [
    # Shared preview system
    'create_distribution_preview_system',
    'SharedGradientPreviewWidget',
    'PreviewController',
    'GradientPreviewLabel',
    
    # Mathematical distributions
    'DISTRIBUTIONS',
    'ColorStopDistribution', 
    'ColorStopDistributionWidget',
    
    # Color distributions
    'get_distribution',
    'get_available_distributions',
    'create_distance_distribution',
    'DISTRIBUTION_REGISTRY',
    'ColorDistributionWidget',
    
    # Integration system
    'integrate_unified_distribution',
    'create_unified_distribution_widget',
    'ensure_distribution_integration',
    'check_integration_status',
    'manual_integrate',
    
    # Status flags
    'SHARED_PREVIEW_AVAILABLE',
    'MATH_DISTRIBUTIONS_AVAILABLE', 
    'COLOR_DISTRIBUTIONS_AVAILABLE',
    'UNIFIED_INTEGRATION_AVAILABLE',
    'AUTO_INTEGRATION_AVAILABLE',
]

# Capability flags
CAPABILITIES = {
    'shared_preview': SHARED_PREVIEW_AVAILABLE,
    'math_distributions': MATH_DISTRIBUTIONS_AVAILABLE,
    'color_distributions': COLOR_DISTRIBUTIONS_AVAILABLE,
    'unified_integration': UNIFIED_INTEGRATION_AVAILABLE,
    'auto_integration': AUTO_INTEGRATION_AVAILABLE,
}

def get_capabilities():
    """Get the current system capabilities."""
    return CAPABILITIES.copy()

def get_system_status():
    """Get comprehensive system status."""
    status = {
        'version': __version__,
        'capabilities': get_capabilities(),
        'math_algorithms': len(DISTRIBUTIONS) if MATH_DISTRIBUTIONS_AVAILABLE else 0,
        'color_algorithms': len(DISTRIBUTION_REGISTRY) if COLOR_DISTRIBUTIONS_AVAILABLE else 0,
    }
    
    if AUTO_INTEGRATION_AVAILABLE:
        status.update(check_integration_status())
    
    return status

def is_fully_functional():
    """Check if all core systems are available."""
    return all([
        SHARED_PREVIEW_AVAILABLE,
        MATH_DISTRIBUTIONS_AVAILABLE,
        COLOR_DISTRIBUTIONS_AVAILABLE,
        UNIFIED_INTEGRATION_AVAILABLE
    ])

def quick_integrate():
    """Quick integration function for easy setup."""
    if not UNIFIED_INTEGRATION_AVAILABLE:
        print("✗ Unified integration not available")
        return False
    
    try:
        success = integrate_unified_distribution()
        if success:
            print("✓ Distribution system integrated successfully!")
        else:
            print("✗ Distribution system integration failed")
        return success
    except Exception as e:
        print(f"Integration error: {e}")
        return False

def create_standalone_preview(gradient_model):
    """Create a standalone preview widget for testing."""
    if not SHARED_PREVIEW_AVAILABLE:
        from PyQt5.QtWidgets import QLabel
        return QLabel("Preview system not available")
    
    preview_widget, controller = create_distribution_preview_system(gradient_model)
    return preview_widget

def list_available_algorithms():
    """List all available distribution algorithms."""
    algorithms = {}
    
    if MATH_DISTRIBUTIONS_AVAILABLE:
        algorithms['mathematical'] = [
            (key, dist.name, dist.description) 
            for key, dist in DISTRIBUTIONS.items()
        ]
    
    if COLOR_DISTRIBUTIONS_AVAILABLE:
        algorithms['color_based'] = get_available_distributions()
    
    return algorithms

# Performance monitoring
_performance_stats = {
    'module_load_time': 0,
    'integration_attempts': 0,
    'successful_integrations': 0
}

def get_performance_stats():
    """Get performance statistics."""
    return _performance_stats.copy()

# Auto-integration trigger
def _trigger_auto_integration():
    """Trigger auto-integration if all systems are available."""
    if not is_fully_functional():
        missing = [name for name, available in CAPABILITIES.items() if not available]
        print(f"⚠ Auto-integration skipped - missing: {', '.join(missing)}")
        return
    
    if AUTO_INTEGRATION_AVAILABLE:
        try:
            _performance_stats['integration_attempts'] += 1
            success = ensure_distribution_integration()
            if success:
                _performance_stats['successful_integrations'] += 1
                print("✓ Auto-integration completed successfully")
            else:
                print("⚠ Auto-integration attempted but failed")
        except Exception as e:
            print(f"Auto-integration error: {e}")

# Module initialization
def _initialize_module():
    """Initialize the distribution module."""
    import time
    start_time = time.time()
    
    # Check system readiness
    total_systems = len(CAPABILITIES)
    available_systems = sum(1 for available in CAPABILITIES.values() if available)
    
    print(f"Distribution system ready: {available_systems}/{total_systems} components loaded")
    
    if is_fully_functional():
        print("🎉 All distribution systems operational")
        _trigger_auto_integration()
    else:
        print("⚠ Some distribution components missing - limited functionality")
    
    _performance_stats['module_load_time'] = time.time() - start_time
    print(f"Module loaded in {_performance_stats['module_load_time']:.3f}s")

# Initialize when imported (unless running as main)
if __name__ != '__main__':
    _initialize_module()


# Test and diagnostic mode
if __name__ == "__main__":
    print("VIIBE Distribution System - Diagnostic Mode")
    print("=" * 50)
    
    # Show system status
    status = get_system_status()
    print(f"Version: {status['version']}")
    print(f"Fully functional: {is_fully_functional()}")
    
    print("\nComponent Status:")
    for component, available in status['capabilities'].items():
        print(f"  {component}: {'✓' if available else '✗'}")
    
    print(f"\nAlgorithms Available:")
    print(f"  Mathematical: {status['math_algorithms']}")
    print(f"  Color-based: {status['color_algorithms']}")
    
    # List algorithms
    algorithms = list_available_algorithms()
    
    if 'mathematical' in algorithms:
        print(f"\nMathematical Distributions:")
        for key, name, desc in algorithms['mathematical']:
            print(f"  {name}: {desc}")
    
    if 'color_based' in algorithms:
        print(f"\nColor-Based Distributions:")
        for key, name, desc in algorithms['color_based']:
            print(f"  {name}: {desc}")
    
    # Performance stats
    perf = get_performance_stats()
    print(f"\nPerformance:")
    print(f"  Load time: {perf['module_load_time']:.3f}s")
    print(f"  Integration attempts: {perf['integration_attempts']}")
    print(f"  Successful integrations: {perf['successful_integrations']}")
    
    # Test integration if available
    if is_fully_functional():
        print(f"\n🧪 Testing integration...")
        result = quick_integrate()
        print(f"Integration test: {'PASS' if result else 'FAIL'}")
    
    print("\nDiagnostic complete!")
