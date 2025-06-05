#!/usr/bin/env python3
"""
Animation Renderer Module for Gradient Generator

This module provides centralized animation rendering capabilities for gradient visualization.
Extracted from animated gradient preview and drawing components for better modularity.
"""
import time
import math
from typing import List, Tuple, Optional, Dict, Any, Callable
from PyQt5.QtCore import Qt, QTimer, QRect, QPointF
from PyQt5.QtGui import (QPainter, QColor, QLinearGradient, QRadialGradient, 
                       QConicalGradient, QPen, QBrush)


class AnimationState:
    """Manages animation state and timing."""
    
    def __init__(self):
        self.animation_step = 0
        self.animation_direction = 1
        self.animation_enabled = True
        self.continuous_enabled = False
        self.animation_type = "linear"
        self.is_animating = False
        self.animation_progress = 0.0
        self.speed = 50  # Default speed
    
    def reset(self):
        """Reset animation state."""
        self.animation_step = 0
        self.animation_direction = 1
        self.is_animating = False
        self.animation_progress = 0.0
    
    def update_step(self):
        """Update animation step for continuous animation."""
        if self.animation_enabled and self.continuous_enabled:
            self.animation_step = (self.animation_step + 1) % 360
            
            # Auto-reverse for variety
            if self.animation_step % 180 == 0:
                self.animation_direction *= -1
    
    def get_speed_interval(self) -> int:
        """Get timer interval based on speed (1-100)."""
        return 110 - max(10, min(100, self.speed))


class GradientInterpolator:
    """Handles gradient color interpolation and blending."""
    
    @staticmethod
    def interpolate_color_at_position(
        position: float, 
        color_stops: List[Tuple[float, Tuple[int, int, int]]]
    ) -> Tuple[int, int, int]:
        """Interpolate color at specific position from color stops."""
        position = max(0.0, min(1.0, position))
        
        if not color_stops:
            return (128, 128, 128)
        
        if len(color_stops) == 1:
            return color_stops[0][1]
        
        # Sort stops by position for proper interpolation
        sorted_stops = sorted(color_stops, key=lambda x: x[0])
        
        # Find bracketing stops
        before_stop = None
        after_stop = None
        
        for stop_pos, stop_color in sorted_stops:
            if stop_pos <= position:
                if before_stop is None or stop_pos >= before_stop[0]:
                    before_stop = (stop_pos, stop_color)
            
            if stop_pos >= position:
                if after_stop is None or stop_pos <= after_stop[0]:
                    after_stop = (stop_pos, stop_color)
        
        # Handle edge cases
        if before_stop is None:
            return sorted_stops[0][1]
        if after_stop is None:
            return sorted_stops[-1][1]
        if before_stop[0] == after_stop[0]:
            return before_stop[1]
        
        # Interpolate colors
        pos1, color1 = before_stop
        pos2, color2 = after_stop
        
        blend_factor = (position - pos1) / (pos2 - pos1)
        blend_factor = max(0.0, min(1.0, blend_factor))
        
        return GradientInterpolator.blend_colors(color1, color2, blend_factor)
    
    @staticmethod
    def blend_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                    factor: float) -> Tuple[int, int, int]:
        """Blend two RGB colors using linear interpolation."""
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        
        r = int(r1 * (1 - factor) + r2 * factor)
        g = int(g1 * (1 - factor) + g2 * factor)
        b = int(b1 * (1 - factor) + b2 * factor)
        
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
    
    @staticmethod
    def interpolate_stops_transition(
        start_stops: List[Tuple[float, Tuple[int, int, int]]], 
        end_stops: List[Tuple[float, Tuple[int, int, int]]], 
        progress: float
    ) -> List[Tuple[float, Tuple[int, int, int]]]:
        """Interpolate between two sets of color stops for transitions."""
        if len(start_stops) != len(end_stops):
            return end_stops.copy() if progress > 0.8 else start_stops.copy()
        
        result = []
        for i in range(len(start_stops)):
            start_pos, start_color = start_stops[i]
            end_pos, end_color = end_stops[i]
            
            # Interpolate position and color
            pos = start_pos + (end_pos - start_pos) * progress
            color = GradientInterpolator.blend_colors(start_color, end_color, progress)
            
            result.append((pos, color))
        
        return result


