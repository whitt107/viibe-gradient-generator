"""
UI Module for Gradient Generator

This module contains the user interface components for the gradient generator.
"""

# Core widgets
from .main_window import MainWindow
from .gradient_preview import GradientPreviewWidget
from .image_to_gradient import ImageToGradientDialog
from .gradient_list import GradientListPanel
from .random_gradient_dialog import RandomGradientDialog
from .gradient_merge import GradientMergeWidget

# Control widgets  
from .controls import ControlPanel, ColorStopsEditor, GradientAdjustmentsWidget

# Additional dialogs
from .batch_operations import BatchOperationsDialog

# Optional imports - these may not be present in all installations
try:
    from .gradient_comparison import GradientComparisonDialog
except ImportError:
    GradientComparisonDialog = None

try:
    from .gradient_comparison import GradientComparisonDialog
except ImportError:
    class GradientComparisonDialog:
        def __init__(self, *args, **kwargs):
            raise ImportError("Gradient comparison not available")    

__all__ = [
    'MainWindow',
    'GradientPreviewWidget',
    'ImageToGradientDialog',
    'GradientListPanel',
    'RandomGradientDialog',
    'GradientMergeWidget',
    'ControlPanel', 
    'ColorStopsEditor',
    'GradientAdjustmentsWidget',
    'BatchOperationsDialog',
    'GradientComparisonDialog'
]