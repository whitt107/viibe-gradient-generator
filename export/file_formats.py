#!/usr/bin/env python3
"""
Enhanced Gradient File Export Module for Gradient Generator

This module implements functions for saving and loading gradients in
various file formats, including MAP (Ultra Fractal/Apophysis) and UGR (JWildfire),
with support for up to 64 color stops per gradient and batch MAP export functionality.
"""
import os
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
import datetime
from typing import List, Tuple, Optional


def save_map_format(gradient, file_path):
    """
    Save gradient in MAP format (JWildfire compatible).
    
    The MAP format used by JWildfire is a simple format where each line
    contains RGB values in 0-255 range, space-separated.
    
    Args:
        gradient: Gradient object to save
        file_path: Path where the MAP file will be saved
        
    Returns:
        True if save was successful, False otherwise
    """
    try:
        with open(file_path, 'w') as f:
            # Get color stops and sort by position
            color_stops = gradient.get_color_stops()
            color_stops.sort(key=lambda x: x[0])
            
            # Generate 256 color entries by sampling the gradient
            num_samples = 256
            for i in range(num_samples):
                position = i / (num_samples - 1)
                color = gradient.get_interpolated_color(position)
                r, g, b = color
                
                # Write RGB values separated by spaces
                f.write(f"{r:3d} {g:3d} {b:3d}\n")
        
        return True
    
    except Exception as e:
        print(f"Error saving MAP file: {e}")
        return False


def export_multiple_maps_batch(gradients_data, output_directory, base_name="gradient", 
                              start_number=1, zero_padding=2):
    """
    Export multiple gradients as sequential MAP files.
    
    Args:
        gradients_data: List of (gradient, name) tuples or list of gradient objects
        output_directory: Directory where MAP files will be saved
        base_name: Base name for the files (default: "gradient")
        start_number: Starting number for the sequence (default: 1)
        zero_padding: Number of digits for zero-padding (default: 2, gives 01, 02, etc.)
        
    Returns:
        Tuple (success_count, total_count, failed_files_list)
    """
    try:
        # Ensure output directory exists
        os.makedirs(output_directory, exist_ok=True)
        
        # Process gradients data to handle both formats
        gradients = []
        if gradients_data:
            # Check if it's a list of tuples or just gradient objects
            first_item = gradients_data[0]
            if isinstance(first_item, tuple):
                # List of (gradient, name) tuples
                gradients = [gradient for gradient, name in gradients_data]
            else:
                # List of gradient objects
                gradients = gradients_data
        
        success_count = 0
        failed_files = []
        total_count = len(gradients)
        
        for i, gradient in enumerate(gradients):
            try:
                # Generate filename with zero-padding
                file_number = start_number + i
                file_name = f"{base_name}_{file_number:0{zero_padding}d}.map"
                file_path = os.path.join(output_directory, file_name)
                
                # Save the MAP file
                if save_map_format(gradient, file_path):
                    success_count += 1
                    print(f"Exported: {file_name}")
                else:
                    failed_files.append(file_name)
                    print(f"Failed to export: {file_name}")
                    
            except Exception as e:
                file_name = f"{base_name}_{start_number + i:0{zero_padding}d}.map"
                failed_files.append(file_name)
                print(f"Error exporting {file_name}: {e}")
        
        return success_count, total_count, failed_files
        
    except Exception as e:
        print(f"Error in batch MAP export: {e}")
        return 0, len(gradients_data) if gradients_data else 0, []


def export_gradient_list_as_maps(gradient_list_panel, output_directory, base_name="gradient"):
    """
    Export all gradients from a gradient list panel as sequential MAP files.
    
    Args:
        gradient_list_panel: GradientListPanel instance with gradients
        output_directory: Directory where MAP files will be saved
        base_name: Base name for the files
        
    Returns:
        Tuple (success_count, total_count, failed_files_list)
    """
    if not hasattr(gradient_list_panel, 'gradients') or not gradient_list_panel.gradients:
        return 0, 0, []
    
    return export_multiple_maps_batch(
        gradient_list_panel.gradients, 
        output_directory, 
        base_name
    )


