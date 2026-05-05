"""
app.py - Main GUI application class
"""

import pygame
import sys
from pathlib import Path

from .data_loader import DataLoader
from .screens import (Mode, MainMenuScreen, InterpolationScreen, 
                      IntegrationScreen, CoolingScreen, FlowScreen)


class AlgoNumApp:
    """
    Main application class for AlgoNum GUI.
    
    Manages:
    - Window and rendering
    - Screen/mode switching
    - Event handling
    - Data loading
    """
    
    def __init__(self, width=1400, height=700, title="AlgoNum - Numerical Analysis GUI"):
        """
        Initialize application.
        
        Parameters
        ----------
        width : int
            Window width in pixels
        height : int
            Window height in pixels
        title : str
            Window title
        """
        pygame.init()
        
        self.width = width
        self.height = height
        self.title = title
        self.display = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60
        
        # Data loader
        self.data_loader = DataLoader(data_dir='./data')
        
        # Screens
        self.screens = {
            Mode.MAIN_MENU: MainMenuScreen(width, height, app=self),
            Mode.INTERPOLATION: InterpolationScreen(width, height, app=self),
            Mode.INTEGRATION: IntegrationScreen(width, height, app=self),
            Mode.COOLING: CoolingScreen(width, height, app=self),
            Mode.FLOW: FlowScreen(width, height, app=self),
        }
        
        self.current_mode = Mode.MAIN_MENU
        self.current_screen = self.screens[self.current_mode]
    
    def switch_mode(self, mode):
        """
        Switch to another screen/mode.
        
        Parameters
        ----------
        mode : Mode
            Target mode enum
        """
        if mode in self.screens:
            self.current_screen.cleanup()
            self.current_mode = mode
            self.current_screen = self.screens[mode]
            print(f"Switched to mode: {mode.name}")
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, 
                              pygame.MOUSEMOTION):
                self.current_screen.handle_event(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self):
        """Update screen state."""
        mouse_pos = pygame.mouse.get_pos()
        self.current_screen.update(mouse_pos)
    
    def render(self):
        """Render current screen."""
        self.current_screen.draw(self.display)
        pygame.display.flip()
    
    def run(self):
        """Main application loop."""
        print(f"Starting {self.title}")
        print(f"Available datasets: {self.data_loader.get_available_datasets()}")
        
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.render()
                self.clock.tick(self.fps)
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup and quit."""
        pygame.quit()
        print("Goodbye!")
    
    def quit(self):
        """Set quit flag."""
        self.running = False


def main():
    """Entry point for GUI application."""
    # Adjust path if running from different directory
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    os.chdir(project_root)
    
    app = AlgoNumApp(width=1400, height=700)
    app.run()


if __name__ == '__main__':
    main()
