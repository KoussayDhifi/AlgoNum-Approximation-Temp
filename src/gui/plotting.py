"""
plotting.py - Graph rendering system for pygame
"""

import pygame
import numpy as np


class PlotArea:
    """
    Graph plotting area with axes, grid, and data visualization.
    
    Parameters
    ----------
    x, y : int
        Top-left position
    width, height : int
        Size
    """
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.padding = 50
        
        # Plot area (accounting for axes)
        self.plot_x = x + self.padding
        self.plot_y = y + self.padding
        self.plot_width = width - self.padding * 2
        self.plot_height = height - self.padding * 2
        
        # Data limits
        self.x_min = 0
        self.x_max = 1
        self.y_min = 0
        self.y_max = 1
        self.auto_scale = True
        
        # Drawing state
        self.font_small = pygame.font.Font(None, 16)
        self.font_label = pygame.font.Font(None, 20)
        self.background_color = (20, 20, 30)
        self.grid_color = (40, 40, 60)
        self.axis_color = (150, 150, 180)
        self.text_color = (200, 200, 200)
    
    def set_data_limits(self, x_min, x_max, y_min, y_max):
        """Set manual data limits."""
        self.x_min = float(x_min)
        self.x_max = float(x_max)
        self.y_min = float(y_min)
        self.y_max = float(y_max)
        self.auto_scale = False
    
    def auto_fit(self, x_data, y_data):
        """Automatically fit limits to data."""
        if x_data is None or len(x_data) == 0:
            return
        
        x_data = np.asarray(x_data)
        y_data = np.asarray(y_data)
        
        self.x_min = float(np.min(x_data))
        self.x_max = float(np.max(x_data))
        self.y_min = float(np.min(y_data))
        self.y_max = float(np.max(y_data))
        
        # Add 10% padding
        x_range = self.x_max - self.x_min
        y_range = self.y_max - self.y_min
        
        if x_range == 0:
            self.x_min -= 0.5
            self.x_max += 0.5
        else:
            self.x_min -= x_range * 0.1
            self.x_max += x_range * 0.1
        
        if y_range == 0:
            self.y_min -= 0.5
            self.y_max += 0.5
        else:
            self.y_min -= y_range * 0.1
            self.y_max += y_range * 0.1
        
        self.auto_scale = True
    
    def _data_to_screen(self, x, y):
        """Convert data coordinates to screen coordinates."""
        # Normalize to [0, 1]
        norm_x = (x - self.x_min) / (self.x_max - self.x_min) if self.x_max != self.x_min else 0
        norm_y = (y - self.y_min) / (self.y_max - self.y_min) if self.y_max != self.y_min else 0
        
        # Clamp
        norm_x = max(0, min(1, norm_x))
        norm_y = max(0, min(1, norm_y))
        
        # Convert to screen coordinates (y is inverted)
        screen_x = self.plot_x + norm_x * self.plot_width
        screen_y = self.plot_y + self.plot_height - norm_y * self.plot_height
        
        return int(screen_x), int(screen_y)
    
    def _draw_grid(self, surface):
        """Draw grid lines."""
        # Vertical grid lines
        num_x_lines = 5
        for i in range(num_x_lines + 1):
            x_screen = self.plot_x + (i / num_x_lines) * self.plot_width
            pygame.draw.line(surface, self.grid_color,
                           (int(x_screen), self.plot_y),
                           (int(x_screen), self.plot_y + self.plot_height), 1)
        
        # Horizontal grid lines
        num_y_lines = 5
        for i in range(num_y_lines + 1):
            y_screen = self.plot_y + (i / num_y_lines) * self.plot_height
            pygame.draw.line(surface, self.grid_color,
                           (self.plot_x, int(y_screen)),
                           (self.plot_x + self.plot_width, int(y_screen)), 1)
    
    def _draw_axes(self, surface):
        """Draw axes and labels."""
        # Axes
        pygame.draw.line(surface, self.axis_color,
                        (self.plot_x, self.plot_y + self.plot_height),
                        (self.plot_x + self.plot_width, self.plot_y + self.plot_height), 2)
        pygame.draw.line(surface, self.axis_color,
                        (self.plot_x, self.plot_y),
                        (self.plot_x, self.plot_y + self.plot_height), 2)
        
        # X-axis labels
        num_x_ticks = 5
        for i in range(num_x_ticks + 1):
            x_val = self.x_min + (i / num_x_ticks) * (self.x_max - self.x_min)
            x_screen = self.plot_x + (i / num_x_ticks) * self.plot_width
            
            # Tick
            pygame.draw.line(surface, self.axis_color,
                           (int(x_screen), self.plot_y + self.plot_height),
                           (int(x_screen), self.plot_y + self.plot_height + 5), 1)
            
            # Label
            label = f"{x_val:.2f}"
            text_surf = self.font_small.render(label, True, self.text_color)
            text_rect = text_surf.get_rect(midtop=(int(x_screen), self.plot_y + self.plot_height + 10))
            surface.blit(text_surf, text_rect)
        
        # Y-axis labels
        num_y_ticks = 5
        for i in range(num_y_ticks + 1):
            y_val = self.y_min + (i / num_y_ticks) * (self.y_max - self.y_min)
            y_screen = self.plot_y + self.plot_height - (i / num_y_ticks) * self.plot_height
            
            # Tick
            pygame.draw.line(surface, self.axis_color,
                           (self.plot_x - 5, int(y_screen)),
                           (self.plot_x, int(y_screen)), 1)
            
            # Label
            label = f"{y_val:.2f}"
            text_surf = self.font_small.render(label, True, self.text_color)
            text_rect = text_surf.get_rect(midright=(self.plot_x - 10, int(y_screen)))
            surface.blit(text_surf, text_rect)
    
    def plot_points(self, surface, x_data, y_data, color=(200, 100, 100), size=5):
        """Plot discrete data points."""
        if x_data is None or len(x_data) == 0:
            return
        
        x_data = np.asarray(x_data, dtype=float)
        y_data = np.asarray(y_data, dtype=float)
        
        for x, y in zip(x_data, y_data):
            screen_x, screen_y = self._data_to_screen(x, y)
            pygame.draw.circle(surface, color, (screen_x, screen_y), size)
    
    def plot_line(self, surface, x_data, y_data, color=(100, 200, 100), width=2):
        """Plot a continuous line."""
        if x_data is None or len(x_data) < 2:
            return
        
        x_data = np.asarray(x_data, dtype=float)
        y_data = np.asarray(y_data, dtype=float)
        
        points = [self._data_to_screen(x, y) for x, y in zip(x_data, y_data)]
        
        # Draw line segments
        for i in range(len(points) - 1):
            pygame.draw.line(surface, color, points[i], points[i + 1], width)
    
    def fill_under_curve(self, surface, x_data, y_data, color=(100, 200, 100, 50)):
        """Fill area under curve."""
        if x_data is None or len(x_data) < 2:
            return
        
        x_data = np.asarray(x_data, dtype=float)
        y_data = np.asarray(y_data, dtype=float)
        
        # Create polygon points
        points = [self._data_to_screen(x, y) for x, y in zip(x_data, y_data)]
        
        # Add baseline points
        baseline_points = [
            self._data_to_screen(x_data[0], self.y_min),
            *points,
            self._data_to_screen(x_data[-1], self.y_min)
        ]
        
        if len(baseline_points) >= 3:
            # Draw filled polygon
            try:
                pygame.draw.polygon(surface, color, baseline_points)
            except:
                # Fallback if polygon fails
                pass
    
    def draw_rectangles(self, surface, x_data, y_data, color=(100, 150, 200)):
        """Draw rectangles for integration visualization."""
        if x_data is None or len(x_data) < 2:
            return
        
        x_data = np.asarray(x_data, dtype=float)
        y_data = np.asarray(y_data, dtype=float)
        
        # Draw rectangles for each interval
        for i in range(len(x_data) - 1):
            x1, y1 = self._data_to_screen(x_data[i], self.y_min)
            x2, y2 = self._data_to_screen(x_data[i + 1], y_data[i])
            
            width = max(1, x2 - x1)
            height = max(1, y1 - y2)
            
            rect = pygame.Rect(x1, y2, width, height)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (150, 150, 150), rect, 1)
    
    def draw(self, surface):
        """Draw the plot area."""
        # Background
        pygame.draw.rect(surface, self.background_color, self.rect)
        pygame.draw.rect(surface, (80, 80, 100), self.rect, 2)
        
        # Content
        self._draw_grid(surface)
        self._draw_axes(surface)


class Legend:
    """Simple legend for plots."""
    
    def __init__(self, x, y, font=None):
        self.x = x
        self.y = y
        self.font = font or pygame.font.Font(None, 16)
        self.items = []  # List of (label, color) tuples
    
    def add_item(self, label, color):
        """Add item to legend."""
        self.items.append((label, color))
    
    def clear(self):
        """Clear all items."""
        self.items.clear()
    
    def draw(self, surface):
        """Draw legend."""
        if not self.items:
            return
        
        box_width = 200
        box_height = len(self.items) * 20 + 10
        
        # Background
        pygame.draw.rect(surface, (30, 30, 40), 
                        (self.x, self.y, box_width, box_height))
        pygame.draw.rect(surface, (150, 150, 180), 
                        (self.x, self.y, box_width, box_height), 1)
        
        # Items
        for i, (label, color) in enumerate(self.items):
            item_y = self.y + 5 + i * 20
            
            # Color square
            pygame.draw.rect(surface, color, (self.x + 5, item_y, 12, 12))
            
            # Label
            text_surf = self.font.render(label, True, (200, 200, 200))
            surface.blit(text_surf, (self.x + 22, item_y - 2))