def export_maps_with_custom_names(gradients_with_names, output_directory):
    """
    Export gradients as MAP files using their custom names.
    
    Args:
        gradients_with_names: List of (gradient, custom_name) tuples
        output_directory: Directory where MAP files will be saved
        
    Returns:
        Tuple (success_count, total_count, failed_files_list)
    """
    try:
        # Ensure output directory exists
        os.makedirs(output_directory, exist_ok=True)
        
        success_count = 0
        failed_files = []
        total_count = len(gradients_with_names)
        
        for gradient, custom_name in gradients_with_names:
            try:
                # Clean the custom name for use as filename
                safe_name = "".join(c for c in custom_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_name = safe_name.replace(' ', '_')
                
                if not safe_name:
                    safe_name = "unnamed_gradient"
                
                file_name = f"{safe_name}.map"
                file_path = os.path.join(output_directory, file_name)
                
                # Handle duplicate filenames by adding a number
                counter = 1
                original_file_path = file_path
                while os.path.exists(file_path):
                    name_part, ext = os.path.splitext(original_file_path)
                    file_path = f"{name_part}_{counter}{ext}"
                    counter += 1
                
                # Save the MAP file
                if save_map_format(gradient, file_path):
                    success_count += 1
                    print(f"Exported: {os.path.basename(file_path)}")
                else:
                    failed_files.append(os.path.basename(file_path))
                    print(f"Failed to export: {os.path.basename(file_path)}")
                    
            except Exception as e:
                file_name = f"{custom_name}.map"
                failed_files.append(file_name)
                print(f"Error exporting {file_name}: {e}")
        
        return success_count, total_count, failed_files
        
    except Exception as e:
        print(f"Error in custom names MAP export: {e}")
        return 0, len(gradients_with_names), []


def load_map_format(file_path):
    """
    Load gradient from MAP format, supporting up to 64 color stops.
    
    Args:
        file_path: Path to the MAP file
        
    Returns:
        Gradient object or None if loading failed
    """
    from ..core.gradient import Gradient
    
    try:
        gradient = Gradient()
        
        # Clear default stops
        gradient._color_stops = []
        
        # Read the MAP file
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Process lines
        colors = []
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Parse RGB values
            try:
                parts = line.split()
                if len(parts) >= 3:
                    r = int(parts[0])
                    g = int(parts[1])
                    b = int(parts[2])
                    colors.append((r, g, b))
            except ValueError:
                continue
        
        # Create color stops from colors
        if colors:
            # Sample the colors to create gradient stops
            # Use more stops for better representation, up to MAX_COLOR_STOPS
            MAX_STOPS = 64  # Maximum number of color stops
            
            # Determine number of stops to create (min 2, max MAX_STOPS)
            # For many colors, use sqrt to reduce the number of stops while maintaining representation
            import math
            num_stops = min(MAX_STOPS, max(10, math.ceil(math.sqrt(len(colors)))))
            
            for i in range(num_stops):
                idx = int(i * (len(colors) - 1) / (num_stops - 1))
                position = i / (num_stops - 1)
                gradient.add_color_stop(position, colors[idx])
        
        # If no stops were loaded, add default stops
        if not gradient._color_stops:
            gradient.reset()
        else:
            # Sort stops by position
            gradient.sort_color_stops()
        
        return gradient
    
    except Exception as e:
        print(f"Error loading MAP file: {e}")
        return None


def save_ugr_format(gradient, file_path, gradient_name=None):
    """
    Save gradient in UGR format (JWildfire compatible).
    
    UGR format is XML-based and used by JWildfire.
    Standard structure:
    <GradientUGR>
        <gradient name="GradientName" cat="Category" data="..." smooth="T">
            <color index="0" rgb="255|0|0"/>
            ...
        </gradient>
    </GradientUGR>
    
    Args:
        gradient: Gradient object to save
        file_path: Path where the UGR file will be saved
        gradient_name: Optional name for the gradient (defaults to gradient's name)
        
    Returns:
        True if save was successful, False otherwise
    """
    try:
        # Use gradient name if not provided
        if gradient_name is None:
            gradient_name = gradient.get_name() or "Gradient"
        
        # Create XML document
        root = ET.Element("gradientUGR")
        
        # Add gradient element
        gradient_elem = ET.SubElement(root, "gradient")
        gradient_elem.set("name", gradient_name)
        gradient_elem.set("cat", gradient.get_ugr_category())
        gradient_elem.set("smooth", "T")  # Smooth gradient
        
        # Get color stops and sort by position
        color_stops = gradient.get_color_stops()
        color_stops.sort(key=lambda x: x[0])
        
        # Add color elements
        # JWildfire uses positions from 0-399
        for position, color in color_stops:
            r, g, b = color
            color_elem = ET.SubElement(gradient_elem, "color")
            
            # JWildfire uses integer position (0-399)
            pos_int = int(position * 399)
            
            # Add color attributes
            color_elem.set("index", str(pos_int))
            color_elem.set("rgb", f"{r}|{g}|{b}")
        
        # Format XML with pretty printing
        rough_string = ET.tostring(root, 'unicode')
        reparsed = minidom.parseString(rough_string)
        xmlstr = reparsed.toprettyxml(indent="  ", newl="\n", encoding=None).strip()
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xmlstr)
        
        return True
    
    except Exception as e:
        print(f"Error saving UGR file: {e}")
        return False


