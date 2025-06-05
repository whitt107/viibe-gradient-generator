#!/usr/bin/env python3
"""
Run Script for VIIBE Gradient Generator

This script provides a simple way to run the application directly
without installing it as a package.
"""
import sys
import os

# Add parent directory to path so we can import the package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the main function from the package
from gradient_generator.main import main

if __name__ == "__main__":
    sys.exit(main())