class SeamlessRenderer:
    """Handles seamless gradient preview rendering."""
    
    @staticmethod
    def create_seamless_preview_stops(
        color_stops: List[Tuple[float, Tuple[int, int, int]]]
    ) -> List[Tuple[float, Tuple[int, int, int]]]:
        """Create seamless preview stops with proper ordering."""
        if len(color_stops) < 2:
            return color_stops
        
        # Sort stops to find true first and last
        sorted_stops = sorted(color_stops, key=lambda x: x[0])
        first_color = sorted_stops[0][1]
        last_pos = sorted_stops[-1][0]
        
        # Create preview stops with last color = first color
        preview_stops = []
        for pos, color in color_stops:
            if abs(pos - last_pos) < 1e-6:
                preview_stops.append((pos, first_color))
            else:
                preview_stops.append((pos, color))
        
        return preview_stops
    
    @staticmethod
    def draw_seamless_overlay(
        painter: QPainter, 
        rect: QRect, 
        gradient_model: Any,
        colors: Dict[str, str]
    ):
        """Draw seamless blending overlay indicators."""
        if not gradient_model.get_seamless_blend():
            return
        
        progressive = gradient_model.get_progressive_blending()
        blend_region = gradient_model.get_blend_region()
        
        if progressive:
            # Progressive blending indicators
            blend_width = int(rect.width() * blend_region)
            
            # End blend region
            end_rect = QRect(rect.right() - blend_width, rect.top(), blend_width, rect.height())
            painter.setPen(QColor(100, 200, 100, 120))
            painter.setBrush(QColor(100, 200, 100, 20))
            painter.drawRect(end_rect)
            
            # Start blend region
            start_rect = QRect(rect.left(), rect.top(), blend_width, rect.height())
            painter.setPen(QColor(100, 200, 100, 80))
            painter.setBrush(QColor(100, 200, 100, 10))
            painter.drawRect(start_rect)
            
            painter.setPen(QColor(100, 255, 100))
            painter.drawText(end_rect.adjusted(2, 2, -2, -2), Qt.AlignCenter, "PROG")
        else:
            # Basic seamless indicator
            indicator_width = 20
            end_rect = QRect(rect.right() - indicator_width, rect.top(), indicator_width, rect.height())
            painter.setPen(QColor(255, 200, 100, 150))
            painter.setBrush(QColor(255, 200, 100, 30))
            painter.drawRect(end_rect)
            
            painter.setPen(QColor(255, 255, 100))
            painter.drawText(end_rect.adjusted(2, 2, -2, -2), Qt.AlignCenter, "=1st")
        
        # Wrap arrow
        arrow_y = rect.center().y()
        painter.setPen(QColor(100, 200, 100))
        painter.drawLine(rect.right() - 10, arrow_y, rect.left() + 10, arrow_y)
        painter.drawLine(rect.left() + 10, arrow_y, rect.left() + 20, arrow_y - 5)
        painter.drawLine(rect.left() + 10, arrow_y, rect.left() + 20, arrow_y + 5)
        
        painter.setPen(QColor(221, 221, 221))
        label = "Seamless" if not progressive else "Progressive Seamless"
        painter.drawText(rect.left() + 5, rect.top() + 15, label)
        painter.drawText(rect.left() + 5, rect.top() + 30, "→")


