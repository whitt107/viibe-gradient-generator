#!/usr/bin/env python3
"""
Fixed Main Module for VIIBE Gradient Generator - Splash Screen Image Loading Fixed

The issue was in the create_default_splash_image() function being called instead of 
using the proper splash image loading mechanism from simplified_splash_screen.py
"""
import sys
import os
import argparse
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QLinearGradient, QColor

# Import UI components
from gradient_generator.ui.main_window import MainWindow

# Import utilities
from gradient_generator.utils.logger import get_logger, set_log_level
from gradient_generator.utils.config import Config

# Import dark theme with better error handling
DARK_THEME_AVAILABLE = False
try:
    from gradient_generator.utils.styles import apply_dark_theme, DarkTheme
    DARK_THEME_AVAILABLE = True
except ImportError:
    try:
        from utils.styles import apply_dark_theme, DarkTheme
        DARK_THEME_AVAILABLE = True
    except ImportError:
        print("WARNING: Dark theme module not available. Using fallback styling.")

# Import splash screen with error handling - FIXED IMPORT
try:
    from gradient_generator.ui.simplified_splash_screen import create_splash_screen, load_splash_pixmap
    SPLASH_AVAILABLE = True
except ImportError:
    try:
        from ui.simplified_splash_screen import create_splash_screen, load_splash_pixmap
        SPLASH_AVAILABLE = True
    except ImportError:
        print("WARNING: Splash screen module not available.")
        SPLASH_AVAILABLE = False
        def create_splash_screen(*args, **kwargs):
            return None
        def load_splash_pixmap(*args, **kwargs):
            return None

# Import animation integration with proper error handling
try:
    from gradient_generator.ui.animation.startup_integration import initialize_animation
    ANIMATION_AVAILABLE = True
except ImportError:
    try:
        from ui.animation.startup_integration import initialize_animation
        ANIMATION_AVAILABLE = True
    except ImportError:
        print("INFO: Animation integration module not found - this is optional")
        ANIMATION_AVAILABLE = False
        def initialize_animation():
            return False

# Application variables
APP_NAME = "VIIBE Gradient Generator"
APP_VERSION = "2.2.0"

# Global objects
logger = None
config = None


def setup_logging(debug=False):
    """Set up logging after application is initialized."""
    global logger
    logger = get_logger()
    if debug:
        set_log_level(logging.DEBUG)
        logger.debug("Debug logging enabled")
    else:
        set_log_level(logging.INFO)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=APP_NAME)
    
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "-f", "--file",
        help="Open gradient file on startup"
    )
    
    parser.add_argument(
        "--no-splash",
        action="store_true",
        help="Disable splash screen"
    )
    
    parser.add_argument(
        "--splash-duration",
        type=int,
        default=5000,  # Increased default duration to 5 seconds
        help="Splash screen duration in milliseconds (default: 5000)"
    )
    
    parser.add_argument(
        "--splash-image",
        help="Custom splash screen image path"
    )
    
    parser.add_argument(
        "--theme",
        choices=["dark", "light", "system"],
        help="Override theme setting (dark, light, or system)"
    )
    
    parser.add_argument(
        "--no-animation",
        action="store_true",
        help="Disable animated gradient preview"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"{APP_NAME} {APP_VERSION}"
    )
    
    return parser.parse_args()


def create_fallback_dark_theme(app):
    """Create a fallback dark theme if the main module isn't available."""
    try:
        from PyQt5.QtGui import QPalette, QColor
        
        # Create dark palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        
        # Apply palette
        app.setPalette(palette)
        
        # Set fusion style which works better with dark themes
        app.setStyle("Fusion")
        
        print("Applied fallback dark theme")
        return True
    except Exception as e:
        print(f"Failed to apply fallback dark theme: {e}")
        return False


def apply_initial_theme(app, theme_name="dark"):
    """Apply initial theme with proper error handling."""
    if not app:
        print("ERROR: No QApplication instance available for theme application")
        return False
    
    try:
        if theme_name == "dark":
            if DARK_THEME_AVAILABLE:
                apply_dark_theme(app)
                if logger:
                    logger.info("Dark theme applied successfully")
                else:
                    print("Dark theme applied successfully")
                return True
            else:
                return create_fallback_dark_theme(app)
        
        elif theme_name == "light":
            # For light theme, just use fusion style for now
            # The main window will handle full light theme application
            app.setStyle("Fusion")
            if logger:
                logger.info("Light theme base applied (will be completed by main window)")
            else:
                print("Light theme base applied")
            return True
            
        elif theme_name == "system":
            # Use system default
            app.setStyle("")  # Reset to system default
            app.setPalette(QApplication.style().standardPalette())
            if logger:
                logger.info("System theme applied")
            else:
                print("System theme applied")
            return True
            
        else:
            # Default to dark theme
            if DARK_THEME_AVAILABLE:
                apply_dark_theme(app)
            else:
                create_fallback_dark_theme(app)
            return True
            
    except Exception as e:
        error_msg = f"Failed to apply theme '{theme_name}': {e}"
        if logger:
            logger.error(error_msg)
        else:
            print(f"ERROR: {error_msg}")
        
        # Try fallback
        try:
            app.setStyle("Fusion")
            return True
        except:
            return False


def get_splash_image_path(custom_path=None):
    """Get the path to the splash image file - FIXED TO USE PROPER DIRECTORIES."""
    if custom_path and os.path.exists(custom_path):
        return custom_path
    
    # FIXED: Use the splash image loading mechanism from simplified_splash_screen
    # This will automatically look in the correct directories and select randomly
    return None  # Let load_splash_pixmap handle the automatic selection


