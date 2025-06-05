#!/usr/bin/env python3
"""
FIXED Main Window Module for Gradient Generator

Clean, efficient main window implementation with WORKING theme switching.
All theme conflicts resolved and proper initialization order established.

Key fixes:
- Removed duplicate theme application methods
- Fixed theme initialization order
- Proper cleanup between theme switches
- Centralized theme management through menu_manager
"""
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QSplitter, 
                           QAction, QMessageBox, QFileDialog, QInputDialog,
                           QApplication, QSizePolicy, QActionGroup)
from PyQt5.QtCore import Qt, QSettings, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QKeySequence, QPalette, QColor

# Core imports
from ..core.gradient import Gradient
from .controls import ControlPanel
from .gradient_list import GradientListPanel
from .animation.animated_gradient_preview import AnimatedGradientPreview
from .random_gradient import RandomGradientGenerator

# Window components
from .window_components import (
    MenuManager, FileOperations, GradientOperations, 
    SessionManager, ClipboardManager
)

# Optional imports with fallbacks
try:
    from .animation.undo_redo_widget import UndoRedoWidget
    UNDO_REDO_AVAILABLE = True
except ImportError:
    UNDO_REDO_AVAILABLE = False

try:
    from ..export.image_exporter import ImageExporter
    from ..export.file_formats import save_map_format, save_ugr_format
    EXPORT_AVAILABLE = True
except ImportError:
    EXPORT_AVAILABLE = False


