#!/usr/bin/env python3
"""
Enhanced Splash Screen Module for VIIBE Gradient Generator

This module implements a splash screen that displays a random slogan
and loads random images from a series (splash_01.png, splash_02.jpg, etc.)
Fixed timing issues and improved image loading behavior.
"""
import os
import math
import random
import glob
from PyQt5.QtWidgets import QSplashScreen, QApplication, QDesktopWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer, QSize, QRect

# Collection of cheesy slogans
CHEESY_SLOGANS = [
    "It's not Stupid. It's Advanced.",
    "It just Works, Somehow.",
    "The Question is Not Why, but Why Not?",
    "VIIBE, an Experience Far Above Your Already Low Expectations",
    "Achieve Colors Previously Only Seen After Consuming Questionable Leftovers.",
    "I'm Not Sure How It Works Either, but Look at These Smooth Transitions!",
    "The Ultimate Gradient Experience",
    "50 Shades of... Well, Whatever Color You Want!",
    "Turn Your Gradients Up to 11.25",
    "Gradients So Good, They Should Be Illegal",
    "The Gradient Generator Your Mother Warned You About",
    "Get Ready to Blend Colors You Didn't Even Know Existed",
    "More Impressive Than Your Color-Coordinated Sock Drawer",
    "Find the Perfect Color Scheme to Match Your Last Failed Relationship",
    "More Color Transitions Than a Chameleon in an Art Supply Store",
    "We Don't Make Mistakes, Just Happy Little Gradients",
    "Gradients So Hot They Need a Warning Label",
    "30 Percent Functioning Code, 70 Percent Pure, Unnecessary VIIBE.",
    "VIIBE: Very Impressive Incredible Blending Experience",
    "Now With a 'Panic' Button for When the Color Stop Handles Become Sentient.",
    "Gradients That Make Even Your Grandma Say 'Lit'",
    "Color Outside the Lines. Then Gradient Fill It.",
    "99 Problems But a Blend Ain't One.",
    "You Had Me at Gradient",
    "Overkill for Your Project, but You're Going to Use It Anyway.",
    "Slide Into Those DMs (Delightful Motifs)",
    "Because Your Color Transitions Deserve the Same Overthinking as Your Life Decisions.",
    "You Thought You Knew Gradients. You Were Wrong.",
    "When You Absolutely, Positively Need the Perfect Gradient",
    "We Put the 'Ooooh' in UGR and MAP Files",
    "All We Have To Decide, Is What To Do With The Gradients We Are Given.",
    "The Most Unnecessary Gradient Generator You'll ever use.",
    "Sweet dreams are made of hues."
]


class SloganSplashScreen(QSplashScreen):
    """A splash screen that displays a random slogan with accurate timing."""
    
    def __init__(self, pixmap=None):
        """
        Initialize the splash screen with an image.
        
        Args:
            pixmap: QPixmap to display
        """
        super().__init__(pixmap, Qt.WindowStaysOnTopHint)
        
        # Set frameless window hint to remove any border
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        
        # Select a random slogan
        self.slogan = random.choice(CHEESY_SLOGANS)
        
        # Store the original pixmap for drawing
        self.original_pixmap = pixmap
        
        # Timer for accurate duration control
        self.close_timer = QTimer()
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self._close_splash)
        
        # Track if splash is closing to prevent multiple close attempts
        self._is_closing = False
    
    def drawContents(self, painter):
        """Override to draw slogan on the splash image."""
        # Draw the original pixmap first
        if self.original_pixmap:
            painter.drawPixmap(self.rect(), self.original_pixmap)
        
        # Draw the slogan at the bottom of the splash image
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        # Set up font and color
        font = QFont("Arial", 12)
        font.setBold(True)
        painter.setFont(font)
        
        # Create a semi-transparent background for the text
        rect = self.rect()
        text_rect = QRect(rect.left() + 10, rect.bottom() - 50, rect.width() - 20, 40)
        
        # Draw semi-transparent background
        painter.fillRect(text_rect, QColor(0, 0, 0, 180))
        
        # Draw text with glow effect for readability
        # First draw text with glow
        painter.setPen(QColor(70, 70, 70, 200))
        for offset in range(1, 3):
            painter.drawText(text_rect.adjusted(offset, offset, offset, offset), 
                          Qt.AlignCenter, self.slogan)
        
        # Then draw the actual text
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(text_rect, Qt.AlignCenter, self.slogan)
    
    def start_timer(self, duration_ms):
        """Start the close timer with specified duration."""
        if not self._is_closing:
            self.close_timer.start(duration_ms)
    
    def _close_splash(self):
        """Internal method to close the splash screen."""
        if not self._is_closing:
            self._is_closing = True
            try:
                self.finish(None)
            except RuntimeError:
                # Widget may have been deleted
                pass
    
    def closeEvent(self, event):
        """Handle close event to stop timer."""
        self._is_closing = True
        self.close_timer.stop()
        super().closeEvent(event)


