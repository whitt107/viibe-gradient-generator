#!/usr/bin/env python3
"""
FIXED Menu Manager Module for Gradient Generator

This module handles the creation and management of the application menu bar,
including PROPERLY WORKING theme switching functionality with complete UI refresh.

Key fixes:
- Complete theme application with proper cleanup
- Forced UI refresh for immediate visual updates
- Comprehensive fallback themes
- Proper action state synchronization
- Better error handling and logging
"""
from PyQt5.QtWidgets import QAction, QMessageBox, QActionGroup, QApplication, QWidget
from PyQt5.QtCore import Qt


class MenuManager:
    """Manages the application menu bar and its actions with FIXED theme switching."""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.dark_theme_enabled = True  # Track current theme state
        self.theme_actions = {}  # Store theme actions for easy access
    
    def create_menu_bar(self):
        """Create the menu bar with actions."""
        # File menu
        self._create_file_menu()
        
        # Edit menu
        self._create_edit_menu()
        
        # View menu
        self._create_view_menu()
        
        # Tools menu
        self._create_tools_menu()
        
        # Help menu
        self._create_help_menu()
    
    def _create_file_menu(self):
        """Create and populate the File menu."""
        file_menu = self.main_window.menuBar().addMenu("&File")
        
        # New gradient action
        self._add_action(file_menu, "&New Gradient", "Ctrl+N", 
                        self.main_window.gradient_operations.new_gradient)
        
        # Create from image action
        self._add_action(file_menu, "Create from &Image...", "Ctrl+I", 
                        self.main_window.gradient_operations.create_from_image)
        
        # Random gradient action
        self._add_action(file_menu, "Create &Random Gradient...", "Ctrl+R", 
                        self.main_window.gradient_operations.create_random_gradient)
        
        file_menu.addSeparator()
        
        # Save actions
        self._add_action(file_menu, "Save as &MAP", "Ctrl+S", 
                        self.main_window.file_operations.save_map)
        self._add_action(file_menu, "Save as &UGR", "Ctrl+U", 
                        self.main_window.file_operations.save_ugr)
        self._add_action(file_menu, "Export &Image", "Ctrl+E", 
                        self.main_window.file_operations.export_image)
        
        file_menu.addSeparator()
        
        # Session management
        self._add_action(file_menu, "Save Session...", "Ctrl+Shift+S", 
                        self.main_window.session_manager.save_session)
        self._add_action(file_menu, "Load Session...", "Ctrl+Shift+O", 
                        self.main_window.session_manager.load_session)
        
        file_menu.addSeparator()
        
        # Exit action
        self._add_action(file_menu, "E&xit", "Ctrl+Q", self.main_window.close)
        
        return file_menu
    
    def _create_edit_menu(self):
        """Create and populate the Edit menu."""
        edit_menu = self.main_window.menuBar().addMenu("&Edit")
        
        # Copy/Paste actions
        self._add_action(edit_menu, "&Copy Gradient", "Ctrl+C", 
                        self.main_window.clipboard_manager.copy_gradient)
        self._add_action(edit_menu, "&Paste Gradient", "Ctrl+V", 
                        self.main_window.clipboard_manager.paste_gradient)
        
        edit_menu.addSeparator()
        
        # Gradient operations
        self._add_action(edit_menu, "&Add to List", "Ctrl+L", 
                        self.main_window.gradient_operations.add_to_gradient_list)
        self._add_action(edit_menu, "&Batch Generate...", "Ctrl+B", 
                        self.main_window.gradient_operations.create_batch_gradients)
        
        return edit_menu
    
    def _create_view_menu(self):
        """Create and populate the View menu."""
        view_menu = self.main_window.menuBar().addMenu("&View")
        
        # Toggle gradient list action
        self._add_action(view_menu, "&Toggle Gradient List", "Ctrl+T", self._toggle_gradient_list)
        
        view_menu.addSeparator()
        
        # Theme selection submenu
        theme_menu = view_menu.addMenu("&Theme")
        
        # Create action group for mutually exclusive theme selection
        self.theme_action_group = QActionGroup(self.main_window)
        self.theme_action_group.setExclusive(True)
        
        # Dark theme action (checked by default)
        self.theme_actions['dark'] = QAction("&Dark Theme", self.main_window)
        self.theme_actions['dark'].setCheckable(True)
        self.theme_actions['dark'].setChecked(True)
        self.theme_actions['dark'].triggered.connect(lambda: self._set_theme("dark"))
        self.theme_action_group.addAction(self.theme_actions['dark'])
        theme_menu.addAction(self.theme_actions['dark'])
        
        # Light theme action
        self.theme_actions['light'] = QAction("&Light Theme", self.main_window)
        self.theme_actions['light'].setCheckable(True)
        self.theme_actions['light'].setChecked(False)
        self.theme_actions['light'].triggered.connect(lambda: self._set_theme("light"))
        self.theme_action_group.addAction(self.theme_actions['light'])
        theme_menu.addAction(self.theme_actions['light'])
        
        # System theme action
        self.theme_actions['system'] = QAction("&System Theme", self.main_window)
        self.theme_actions['system'].setCheckable(True)
        self.theme_actions['system'].setChecked(False)
        self.theme_actions['system'].triggered.connect(lambda: self._set_theme("system"))
        self.theme_action_group.addAction(self.theme_actions['system'])
        theme_menu.addAction(self.theme_actions['system'])
        
        return view_menu
    
    def _create_tools_menu(self):
        """Create and populate the Tools menu."""
        tools_menu = self.main_window.menuBar().addMenu("&Tools")
        
        # Reset application action
        self._add_action(tools_menu, "&Reset All Settings", None, self._reset_application)
        
        tools_menu.addSeparator()
        
        # Preferences/Settings action
        self._add_action(tools_menu, "&Preferences...", "Ctrl+,", self._show_preferences)
        
        return tools_menu
    
    def _create_help_menu(self):
        """Create and populate the Help menu."""
        help_menu = self.main_window.menuBar().addMenu("&Help")
        
        # About action
        self._add_action(help_menu, "&About", None, self._show_about)
        
        return help_menu
    
    def _add_action(self, menu, text, shortcut, slot):
        """Helper method to add an action to a menu."""
        action = QAction(text, self.main_window)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(slot)
        menu.addAction(action)
        return action
    
    def _toggle_gradient_list(self):
        """Toggle visibility of the gradient list panel."""
        if self.main_window.gradient_list_panel.isVisible():
            self.main_window.gradient_list_panel.hide()
        else:
            self.main_window.gradient_list_panel.show()
    
    def _set_theme(self, theme_name):
        """Set the application theme with complete refresh - FIXED VERSION."""
        try:
            print(f"Switching to theme: {theme_name}")
            
            # Get QApplication instance
            app = QApplication.instance()
            if not app:
                print("Error: No QApplication instance found")
                return
            
            # Store current theme for rollback if needed
            current_theme = self.main_window.settings.value("theme", "dark")
            
            # Apply the theme
            success = self._apply_theme_complete(app, theme_name)
            
            if success:
                # Update internal state
                self.dark_theme_enabled = (theme_name == "dark")
                
                # Save theme preference
                self.main_window.settings.setValue("theme", theme_name)
                
                # Update menu action states
                self._update_theme_actions(theme_name)
                
                # Force complete UI refresh
                self._force_ui_refresh(app)
                
                # Show status message
                self.main_window.statusBar().showMessage(f"{theme_name.capitalize()} theme applied", 3000)
                
                print(f"✓ Successfully applied {theme_name} theme")
            else:
                # Rollback on failure
                print(f"✗ Failed to apply {theme_name} theme, rolling back to {current_theme}")
                self._update_theme_actions(current_theme)
                self._show_theme_error(f"Failed to apply {theme_name} theme")
                
        except Exception as e:
            print(f"Error in _set_theme: {e}")
            self._show_theme_error(f"Error applying {theme_name} theme: {str(e)}")
    
    def _apply_theme_complete(self, app, theme_name):
        """Apply theme with complete widget refresh - FIXED VERSION."""
        try:
            # Clear any existing stylesheets first
            app.setStyleSheet("")
            
            if theme_name == "dark":
                success = self._apply_dark_theme_complete(app)
            elif theme_name == "light":
                success = self._apply_light_theme_complete(app)
            elif theme_name == "system":
                success = self._apply_system_theme_complete(app)
            else:
                print(f"Unknown theme: {theme_name}")
                return False
            
            if success:
                # Process all pending events to ensure immediate application
                app.processEvents()
                
            return success
            
        except Exception as e:
            print(f"Theme application error: {e}")
            return False
    
    def _apply_dark_theme_complete(self, app):
        """Apply dark theme with complete refresh - FIXED VERSION."""
        try:
            # Try to import and use the enhanced theme utilities
            try:
                from gradient_generator.utils.styles import apply_dark_theme
                return apply_dark_theme(app)
            except ImportError:
                try:
                    from utils.styles import apply_dark_theme
                    return apply_dark_theme(app)
                except ImportError:
                    # Use fallback implementation
                    return self._apply_fallback_dark_theme(app)
                    
        except Exception as e:
            print(f"Dark theme application failed: {e}")
            return self._apply_fallback_dark_theme(app)
    
    def _apply_light_theme_complete(self, app):
        """Apply light theme with complete refresh - FIXED VERSION."""
        try:
            # Try to import and use the enhanced theme utilities
            try:
                from gradient_generator.utils.styles import apply_light_theme
                return apply_light_theme(app)
            except ImportError:
                try:
                    from utils.styles import apply_light_theme
                    return apply_light_theme(app)
                except ImportError:
                    # Use fallback implementation
                    return self._apply_fallback_light_theme(app)
                    
        except Exception as e:
            print(f"Light theme application failed: {e}")
            return self._apply_fallback_light_theme(app)
    
    def _apply_system_theme_complete(self, app):
        """Apply system theme with complete refresh - FIXED VERSION."""
        try:
            from PyQt5.QtGui import QPalette
            
            # Reset to system defaults
            app.setPalette(app.style().standardPalette())
            app.setStyleSheet("")
            
            # Process events to ensure application
            app.processEvents()
            
            return True
            
        except Exception as e:
            print(f"System theme application failed: {e}")
            return False
    
    def _apply_fallback_dark_theme(self, app):
        """Fallback dark theme implementation - COMPREHENSIVE VERSION."""
        try:
            from PyQt5.QtGui import QPalette, QColor
            
            # Create comprehensive dark palette
            palette = QPalette()
            
            # Base colors
            dark_bg = QColor(42, 42, 42)
            darker_bg = QColor(25, 25, 25)
            light_text = QColor(221, 221, 221)
            disabled_text = QColor(120, 120, 120)
            button_bg = QColor(68, 68, 68)
            hover_bg = QColor(85, 85, 85)
            selection_bg = QColor(42, 130, 218)
            
            # Set all palette colors
            palette.setColor(QPalette.Window, dark_bg)
            palette.setColor(QPalette.WindowText, light_text)
            palette.setColor(QPalette.Base, darker_bg)
            palette.setColor(QPalette.AlternateBase, dark_bg)
            palette.setColor(QPalette.ToolTipBase, light_text)
            palette.setColor(QPalette.ToolTipText, light_text)
            palette.setColor(QPalette.Text, light_text)
            palette.setColor(QPalette.Button, button_bg)
            palette.setColor(QPalette.ButtonText, light_text)
            palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
            palette.setColor(QPalette.Link, selection_bg)
            palette.setColor(QPalette.Highlight, selection_bg)
            palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
            
            # Disabled states
            palette.setColor(QPalette.Disabled, QPalette.WindowText, disabled_text)
            palette.setColor(QPalette.Disabled, QPalette.Text, disabled_text)
            palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_text)
            
            # Apply palette and style
            app.setPalette(palette)
            app.setStyle("Fusion")
            
            # Apply comprehensive dark stylesheet
            dark_stylesheet = self._get_comprehensive_dark_stylesheet()
            app.setStyleSheet(dark_stylesheet)
            
            print("Applied fallback dark theme")
            return True
            
        except Exception as e:
            print(f"Fallback dark theme failed: {e}")
            return False
    
    def _apply_fallback_light_theme(self, app):
        """Fallback light theme implementation - COMPREHENSIVE VERSION."""
        try:
            from PyQt5.QtGui import QPalette, QColor
            
            # Create comprehensive light palette
            palette = QPalette()
            
            # Base colors
            light_bg = QColor(240, 240, 240)
            white_bg = QColor(255, 255, 255)
            dark_text = QColor(0, 0, 0)
            disabled_text = QColor(120, 120, 120)
            button_bg = QColor(225, 225, 225)
            selection_bg = QColor(0, 120, 215)
            
            # Set all palette colors
            palette.setColor(QPalette.Window, light_bg)
            palette.setColor(QPalette.WindowText, dark_text)
            palette.setColor(QPalette.Base, white_bg)
            palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
            palette.setColor(QPalette.ToolTipBase, white_bg)
            palette.setColor(QPalette.ToolTipText, dark_text)
            palette.setColor(QPalette.Text, dark_text)
            palette.setColor(QPalette.Button, button_bg)
            palette.setColor(QPalette.ButtonText, dark_text)
            palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
            palette.setColor(QPalette.Link, selection_bg)
            palette.setColor(QPalette.Highlight, selection_bg)
            palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
            
            # Disabled states
            palette.setColor(QPalette.Disabled, QPalette.WindowText, disabled_text)
            palette.setColor(QPalette.Disabled, QPalette.Text, disabled_text)
            palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_text)
            
            # Apply palette and style
            app.setPalette(palette)
            app.setStyle("Fusion")
            
            # Apply comprehensive light stylesheet
            light_stylesheet = self._get_comprehensive_light_stylesheet()
            app.setStyleSheet(light_stylesheet)
            
            print("Applied fallback light theme")
            return True
            
        except Exception as e:
            print(f"Fallback light theme failed: {e}")
            return False
    
    def _get_comprehensive_dark_stylesheet(self):
        """Get comprehensive dark theme stylesheet."""
        return """
        QWidget {
            background-color: #2a2a2a;
            color: #dddddd;
            font-family: "Segoe UI", Arial, sans-serif;
        }
        
        QMainWindow {
            background-color: #2a2a2a;
        }
        
        QPushButton {
            background-color: #444444;
            border: 1px solid #555555;
            color: #dddddd;
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: 500;
        }
        
        QPushButton:hover {
            background-color: #555555;
            border: 1px solid #666666;
        }
        
        QPushButton:pressed {
            background-color: #333333;
        }
        
        QPushButton:disabled {
            background-color: #2a2a2a;
            color: #787878;
            border: 1px solid #444444;
        }
        
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #1e1e1e;
            border: 1px solid #555555;
            color: #dddddd;
            padding: 4px 8px;
            border-radius: 3px;
        }
        
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
            border: 2px solid #4a9eff;
            background-color: #333333;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid #dddddd;
            margin: 0 4px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #404040;
            border: 1px solid #555555;
            color: #dddddd;
            selection-background-color: #4a9eff;
        }
        
        QGroupBox {
            background-color: #2a2a2a;
            border: 1px solid #555555;
            border-radius: 6px;
            margin-top: 1ex;
            padding-top: 10px;
            font-weight: bold;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #dddddd;
        }
        
        QTabWidget::pane {
            background-color: #2a2a2a;
            border: 1px solid #555555;
            border-radius: 4px;
        }
        
        QTabBar::tab {
            background-color: #404040;
            border: 1px solid #555555;
            color: #dddddd;
            padding: 6px 12px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: #2a2a2a;
            border-bottom: 1px solid #2a2a2a;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #555555;
        }
        
        QListWidget {
            background-color: #1e1e1e;
            border: 1px solid #555555;
            border-radius: 4px;
            color: #dddddd;
        }
        
        QListWidget::item {
            padding: 4px;
            border-bottom: 1px solid #444444;
        }
        
        QListWidget::item:selected {
            background-color: #4a9eff;
            color: white;
        }
        
        QListWidget::item:hover:!selected {
            background-color: #404040;
        }
        
        QScrollBar:vertical {
            background-color: #2a2a2a;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #555555;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #666666;
        }
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            background-color: #2a2a2a;
            height: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #555555;
            border-radius: 6px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #666666;
        }
        
        QMenuBar {
            background-color: #2a2a2a;
            color: #dddddd;
            border-bottom: 1px solid #555555;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
        }
        
        QMenuBar::item:selected {
            background-color: #555555;
            border-radius: 3px;
        }
        
        QMenu {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 4px;
            color: #dddddd;
        }
        
        QMenu::item {
            padding: 6px 12px;
        }
        
        QMenu::item:selected {
            background-color: #4a9eff;
            color: white;
        }
        
        QMenu::separator {
            background-color: #555555;
            height: 1px;
            margin: 4px 8px;
        }
        
        QStatusBar {
            background-color: #2a2a2a;
            color: #bbbbbb;
            border-top: 1px solid #555555;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #555555;
            background-color: #1e1e1e;
            border-radius: 3px;
        }
        
        QCheckBox::indicator:checked {
            background-color: #4a9eff;
            border-color: #4a9eff;
        }
        
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #555555;
            background-color: #1e1e1e;
            border-radius: 8px;
        }
        
        QRadioButton::indicator:checked {
            background-color: #4a9eff;
            border-color: #4a9eff;
        }
        
        QSlider::groove:horizontal {
            background-color: #555555;
            height: 8px;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background-color: #4a9eff;
            width: 18px;
            height: 18px;
            margin: -5px 0;
            border-radius: 9px;
            border: 1px solid #4a9eff;
        }
        
        QSlider::handle:horizontal:hover {
            background-color: #5ba7ff;
        }
        
        QSplitter::handle {
            background-color: #555555;
        }
        
        QSplitter::handle:horizontal {
            width: 3px;
        }
        
        QSplitter::handle:vertical {
            height: 3px;
        }
        
        QSplitter::handle:hover {
            background-color: #4a9eff;
        }
        """
    
    def _get_comprehensive_light_stylesheet(self):
        """Get comprehensive light theme stylesheet."""
        return """
        QWidget {
            background-color: #f0f0f0;
            color: #000000;
            font-family: "Segoe UI", Arial, sans-serif;
        }
        
        QMainWindow {
            background-color: #f0f0f0;
        }
        
        QPushButton {
            background-color: #e1e1e1;
            border: 1px solid #adadad;
            color: #000000;
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: 500;
        }
        
        QPushButton:hover {
            background-color: #d1d1d1;
            border: 1px solid #9a9a9a;
        }
        
        QPushButton:pressed {
            background-color: #c1c1c1;
        }
        
        QPushButton:disabled {
            background-color: #f0f0f0;
            color: #787878;
            border: 1px solid #cccccc;
        }
        
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #ffffff;
            border: 1px solid #adadad;
            color: #000000;
            padding: 4px 8px;
            border-radius: 3px;
        }
        
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
            border: 2px solid #0078d7;
            background-color: #ffffff;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid #000000;
            margin: 0 4px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            border: 1px solid #adadad;
            color: #000000;
            selection-background-color: #0078d7;
            selection-color: white;
        }
        
        QGroupBox {
            background-color: #f0f0f0;
            border: 1px solid #adadad;
            border-radius: 6px;
            margin-top: 1ex;
            padding-top: 10px;
            font-weight: bold;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #000000;
        }
        
        QTabWidget::pane {
            background-color: #f0f0f0;
            border: 1px solid #adadad;
            border-radius: 4px;
        }
        
        QTabBar::tab {
            background-color: #e1e1e1;
            border: 1px solid #adadad;
            color: #000000;
            padding: 6px 12px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom: 1px solid #ffffff;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #d1d1d1;
        }
        
        QListWidget {
            background-color: #ffffff;
            border: 1px solid #adadad;
            border-radius: 4px;
            color: #000000;
        }
        
        QListWidget::item {
            padding: 4px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        QListWidget::item:selected {
            background-color: #0078d7;
            color: white;
        }
        
        QListWidget::item:hover:!selected {
            background-color: #e5f3ff;
        }
        
        QScrollBar:vertical {
            background-color: #f0f0f0;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #c1c1c1;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #a1a1a1;
        }
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            background-color: #f0f0f0;
            height: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #c1c1c1;
            border-radius: 6px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #a1a1a1;
        }
        
        QMenuBar {
            background-color: #f0f0f0;
            color: #000000;
            border-bottom: 1px solid #adadad;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
        }
        
        QMenuBar::item:selected {
            background-color: #d1d1d1;
            border-radius: 3px;
        }
        
        QMenu {
            background-color: #ffffff;
            border: 1px solid #adadad;
            border-radius: 4px;
            color: #000000;
        }
        
        QMenu::item {
            padding: 6px 12px;
        }
        
        QMenu::item:selected {
            background-color: #0078d7;
            color: white;
        }
        
        QMenu::separator {
            background-color: #adadad;
            height: 1px;
            margin: 4px 8px;
        }
        
        QStatusBar {
            background-color: #f0f0f0;
            color: #555555;
            border-top: 1px solid #adadad;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #adadad;
            background-color: #ffffff;
            border-radius: 3px;
        }
        
        QCheckBox::indicator:checked {
            background-color: #0078d7;
            border-color: #0078d7;
        }
        
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #adadad;
            background-color: #ffffff;
            border-radius: 8px;
        }
        
        QRadioButton::indicator:checked {
            background-color: #0078d7;
            border-color: #0078d7;
        }
        
        QSlider::groove:horizontal {
            background-color: #e1e1e1;
            height: 8px;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background-color: #0078d7;
            width: 18px;
            height: 18px;
            margin: -5px 0;
            border-radius: 9px;
            border: 1px solid #0078d7;
        }
        
        QSlider::handle:horizontal:hover {
            background-color: #106ebe;
        }
        
        QSplitter::handle {
            background-color: #adadad;
        }
        
        QSplitter::handle:horizontal {
            width: 3px;
        }
        
        QSplitter::handle:vertical {
            height: 3px;
        }
        
        QSplitter::handle:hover {
            background-color: #0078d7;
        }
        """
    
    def _force_ui_refresh(self, app):
        """Force complete UI refresh after theme change."""
        try:
            # Process all pending events
            app.processEvents()
            
            # Get all top-level widgets
            top_level_widgets = app.topLevelWidgets()
            
            # Force repaint of all widgets
            for widget in top_level_widgets:
                if widget.isVisible():
                    self._refresh_widget_tree(widget)
            
            # Process events again to ensure all updates are applied
            app.processEvents()
            
        except Exception as e:
            print(f"Error during UI refresh: {e}")
    
    def _refresh_widget_tree(self, widget):
        """Recursively refresh a widget and all its children."""
        try:
            # Force style recalculation
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            
            # Update widget
            widget.update()
            widget.repaint()
            
            # Recursively refresh all children
            for child in widget.findChildren(QWidget):
                child.style().unpolish(child)
                child.style().polish(child)
                child.update()
                child.repaint()
                
        except Exception as e:
            print(f"Error refreshing widget: {e}")
    
    def _update_theme_actions(self, theme_name):
        """Update the checked state of theme actions."""
        try:
            for name, action in self.theme_actions.items():
                action.setChecked(name == theme_name)
        except Exception as e:
            print(f"Error updating theme actions: {e}")
    
    def _show_theme_error(self, message):
        """Show an error message for theme-related issues."""
        print(f"Theme error: {message}")
        try:
            QMessageBox.warning(
                self.main_window, 
                "Theme Error", 
                message
            )
        except:
            pass
    
    def load_theme_preference(self):
        """Load and apply the saved theme preference on startup."""
        try:
            theme = self.main_window.settings.value("theme", "dark")
            print(f"Loading theme preference: {theme}")
            
            # Update menu actions first
            self._update_theme_actions(theme)
            
            # Apply the theme
            app = QApplication.instance()
            if app:
                success = self._apply_theme_complete(app, theme)
                
                if success:
                    self.dark_theme_enabled = (theme == "dark")
                    print(f"✓ Successfully loaded theme: {theme}")
                else:
                    print(f"✗ Failed to load theme: {theme}, falling back to dark")
                    # Fallback to dark theme
                    self._update_theme_actions("dark")
                    self._apply_theme_complete(app, "dark")
                    self.dark_theme_enabled = True
            else:
                print("Error: No QApplication instance found during theme loading")
                    
        except Exception as e:
            print(f"Error loading theme preference: {e}")
            # Fallback to dark theme
            try:
                self._update_theme_actions("dark")
                app = QApplication.instance()
                if app:
                    self._apply_theme_complete(app, "dark")
                self.dark_theme_enabled = True
            except:
                pass
    
    def _reset_application(self):
        """Reset the application to default settings."""
        reply = QMessageBox.question(
            self.main_window,
            "Reset Application",
            "This will reset all application settings to defaults. Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Clear settings
                self.main_window.settings.clear()
                
                # Reset to dark theme (default)
                self._update_theme_actions("dark")
                app = QApplication.instance()
                if app:
                    self._apply_theme_complete(app, "dark")
                
                # Clear gradient list
                self.main_window.gradient_list_panel.clear_all_gradients()
                
                # Reset current gradient
                self.main_window.current_gradient.reset()
                self.main_window.update_ui_for_new_gradient()
                
                # Show status message
                self.main_window.statusBar().showMessage("Application reset to defaults", 5000)
            except Exception as e:
                QMessageBox.critical(
                    self.main_window,
                    "Reset Error",
                    f"Failed to reset application: {str(e)}"
                )
    
    def _show_preferences(self):
        """Show the preferences dialog."""
        QMessageBox.information(
            self.main_window,
            "Preferences",
            "Preferences dialog is not yet implemented.\n\n"
            "You can change themes through the View → Theme menu."
        )
    
    def _show_about(self):
        """Show the about dialog."""
        try:
            from PyQt5.QtWidgets import QTextBrowser, QVBoxLayout, QDialog, QPushButton, QLabel, QHBoxLayout
            from PyQt5.QtCore import QSize
            from PyQt5.QtGui import QFont, QPixmap
            
            # Create a custom dialog
            about_dialog = QDialog(self.main_window)
            about_dialog.setWindowTitle("About VIIBE Gradient Generator")
            about_dialog.setMinimumSize(600, 500)
            
            layout = QVBoxLayout(about_dialog)
            
            # Title
            title_label = QLabel("VIIBE Gradient Generator")
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setBold(True)
            title_label.setFont(title_font)
            title_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)
            
            # Version
            version_label = QLabel("Version 2.2.0")
            version_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(version_label)
            
            # Description
            description = QTextBrowser()
            description.setReadOnly(True)
            description.setOpenExternalLinks(True)
            
            html_content = """
            <h3>Professional Gradient Generator</h3>
            <p>A comprehensive standalone modular tool for creating and editing gradients compatible with 
            JWildfire, Ultra Fractal, Apophysis, and other fractal flame software.</p>
            
            <h4>Core Features:</h4>
            <ul>
                <li><b>Professional Gradient Editing:</b> Up to 64 color stops with precise control</li>
                <li><b>Multiple Export Formats:</b> MAP and UGR (both individual and combined) files</li>
                <li><b>Interactive Preview:</b> Real-time animated gradient visualization with seamless blending</li>
                <li><b>Multiple Theme Support:</b> Dark, Light, and System themes with complete UI refresh</li>
                <li><b>Session Management:</b> Save and restore complete gradient collections</li>
                <li><b>Batch Operations:</b> Generate multiple gradient variations efficiently</li>
            </ul>
            
            <h4>Advanced Generation:</h4>
            <ul>
                <li><b>Random Generation:</b> 6+ color schemes (Harmonious, Monochromatic, Analogous, etc.)</li>
                <li><b>Theme Generators:</b> Foliage, Flowers, Cosmic, Fire, Mood, Metal & Stone themes</li>
                <li><b>Image Analysis:</b> Extract gradients from uploaded images using K-means clustering</li>
                <li><b>Mathematical Distributions:</b> Sine waves, spirographs, golden ratio patterns</li>
                <li><b>Color-Based Reordering:</b> Sort stops by brightness, hue, saturation, or distance</li>
            </ul>
            
            <h4>Professional Tools:</h4>
            <ul>
                <li><b>Seamless Blending:</b> Basic and progressive seamless wrapping for tiled patterns</li>
                <li><b>Gradient Adjustments:</b> Brightness, contrast, gamma, saturation, hue shift controls</li>
                <li><b>Gradient Blending:</b> Merge multiple gradients with various algorithms</li>
                <li><b>Undo/Redo System:</b> Complete history management with auto-save</li>
                <li><b>Gradient Comparison:</b> Side-by-side comparison of multiple gradients</li>
                <li><b>Batch MAP Export:</b> Export multiple gradients as sequential MAP files</li>
            </ul>
            
            <h4>Interactive Features:</h4>
            <ul>
                <li><b>Live Editing:</b> Right-click to delete, left-click to add, drag to move color stops</li>
                <li><b>Context Menus:</b> Quick access to editing operations</li>
                <li><b>Visual Hints:</b> Interactive guides for adding stops and parameter adjustment</li>
                <li><b>Keyboard Shortcuts:</b> Complete keyboard support for efficient workflow</li>
            </ul>
            
            <p><small>© 2025 Whittaker Courtney - VIIBE Gradient Generator</small></p>
            """
            
            description.setHtml(html_content)
            layout.addWidget(description)
            
            # Close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(about_dialog.accept)
            layout.addWidget(close_button)
            
            about_dialog.exec_()
            
        except Exception as e:
            # Fallback simple about dialog
            QMessageBox.about(
                self.main_window,
                "About VIIBE Gradient Generator",
                "VIIBE Gradient Generator v2.2.0\n\n"
                "Professional gradient creation tool with theme support.\n"
                "Compatible with JWildfire, Ultra Fractal, and Apophysis."
            )