class GradientRenderer:
    """Core gradient rendering engine with animation support."""
    
    def __init__(self):
        self.animation_state = AnimationState()
        self.interpolator = GradientInterpolator()
        self.seamless_renderer = SeamlessRenderer()
    
    def render_linear_gradient(
        self, 
        painter: QPainter, 
        rect: QRect, 
        color_stops: List[Tuple[float, Tuple[int, int, int]]],
        gradient_model: Any = None,
        use_seamless_preview: bool = False
    ):
        """Render linear gradient with animation support."""
        w, h = rect.width(), rect.height()
        
        # Determine which stops to use for rendering
        if use_seamless_preview and gradient_model and gradient_model.get_seamless_blend():
            if hasattr(gradient_model, 'get_seamless_preview_stops'):
                preview_stops = gradient_model.get_seamless_preview_stops()
            else:
                preview_stops = self.seamless_renderer.create_seamless_preview_stops(color_stops)
        else:
            preview_stops = color_stops
        
        if not preview_stops:
            painter.fillRect(rect, QColor(60, 60, 60))
            return
        
        # Enhanced sampling for smooth gradients
        num_samples = max(w * 2, 400)
        
        for i in range(num_samples):
            x = rect.left() + (i * w / num_samples)
            strip_width = max(1.0, w / num_samples) + 0.5
            
            # Calculate position with animation offset
            position = i / num_samples
            if (self.animation_state.animation_enabled and 
                self.animation_state.animation_step > 0):
                offset = (self.animation_state.animation_step / 360.0) * self.animation_state.animation_direction
                position = (position + offset) % 1.0
            
            color = self.interpolator.interpolate_color_at_position(position, preview_stops)
            
            strip_rect = QRect(int(x), rect.top(), int(strip_width), h)
            painter.fillRect(strip_rect, QColor(*color))
        
        # Draw border
        painter.setPen(QColor(85, 85, 85))
        painter.drawRect(rect)
    
    def render_radial_gradient(
        self, 
        painter: QPainter, 
        rect: QRect, 
        color_stops: List[Tuple[float, Tuple[int, int, int]]]
    ):
        """Render radial gradient with animation."""
        center_x = rect.center().x()
        center_y = rect.center().y()
        base_radius = rect.width() // 2
        
        pulse = 0
        if (self.animation_state.animation_enabled and 
            self.animation_state.animation_step > 0):
            pulse = 0.1 * (1 + math.sin(math.radians(
                self.animation_state.animation_step * self.animation_state.animation_direction
            )))
        
        radius = int(base_radius * (1.0 + pulse))
        
        gradient = QRadialGradient(center_x, center_y, radius, center_x, center_y)
        
        sorted_stops = sorted(color_stops, key=lambda x: x[0])
        for position, color in sorted_stops:
            gradient.setColorAt(position, QColor(*color))
        
        painter.fillRect(rect, gradient)
        painter.setPen(QColor(85, 85, 85))
        painter.drawRect(rect)
    
    def render_conical_gradient(
        self, 
        painter: QPainter, 
        rect: QRect, 
        color_stops: List[Tuple[float, Tuple[int, int, int]]]
    ):
        """Render conical gradient with rotation."""
        center_x = rect.center().x()
        center_y = rect.center().y()
        
        angle = 0
        if (self.animation_state.animation_enabled and 
            self.animation_state.animation_step > 0):
            angle = self.animation_state.animation_step * self.animation_state.animation_direction
        
        gradient = QConicalGradient(center_x, center_y, angle)
        
        sorted_stops = sorted(color_stops, key=lambda x: x[0])
        for position, color in sorted_stops:
            gradient.setColorAt(position, QColor(*color))
        
        painter.fillRect(rect, gradient)
        painter.setPen(QColor(85, 85, 85))
        painter.drawRect(rect)
    
    def render_gradient(
        self, 
        painter: QPainter, 
        rect: QRect, 
        color_stops: List[Tuple[float, Tuple[int, int, int]]],
        gradient_model: Any = None,
        use_seamless_preview: bool = False
    ):
        """Render gradient based on current animation type."""
        if not color_stops:
            painter.fillRect(rect, QColor(60, 60, 60))
            painter.setPen(QColor(100, 100, 100))
            painter.drawText(rect, Qt.AlignCenter, "No Gradient Data")
            return
        
        if self.animation_state.animation_type == "linear":
            self.render_linear_gradient(painter, rect, color_stops, gradient_model, use_seamless_preview)
        elif self.animation_state.animation_type == "radial":
            self.render_radial_gradient(painter, rect, color_stops)
        else:  # conical
            self.render_conical_gradient(painter, rect, color_stops)
    
    def draw_color_stops(
        self, 
        painter: QPainter, 
        color_stops: List[Tuple[float, Tuple[int, int, int]]],
        left: int, 
        right: int, 
        y: int,
        selected_index: int = -1,
        hover_index: int = -1,
        stop_radius: int = 10
    ):
        """Draw interactive color stop handles."""
        if not color_stops:
            return
        
        width = right - left
        
        # Track line
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawLine(left, int(y), right, int(y))
        
        # Stop handles
        for i, (position, color) in enumerate(color_stops):
            x = left + (position * width)
            selected = (i == selected_index)
            hovered = (i == hover_index)
            
            self._draw_stop_handle(painter, x, y, color, selected, hovered, stop_radius)
            
            if selected:
                painter.setPen(Qt.white)
                painter.drawText(int(x - 20), int(y + 20), 40, 16, 
                               Qt.AlignCenter, f"{position:.2f}")
    
    def _draw_stop_handle(
        self, 
        painter: QPainter, 
        x: float, 
        y: float, 
        color: Tuple[int, int, int], 
        selected: bool, 
        hovered: bool,
        stop_radius: int
    ):
        """Draw individual stop handle."""
        radius = stop_radius + (1 if selected else 0.5 if hovered else 0)
        
        # Connection line
        painter.setPen(QColor(140, 140, 140))
        painter.drawLine(int(x), int(y - 8), int(x), int(y))
        
        # Outer ring
        outer_color = Qt.white if selected else QColor(200, 200, 200)
        painter.setPen(QPen(outer_color, 2 if selected else 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(x, y - 8), radius, radius)
        
        # Inner color
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(*color))
        painter.drawEllipse(QPointF(x, y - 8), radius - 2, radius - 2)
        
        # Selection glow
        if selected:
            painter.setPen(QPen(QColor(255, 255, 255, 100), 3))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(x, y - 8), radius + 2, radius + 2)
    
    def draw_add_hints(
        self, 
        painter: QPainter, 
        gradient_rect: QRect,
        mouse_pos: Optional[QPointF] = None
    ):
        """Draw hints for adding stops."""
        if not mouse_pos or not gradient_rect.contains(mouse_pos.toPoint()):
            return
        
        position = (mouse_pos.x() - gradient_rect.left()) / gradient_rect.width()
        position = max(0.0, min(1.0, position))
        x = gradient_rect.left() + position * gradient_rect.width()
        
        # Hint line
        painter.setPen(QPen(QColor(255, 255, 255, 150), 2))
        painter.drawLine(int(x), gradient_rect.top(), int(x), gradient_rect.bottom())
        
        # Plus icon
        painter.setPen(QPen(QColor(255, 255, 255, 200), 2))
        plus_y = gradient_rect.bottom() + 5
        painter.drawLine(int(x - 4), plus_y, int(x + 4), plus_y)
        painter.drawLine(int(x), plus_y - 4, int(x), plus_y + 4)
    
    def draw_seamless_overlay(
        self, 
        painter: QPainter, 
        rect: QRect, 
        gradient_model: Any
    ):
        """Draw seamless overlay if enabled."""
        if gradient_model.get_preview_overlay():
            self.seamless_renderer.draw_seamless_overlay(
                painter, rect, gradient_model, {}
            )
    
    def set_animation_type(self, animation_type: str):
        """Set animation type."""
        if animation_type in ["linear", "radial", "conical"]:
            self.animation_state.animation_type = animation_type
    
    def set_animation_enabled(self, enabled: bool):
        """Enable/disable animation."""
        self.animation_state.animation_enabled = enabled
    
    def set_continuous_enabled(self, enabled: bool):
        """Enable/disable continuous animation."""
        self.animation_state.continuous_enabled = enabled
    
    def set_animation_step(self, step: int):
        """Set animation step manually."""
        self.animation_state.animation_step = step
    
    def set_animation_direction(self, direction: int):
        """Set animation direction."""
        self.animation_state.animation_direction = direction
    
    def set_animation_speed(self, speed: int):
        """Set animation speed (1-100)."""
        self.animation_state.speed = max(1, min(100, speed))
    
    def update_animation_step(self):
        """Update animation step for continuous animation."""
        self.animation_state.update_step()
    
    def get_animation_state(self) -> Dict[str, Any]:
        """Get current animation state."""
        return {
            'step': self.animation_state.animation_step,
            'direction': self.animation_state.animation_direction,
            'enabled': self.animation_state.animation_enabled,
            'continuous': self.animation_state.continuous_enabled,
            'type': self.animation_state.animation_type,
            'is_animating': self.animation_state.is_animating,
            'progress': self.animation_state.animation_progress,
            'speed': self.animation_state.speed
        }
    
    def reset_animation(self):
        """Reset animation to initial state."""
        self.animation_state.reset()