def find_splash_images(base_directory):
    """
    Find all splash images in the specified directory.
    Looks for files named splash_01.png, splash_02.jpg, etc.
    
    Args:
        base_directory: Base directory to search in
        
    Returns:
        List of found image file paths
    """
    # Determine splash images directory
    splash_dir = os.path.join(base_directory, "gradient_generator", "splash_images")
    
    # If that doesn't exist, try relative to the current script
    if not os.path.exists(splash_dir):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        splash_dir = os.path.join(script_dir, "..", "splash_images")
    
    # If still not found, try a few more locations
    if not os.path.exists(splash_dir):
        possible_dirs = [
            os.path.join(os.getcwd(), "splash_images"),
            os.path.join(os.getcwd(), "assets", "splash_images"),
            os.path.join(os.getcwd(), "resources", "splash_images"),
            os.path.join(os.path.dirname(__file__), "splash_images"),
            os.path.join(os.path.dirname(__file__), "..", "..", "splash_images")
        ]
        
        for possible_dir in possible_dirs:
            if os.path.exists(possible_dir):
                splash_dir = possible_dir
                break
    
    if not os.path.exists(splash_dir):
        print(f"Splash images directory not found. Checked: {splash_dir}")
        return []
    
    # Look for splash images with patterns: splash_01.png, splash_02.jpg, etc.
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif']
    splash_files = []
    
    for extension in image_extensions:
        # Pattern: splash_XX.ext where XX is numbers
        pattern = os.path.join(splash_dir, f"splash_*{extension}")
        matches = glob.glob(pattern)
        splash_files.extend(matches)
    
    # Sort to ensure consistent ordering
    splash_files.sort()
    
    print(f"Found {len(splash_files)} splash images in {splash_dir}")
    for img in splash_files:
        print(f"  - {os.path.basename(img)}")
    
    return splash_files


def select_random_splash_image(base_directory=None):
    """
    Select a random splash image from available images.
    
    Args:
        base_directory: Base directory to search for images (optional)
        
    Returns:
        Path to selected image file or None if no images found
    """
    if base_directory is None:
        base_directory = os.getcwd()
    
    splash_images = find_splash_images(base_directory)
    
    if not splash_images:
        return None
    
    # Randomly select one image
    selected_image = random.choice(splash_images)
    print(f"Selected splash image: {os.path.basename(selected_image)}")
    
    return selected_image


