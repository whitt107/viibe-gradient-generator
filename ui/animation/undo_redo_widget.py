#!/usr/bin/env python3
"""
Undo/Redo Widget Module for Animated Gradient Preview

This module provides a compact widget with undo/redo buttons and status display.
"""
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel, 
                           QToolTip, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QCursor


class UndoRedoWidget(QWidget):
    """Widget providing undo/redo buttons with status information."""
    
    # Signals
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the undo/redo widget."""
        super().__init__(parent)
        
        # State tracking
        self.undo_available = False
        self.redo_available = False
        self.current_description = "No state"
        
        # Tooltip timer
        self.tooltip_timer = QTimer()
        self.tooltip_timer.setSingleShot(True)
        self.tooltip_timer.timeout.connect(self._show_tooltip)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        # Create buttons with compact styling
        self.undo_button = self._create_button("↶", "Undo")
        self.redo_button = self._create_button("↷", "Redo")
        
        # Connect signals
        self.undo_button.clicked.connect(self._on_undo_clicked)
        self.redo_button.clicked.connect(self._on_redo_clicked)
        
        # Status label (optional, can be hidden)
        self.status_label = QLabel()
        self.status_label.setStyleSheet(
            "color: #888; font-size: 9px; font-style: italic;"
        )
        self.status_label.setVisible(False)  # Hidden by default
        
        # Add widgets to layout
        layout.addWidget(self.undo_button)
        layout.addWidget(self.redo_button)
        layout.addWidget(self.status_label)
        layout.addStretch()
        
        # Set initial state
        self.update_button_states(False, False)
        
        # Compact size policy
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.setMaximumHeight(30)
    
    def _create_button(self, text: str, tooltip: str) -> QPushButton:
        """
        Create a styled button.
        
        Args:
            text: Button text/symbol
            tooltip: Tooltip text
            
        Returns:
            Configured QPushButton
        """
        button = QPushButton(text)
        button.setFixedSize(24, 24)
        button.setToolTip(tooltip)
        
        # Style the button
        button.setStyleSheet("""
            QPushButton {
                border: 1px solid #555;
                border-radius: 3px;
                background-color: #444;
                color: #ddd;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #555;
                border-color: #666;
            }
            QPushButton:pressed {
                background-color: #333;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666;
                border-color: #333;
            }
        """)
        
        return button
    
    def _on_undo_clicked(self):
        """Handle undo button click."""
        if self.undo_available:
            self.undo_requested.emit()
            self._show_feedback("Undo")
    
    def _on_redo_clicked(self):
        """Handle redo button click."""
        if self.redo_available:
            self.redo_requested.emit()
            self._show_feedback("Redo")
    
    def update_button_states(self, can_undo: bool, can_redo: bool):
        """
        Update the enabled state of buttons.
        
        Args:
            can_undo: Whether undo is available
            can_redo: Whether redo is available
        """
        self.undo_available = can_undo
        self.redo_available = can_redo
        
        self.undo_button.setEnabled(can_undo)
        self.redo_button.setEnabled(can_redo)
        
        # Update tooltips with availability info
        undo_tooltip = "Undo last change" if can_undo else "Nothing to undo"
        redo_tooltip = "Redo last undone change" if can_redo else "Nothing to redo"
        
        self.undo_button.setToolTip(undo_tooltip)
        self.redo_button.setToolTip(redo_tooltip)
        
        # Update visual feedback
        self._update_visual_state()
    
    def set_current_description(self, description: str):
        """
        Set the current state description.
        
        Args:
            description: Description of current state
        """
        self.current_description = description
        self.status_label.setText(f"State: {description}")
    
    def show_status_label(self, show: bool = True):
        """
        Show or hide the status label.
        
        Args:
            show: Whether to show the status label
        """
        self.status_label.setVisible(show)
    
    def _update_visual_state(self):
        """Update visual state indicators."""
        # Visual state is primarily handled through enabled/disabled state
        # Additional visual feedback could be added here if needed
        pass
    
    def _show_feedback(self, action: str):
        """
        Show visual feedback for an action.
        
        Args:
            action: Action that was performed ("Undo" or "Redo")
        """
        # Flash the button or show temporary status
        button = self.undo_button if action == "Undo" else self.redo_button
        
        # Simple feedback - change button style temporarily
        original_style = button.styleSheet()
        highlight_style = original_style.replace("background-color: #444", 
                                                "background-color: #666")
        button.setStyleSheet(highlight_style)
        
        # Reset after short delay
        QTimer.singleShot(100, lambda: button.setStyleSheet(original_style))
    
    def _show_tooltip(self):
        """Show detailed tooltip with history information."""
        if self.underMouse():
            tooltip_text = f"Current: {self.current_description}\n"
            tooltip_text += f"Undo: {'Available' if self.undo_available else 'Not available'}\n"
            tooltip_text += f"Redo: {'Available' if self.redo_available else 'Not available'}"
            
            QToolTip.showText(QCursor.pos(), tooltip_text, self)
    
    def enterEvent(self, event):
        """Handle mouse enter for delayed tooltip."""
        super().enterEvent(event)
        self.tooltip_timer.start(1000)  # Show detailed tooltip after 1 second
    
    def leaveEvent(self, event):
        """Handle mouse leave."""
        super().leaveEvent(event)
        self.tooltip_timer.stop()
        QToolTip.hideText()
    
    def set_compact_mode(self, compact: bool = True):
        """
        Set compact display mode.
        
        Args:
            compact: Whether to use compact mode
        """
        if compact:
            self.undo_button.setText("↶")
            self.redo_button.setText("↷")
            self.show_status_label(False)
        else:
            self.undo_button.setText("Undo")
            self.redo_button.setText("Redo")
            self.show_status_label(True)
            
            # Resize buttons for text
            self.undo_button.setFixedSize(50, 24)
            self.redo_button.setFixedSize(50, 24)
    
    def get_state_info(self) -> dict:
        """
        Get current widget state information.
        
        Returns:
            Dictionary with state information
        """
        return {
            "undo_available": self.undo_available,
            "redo_available": self.redo_available,
            "current_description": self.current_description,
            "compact_mode": self.undo_button.text() in ["↶", "↷"]
        }