def load_ugr_format(file_path):
    """
    Load gradient from UGR format, supporting up to 64 color stops per gradient.
    
    Args:
        file_path: Path to the UGR file
        
    Returns:
        List of Gradient objects or empty list if loading failed
    """
    from ..core.gradient import Gradient
    
    try:
        # Parse XML
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        gradients = []
        MAX_STOPS = 64  # Maximum number of color stops per gradient
        
        # Process each gradient element
        for gradient_elem in root.findall(".//gradient"):
            gradient = Gradient()
            
            # Clear default stops
            gradient._color_stops = []
            
            # Get metadata
            gradient.set_name(gradient_elem.get("name", "Untitled"))
            gradient.set_ugr_category(gradient_elem.get("cat", "Custom"))
            
            # Process color stops - collect all and then filter if needed
            all_stops = []
            for color_elem in gradient_elem.findall("color"):
                # Get position (convert from 0-399 to 0-1)
                index = int(color_elem.get("index", "0"))
                position = index / 399.0
                
                # Get color (format: "r|g|b")
                rgb_str = color_elem.get("rgb", "0|0|0")
                rgb_parts = rgb_str.split("|")
                
                if len(rgb_parts) >= 3:
                    r = int(rgb_parts[0])
                    g = int(rgb_parts[1])
                    b = int(rgb_parts[2])
                    
                    # Add to all stops list
                    all_stops.append((position, (r, g, b)))
            
            # Sort by position
            all_stops.sort(key=lambda x: x[0])
            
            # If we have too many stops, sample them to reduce to MAX_STOPS
            if len(all_stops) > MAX_STOPS:
                sampled_stops = []
                
                # Always include first and last stop
                sampled_stops.append(all_stops[0])
                
                # Sample middle stops
                for i in range(1, MAX_STOPS - 1):
                    idx = i * (len(all_stops) - 2) // (MAX_STOPS - 2) + 1
                    sampled_stops.append(all_stops[idx])
                
                # Add last stop
                sampled_stops.append(all_stops[-1])
                
                # Use sampled stops
                all_stops = sampled_stops
            
            # Add stops to gradient
            for position, color in all_stops:
                gradient.add_color_stop(position, color)
            
            # If no stops were loaded, add default stops
            if not gradient._color_stops:
                gradient.reset()
            else:
                # Sort stops by position
                gradient.sort_color_stops()
            
            gradients.append(gradient)
        
        return gradients
    
    except Exception as e:
        print(f"Error loading UGR file: {e}")
        return []


def export_multiple_gradients_ugr(gradients, file_path):
    """
    Export multiple gradients to a single UGR file.
    
    Args:
        gradients: List of (gradient, name) tuples
        file_path: Path where the UGR file will be saved
        
    Returns:
        True if export was successful, False otherwise
    """
    try:
        # Create XML document
        root = ET.Element("gradientUGR")
        
        # Add metadata for the UGR file
        root.set("version", "1.0")
        root.set("date", datetime.datetime.now().strftime("%Y-%m-%d"))
        root.set("generator", "VIIBE Gradient Generator")
        
        # Add gradient elements
        for gradient, name in gradients:
            gradient_elem = ET.SubElement(root, "gradient")
            gradient_elem.set("name", name or gradient.get_name() or "Gradient")
            gradient_elem.set("cat", gradient.get_ugr_category())
            gradient_elem.set("smooth", "T")
            
            # Get color stops and sort by position
            color_stops = gradient.get_color_stops()
            color_stops.sort(key=lambda x: x[0])
            
            # Add color elements
            for position, color in color_stops:
                r, g, b = color
                color_elem = ET.SubElement(gradient_elem, "color")
                
                # JWildfire uses integer position (0-399)
                pos_int = int(position * 399)
                
                # Add color attributes
                color_elem.set("index", str(pos_int))
                color_elem.set("rgb", f"{r}|{g}|{b}")
        
        # Format XML with pretty printing
        rough_string = ET.tostring(root, 'unicode')
        reparsed = minidom.parseString(rough_string)
        xmlstr = reparsed.toprettyxml(indent="  ", newl="\n", encoding=None).strip()
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xmlstr)
        
        return True
    
    except Exception as e:
        print(f"Error exporting multiple gradients: {e}")
        return False