def load_splash_pixmap(image_path=None, base_directory=None):
    """
    Load a splash pixmap from file or create a default one.
    
    Args:
        image_path: Specific image path (optional)
        base_directory: Base directory for random selection (optional)
        
    Returns:
        QPixmap or None if loading failed
    """
    # If no specific path provided, try to find and select randomly
    if image_path is None:
        image_path = select_random_splash_image(base_directory)
    
    # Try to load the selected/specified image
    if image_path and os.path.exists(image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            print(f"Loaded splash image: {image_path}")
            return pixmap
        else:
            print(f"Failed to load splash image: {image_path}")
    
    # Fallback: create default splash image
    print("Creating default splash image")
    return create_default_splash_pixmap()


def create_default_splash_pixmap():
    """Create a default splash image with gradient background."""
    try:
        from PyQt5.QtGui import QLinearGradient
        
        # Create a 400x300 pixmap with gradient
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create a beautiful gradient background
        gradient = QLinearGradient(0, 0, pixmap.width(), pixmap.height())
        gradient.setColorAt(0.0, QColor(15, 10, 39))    # Deep blue
        gradient.setColorAt(0.2, QColor(120, 33, 100))  # Purple
        gradient.setColorAt(0.5, QColor(191, 64, 95))   # Pink
        gradient.setColorAt(0.8, QColor(255, 93, 35))   # Orange
        gradient.setColorAt(1.0, QColor(254, 192, 81))  # Yellow
        
        painter.fillRect(pixmap.rect(), gradient)
        
        # Add title text
        painter.setPen(QColor(255, 255, 255))
        font = painter.font()
        font.setPointSize(24)
        font.setBold(True)
        painter.setFont(font)
        
        # Draw title with shadow effect
        title_rect = pixmap.rect().adjusted(0, 50, 0, -100)
        
        # Shadow
        painter.setPen(QColor(0, 0, 0, 150))
        painter.drawText(title_rect.adjusted(2, 2, 2, 2), Qt.AlignCenter, "VIIBE")
        
        # Main text
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(title_rect, Qt.AlignCenter, "VIIBE")
        
        # Subtitle
        font.setPointSize(12)
        font.setBold(False)
        painter.setFont(font)
        subtitle_rect = pixmap.rect().adjusted(0, 120, 0, -50)
        painter.drawText(subtitle_rect, Qt.AlignCenter, "Gradient Generator")
        
        # Version
        font.setPointSize(10)
        painter.setFont(font)
        version_rect = pixmap.rect().adjusted(0, 150, 0, -20)
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(version_rect, Qt.AlignCenter, "Version 2.2.0")
        
        painter.end()
        
        return pixmap
    except Exception as e:
        print(f"Failed to create default splash image: {e}")
        return None


def get_scaled_size(original_size, screen_size, target_fraction=0.4):
    """
    Calculate a scaled size that maintains aspect ratio and fits screen.
    
    Args:
        original_size: QSize of the original image
        screen_size: QSize of the screen
        target_fraction: Fraction of screen area to target (0.4 = 40%)
        
    Returns:
        QSize with the scaled dimensions
    """
    # Extract dimensions
    orig_width = original_size.width()
    orig_height = original_size.height()
    screen_width = screen_size.width()
    screen_height = screen_size.height()
    
    # Calculate the target area
    screen_area = screen_width * screen_height
    target_area = screen_area * target_fraction
    
    # Calculate the scaling factor to maintain aspect ratio
    orig_area = orig_width * orig_height
    if orig_area <= 0:  # Guard against division by zero
        return QSize(screen_width // 2, screen_height // 2)
        
    scale = math.sqrt(target_area / orig_area)
    
    # Apply the scaling
    new_width = int(orig_width * scale * 0.75)
    new_height = int(orig_height * scale * 0.75)
    
    # Ensure we don't exceed screen dimensions
    max_width = int(screen_width * 0.8)
    max_height = int(screen_height * 0.8)
    
    if new_width > max_width:
        scale_factor = max_width / new_width
        new_width = int(new_width * scale_factor)
        new_height = int(new_height * scale_factor)
    
    if new_height > max_height:
        scale_factor = max_height / new_height
        new_width = int(new_width * scale_factor)
        new_height = int(new_height * scale_factor)
    
    # Ensure minimum size
    new_width = max(300, new_width)
    new_height = max(200, new_height)
    
    return QSize(new_width, new_height)


def create_splash_screen(app, splash_source=None, duration=5000):
    """
    Create and display a splash screen with accurate timing and random image loading.
    
    Args:
        app: QApplication instance
        splash_source: Can be:
                      - None: Auto-select random image from splash_images folder
                      - str: Path to specific image file OR base directory for random selection
                      - QPixmap: Pre-loaded pixmap
        duration: Duration to show splash screen in milliseconds (default: 3000ms)
        
    Returns:
        SloganSplashScreen instance or None if creation failed
    """
    try:
        print(f"Creating splash screen with duration: {duration}ms")
        
        # Handle different input types for splash_source
        if splash_source is None:
            # Auto-select random image
            pixmap = load_splash_pixmap()
        elif isinstance(splash_source, str):
            if os.path.isfile(splash_source):
                # It's a specific file path
                pixmap = load_splash_pixmap(splash_source)
            elif os.path.isdir(splash_source):
                # It's a directory - use for random selection
                pixmap = load_splash_pixmap(base_directory=splash_source)
            else:
                # Try to use as base directory anyway
                pixmap = load_splash_pixmap(base_directory=splash_source)
        elif isinstance(splash_source, QPixmap):
            # It's already a QPixmap
            pixmap = splash_source
        else:
            print(f"Invalid splash source type: {type(splash_source)}, using default")
            pixmap = load_splash_pixmap()
        
        # Fallback to default if loading failed
        if pixmap is None or pixmap.isNull():
            print("Failed to load any splash image, using default")
            pixmap = create_default_splash_pixmap()
        
        if pixmap is None or pixmap.isNull():
            print("Failed to create splash screen - no valid image")
            return None
        
        # Get screen dimensions
        desktop = QDesktopWidget()
        screen_rect = desktop.availableGeometry(desktop.primaryScreen())
        screen_size = QSize(screen_rect.width(), screen_rect.height())
        
        # Calculate scaled size (about 40% of the screen area)
        scaled_size = get_scaled_size(pixmap.size(), screen_size, 0.4)
        
        # Scale the pixmap maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            scaled_size.width(), 
            scaled_size.height(),
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        # Create splash screen with scaled image and random slogan
        splash = SloganSplashScreen(scaled_pixmap)
        
        # Center on screen
        splash_x = screen_rect.x() + (screen_rect.width() - scaled_pixmap.width()) // 2
        splash_y = screen_rect.y() + (screen_rect.height() - scaled_pixmap.height()) // 2
        splash.move(splash_x, splash_y)
        
        # Show splash screen
        splash.show()
        splash.raise_()
        splash.activateWindow()
        
        # Process events to ensure splash is visible
        app.processEvents()
        
        # Start the accurate timer
        splash.start_timer(duration)
        
        print(f"Splash screen displayed for {duration}ms with slogan: '{splash.slogan}'")
        
        return splash
        
    except Exception as e:
        print(f"Error creating splash screen: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_splash_images_directory():
    """
    Create splash_images directory and some example files for testing.
    This is a utility function for setting up the directory structure.
    """
    try:
        # Create directory relative to current working directory
        splash_dir = os.path.join(os.getcwd(), "gradient_generator", "splash_images")
        os.makedirs(splash_dir, exist_ok=True)
        
        print(f"Created splash images directory: {splash_dir}")
        print("Place your splash images here with names like:")
        print("  - splash_01.png")
        print("  - splash_02.jpg") 
        print("  - splash_03.png")
        print("  - etc.")
        
        return splash_dir
        
    except Exception as e:
        print(f"Error creating splash images directory: {e}")
        return None


# Utility function for testing
def test_splash_screen():
    """Test function to display the splash screen with random images."""
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test 1: Auto-select random image (will use default if no images found)
    print("Test 1: Auto-select random image")
    splash1 = create_splash_screen(app, duration=2000)
    
    if splash1:
        print("Splash screen 1 created successfully")
        
        # Test 2: Create another with different duration after first closes
        def create_second_splash():
            print("Test 2: Creating second splash with different duration")
            splash2 = create_splash_screen(app, duration=3000)
            if splash2:
                print("Splash screen 2 created successfully")
        
        # Schedule second splash after first one should close
        QTimer.singleShot(2500, create_second_splash)
        
        # Exit after all tests
        QTimer.singleShot(6000, app.quit)
        
        sys.exit(app.exec_())
    else:
        print("Failed to create splash screen")


if __name__ == "__main__":
    test_splash_screen()