class FixedAnimatedGradientPreview(AnimatedGradientPreview):
    """Animated gradient preview with stable sizing."""
    
    def __init__(self, gradient_model):
        super().__init__(gradient_model)
        self.setMinimumHeight(240)
        self.setMaximumHeight(240)
        self.setMinimumWidth(400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._size_hint = QSize(800, 150)
    
    def sizeHint(self):
        return self._size_hint
    
    def minimumSizeHint(self):
        return QSize(400, 120)


class MainWindow(QMainWindow):
    """Main application window with FIXED theme switching capabilities."""
    
    gradient_state_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Core state
        self.settings = QSettings("GradientGenerator", "JWildfire")
        self.current_gradient = Gradient()
        
        # CRITICAL: Initialize components in correct order
        self._init_ui()
        self._init_window_components()  # Create menu manager FIRST
        self._setup_undo_redo()
        self._connect_signals()
        self._load_settings_without_theme()  # Load settings but NOT theme
        self._apply_startup_theme()  # Apply theme AFTER menu manager exists
        self._create_samples()
    
    def _init_ui(self):
        """Initialize the user interface - NO theme application here."""
        self.setWindowTitle("VIIBE Gradient Generator v2.2.0")
        self.setMinimumSize(1200, 800)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Preview container
        preview_container = QWidget()
        preview_container.setMinimumHeight(240)
        preview_container.setMaximumHeight(240)
        preview_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        # Animated preview
        self.animated_preview = FixedAnimatedGradientPreview(self.current_gradient)
        preview_layout.addWidget(self.animated_preview)
        layout.addWidget(preview_container)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        self.gradient_list_panel = GradientListPanel()
        self.gradient_list_panel.setMinimumWidth(250)
        splitter.addWidget(self.gradient_list_panel)
        
        self.control_panel = ControlPanel(self.current_gradient)
        self.control_panel.setMinimumWidth(600)
        splitter.addWidget(self.control_panel)
        
        splitter.setSizes([300, 900])
        layout.addWidget(splitter, 1)
        
        self.statusBar().showMessage("Ready - Gradient Generator v2.2.0")
    
    def _init_window_components(self):
        """Initialize window components - CRITICAL: Menu manager created here."""
        # Create all window component managers
        self.menu_manager = MenuManager(self)
        self.file_operations = FileOperations(self)
        self.gradient_operations = GradientOperations(self)
        self.session_manager = SessionManager(self)
        self.clipboard_manager = ClipboardManager(self)
        
        # Create menu bar AFTER menu_manager exists
        self.menu_manager.create_menu_bar()
        
        print("✅ Window components initialized - Menu manager ready for theme switching")
    
    def _setup_undo_redo(self):
        """Setup undo/redo system."""
        if not UNDO_REDO_AVAILABLE:
            return
        
        if hasattr(self.animated_preview, 'history_manager'):
            history = self.animated_preview.history_manager
            if history:
                history.undo_available.connect(self._update_undo_state)
                history.redo_available.connect(self._update_redo_state)
                history.history_changed.connect(self._update_history_state)
        
        self._save_state("Initial state")
    
    def _connect_signals(self):
        """Connect UI signals."""
        # Control panel
        self.control_panel.gradient_updated.connect(self._on_gradient_updated)
        
        # Gradient list
        self.gradient_list_panel.gradient_selected.connect(self._load_gradient_from_list)
        
        # Interactive preview
        for signal in ['stop_added', 'stop_deleted', 'stop_color_changed', 'stop_moved']:
            if hasattr(self.animated_preview, signal):
                getattr(self.animated_preview, signal).connect(self._on_interactive_change)
    
    def _load_settings_without_theme(self):
        """Load settings but DO NOT apply theme yet - theme comes later."""
        try:
            # Window geometry
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
            
            print("✅ Settings loaded (theme will be applied separately)")
            
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def _apply_startup_theme(self):
        """Apply theme AFTER menu manager is initialized - CRITICAL FIX."""
        try:
            if hasattr(self, 'menu_manager') and self.menu_manager:
                print("🎨 Applying startup theme through menu manager...")
                
                # Load theme preference through menu manager
                self.menu_manager.load_theme_preference()
                
                print("✅ Startup theme applied successfully")
            else:
                print("❌ Error: Menu manager not available for theme application")
                # Fallback to basic dark theme
                self._apply_fallback_dark_theme()
                
        except Exception as e:
            print(f"Error applying startup theme: {e}")
            # Fallback to basic dark theme
            self._apply_fallback_dark_theme()
    
    def _apply_fallback_dark_theme(self):
        """Fallback dark theme if menu manager fails."""
        try:
            print("🎨 Applying fallback dark theme...")
            
            app = QApplication.instance()
            if app:
                # Try to use the styles module
                try:
                    from ..utils.styles import apply_dark_theme
                    apply_dark_theme(app)
                    print("✅ Fallback dark theme applied via styles module")
                except ImportError:
                    # Very basic fallback
                    palette = QPalette()
                    palette.setColor(QPalette.Window, QColor(42, 42, 42))
                    palette.setColor(QPalette.WindowText, QColor(221, 221, 221))
                    palette.setColor(QPalette.Base, QColor(25, 25, 25))
                    palette.setColor(QPalette.Text, QColor(221, 221, 221))
                    app.setPalette(palette)
                    app.setStyle("Fusion")
                    print("✅ Basic fallback dark theme applied")
            
        except Exception as e:
            print(f"Error applying fallback theme: {e}")
    
    def _create_samples(self):
        """Create sample gradients."""
        samples = [
            ("Random Spectrum", RandomGradientGenerator.generate_random_gradient(10, harmonious=False)),
            ("Sunset Dreams", RandomGradientGenerator.generate_random_gradient(8, triadic=True)),
            ("Ocean Depths", RandomGradientGenerator.generate_random_gradient(12, monochromatic=True))
        ]
        
        for name, gradient in samples:
            if gradient:
                gradient.set_name(name)
                self.gradient_list_panel.add_gradient(gradient, name)
        
        if samples and samples[0][1]:
            self._copy_gradient_data(samples[0][1], self.current_gradient)
            self._update_ui_for_gradient()
            self.gradient_list_panel.list_widget.setCurrentRow(0)
    
    # File Operations
    def _new_gradient(self):
        """Create new gradient."""
        if self._confirm_action("Create new gradient?"):
            self.current_gradient.reset()
            self._update_ui_for_gradient()
            self._save_state("New gradient created")
    
    def _create_from_image(self):
        """Create gradient from image."""
        try:
            from ..ui.image_to_gradient import ImageToGradientDialog
            if self._confirm_action("Create gradient from image?"):
                dialog = ImageToGradientDialog(self)
                dialog.gradient_created.connect(self._apply_generated_gradient)
                dialog.exec_()
        except ImportError:
            QMessageBox.warning(self, "Unavailable", "Image to gradient feature not available.")
    
    def _create_random(self):
        """Create random gradient."""
        try:
            from ..ui.random_gradient_dialog import RandomGradientDialog
            if self._confirm_action("Create random gradient?"):
                dialog = RandomGradientDialog(self)
                dialog.gradient_generated.connect(self._apply_generated_gradient)
                dialog.exec_()
        except ImportError:
            QMessageBox.warning(self, "Unavailable", "Random gradient dialog not available.")
    
    def _save_map(self):
        """Save as MAP file."""
        if EXPORT_AVAILABLE:
            self._save_file("MAP Files (*.map)", save_map_format, "MAP")
    
    def _save_ugr(self):
        """Save as UGR file."""
        if not EXPORT_AVAILABLE:
            return
        
        name = self.current_gradient.get_name() or "Gradient"
        if not name or name == "New Gradient":
            name, ok = QInputDialog.getText(self, "Gradient Name", "Enter name:")
            if not ok or not name:
                return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Save UGR File", "", "UGR Files (*.ugr)")
        if file_path:
            try:
                save_ugr_format(self.current_gradient, file_path, name)
                self.statusBar().showMessage(f"Saved: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save: {str(e)}")
    
    def _export_image(self):
        """Export as image."""
        if EXPORT_AVAILABLE:
            self._save_file("PNG Images (*.png);;JPEG Images (*.jpg)", 
                           lambda g, p: ImageExporter().export(g, p), "Image")
    
    def _save_file(self, filter_str, save_func, format_name):
        """Generic file save method."""
        file_path, _ = QFileDialog.getSaveFileName(self, f"Save {format_name}", "", filter_str)
        if file_path:
            try:
                save_func(self.current_gradient, file_path)
                self.statusBar().showMessage(f"Saved: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
    
    def _save_session(self):
        """Save session."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Session", "", "JSON Files (*.json)")
        if file_path:
            try:
                import json
                session_data = {
                    "current_gradient": self._serialize_gradient(self.current_gradient),
                    "gradient_list": [(name, self._serialize_gradient(grad)) 
                                    for grad, name in self.gradient_list_panel.gradients]
                }
                with open(file_path, 'w') as f:
                    json.dump(session_data, f, indent=2)
                self.statusBar().showMessage(f"Session saved: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save session: {str(e)}")
    
    def _load_session(self):
        """Load session."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Session", "", "JSON Files (*.json)")
        if file_path:
            try:
                import json
                with open(file_path, 'r') as f:
                    session_data = json.load(f)
                
                self.gradient_list_panel.clear_all_gradients()
                
                for name, grad_data in session_data.get("gradient_list", []):
                    gradient = self._deserialize_gradient(grad_data)
                    self.gradient_list_panel.add_gradient(gradient, name)
                
                if "current_gradient" in session_data:
                    current = self._deserialize_gradient(session_data["current_gradient"])
                    self._copy_gradient_data(current, self.current_gradient)
                    self._update_ui_for_gradient()
                
                self.statusBar().showMessage(f"Session loaded: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load session: {str(e)}")
    
    # Edit Operations
    def _copy_gradient(self):
        """Copy gradient to clipboard."""
        try:
            import json
            data = json.dumps(self._serialize_gradient(self.current_gradient))
            QApplication.clipboard().setText(data)
            self.statusBar().showMessage("Gradient copied to clipboard")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy: {str(e)}")
    
    def _paste_gradient(self):
        """Paste gradient from clipboard."""
        try:
            import json
            text = QApplication.clipboard().text()
            data = json.loads(text)
            gradient = self._deserialize_gradient(data)
            
            if self._confirm_action("Paste gradient from clipboard?"):
                self._copy_gradient_data(gradient, self.current_gradient)
                self._update_ui_for_gradient()
                self._save_state("Gradient pasted")
                self.statusBar().showMessage("Gradient pasted from clipboard")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to paste: {str(e)}")
    
    def _add_to_list(self):
        """Add current gradient to list with smart auto-naming."""
        gradient_copy = self.current_gradient.clone()
        
        # Smart auto-generate name without dialog
        name = gradient_copy.get_name()
        if not name or name in ["New Gradient", "Unnamed Gradient", ""]:
            # Find next available counter number to avoid duplicates
            existing_names = [grad_name for _, grad_name in self.gradient_list_panel.gradients]
            counter = 1
            while f"Gradient {counter:02d}" in existing_names:
                counter += 1
            name = f"Gradient {counter:02d}"
        else:
            # If gradient has a meaningful name, check for duplicates
            existing_names = [grad_name for _, grad_name in self.gradient_list_panel.gradients]
            if name in existing_names:
                counter = 2
                base_name = name
                while f"{base_name} ({counter})" in existing_names:
                    counter += 1
                name = f"{base_name} ({counter})"
        
        gradient_copy.set_name(name)
        self.gradient_list_panel.add_gradient(gradient_copy, name)
        self.statusBar().showMessage(f"Added to list: {name}", 3000)
    
    # View Operations - REMOVED duplicate theme methods
    def _toggle_list(self):
        """Toggle gradient list visibility."""
        visible = self.gradient_list_panel.isVisible()
        self.gradient_list_panel.setVisible(not visible)
    
    # Help Operations
    def _show_shortcuts(self):
        """Show keyboard shortcuts."""
        shortcuts_text = """
<b>VIIBE Gradient Generator - Keyboard Shortcuts</b><br><br>

<b>File Operations:</b><br>
• Ctrl+N - New Gradient<br>
• Ctrl+I - Create from Image<br>
• Ctrl+R - Create Random Gradient<br>
• Ctrl+S - Save as MAP<br>
• Ctrl+U - Save as UGR<br>
• Ctrl+E - Export Image<br>
• Ctrl+Shift+S - Save Session<br>
• Ctrl+Shift+O - Load Session<br>
• Ctrl+Q - Exit<br><br>

<b>Edit Operations:</b><br>
• Ctrl+Z - Undo<br>
• Ctrl+Y - Redo<br>
• Ctrl+C - Copy Gradient<br>
• Ctrl+V - Paste Gradient<br>
• Ctrl+L - Add to List<br><br>

<b>View Operations:</b><br>
• Ctrl+T - Toggle Gradient List<br>
• F1 - Show this help<br><br>

<b>Interactive Preview:</b><br>
• Left-click - Add color stop<br>
• Right-click - Delete color stop<br>
• Drag - Move color stop<br>
• Double-click - Edit color<br>
        """
        
        QMessageBox.about(self, "Keyboard Shortcuts", shortcuts_text)
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About VIIBE Gradient Generator",
            "VIIBE Gradient Generator v2.2.0\n\n"
            "Professional gradient creation tool with seamless blending,\n"
            "undo/redo functionality, and JWildfire compatibility.\n\n"
            "Features:\n"
            "• Up to 64 color stops per gradient\n"
            "• Enhanced seamless blending\n"
            "• Interactive animated preview\n"
            "• Multiple export formats (MAP, UGR, Images)\n"
            "• Full undo/redo support\n"
            "• Dark/Light/System themes\n"
            "• Session save/load\n"
            "• Mathematical and color-based distributions\n\n"
            "© 2025 VIIBE Gradient Generator Team")
    
    # Undo/Redo Operations
    def _undo(self):
        """Perform undo."""
        if UNDO_REDO_AVAILABLE and hasattr(self.animated_preview, 'undo'):
            if self.animated_preview.undo():
                self._update_ui_for_gradient()
                self.statusBar().showMessage("Undo performed", 2000)
    
    def _redo(self):
        """Perform redo."""
        if UNDO_REDO_AVAILABLE and hasattr(self.animated_preview, 'redo'):
            if self.animated_preview.redo():
                self._update_ui_for_gradient()
                self.statusBar().showMessage("Redo performed", 2000)
    
    def _save_state(self, description):
        """Save current state to history."""
        if UNDO_REDO_AVAILABLE and hasattr(self.animated_preview, 'save_state_to_history'):
            self.animated_preview.save_state_to_history(description, force=True)
    
    def _update_undo_state(self, available):
        """Update undo action state."""
        if hasattr(self, 'undo_action'):
            self.undo_action.setEnabled(available)
    
    def _update_redo_state(self, available):
        """Update redo action state."""
        if hasattr(self, 'redo_action'):
            self.redo_action.setEnabled(available)
    
    def _update_history_state(self):
        """Update history-related UI."""
        pass  # Simplified - no complex history status updates
    
    # Event Handlers
    def _on_gradient_updated(self):
        """Handle gradient updates from controls."""
        if hasattr(self.animated_preview, 'update_gradient'):
            self.animated_preview.update_gradient(save_to_history=True)
        self.gradient_state_changed.emit()
    
    def _on_interactive_change(self, *args):
        """Handle interactive changes from animated preview."""
        QTimer.singleShot(50, self._update_controls_from_model)
        self.gradient_state_changed.emit()
    
    def _update_controls_from_model(self):
        """Update control panel from model."""
        try:
            if hasattr(self.control_panel, 'color_stops_editor'):
                editor = self.control_panel.color_stops_editor
                if hasattr(editor, 'update_from_model'):
                    editor.update_from_model()
        except Exception:
            pass  # Simplified error handling
    
    def _load_gradient_from_list(self, gradient):
        """Load gradient from list selection."""
        if gradient and self._confirm_action("Load selected gradient?"):
            self._copy_gradient_data(gradient, self.current_gradient)
            self._update_ui_for_gradient()
            self._save_state(f"Loaded: {gradient.get_name()}")
    
    def _apply_generated_gradient(self, gradient):
        """Apply generated gradient."""
        if gradient:
            self._copy_gradient_data(gradient, self.current_gradient)
            self._update_ui_for_gradient()
            self._save_state(f"Generated: {gradient.get_name()}")
    
    def _update_ui_for_gradient(self):
        """Update all UI components for gradient change."""
        if hasattr(self.control_panel, 'reset_controls'):
            self.control_panel.reset_controls()
        
        if hasattr(self.animated_preview, 'update_gradient'):
            self.animated_preview.update_gradient()
    
    # Utility Methods
    def _confirm_action(self, message):
        """Confirm action if gradient is not empty."""
        if not self.current_gradient.is_empty():
            reply = QMessageBox.question(self, "Confirm", f"{message}\nUnsaved changes will be lost.",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            return reply == QMessageBox.Yes
        return True
    
    def _copy_gradient_data(self, source, target):
        """Copy gradient data between instances."""
        target._color_stops = []
        for stop in source.get_color_stop_objects():
            target.add_color_stop(stop.position, stop.color)
        
        # Copy metadata
        metadata_attrs = ['name', 'author', 'description', 'ugr_category', 'combine_gradients', 
                         'seamless_blend', 'blend_region', 'progressive_blending', 'intensity_falloff']
        
        for attr in metadata_attrs:
            getter = f'get_{attr}'
            setter = f'set_{attr}'
            if hasattr(source, getter) and hasattr(target, setter):
                try:
                    value = getattr(source, getter)()
                    getattr(target, setter)(value)
                except:
                    pass
    
    def _serialize_gradient(self, gradient):
        """Serialize gradient to dict."""
        data = {
            "color_stops": gradient.get_color_stops(),
            "name": gradient.get_name(),
            "author": gradient.get_author(),
            "description": gradient.get_description(),
            "ugr_category": gradient.get_ugr_category(),
            "combine_gradients": gradient.get_combine_gradients(),
            "seamless_blend": gradient.get_seamless_blend(),
            "blend_region": gradient.get_blend_region(),
        }
        
        # Add enhanced properties if available
        for attr in ['progressive_blending', 'intensity_falloff']:
            if hasattr(gradient, f'get_{attr}'):
                try:
                    data[attr] = getattr(gradient, f'get_{attr}')()
                except:
                    pass
        
        return data
    
    def _deserialize_gradient(self, data):
        """Deserialize gradient from dict."""
        gradient = Gradient()
        gradient._color_stops = []
        
        for position, color in data.get("color_stops", []):
            gradient.add_color_stop(position, color)
        
        # Set properties
        setters = {
            'name': 'set_name', 'author': 'set_author', 'description': 'set_description',
            'ugr_category': 'set_ugr_category', 'combine_gradients': 'set_combine_gradients',
            'seamless_blend': 'set_seamless_blend', 'blend_region': 'set_blend_region',
            'progressive_blending': 'set_progressive_blending', 'intensity_falloff': 'set_intensity_falloff'
        }
        
        for key, setter_name in setters.items():
            if key in data and hasattr(gradient, setter_name):
                try:
                    getattr(gradient, setter_name)(data[key])
                except:
                    pass
        
        return gradient
    
    # Window Events
    def closeEvent(self, event):
        """Handle window close."""
        # Save settings
        self.settings.setValue("geometry", self.saveGeometry())
        
        # Stop animations
        if hasattr(self.animated_preview, 'stop_all_animations'):
            try:
                self.animated_preview.stop_all_animations()
            except:
                pass
        
        # Confirm close if changes exist
        if not self.current_gradient.is_empty():
            reply = QMessageBox.question(self, "Exit", "Exit without saving changes?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        event.accept()
    
    def keyPressEvent(self, event):
        """Handle global keyboard shortcuts."""
        # Handle undo/redo shortcuts
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_Z and not event.modifiers() & Qt.ShiftModifier:
                self._undo()
                event.accept()
                return
            elif event.key() == Qt.Key_Y or (event.key() == Qt.Key_Z and event.modifiers() & Qt.ShiftModifier):
                self._redo()
                event.accept()
                return
        
        # Handle other shortcuts
        if event.key() == Qt.Key_F1:
            self._show_shortcuts()
            event.accept()
        elif event.key() == Qt.Key_F5:
            self._update_ui_for_gradient()
            self.statusBar().showMessage("UI refreshed", 2000)
            event.accept()
        else:
            super().keyPressEvent(event)