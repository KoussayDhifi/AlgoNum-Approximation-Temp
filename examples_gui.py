"""
examples_gui.py - Example usage patterns for AlgoNum GUI components

This file demonstrates how to use the GUI system in various ways,
from simple data plotting to advanced screen customization.
"""

import pygame
import numpy as np
from src.gui.data_loader import DataLoader
from src.gui.ui_components import Button, Slider, Dropdown, Label
from src.gui.plotting import PlotArea, Legend
from src.gui.app import AlgoNumApp


# ============================================================================
# Example 1: Simple Plotting
# ============================================================================

def example_simple_plot():
    """
    Example 1: Load data and display on a plot.
    """
    print("Example 1: Simple Plotting")
    print("-" * 50)
    
    # Initialize pygame
    pygame.init()
    surface = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Example 1: Simple Plot")
    
    # Load data
    loader = DataLoader('./data')
    x_data, y_data = loader.get_dataset('cooling_data')
    
    if x_data is None:
        print("Error: Could not load cooling_data")
        pygame.quit()
        return
    
    # Create plot
    plot = PlotArea(50, 50, 700, 500)
    plot.auto_fit(x_data, y_data)
    
    # Render loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        surface.fill((10, 10, 20))
        plot.draw(surface)
        plot.plot_points(surface, x_data, y_data, color=(255, 100, 100), size=6)
        plot.plot_line(surface, x_data, y_data, color=(100, 200, 100), width=2)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("✓ Example 1 complete\n")


# ============================================================================
# Example 2: Interactive Slider
# ============================================================================

def example_slider_interaction():
    """
    Example 2: Use a slider to control a parameter in real-time.
    """
    print("Example 2: Interactive Slider")
    print("-" * 50)
    
    pygame.init()
    surface = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Example 2: Slider")
    
    # Create a slider
    slider = Slider(50, 100, 300,
                   min_val=0.01, max_val=2.0, initial_val=1.0,
                   label="Frequency",
                   font=pygame.font.Font(None, 20))
    
    # Generate data for a sine wave
    x = np.linspace(0, 10, 100)
    
    # Create plot
    plot = PlotArea(50, 200, 700, 350)
    plot.set_data_limits(0, 10, -2, 2)
    
    # Render loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            slider.handle_event(event)
        
        slider.update(mouse_pos)
        
        # Generate sine wave with current frequency
        y = np.sin(slider.value * x)
        
        surface.fill((10, 10, 20))
        slider.draw(surface)
        
        plot.draw(surface)
        plot.plot_line(surface, x, y, color=(100, 150, 255), width=2)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("✓ Example 2 complete\n")


# ============================================================================
# Example 3: Multiple UI Components
# ============================================================================

def example_ui_components():
    """
    Example 3: Combine buttons, sliders, and dropdowns.
    """
    print("Example 3: Multiple UI Components")
    print("-" * 50)
    
    pygame.init()
    surface = pygame.display.set_mode((900, 700))
    pygame.display.set_caption("Example 3: UI Components")
    
    # State variables
    state = {
        'value': 0,
        'method': 'Linear',
        'dataset': None
    }
    
    def on_button_click():
        state['value'] += 1
        print(f"Button clicked! Counter: {state['value']}")
    
    def on_slider_change(val):
        state['slider_val'] = val
    
    def on_dropdown_change(index, option):
        state['method'] = option
        print(f"Selected method: {option}")
    
    # Create UI components
    button = Button(20, 20, 150, 40, "Increment",
                   callback=on_button_click,
                   color=(100, 150, 100))
    
    slider = Slider(20, 80, 300,
                   min_val=0, max_val=100, initial_val=50,
                   label="Parameter",
                   on_change=on_slider_change,
                   font=pygame.font.Font(None, 16))
    
    dropdown = Dropdown(20, 160, 300,
                       options=["Linear", "Quadratic", "Cubic", "Exponential"],
                       label="Method",
                       on_change=on_dropdown_change,
                       font=pygame.font.Font(None, 16))
    
    label = Label(20, 220, "Status: Ready",
                 color=(100, 200, 100),
                 font=pygame.font.Font(None, 18))
    
    components = [button, slider, dropdown, label]
    
    # Render loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            for component in components:
                component.handle_event(event)
        
        for component in components:
            component.update(mouse_pos)
        
        # Update label text
        label.set_text(f"Status: {state['method']} | "
                      f"Clicks: {state['value']}")
        
        surface.fill((10, 10, 20))
        for component in components:
            component.draw(surface)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("✓ Example 3 complete\n")


# ============================================================================
# Example 4: Custom Screen Implementation
# ============================================================================

