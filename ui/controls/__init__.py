"""
Controls Module for Gradient Generator UI

This module provides all the control widgets for the gradient generator,
organized into separate files for maintainability.
"""

# Import all widgets to maintain the same import path for other modules
from .color_stops import ColorStopWidget, ColorStopsEditor
from .export_options import ExportOptionsWidget
from .seamless import SeamlessBlendingWidget
from .gradient_adjustments import GradientAdjustmentsWidget
from .control_panel import ControlPanel

# Make all widgets available at the module level
__all__ = [
    'ColorStopWidget',
    'ColorStopsEditor',
    'ExportOptionsWidget',  # This now points to EnhancedExportOptionsWidget
    'SeamlessBlendingWidget',
    'GradientAdjustmentsWidget',
    'ControlPanel'
]
