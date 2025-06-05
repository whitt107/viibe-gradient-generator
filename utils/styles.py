#!/usr/bin/env python3
"""
Refactored Enhanced Dark & Light Theme Style Module for Gradient Generator

Streamlined theme switching with compact UI design and minimal debug output.
Key improvements:
- Reduced button sizes for better space utilization
- Removed excessive debug statements
- Simplified theme application with essential logging only
- Optimized widget refresh mechanism
- Compact UI elements for better visibility
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication, QWidget


def clear_all_styles(app):
    """Clear all existing styles before applying new theme."""
    try:
        app.setStyleSheet("")
        app.setPalette(QPalette())
        app.processEvents()
        return True
    except Exception:
        return False


def force_widget_refresh(app):
    """Force complete refresh of all widgets after theme change."""
    try:
        app.processEvents()
        
        for widget in app.topLevelWidgets():
            if widget.isVisible():
                widget.style().unpolish(widget)
                widget.style().polish(widget)
                widget.update()
                
                for child in widget.findChildren(QWidget):
                    child.style().unpolish(child)
                    child.style().polish(child)
                    child.update()
        
        app.processEvents()
        return True
    except Exception:
        return False


class CompactTheme:
    """Base class for compact theme styling with smaller UI elements."""
    
    # Compact design constants - reduced sizes
    BORDER_RADIUS = 4
    BUTTON_RADIUS = 3
    INPUT_RADIUS = 3
    CARD_RADIUS = 6
    SMALL_RADIUS = 2
    
    # Reduced spacing and sizing for compact UI
    PADDING_TINY = 2
    PADDING_SMALL = 4
    PADDING_MEDIUM = 6
    PADDING_LARGE = 8
    
    # Compact button dimensions - slightly taller
    BUTTON_HEIGHT = 22
    BUTTON_MIN_WIDTH = 60
    
    @staticmethod
    def get_base_stylesheet(colors):
        """Get base stylesheet with compact design and theme colors."""
        c = colors
        return f"""
        QWidget {{
            font-family: "Segoe UI", "Arial", sans-serif;
            font-size: 9pt;
            background-color: {c['primary']};
            color: {c['text_primary']};
        }}
        
        QMainWindow {{
            background-color: {c['primary']};
            color: {c['text_primary']};
        }}
        
        /* Compact buttons with smaller padding */
        QPushButton {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            color: {c['text_primary']};
            padding: {CompactTheme.PADDING_TINY}px {CompactTheme.PADDING_SMALL}px;
            border-radius: {CompactTheme.BUTTON_RADIUS}px;
            font-weight: 500;
            font-size: 9pt;
            min-height: {CompactTheme.BUTTON_HEIGHT}px;
            min-width: {CompactTheme.BUTTON_MIN_WIDTH}px;
            max-height: 28px;
        }}
        
        QPushButton:hover {{
            background-color: {c['hover']};
            border: 1px solid {c['border_focus']};
        }}
        
        QPushButton:pressed {{
            background-color: {c['pressed']};
            padding: {CompactTheme.PADDING_TINY + 1}px {CompactTheme.PADDING_SMALL + 1}px {CompactTheme.PADDING_TINY - 1}px {CompactTheme.PADDING_SMALL - 1}px;
        }}
        
        QPushButton:disabled {{
            background-color: {c['secondary']};
            color: {c['text_disabled']};
            border: 1px dashed {c['text_disabled']};
        }}
        
        /* Compact input fields */
        QLineEdit, QSpinBox, QDoubleSpinBox {{
            background-color: {c['background']};
            border: 1px solid {c['border']};
            color: {c['text_primary']};
            padding: {CompactTheme.PADDING_TINY}px {CompactTheme.PADDING_SMALL}px;
            border-radius: {CompactTheme.INPUT_RADIUS}px;
            min-height: 16px;
            max-height: 20px;
            font-size: 9pt;
            selection-background-color: {c['selection_bg']};
        }}
        
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {c['border_focus']};
            background-color: {c.get('focus_bg', c['surface'])};
        }}
        
        QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {{
            background-color: {c['secondary']};
            color: {c['text_disabled']};
            border: 1px solid {c['text_disabled']};
        }}
        
        /* Compact ComboBox */
        QComboBox {{
            background-color: {c['background']};
            border: 1px solid {c['border']};
            color: {c['text_primary']};
            padding: {CompactTheme.PADDING_TINY}px {CompactTheme.PADDING_SMALL}px;
            border-radius: {CompactTheme.INPUT_RADIUS}px;
            min-height: 16px;
            max-height: 20px;
            font-size: 9pt;
        }}
        
        QComboBox:focus {{
            border: 2px solid {c['border_focus']};
            background-color: {c.get('focus_bg', c['surface'])};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 16px;
            border-radius: {CompactTheme.INPUT_RADIUS}px;
            background-color: {c['surface']};
        }}
        
        QComboBox::drop-down:hover {{
            background-color: {c['hover']};
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {c.get('dropdown_bg', c['secondary'])};
            border: 1px solid {c['border']};
            border-radius: {CompactTheme.INPUT_RADIUS}px;
            padding: {CompactTheme.PADDING_TINY}px;
            color: {c['text_primary']};
            font-size: 9pt;
            selection-background-color: {c['selection_bg']};
        }}
        
        /* Compact group boxes */
        QGroupBox {{
            background-color: {c['primary']};
            border: 1px solid {c['border']};
            border-radius: {CompactTheme.BORDER_RADIUS}px;
            margin-top: 8px;
            padding-top: {CompactTheme.PADDING_MEDIUM}px;
            font-weight: 600;
            font-size: 9pt;
            color: {c['text_primary']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {CompactTheme.PADDING_SMALL}px;
            padding: 0 {CompactTheme.PADDING_TINY}px;
            color: {c['text_secondary']};
            font-size: 9pt;
        }}
        
        /* Compact list widgets */
        QListWidget {{
            background-color: {c['background']};
            border: 1px solid {c['border']};
            border-radius: {CompactTheme.BORDER_RADIUS}px;
            padding: {CompactTheme.PADDING_TINY}px;
            color: {c['text_primary']};
            font-size: 9pt;
        }}
        
        QListWidget::item {{
            border-radius: {CompactTheme.SMALL_RADIUS}px;
            padding: {CompactTheme.PADDING_TINY}px;
            margin: 1px;
            min-height: 16px;
        }}
        
        QListWidget::item:selected {{
            background-color: {c['selection_bg']};
            color: {c['text_primary']};
            border-radius: {CompactTheme.SMALL_RADIUS}px;
        }}
        
        QListWidget::item:hover:!selected {{
            background-color: {c['secondary']};
            border-radius: {CompactTheme.SMALL_RADIUS}px;
        }}
        
        /* Compact menu styling */
        QMenuBar {{
            background-color: {c['primary']};
            color: {c['text_primary']};
            border-bottom: 1px solid {c['border']};
            padding: 1px;
            font-size: 9pt;
        }}
        
        QMenuBar::item {{
            padding: {CompactTheme.PADDING_TINY}px {CompactTheme.PADDING_SMALL}px;
            border-radius: {CompactTheme.SMALL_RADIUS}px;
            margin: 0px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {c['hover']};
        }}
        
        QMenu {{
            background-color: {c.get('dropdown_bg', c['secondary'])};
            border: 1px solid {c['border']};
            border-radius: {CompactTheme.BORDER_RADIUS}px;
            padding: {CompactTheme.PADDING_TINY}px;
            color: {c['text_primary']};
            font-size: 9pt;
        }}
        
        QMenu::item {{
            padding: {CompactTheme.PADDING_TINY}px {CompactTheme.PADDING_MEDIUM}px;
            border-radius: {CompactTheme.SMALL_RADIUS}px;
            margin: 1px;
        }}
        
        QMenu::item:selected {{
            background-color: {c['selection_bg']};
        }}
        
        QMenu::separator {{
            background-color: {c['border']};
            height: 1px;
            margin: {CompactTheme.PADDING_TINY}px {CompactTheme.PADDING_SMALL}px;
            border-radius: 1px;
        }}
        
        /* Compact status bar */
        QStatusBar {{
            background-color: {c['primary']};
            color: {c['text_secondary']};
            border-top: 1px solid {c['border']};
            padding: {CompactTheme.PADDING_TINY}px;
            font-size: 9pt;
        }}
        
        /* Compact checkboxes and radio buttons */
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 12px;
            height: 12px;
            border-radius: {CompactTheme.SMALL_RADIUS}px;
            border: 1px solid {c['border']};
            background-color: {c['background']};
        }}
        
        QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
            background-color: {c['accent']};
            border-color: {c['accent']};
        }}
        
        QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
            border-color: {c['border_focus']};
        }}
        
        QRadioButton::indicator {{
            border-radius: 6px;
        }}
        
        QCheckBox, QRadioButton {{
            color: {c['text_primary']};
            font-size: 9pt;
        }}
        
        /* Compact scroll bars */
        QScrollBar:vertical {{
            background-color: {c['secondary']};
            border: none;
            width: 10px;
            border-radius: 5px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {c['surface']};
            border-radius: 5px;
            min-height: 16px;
            margin: 1px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {c['hover']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {c['secondary']};
            border: none;
            height: 10px;
            border-radius: 5px;
            margin: 0;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {c['surface']};
            border-radius: 5px;
            min-width: 16px;
            margin: 1px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {c['hover']};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        /* Compact sliders */
        QSlider::groove:horizontal {{
            background-color: {c['secondary']};
            height: 6px;
            border-radius: 3px;
            border: 1px solid {c['border']};
        }}
        
        QSlider::handle:horizontal {{
            background-color: {c['accent']};
            width: 14px;
            height: 14px;
            margin: -5px 0;
            border-radius: 7px;
            border: 1px solid {c['accent']};
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: {c['accent_hover']};
            border-color: {c['accent_hover']};
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}
        
        QSlider::groove:vertical {{
            background-color: {c['secondary']};
            width: 6px;
            border-radius: 3px;
            border: 1px solid {c['border']};
        }}
        
        QSlider::handle:vertical {{
            background-color: {c['accent']};
            width: 14px;
            height: 14px;
            margin: 0 -5px;
            border-radius: 7px;
            border: 1px solid {c['accent']};
        }}
        
        /* Compact splitter handles */
        QSplitter::handle {{
            background-color: {c['border']};
            border-radius: 1px;
        }}
        
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        
        QSplitter::handle:vertical {{
            height: 2px;
        }}
        
        QSplitter::handle:hover {{
            background-color: {c['accent']};
        }}
        
        /* Compact tab widgets */
        QTabWidget::pane {{
            background-color: {c['primary']};
            border: 1px solid {c['border']};
            border-radius: {CompactTheme.BORDER_RADIUS}px;
        }}
        
        QTabBar::tab {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            color: {c['text_primary']};
            padding: {CompactTheme.PADDING_SMALL}px {CompactTheme.PADDING_MEDIUM}px;
            margin-right: 1px;
            border-top-left-radius: {CompactTheme.SMALL_RADIUS}px;
            border-top-right-radius: {CompactTheme.SMALL_RADIUS}px;
            font-size: 9pt;
            min-height: 20px;
            min-width: 80px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {c['primary']};
            border-bottom: 1px solid {c['primary']};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {c['hover']};
        }}
        """


class DarkTheme(CompactTheme):
    """Enhanced dark theme with compact UI elements."""
    
    COLORS = {
        'primary': '#2a2a2a',
        'secondary': '#353535', 
        'surface': '#404040',
        'background': '#1e1e1e',
        'text_primary': '#ffffff',
        'text_secondary': '#dddddd',
        'text_disabled': '#888888',
        'accent': '#4a9eff',
        'accent_hover': '#5ba7ff',
        'accent_pressed': '#3d8de6',
        'border': '#555555',
        'border_focus': '#4a9eff',
        'hover': '#4a4a4a',
        'pressed': '#2d2d2d',
        'success': '#4caf50',
        'warning': '#ff9800',
        'error': '#f44336',
        'selection': '#4a9eff',
        'selection_bg': 'rgba(74, 158, 255, 0.3)',
        'focus_bg': '#353535',
        'dropdown_bg': '#404040',
    }
    
    @staticmethod
    def get_palette():
        """Get QPalette with dark theme colors."""
        palette = QPalette()
        c = DarkTheme.COLORS
        
        palette.setColor(QPalette.Window, QColor(c['primary']))
        palette.setColor(QPalette.WindowText, QColor(c['text_primary']))
        palette.setColor(QPalette.Base, QColor(c['background']))
        palette.setColor(QPalette.AlternateBase, QColor(c['secondary']))
        palette.setColor(QPalette.Text, QColor(c['text_primary']))
        palette.setColor(QPalette.Button, QColor(c['surface']))
        palette.setColor(QPalette.ButtonText, QColor(c['text_primary']))
        palette.setColor(QPalette.BrightText, QColor('#ff6b6b'))
        palette.setColor(QPalette.Highlight, QColor(c['selection']))
        palette.setColor(QPalette.HighlightedText, QColor('#ffffff'))
        palette.setColor(QPalette.Link, QColor(c['accent']))
        palette.setColor(QPalette.LinkVisited, QColor('#9c27b0'))
        
        # Disabled states
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(c['text_disabled']))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(c['text_disabled']))
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(c['text_disabled']))
        palette.setColor(QPalette.Disabled, QPalette.Window, QColor(c['secondary']))
        palette.setColor(QPalette.Disabled, QPalette.Base, QColor(c['secondary']))
        
        return palette
    
    @staticmethod
    def get_style_sheet():
        """Get complete dark theme stylesheet."""
        return CompactTheme.get_base_stylesheet(DarkTheme.COLORS)


class LightTheme(CompactTheme):
    """Enhanced light theme with compact UI elements."""
    
    COLORS = {
        'primary': '#ffffff',
        'secondary': '#f5f5f5',
        'surface': '#fafafa',
        'background': '#ffffff',
        'text_primary': '#212121',
        'text_secondary': '#757575',
        'text_disabled': '#bdbdbd',
        'accent': '#2196f3',
        'accent_hover': '#42a5f5',
        'accent_pressed': '#1976d2',
        'border': '#e0e0e0',
        'border_focus': '#2196f3',
        'hover': '#f0f0f0',
        'pressed': '#e8e8e8',
        'success': '#4caf50',
        'warning': '#ff9800',
        'error': '#f44336',
        'selection': '#2196f3',
        'selection_bg': 'rgba(33, 150, 243, 0.2)',
        'focus_bg': '#fafafa',
        'dropdown_bg': '#ffffff',
    }
    
    @staticmethod
    def get_palette():
        """Get QPalette with light theme colors."""
        palette = QPalette()
        c = LightTheme.COLORS
        
        palette.setColor(QPalette.Window, QColor(c['primary']))
        palette.setColor(QPalette.WindowText, QColor(c['text_primary']))
        palette.setColor(QPalette.Base, QColor(c['background']))
        palette.setColor(QPalette.AlternateBase, QColor(c['secondary']))
        palette.setColor(QPalette.Text, QColor(c['text_primary']))
        palette.setColor(QPalette.Button, QColor(c['surface']))
        palette.setColor(QPalette.ButtonText, QColor(c['text_primary']))
        palette.setColor(QPalette.BrightText, QColor('#ff1744'))
        palette.setColor(QPalette.Highlight, QColor(c['selection']))
        palette.setColor(QPalette.HighlightedText, QColor('#ffffff'))
        palette.setColor(QPalette.Link, QColor(c['accent']))
        palette.setColor(QPalette.LinkVisited, QColor('#9c27b0'))
        
        # Disabled states
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(c['text_disabled']))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(c['text_disabled']))
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(c['text_disabled']))
        palette.setColor(QPalette.Disabled, QPalette.Window, QColor(c['secondary']))
        palette.setColor(QPalette.Disabled, QPalette.Base, QColor(c['secondary']))
        
        return palette
    
    @staticmethod
    def get_style_sheet():
        """Get complete light theme stylesheet."""
        return CompactTheme.get_base_stylesheet(LightTheme.COLORS)


# Streamlined theme application functions
def apply_dark_theme(app: QApplication):
    """Apply the compact dark theme to the application."""
    try:
        if not app:
            return False
        
        clear_all_styles(app)
        app.setPalette(DarkTheme.get_palette())
        app.setStyleSheet(DarkTheme.get_style_sheet())
        app.setStyle("Fusion")
        force_widget_refresh(app)
        
        return True
        
    except Exception:
        return False


def apply_light_theme(app: QApplication):
    """Apply the compact light theme to the application."""
    try:
        if not app:
            return False
        
        clear_all_styles(app)
        app.setPalette(LightTheme.get_palette())
        app.setStyleSheet(LightTheme.get_style_sheet())
        app.setStyle("Fusion")
        force_widget_refresh(app)
        
        return True
        
    except Exception:
        return False


def apply_system_theme(app: QApplication):
    """Apply the system default theme."""
    try:
        if not app:
            return False
        
        clear_all_styles(app)
        app.setPalette(app.style().standardPalette())
        app.setStyleSheet("")
        force_widget_refresh(app)
        
        return True
        
    except Exception:
        return False


def apply_widget_dark_theme(widget: QWidget):
    """Apply dark theme to a specific widget."""
    try:
        if not widget:
            return False
        
        widget.setPalette(DarkTheme.get_palette())
        widget.setStyleSheet(DarkTheme.get_style_sheet())
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()
        
        return True
        
    except Exception:
        return False


def apply_widget_light_theme(widget: QWidget):
    """Apply light theme to a specific widget."""
    try:
        if not widget:
            return False
        
        widget.setPalette(LightTheme.get_palette())
        widget.setStyleSheet(LightTheme.get_style_sheet())
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()
        
        return True
        
    except Exception:
        return False


def get_theme_colors(theme_name: str) -> dict:
    """Get color dictionary for a specific theme."""
    if theme_name.lower() == "dark":
        return DarkTheme.COLORS.copy()
    elif theme_name.lower() == "light":
        return LightTheme.COLORS.copy()
    else:
        return {}


def get_available_themes():
    """Get list of available theme names."""
    return ["dark", "light", "system"]


def is_theme_available(theme_name: str) -> bool:
    """Check if a specific theme is available."""
    return theme_name.lower() in get_available_themes()


# Testing function (simplified)
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
    
    def test_compact_themes():
        """Test the compact themes with a sample application."""
        app = QApplication(sys.argv)
        
        # Create test window
        window = QMainWindow()
        window.setWindowTitle("Compact Theme Test")
        window.setGeometry(100, 100, 600, 400)
        
        # Create central widget with test controls
        central = QWidget()
        layout = QVBoxLayout(central)
        
        title = QLabel("Compact Theme Test - Smaller UI Elements")
        title.setStyleSheet("font-size: 12px; font-weight: bold; margin: 5px;")
        layout.addWidget(title)
        
        # Add compact test buttons
        for i, (text, theme_func) in enumerate([
            ("Compact Dark Theme", lambda: apply_dark_theme(app)),
            ("Compact Light Theme", lambda: apply_light_theme(app)),
            ("System Theme", lambda: apply_system_theme(app))
        ]):
            btn = QPushButton(text)
            btn.clicked.connect(theme_func)
            layout.addWidget(btn)
        
        info = QLabel("Compact UI with smaller buttons and reduced spacing for better visibility.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        window.setCentralWidget(central)
        
        # Apply dark theme by default
        apply_dark_theme(app)
        window.show()
        
        return app.exec_()
    
    # Run test if executed directly
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sys.exit(test_compact_themes())
