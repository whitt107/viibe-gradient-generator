#!/usr/bin/env python3
"""
Streamlined Gradient List Panel for Gradient Generator - Preview Strip Removed

Refactored to remove excess debug code, eliminate dialog popups for add/delete,
and reorganize button layout for better user experience. Top preview strip removed.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QListWidget, QMenu, QMessageBox, QFileDialog, 
                           QInputDialog, QLabel, QShortcut)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QKeySequence

# Import the GradientListItem from the same package
from .gradient_list_item import GradientListItem, create_mini_preview

# Handle imports with error catching
try:
    from ..core.gradient import Gradient
    from ..export.file_formats import (
        save_ugr_format, save_map_format, load_ugr_format, load_map_format
    )
except ImportError:
    try:
        from gradient_generator.core.gradient import Gradient
        from gradient_generator.export.file_formats import (
            save_ugr_format, save_map_format, load_ugr_format, load_map_format
        )
    except ImportError:
        try:
            from core.gradient import Gradient
            from export.file_formats import (
                save_ugr_format, save_map_format, load_ugr_format, load_map_format
            )
        except ImportError:
            import sys
            print("Error: Cannot import required modules. Check your Python path.", file=sys.stderr)


class GradientListPanel(QWidget):
    """Streamlined panel for managing multiple gradients with simplified operations."""
    
    gradient_selected = pyqtSignal(object)  # Emitted when a gradient is selected
    gradient_added = pyqtSignal(object)     # Emitted when a gradient is added
    gradient_deleted = pyqtSignal(int)      # Emitted when a gradient is deleted
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gradients = []  # List of (gradient, name) tuples
        self.current_index = -1
        self.auto_name_counter = 1  # Counter for auto-generated names
        self.init_ui()
    
    def init_ui(self):
        """Initialize the streamlined user interface without preview strip."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Simple header with just title
        title_label = QLabel("Gradient List")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        main_layout.addWidget(title_label)
        
        # Create list widget with drag-drop support
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.MoveAction)
        self.list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        self.list_widget.setIconSize(QSize(180, 60))
        
        main_layout.addWidget(self.list_widget)
        
        # Setup keyboard shortcuts
        self._setup_shortcuts()
        
        # Reorganized button layout - 3 rows as requested
        self._create_button_layout(main_layout)
    
    def _create_button_layout(self, main_layout):
        """Create the reorganized button layout."""
        # Row 1: Basic operations
        row1 = QHBoxLayout()
        self.add_button = self._create_button("Add Current", "Add current gradient to list", 
                                            self.add_current_gradient)
        self.delete_button = self._create_button("Delete", "Delete selected gradient", 
                                                self.delete_selected_gradient, False)
        self.duplicate_button = self._create_button("Duplicate", "Duplicate selected gradient", 
                                                  self.duplicate_selected_gradient, False)
        
        row1.addWidget(self.add_button)
        row1.addWidget(self.delete_button)
        row1.addWidget(self.duplicate_button)
        main_layout.addLayout(row1)
        
        # Row 2: Batch operations with file operations (reorganized as requested)
        row2 = QHBoxLayout()
        self.batch_button = self._create_button("Batch Generate", 
                                               "Generate variations of current gradient", 
                                               self.batch_generate_gradients)
        self.load_files_button = self._create_button("Load Files", 
                                                   "Load gradients from UGR or MAP files", 
                                                   self.load_gradient_files)
        self.clear_all_button = self._create_button("Clear All", 
                                                  "Remove all gradients from list", 
                                                  self.clear_all_gradients)
        
        row2.addWidget(self.batch_button)
        row2.addWidget(self.load_files_button)
        row2.addWidget(self.clear_all_button)
        main_layout.addLayout(row2)
    
    def _create_button(self, text, tooltip, callback=None, enabled=True):
        """Helper to create a button with common settings."""
        button = QPushButton(text)
        button.setToolTip(tooltip)
        if callback:
            button.clicked.connect(callback)
        button.setEnabled(enabled)
        return button
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts for the list panel."""
        shortcuts = [
            (QKeySequence.Delete, self.delete_selected_gradient),
            (QKeySequence("F2"), self.rename_selected_gradient),
            (QKeySequence("Ctrl+D"), self.duplicate_selected_gradient)
        ]
        
        for key, callback in shortcuts:
            shortcut = QShortcut(key, self.list_widget)
            shortcut.activated.connect(callback)
    
    def add_current_gradient(self):
        """Add current gradient from main window with smart auto-naming (no dialog popup)."""
        try:
            main_window = self.window()
            if hasattr(main_window, 'current_gradient'):
                gradient_copy = main_window.current_gradient.clone()
                
                # Smart auto-generate name without any dialog
                name = gradient_copy.get_name()
                if not name or name in ["New Gradient", "Unnamed Gradient", ""]:
                    # Find next available counter number to avoid duplicates
                    existing_names = [grad_name for _, grad_name in self.gradients]
                    counter = 1
                    while f"Gradient {counter:02d}" in existing_names:
                        counter += 1
                    name = f"Gradient {counter:02d}"
                    self.auto_name_counter = max(self.auto_name_counter, counter + 1)
                else:
                    # If gradient has a meaningful name, check for duplicates
                    existing_names = [grad_name for _, grad_name in self.gradients]
                    if name in existing_names:
                        counter = 2
                        base_name = name
                        while f"{base_name} ({counter})" in existing_names:
                            counter += 1
                        name = f"{base_name} ({counter})"
                
                # Use add_gradient with clone=False since we already cloned
                self.add_gradient(gradient_copy, name, clone=False)
                
                # Show status
                if hasattr(main_window, 'statusBar'):
                    main_window.statusBar().showMessage(f"Added: {name}", 3000)
            else:
                self._show_error("No current gradient found")
        except Exception as e:
            self._show_error(f"Failed to add gradient: {str(e)}")
    
    def add_gradient(self, gradient, name=None, clone=True):
        """Add a gradient to the list with optional cloning control."""
        # Only clone if requested (default True for backward compatibility)
        if clone:
            gradient_copy = gradient.clone()
        else:
            gradient_copy = gradient
        
        # Auto-generate name if not provided
        if not name:
            name = gradient_copy.get_name()
            if not name or name in ["New Gradient", "Unnamed Gradient", ""]:
                name = f"Gradient {self.auto_name_counter:02d}"
                self.auto_name_counter += 1
        
        gradient_copy.set_name(name)
        
        item = GradientListItem(gradient_copy, name)
        self.list_widget.addItem(item)
        self.gradients.append((gradient_copy, name))
        self.update_button_states()
        self.gradient_added.emit(gradient_copy)
    
    def delete_selected_gradient(self):
        """Delete the selected gradient without confirmation dialog."""
        current_row = self.list_widget.currentRow()
        if current_row < 0:
            return
        
        # Delete immediately without popup
        self.list_widget.takeItem(current_row)
        self.gradients.pop(current_row)
        self.update_button_states()
        self.gradient_deleted.emit(current_row)
        
        # Show brief status message
        try:
            main_window = self.window()
            if hasattr(main_window, 'statusBar'):
                main_window.statusBar().showMessage("Gradient deleted", 2000)
        except:
            pass
    
    def duplicate_selected_gradient(self):
        """Duplicate the selected gradient."""
        current_row = self.list_widget.currentRow()
        if current_row < 0:
            return
            
        gradient, name = self.gradients[current_row]
        new_gradient = gradient.clone()
        new_name = f"{name} Copy"
        new_gradient.set_name(new_name)
        self.add_gradient(new_gradient, new_name)
    
    def rename_selected_gradient(self):
        """Rename the selected gradient."""
        current_row = self.list_widget.currentRow()
        item = self.list_widget.currentItem()
        if current_row < 0 or not item:
            return
            
        gradient, old_name = self.gradients[current_row]
        new_name, ok = QInputDialog.getText(
            self, "Rename Gradient", "Enter new name:", text=old_name
        )
        
        if ok and new_name:
            item.update_name(new_name)
            self.gradients[current_row] = (gradient, new_name)
    
    def on_item_double_clicked(self, item):
        """Handle double-click on an item - load the gradient for editing."""
        current_row = self.list_widget.row(item)
        if current_row >= 0:
            gradient, _ = self.gradients[current_row]
            self.gradient_selected.emit(gradient)
            
            # Show feedback message in status bar if accessible
            try:
                main_window = self.window()
                if hasattr(main_window, 'statusBar'):
                    main_window.statusBar().showMessage(f"Loaded: {gradient.get_name()}", 3000)
            except:
                pass
    
    def clear_all_gradients(self):
        """Clear all gradients without confirmation dialog."""
        if not self.gradients:
            return
        
        # Clear immediately
        count = len(self.gradients)
        self.list_widget.clear()
        self.gradients.clear()
        self.auto_name_counter = 1  # Reset counter
        self.update_button_states()
        
        # Show status
        try:
            main_window = self.window()
            if hasattr(main_window, 'statusBar'):
                main_window.statusBar().showMessage(f"Cleared {count} gradients", 3000)
        except:
            pass
    
    def load_gradient_files(self):
        """Load gradients from UGR or MAP files (supports multiple files)."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Load Gradient Files", "", 
            "Gradient Files (*.ugr *.map);;UGR Files (*.ugr);;MAP Files (*.map);;All Files (*)"
        )
        
        if not file_paths:
            return
        
        loaded_count = 0
        failed_files = []
        
        for file_path in file_paths:
            try:
                if file_path.lower().endswith('.ugr'):
                    # Load UGR file (may contain multiple gradients)
                    gradients = load_ugr_format(file_path)
                    if gradients:
                        for gradient in gradients:
                            self.add_gradient(gradient, gradient.get_name())
                            loaded_count += 1
                    else:
                        failed_files.append(file_path)
                        
                elif file_path.lower().endswith('.map'):
                    # Load MAP file (single gradient)
                    gradient = load_map_format(file_path)
                    if gradient:
                        # Generate name from filename
                        import os
                        base_name = os.path.splitext(os.path.basename(file_path))[0]
                        gradient.set_name(base_name)
                        self.add_gradient(gradient, base_name)
                        loaded_count += 1
                    else:
                        failed_files.append(file_path)
                        
            except Exception as e:
                failed_files.append(f"{file_path} ({str(e)})")
        
        # Show streamlined results
        if loaded_count > 0:
            message = f"Loaded {loaded_count} gradient(s)"
            if failed_files and len(failed_files) <= 3:
                # Show up to 3 failed files briefly
                failed_names = [f.split('/')[-1].split('\\')[-1] for f in failed_files[:3]]
                message += f" • Failed: {', '.join(failed_names)}"
            elif failed_files:
                message += f" • {len(failed_files)} files failed"
            
            try:
                main_window = self.window()
                if hasattr(main_window, 'statusBar'):
                    main_window.statusBar().showMessage(message, 5000)
            except:
                pass
            
            # Only show dialog for serious errors
            if len(failed_files) > len(file_paths) // 2:
                QMessageBox.warning(self, "Load Issues", 
                    f"Successfully loaded {loaded_count} gradients, but {len(failed_files)} files failed to load.")
        else:
            QMessageBox.warning(self, "Load Failed", 
                "No gradients could be loaded from the selected files.")
    
    def on_selection_changed(self):
        """Handle selection change in the list."""
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            gradient, _ = self.gradients[current_row]
            self.current_index = current_row
        
        self.update_button_states()
    
    def show_context_menu(self, position):
        """Show context menu for list items."""
        item = self.list_widget.itemAt(position)
        if not item:
            return
            
        menu = QMenu()
        
        # Essential actions only
        actions = [
            ("Apply Gradient", lambda: self.on_item_double_clicked(item)),
            ("Rename", self.rename_selected_gradient),
            ("Duplicate", self.duplicate_selected_gradient),
            ("Export", self.export_selected_gradient),
            (None, None),  # Separator
            ("Delete", self.delete_selected_gradient)
        ]
        
        for text, callback in actions:
            if text is None:
                menu.addSeparator()
            else:
                action = menu.addAction(text)
                action.triggered.connect(callback)
        
        # Add compare option if multiple items selected
        selected_items = self.list_widget.selectedItems()
        if len(selected_items) >= 2:
            menu.addSeparator()
            compare_action = menu.addAction("Compare Gradients")
            compare_action.triggered.connect(self.compare_gradients)
        
        menu.exec_(self.list_widget.mapToGlobal(position))
    
    def compare_gradients(self):
        """Compare selected gradients in a new window."""
        selected_items = self.list_widget.selectedItems()
        if len(selected_items) < 2:
            self._show_message("Please select at least 2 gradients to compare.")
            return
        
        try:
            # Import only when needed to avoid circular imports
            from ..gradient_comparison import GradientComparisonDialog
            
            gradients = [self.gradients[self.list_widget.row(item)] for item in selected_items]
            dialog = GradientComparisonDialog(gradients, self)
            dialog.exec_()
        except ImportError:
            try:
                # Try an alternative import path
                from gradient_generator.ui.gradient_comparison import GradientComparisonDialog
                
                gradients = [self.gradients[self.list_widget.row(item)] for item in selected_items]
                dialog = GradientComparisonDialog(gradients, self)
                dialog.exec_()
            except ImportError:
                self._show_message("Gradient comparison feature is not available.")
        except Exception as e:
            self._show_error(f"Failed to open comparison: {str(e)}")
    
    def export_selected_gradient(self):
        """Export the selected gradient."""
        current_row = self.list_widget.currentRow()
        if current_row < 0:
            return
            
        gradient, name = self.gradients[current_row]
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Gradient", "", "MAP Files (*.map);;UGR Files (*.ugr);;All Files (*)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.map'):
                    save_map_format(gradient, file_path)
                else:
                    save_ugr_format(gradient, file_path, name)
                
                # Show brief status instead of dialog
                try:
                    main_window = self.window()
                    if hasattr(main_window, 'statusBar'):
                        main_window.statusBar().showMessage(f"Exported: {name}", 3000)
                except:
                    pass
            except Exception as e:
                self._show_error(f"Export failed: {str(e)}")
    
    def update_button_states(self):
        """Update the enabled state of buttons."""
        has_selection = self.list_widget.currentRow() >= 0
        has_gradients = len(self.gradients) > 0
        
        self.delete_button.setEnabled(has_selection)
        self.duplicate_button.setEnabled(has_selection)
        self.clear_all_button.setEnabled(has_gradients)
        self.batch_button.setEnabled(has_gradients)  # Enable batch only if gradients exist
    
    def get_current_gradient(self):
        """Get the currently selected gradient."""
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            return self.gradients[current_row][0]
        return None
    
    def set_current_index(self, index):
        """Set the current selection index."""
        if 0 <= index < len(self.gradients):
            self.list_widget.setCurrentRow(index)
    
    def batch_generate_gradients(self):
        """Open batch generation dialog."""
        if not self.gradients:
            self._show_message("Add a gradient first to generate variations.")
            return
        
        current_gradient = self.get_current_gradient() or self.gradients[0][0]
        
        try:
            # Import here to avoid circular imports
            from ..batch_operations import BatchOperationsDialog
            
            dialog = BatchOperationsDialog(current_gradient, self)
            dialog.gradients_generated.connect(self.on_batch_gradients_generated)
            dialog.exec_()
        except ImportError:
            try:
                # Try alternative import path
                from gradient_generator.ui.batch_operations import BatchOperationsDialog
                
                dialog = BatchOperationsDialog(current_gradient, self)
                dialog.gradients_generated.connect(self.on_batch_gradients_generated)
                dialog.exec_()
            except ImportError as e:
                self._show_error(f"Batch operations not available: {str(e)}")
        except Exception as e:
            self._show_error(f"Failed to open batch operations: {str(e)}")
    
    def on_batch_gradients_generated(self, gradients):
        """Handle batch generated gradients."""
        for gradient, name in gradients:
            self.add_gradient(gradient, name)
        
        if gradients:
            # Show result in status
            try:
                main_window = self.window()
                if hasattr(main_window, 'statusBar'):
                    main_window.statusBar().showMessage(f"Generated {len(gradients)} variations", 3000)
            except:
                pass
    
    # Utility methods for consistent messaging
    def _show_message(self, message):
        """Show informational message via status bar or dialog."""
        try:
            main_window = self.window()
            if hasattr(main_window, 'statusBar'):
                main_window.statusBar().showMessage(message, 3000)
                return
        except:
            pass
        
        # Fallback to message box
        QMessageBox.information(self, "Gradient List", message)
    
    def _show_error(self, message):
        """Show error message via status bar or dialog."""
        try:
            main_window = self.window()
            if hasattr(main_window, 'statusBar'):
                main_window.statusBar().showMessage(f"Error: {message}", 5000)
                return
        except:
            pass
        
        # Fallback to message box
        QMessageBox.warning(self, "Gradient List Error", message)