class ApplicationStartup:
    """Manages the application startup sequence with proper timing and FIXED splash loading."""
    
    def __init__(self, args):
        self.args = args
        self.app = None
        self.splash = None
        self.main_window = None
        self.splash_duration = args.splash_duration
        
    def run(self):
        """Run the complete startup sequence."""
        try:
            # Phase 1: Create QApplication
            self._create_application()
            
            # Phase 2: Apply initial theme
            self._apply_initial_theme()
            
            # Phase 3: Show splash screen (if enabled) - FIXED
            self._show_splash_screen()
            
            # Phase 4: Initialize main window (but don't show it yet)
            self._create_main_window()
            
            # Phase 5: Schedule main window display after splash duration
            self._schedule_main_window_display()
            
            # Phase 6: Start event loop
            return self._start_event_loop()
            
        except Exception as e:
            print(f"Application startup failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    def _create_application(self):
        """Create QApplication with proper attributes."""
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setOrganizationName("VIIBE")
        
        # Set up logging after QApplication is created
        setup_logging(self.args.debug)
        
        # Initialize config
        global config
        config = Config()
        
        logger.info(f"{APP_NAME} starting with splash duration: {self.splash_duration}ms")
    
    def _apply_initial_theme(self):
        """Apply the initial theme."""
        self.app.setStyle("Fusion")
        
        # Determine initial theme
        initial_theme = self.args.theme if self.args.theme else config.get("theme", "dark")
        
        # Apply initial theme
        theme_success = apply_initial_theme(self.app, initial_theme)
        if not theme_success:
            logger.warning("Theme application failed, using basic styling")
    
    def _show_splash_screen(self):
        """Show splash screen if enabled - FIXED TO USE PROPER IMAGE LOADING."""
        if self.args.no_splash or not SPLASH_AVAILABLE:
            logger.info("Splash screen disabled or not available")
            return
        
        try:
            # FIXED: Use the proper splash screen creation method
            # This will automatically handle random image selection from splash_images folder
            splash_source = None
            
            # If custom image specified, use it
            if self.args.splash_image and os.path.exists(self.args.splash_image):
                splash_source = self.args.splash_image
                logger.info(f"Using custom splash image: {self.args.splash_image}")
            else:
                # Let create_splash_screen handle automatic selection
                # It will look in gradient_generator/splash_images folder automatically
                logger.info("Using automatic splash image selection")
            
            # Create splash screen with proper image loading
            self.splash = create_splash_screen(
                self.app, 
                splash_source=splash_source, 
                duration=self.splash_duration
            )
            
            if self.splash:
                logger.info(f"Splash screen created successfully, duration: {self.splash_duration}ms")
                logger.info(f"Splash slogan: '{self.splash.slogan}'")
            else:
                logger.warning("Failed to create splash screen")
                
        except Exception as e:
            logger.error(f"Error creating splash screen: {e}")
            self.splash = None
    
    def _create_main_window(self):
        """Create main window but don't show it yet."""
        try:
            self.main_window = MainWindow()
            self.main_window.setWindowTitle(APP_NAME)
            
            # Store theme override in window if provided
            if self.args.theme:
                # Set theme preference in main window if it has this method
                if hasattr(self.main_window, 'set_theme_preference'):
                    self.main_window.set_theme_preference(self.args.theme)
            
            logger.info("Main window created successfully (not shown yet)")
            
        except Exception as e:
            logger.error(f"Failed to create main window: {e}")
            raise
    
    def _schedule_main_window_display(self):
        """Schedule main window to be displayed after splash screen."""
        if self.splash:
            # Show main window after splash duration + small buffer
            display_delay = self.splash_duration + 200  # 200ms buffer
        else:
            # No splash, show immediately with small delay for initialization
            display_delay = 500
        
        logger.info(f"Scheduling main window display in {display_delay}ms")
        
        # Schedule main window display
        QTimer.singleShot(display_delay, self._show_main_window)
        
        # Schedule animation initialization even later
        if not self.args.no_animation and ANIMATION_AVAILABLE:
            animation_delay = display_delay + 1000  # 1 second after main window
            QTimer.singleShot(animation_delay, self._initialize_animation)
    
    def _show_main_window(self):
        """Show and setup the main window."""
        try:
            if not self.main_window:
                logger.error("Main window not created")
                return
            
            # Show the main window
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            
            # Handle file opening if specified
            if self.args.file:
                logger.info(f"Opening file: {self.args.file}")
                # TODO: Implement file opening
            
            # Close splash screen explicitly if it's still showing
            if self.splash and not getattr(self.splash, '_is_closing', False):
                try:
                    self.splash.close()
                except:
                    pass  # Splash might have already closed
            
            logger.info("Main window displayed successfully")
            
        except Exception as e:
            logger.error(f"Error showing main window: {e}")
    
    def _initialize_animation(self):
        """Initialize animation module."""
        try:
            logger.info("Initializing animation module...")
            success = initialize_animation()
            if success:
                logger.info("Animation module initialized successfully")
            else:
                logger.info("Animation module initialization completed with warnings")
        except Exception as e:
            logger.warning(f"Animation initialization failed: {e}")
    
    def _start_event_loop(self):
        """Start the application event loop."""
        try:
            exit_code = self.app.exec_()
            logger.info(f"{APP_NAME} exiting with code {exit_code}")
            return exit_code
        except Exception as e:
            logger.error(f"Application crashed: {e}")
            return 1


def main():
    """Run the application with proper splash screen timing and FIXED image loading."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Create and run startup manager
    startup = ApplicationStartup(args)
    return startup.run()


if __name__ == "__main__":
    sys.exit(main())