class AnimationTimer:
    """Manages animation timing and callbacks."""
    
    def __init__(self, update_callback: Callable):
        self.update_callback = update_callback
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timeout)
        self.is_running = False
        self.interval = 50  # Default 20fps
    
    def start(self, interval: int = None):
        """Start the animation timer."""
        if interval is not None:
            self.interval = interval
        
        self.timer.start(self.interval)
        self.is_running = True
    
    def stop(self):
        """Stop the animation timer."""
        self.timer.stop()
        self.is_running = False
    
    def set_interval(self, interval: int):
        """Set timer interval."""
        self.interval = interval
        if self.is_running:
            self.timer.stop()
            self.timer.start(interval)
    
    def _on_timeout(self):
        """Handle timer timeout."""
        if self.update_callback:
            self.update_callback()


# Factory functions for easy integration
def create_gradient_renderer() -> GradientRenderer:
    """Create a new gradient renderer instance."""
    return GradientRenderer()


def create_animation_timer(update_callback: Callable) -> AnimationTimer:
    """Create a new animation timer instance."""
    return AnimationTimer(update_callback)


# Utility functions
def interpolate_color_at_position(
    position: float, 
    color_stops: List[Tuple[float, Tuple[int, int, int]]]
) -> Tuple[int, int, int]:
    """Standalone function for color interpolation."""
    return GradientInterpolator.interpolate_color_at_position(position, color_stops)


def blend_colors(
    color1: Tuple[int, int, int], 
    color2: Tuple[int, int, int], 
    factor: float
) -> Tuple[int, int, int]:
    """Standalone function for color blending."""
    return GradientInterpolator.blend_colors(color1, color2, factor)


def create_seamless_preview_stops(
    color_stops: List[Tuple[float, Tuple[int, int, int]]]
) -> List[Tuple[float, Tuple[int, int, int]]]:
    """Standalone function for creating seamless preview stops."""
    return SeamlessRenderer.create_seamless_preview_stops(color_stops)


# Export all public classes and functions
__all__ = [
    'AnimationState',
    'GradientInterpolator', 
    'SeamlessRenderer',
    'GradientRenderer',
    'AnimationTimer',
    'create_gradient_renderer',
    'create_animation_timer',
    'interpolate_color_at_position',
    'blend_colors',
    'create_seamless_preview_stops'
]
