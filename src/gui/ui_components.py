"""
ui_components.py - Reusable UI elements (Button, Slider, Dropdown)
"""

import pygame
import numpy as np


class UIComponent:
    """Base class for all UI components."""
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.hovered = False
        self.active = False
    
    def update(self, mouse_pos):
        """Update component state based on mouse position."""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def handle_event(self, event):
        """Handle pygame events. Override in subclasses."""
        pass
    
    def draw(self, surface):
        """Draw component on surface. Override in subclasses."""
        pass


class Button(UIComponent):
    """
    Clickable button with text.
    
    Parameters
    ----------
    x, y : int
        Position
    width, height : int
        Size
    text : str
        Button label
    callback : callable
        Function called on click
    color : tuple
        RGB color
    text_color : tuple
        RGB text color
    font : pygame.font.Font
        Font for text
    """
    
    def __init__(self, x, y, width, height, text, callback=None,
                 color=(100, 100, 100), text_color=(255, 255, 255),
                 font=None):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color
        self.color_hover = tuple(min(c + 40, 255) for c in color)
        self.text_color = text_color
        self.font = font or pygame.font.Font(None, 24)
        self.pressed = False
    
    def handle_event(self, event):
        """Handle mouse click."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                self.pressed = True
                if self.callback:
                    self.callback()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.pressed = False
    
    def draw(self, surface):
        """Draw button with text."""
        color = self.color_hover if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class Slider(UIComponent):
    """
    Horizontal slider for numeric input.
    
    Parameters
    ----------
    x, y : int
        Position
    width : int
        Slider width
    min_val, max_val : float
        Range
    initial_val : float
        Starting value
    label : str
        Label text
    on_change : callable
        Callback when value changes
    font : pygame.font.Font
        Font for label
    """
    
    def __init__(self, x, y, width, min_val, max_val, initial_val=None,
                 label="", on_change=None, font=None):
        height = 20
        super().__init__(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val if initial_val is not None else (min_val + max_val) / 2
        self.label = label
        self.on_change = on_change
        self.font = font or pygame.font.Font(None, 18)
        self.dragging = False
        self.handle_radius = 8
    
    def _value_to_x(self):
        """Convert value to x position."""
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        return self.rect.x + ratio * self.rect.width
    
    def _x_to_value(self, x):
        """Convert x position to value."""
        ratio = max(0, min(1, (x - self.rect.x) / self.rect.width))
        return self.min_val + ratio * (self.max_val - self.min_val)
    
    def handle_event(self, event):
        """Handle slider interaction."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            old_value = self.value
            self.value = self._x_to_value(event.pos[0])
            if self.value != old_value and self.on_change:
                self.on_change(self.value)
    
    def update(self, mouse_pos):
        """Update slider state."""
        super().update(mouse_pos)
        handle_x = self._value_to_x()
        handle_rect = pygame.Rect(handle_x - self.handle_radius, self.rect.y - 5,
                                  self.handle_radius * 2, self.rect.height + 10)
        self.hovered = handle_rect.collidepoint(mouse_pos)
    
    def draw(self, surface):
        """Draw slider."""
        # Track
        track_y = self.rect.centery
        pygame.draw.line(surface, (150, 150, 150), 
                        (self.rect.left, track_y),
                        (self.rect.right, track_y), 2)
        
        # Handle
        handle_x = self._value_to_x()
        handle_color = (100, 150, 255) if self.hovered else (80, 120, 200)
        pygame.draw.circle(surface, handle_color, (int(handle_x), track_y), 
                          self.handle_radius)
        
        # Label and value
        text = f"{self.label}: {self.value:.3f}"
        text_surf = self.font.render(text, True, (200, 200, 200))
        surface.blit(text_surf, (self.rect.x, self.rect.y - 20))


class Dropdown(UIComponent):
    """
    Dropdown menu for selecting from options.
    
    Parameters
    ----------
    x, y : int
        Position
    width : int
        Width
    options : list
        List of option strings
    initial_index : int
        Initially selected index
    label : str
        Label text
    on_change : callable
        Callback when selection changes
    font : pygame.font.Font
        Font
    """
    
    def __init__(self, x, y, width, options, initial_index=0, label="",
                 on_change=None, font=None):
        height = 30
        super().__init__(x, y, width, height)
        self.options = options
        self.selected_index = initial_index
        self.label = label
        self.on_change = on_change
        self.font = font or pygame.font.Font(None, 20)
        self.expanded = False
        self.option_height = 25
    
    def handle_event(self, event):
        """Handle dropdown interaction."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.expanded = not self.expanded
            elif self.expanded:
                # Check if clicked on an option
                for i, option in enumerate(self.options):
                    option_rect = pygame.Rect(self.rect.x, 
                                             self.rect.y + (i + 1) * self.option_height,
                                             self.rect.width, self.option_height)
                    if option_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.expanded = False
                        if self.on_change:
                            self.on_change(self.selected_index, option)
    
    def get_selected(self):
        """Get currently selected option."""
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index]
        return None
    
    def draw(self, surface):
        """Draw dropdown."""
        # Main button
        color = (100, 120, 140) if self.expanded else (80, 100, 120)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)
        
        # Label and selected option
        display_text = self.get_selected() or "Select..."
        text = f"{self.label}: {display_text}" if self.label else display_text
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 5, self.rect.centery))
        surface.blit(text_surf, text_rect)
        
        # Expanded menu
        if self.expanded:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, 
                                         self.rect.y + (i + 1) * self.option_height,
                                         self.rect.width, self.option_height)
                
                opt_color = (120, 140, 160) if i == self.selected_index else (80, 100, 120)
                pygame.draw.rect(surface, opt_color, option_rect)
                pygame.draw.rect(surface, (200, 200, 200), option_rect, 1)
                
                opt_text = self.font.render(option, True, (255, 255, 255))
                opt_rect = opt_text.get_rect(midleft=(option_rect.x + 5, option_rect.centery))
                surface.blit(opt_text, opt_rect)


class Label(UIComponent):
    """Simple text label."""
    
    def __init__(self, x, y, text, color=(200, 200, 200), font=None):
        super().__init__(x, y, 0, 0)
        self.text = text
        self.color = color
        self.font = font or pygame.font.Font(None, 20)
    
    def set_text(self, text):
        """Update label text."""
        self.text = str(text)
    
    def draw(self, surface):
        """Draw label."""
        text_surf = self.font.render(self.text, True, self.color)
        surface.blit(text_surf, (self.rect.x, self.rect.y))