def import_jwf_palette(file_path):
    """
    Import a JWildfire palette file (.jwf) and convert it to a gradient.
    
    Args:
        file_path: Path to the JWF palette file
        
    Returns:
        Gradient object or None if import failed
    """
    from ..core.gradient import Gradient
    
    try:
        # Create a new gradient
        gradient = Gradient()
        gradient._color_stops = []
        
        # Read the palette file
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # JWF palette format has RGB values separated by space in each line
        # The first lines might be header information (non-numeric)
        colors = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to parse as RGB values
            try:
                parts = line.split()
                if len(parts) >= 3:
                    r = int(parts[0])
                    g = int(parts[1])
                    b = int(parts[2])
                    colors.append((r, g, b))
            except ValueError:
                # Not a color line, could be header
                continue
        
        # If we have colors, create a gradient
        if colors:
            # Determine how many stops to use (max 64)
            MAX_STOPS = 64
            num_stops = min(MAX_STOPS, max(10, len(colors)))
            
            # Create evenly distributed stops
            for i in range(num_stops):
                # Sample colors at regular intervals
                idx = int(i * (len(colors) - 1) / (num_stops - 1))
                position = i / (num_stops - 1)
                gradient.add_color_stop(position, colors[idx])
            
            # Set gradient name based on file name
            import os
            base_name = os.path.basename(file_path)
            name, _ = os.path.splitext(base_name)
            gradient.set_name(f"Imported from {name}")
            
            return gradient
        else:
            return None
    
    except Exception as e:
        print(f"Error importing JWF palette: {e}")
        return None


def export_jwf_palette(gradient, file_path, num_samples=256):
    """
    Export a gradient as a JWildfire palette file (.jwf).
    
    Args:
        gradient: Gradient object to export
        file_path: Path where to save the palette file
        num_samples: Number of color samples to generate (default: 256)
        
    Returns:
        True if export was successful, False otherwise
    """
    try:
        with open(file_path, 'w') as f:
            # Write header
            f.write(f"# JWildfire Palette - {gradient.get_name()}\n")
            f.write(f"# Exported from VIIBE Gradient Generator\n")
            f.write(f"# Date: {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"# Samples: {num_samples}\n")
            f.write("\n")
            
            # Generate color samples
            for i in range(num_samples):
                position = i / (num_samples - 1) if num_samples > 1 else 0
                color = gradient.get_interpolated_color(position)
                r, g, b = color
                
                # Write RGB values
                f.write(f"{r} {g} {b}\n")
            
        return True
        
    except Exception as e:
        print(f"Error exporting JWF palette: {e}")
        return False


# Utility functions for batch operations
def create_gradient_export_summary(success_count, total_count, failed_files):
    """
    Create a summary report for batch export operations.
    
    Args:
        success_count: Number of successfully exported files
        total_count: Total number of files attempted
        failed_files: List of failed file names
        
    Returns:
        Dictionary containing export summary
    """
    return {
        'success_count': success_count,
        'total_count': total_count,
        'failed_count': len(failed_files),
        'failed_files': failed_files,
        'success_rate': (success_count / total_count * 100) if total_count > 0 else 0
    }


def validate_export_directory(directory_path):
    """
    Validate that a directory exists and is writable for export.
    
    Args:
        directory_path: Path to validate
        
    Returns:
        Tuple (is_valid, error_message)
    """
    try:
        # Check if directory exists
        if not os.path.exists(directory_path):
            try:
                os.makedirs(directory_path, exist_ok=True)
            except Exception as e:
                return False, f"Cannot create directory: {e}"
        
        # Check if directory is writable
        if not os.access(directory_path, os.W_OK):
            return False, "Directory is not writable"
        
        return True, ""
        
    except Exception as e:
        return False, f"Directory validation error: {e}"


# Example usage and testing functions
if __name__ == "__main__":
    print("Enhanced File Formats Module with Batch MAP Export")
    print("Available functions:")
    print("- save_map_format(gradient, file_path)")
    print("- export_multiple_maps_batch(gradients_data, output_directory, base_name)")
    print("- export_gradient_list_as_maps(gradient_list_panel, output_directory)")
    print("- export_maps_with_custom_names(gradients_with_names, output_directory)")
    print("\nBatch export features:")
    print("1. Sequential naming (name_01.map, name_02.map, etc.)")
    print("2. Custom names export")
    print("3. Validation and error reporting")
    print("4. Progress tracking and summaries")