def example_custom_screen():
    """
    Example 4: Create a custom screen for a specific task.
    """
    from src.gui.screens import Screen
    from src.gui.ui_components import Button, Label
    
    class CustomScreen(Screen):
        """Custom screen with specific functionality."""
        
        def __init__(self, width, height):
            super().__init__(width, height)
            self.counter = 0
            
            # Add components
            self.components.append(
                Button(width // 2 - 75, 200, 150, 50, "Increment",
                      callback=self._increment,
                      color=(100, 150, 100))
            )
            
            self.label = Label(width // 2 - 100, 100, "Counter: 0",
                             color=(100, 200, 100),
                             font=pygame.font.Font(None, 32))
            self.components.append(self.label)
        
        def _increment(self):
            self.counter += 1
            self.label.set_text(f"Counter: {self.counter}")
            print(f"Counter incremented to {self.counter}")
        
        def draw(self, surface):
            surface.fill((10, 10, 20))
            for component in self.components:
                component.draw(surface)
    
    # Create and run screen
    pygame.init()
    surface = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Example 4: Custom Screen")
    
    screen = CustomScreen(800, 600)
    clock = pygame.time.Clock()
    running = True
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            screen.handle_event(event)
        
        screen.update(mouse_pos)
        screen.draw(surface)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("✓ Example 4 complete\n")


# ============================================================================
# Example 5: Full Application (Main GUI)
# ============================================================================

def example_full_app():
    """
    Example 5: Run the complete AlgoNum GUI application.
    
    This launches the full interactive GUI with all modes:
    - Interpolation
    - Integration
    - Cooling Problem
    - Flow Problem
    """
    print("Example 5: Full Application")
    print("-" * 50)
    print("Launching AlgoNum GUI application...")
    
    app = AlgoNumApp(width=1400, height=700)
    app.run()
    
    print("✓ Example 5 complete\n")


# ============================================================================
# Example 6: Data Analysis Workflow
# ============================================================================

def example_data_workflow():
    """
    Example 6: Complete workflow for data analysis.
    """
    print("Example 6: Data Analysis Workflow")
    print("-" * 50)
    
    # 1. Load data
    loader = DataLoader('./data')
    datasets = loader.get_available_datasets()
    print(f"Available datasets: {datasets}")
    
    # 2. Select dataset
    if 'cooling_data' in datasets:
        x_data, y_data = loader.get_dataset('cooling_data')
        print(f"Loaded cooling_data: {len(x_data)} points")
        print(f"  X range: [{x_data.min():.2f}, {x_data.max():.2f}]")
        print(f"  Y range: [{y_data.min():.2f}, {y_data.max():.2f}]")
        
        # 3. Interpolate
        from src.interpolation.cubic_spline import CubicSpline
        spline = CubicSpline(x_data, y_data)
        x_fine = np.linspace(x_data[0], x_data[-1], 100)
        y_fine = spline.evaluate(x_fine)
        print(f"Interpolated {len(x_fine)} points using CubicSpline")
        
        # 4. Compute integral
        from src.integration.adaptive import AdaptiveIntegration
        ai = AdaptiveIntegration(tol=1e-6)
        integral = ai.adaptive_simpson(spline.evaluate, x_data[0], x_data[-1])
        print(f"Integral under curve: {integral:.4f}")
        
        # 5. Analyze with application model
        from src.applications.cooling import CoolingProblem
        cooling = CoolingProblem(x_data, y_data, T_ambient=20.0)
        k_opt = cooling.estimate_k()
        print(f"Optimal cooling coefficient: k = {k_opt:.6f}")
    
    print("✓ Example 6 complete\n")


# ============================================================================
# Main: Run Examples
# ============================================================================

def main():
    """Run all examples."""
    print("\n")
    print("=" * 70)
    print("AlgoNum GUI - Usage Examples")
    print("=" * 70)
    print()
    
    examples = [
        ("1. Simple Plotting", example_simple_plot),
        ("2. Interactive Slider", example_slider_interaction),
        ("3. Multiple UI Components", example_ui_components),
        ("4. Custom Screen", example_custom_screen),
        ("5. Full Application", example_full_app),
        ("6. Data Analysis Workflow", example_data_workflow),
    ]
    
    print("Available examples:")
    for name, _ in examples:
        print(f"  {name}")
    print()
    
    choice = input("Enter example number (1-6) or 'all' to skip: ").strip()
    
    if choice.lower() == 'all':
        print("Skipping examples.")
    elif choice in ['1', '2', '3', '4', '5', '6']:
        idx = int(choice) - 1
        print(f"\nRunning {examples[idx][0]}...\n")
        try:
            examples[idx][1]()
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Invalid choice. Exiting.")
    
    print()
    print("=" * 70)
    print("Examples completed!")
    print("=" * 70)


if __name__ == '__main__':
    main()
