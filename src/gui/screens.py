"""
screens.py - Screen/Mode management for GUI application
"""

import pygame
import numpy as np
from enum import Enum
from .ui_components import Button, Slider, Dropdown, Label
from .plotting import PlotArea, Legend


class Mode(Enum):
    """Application modes."""
    MAIN_MENU = 1
    INTERPOLATION = 2
    INTEGRATION = 3
    COOLING = 4
    FLOW = 5


class Screen:
    """Base class for screens."""
    
    def __init__(self, width, height, app=None):
        self.width = width
        self.height = height
        self.app = app
        self.components = []
        self.plot_area = None
        self.legend = None
    
    def handle_event(self, event):
        """Handle pygame events."""
        for component in self.components:
            component.handle_event(event)
    
    def update(self, mouse_pos):
        """Update screen state."""
        for component in self.components:
            component.update(mouse_pos)
    
    def draw(self, surface):
        """Draw screen."""
        surface.fill((10, 10, 20))
        
        if self.plot_area:
            self.plot_area.draw(surface)
        
        for component in self.components:
            component.draw(surface)
        
        if self.legend:
            self.legend.draw(surface)
    
    def cleanup(self):
        """Cleanup before switching screens."""
        pass


class MainMenuScreen(Screen):
    """Main menu screen."""
    
    def __init__(self, width, height, app=None):
        super().__init__(width, height, app)
        
        # Title
        font_title = pygame.font.Font(None, 48)
        title_text = "AlgoNum - GUI"
        self.title_surf = font_title.render(title_text, True, (100, 200, 255))
        
        # Buttons
        button_width = 200
        button_height = 50
        button_x = width // 2 - button_width // 2
        
        self.components.append(
            Button(button_x, 150, button_width, button_height, 
                  "Interpolation", lambda: self._switch_mode(Mode.INTERPOLATION),
                  color=(80, 120, 160))
        )
        
        self.components.append(
            Button(button_x, 220, button_width, button_height,
                  "Integration", lambda: self._switch_mode(Mode.INTEGRATION),
                  color=(80, 120, 160))
        )
        
        self.components.append(
            Button(button_x, 290, button_width, button_height,
                  "Cooling", lambda: self._switch_mode(Mode.COOLING),
                  color=(80, 120, 160))
        )
        
        self.components.append(
            Button(button_x, 360, button_width, button_height,
                  "Flow", lambda: self._switch_mode(Mode.FLOW),
                  color=(80, 120, 160))
        )
        
        self.components.append(
            Button(button_x, 430, button_width, button_height,
                  "Exit", lambda: self._exit(),
                  color=(160, 80, 80))
        )
    
    def _switch_mode(self, mode):
        """Switch to another mode."""
        if self.app:
            self.app.switch_mode(mode)
    
    def _exit(self):
        """Exit application."""
        if self.app:
            self.app.quit()
    
    def draw(self, surface):
        """Draw main menu."""
        surface.fill((10, 10, 20))
        
        # Title
        title_rect = self.title_surf.get_rect(center=(self.width // 2, 80))
        surface.blit(self.title_surf, title_rect)
        
        # Components
        for component in self.components:
            component.draw(surface)


class InterpolationScreen(Screen):
    """Interpolation mode screen."""
    
    def __init__(self, width, height, app=None):
        super().__init__(width, height, app)
        
        # Plot area
        self.plot_area = PlotArea(300, 20, width - 320, height - 40)
        self.legend = Legend(width - 290, 30)
        
        # Left panel - Controls
        self._setup_controls()
        
        # State
        self.x_data = None
        self.y_data = None
        self.dataset_name = None
        self.method = None
        self.interpolated_x = None
        self.interpolated_y = None
    
    def _setup_controls(self):
        """Setup control panel."""
        x_panel = 10
        y_start = 20
        spacing = 60
        
        # Dataset selector
        datasets = self.app.data_loader.get_available_datasets() if self.app else []
        self.dataset_dropdown = Dropdown(
            x_panel, y_start, 280, datasets,
            label="Dataset",
            on_change=self._on_dataset_changed,
            font=pygame.font.Font(None, 16)
        )
        self.components.append(self.dataset_dropdown)
        
        # Method selector
        methods = ["Lagrange", "Newton", "LinearSpline", "CubicSpline"]
        self.method_dropdown = Dropdown(
            x_panel, y_start + spacing, 280, methods,
            label="Method",
            on_change=self._on_method_changed,
            font=pygame.font.Font(None, 16)
        )
        self.components.append(self.method_dropdown)
        
        # Back button
        self.components.append(
            Button(x_panel, self.height - 40, 280, 30,
                  "Back to Menu", lambda: self.app.switch_mode(Mode.MAIN_MENU),
                  color=(100, 100, 100))
        )
    
    def _on_dataset_changed(self, index, dataset_name):
        """Load selected dataset."""
        if not self.app:
            return
        
        self.x_data, self.y_data = self.app.data_loader.get_dataset(dataset_name)
        self.dataset_name = dataset_name
        
        if self.x_data is not None:
            self.plot_area.auto_fit(self.x_data, self.y_data)
            self._update_interpolation()
    
    def _on_method_changed(self, index, method_name):
        """Change interpolation method."""
        self.method = method_name
        self._update_interpolation()
    
    def _update_interpolation(self):
        """Update interpolation based on current settings."""
        if self.x_data is None or self.method is None:
            return
        
        try:
            if self.method == "Lagrange":
                from src.interpolation.polynomial import PolynomialInterpolation
                poly = PolynomialInterpolation(self.x_data, self.y_data)
                self.interpolated_x = np.linspace(self.x_data[0], self.x_data[-1], 200)
                self.interpolated_y = poly.lagrange(self.interpolated_x)
            
            elif self.method == "Newton":
                from src.interpolation.polynomial import PolynomialInterpolation
                poly = PolynomialInterpolation(self.x_data, self.y_data)
                self.interpolated_x = np.linspace(self.x_data[0], self.x_data[-1], 200)
                self.interpolated_y = poly.newton_eval(self.interpolated_x)
            
            elif self.method == "LinearSpline":
                from src.interpolation.linear_spline import LinearSpline
                spline = LinearSpline(self.x_data, self.y_data)
                self.interpolated_x = np.linspace(self.x_data[0], self.x_data[-1], 200)
                self.interpolated_y = spline.evaluate(self.interpolated_x)
            
            elif self.method == "CubicSpline":
                from src.interpolation.cubic_spline import CubicSpline
                spline = CubicSpline(self.x_data, self.y_data)
                self.interpolated_x = np.linspace(self.x_data[0], self.x_data[-1], 200)
                self.interpolated_y = spline.evaluate(self.interpolated_x)
        
        except Exception as e:
            print(f"Error in interpolation: {e}")
            self.interpolated_y = None
    
    def update(self, mouse_pos):
        """Update screen."""
        super().update(mouse_pos)
    
    def draw(self, surface):
        """Draw screen."""
        surface.fill((10, 10, 20))
        
        # Plot area
        self.plot_area.draw(surface)
        
        if self.x_data is not None:
            self.plot_area.plot_points(surface, self.x_data, self.y_data, 
                                      color=(255, 100, 100), size=6)
            self.legend.clear()
            self.legend.add_item("Data", (255, 100, 100))
        
        if self.interpolated_y is not None:
            colors = {
                "Lagrange": (100, 200, 255),
                "Newton": (100, 255, 200),
                "LinearSpline": (200, 100, 255),
                "CubicSpline": (255, 200, 100)
            }
            color = colors.get(self.method, (100, 200, 100))
            self.plot_area.plot_line(surface, self.interpolated_x, self.interpolated_y,
                                    color=color, width=2)
            self.legend.add_item(self.method, color)
        
        self.legend.draw(surface)
        
        # Controls
        for component in self.components:
            component.draw(surface)


class IntegrationScreen(Screen):
    """Integration mode screen."""
    
    def __init__(self, width, height, app=None):
        super().__init__(width, height, app)
        
        self.plot_area = PlotArea(300, 20, width - 320, height - 40)
        self.legend = Legend(width - 290, 30)
        
        self._setup_controls()
        
        # State
        self.x_data = None
        self.y_data = None
        self.method = None
        self.n_intervals = 10
        self.integral_value = 0.0
    
    def _setup_controls(self):
        """Setup control panel."""
        x_panel = 10
        y_start = 20
        spacing = 60
        
        # Dataset selector
        datasets = self.app.data_loader.get_available_datasets() if self.app else []
        self.dataset_dropdown = Dropdown(
            x_panel, y_start, 280, datasets,
            label="Dataset",
            on_change=self._on_dataset_changed,
            font=pygame.font.Font(None, 16)
        )
        self.components.append(self.dataset_dropdown)
        
        # Method selector
        methods = ["Rectangle", "Trapezoidal", "Simpson", "Adaptive"]
        self.method_dropdown = Dropdown(
            x_panel, y_start + spacing, 280, methods,
            label="Method",
            on_change=self._on_method_changed,
            font=pygame.font.Font(None, 16)
        )
        self.components.append(self.method_dropdown)
        
        # Number of intervals slider
        self.n_slider = Slider(
            x_panel, y_start + spacing * 2, 280,
            min_val=2, max_val=200, initial_val=10,
            label="Intervals (n)",
            on_change=self._on_n_changed,
            font=pygame.font.Font(None, 14)
        )
        self.components.append(self.n_slider)
        
        # Result label
        self.result_label = Label(x_panel, y_start + spacing * 3 + 40,
                                 "Integral: --",
                                 color=(100, 200, 100),
                                 font=pygame.font.Font(None, 16))
        self.components.append(self.result_label)
        
        # Back button
        self.components.append(
            Button(x_panel, self.height - 40, 280, 30,
                  "Back to Menu", lambda: self.app.switch_mode(Mode.MAIN_MENU),
                  color=(100, 100, 100))
        )
    
    def _on_dataset_changed(self, index, dataset_name):
        """Load dataset."""
        if not self.app:
            return
        
        self.x_data, self.y_data = self.app.data_loader.get_dataset(dataset_name)
        
        if self.x_data is not None:
            self.plot_area.auto_fit(self.x_data, self.y_data)
            self._update_integration()
    
    def _on_method_changed(self, index, method_name):
        """Change method."""
        self.method = method_name
        self._update_integration()
    
    def _on_n_changed(self, value):
        """Update number of intervals."""
        self.n_intervals = int(value)
        self._update_integration()
    
    def _update_integration(self):
        """Update integration visualization."""
        if self.x_data is None or self.method is None:
            return
        
        try:
            from src.integration.newton_cotes import NewtonCotes
            from src.integration.adaptive import AdaptiveIntegration
            
            # Simple function integration using data points
            # For visualization, we interpolate and integrate
            from src.interpolation.cubic_spline import CubicSpline
            
            spline = CubicSpline(self.x_data, self.y_data)
            
            if self.method == "Rectangle":
                self.integral_value = NewtonCotes.rectangle(spline.evaluate, 
                                                           self.x_data[0], 
                                                           self.x_data[-1],
                                                           self.n_intervals)
            
            elif self.method == "Trapezoidal":
                self.integral_value = NewtonCotes.trapezoidal(spline.evaluate,
                                                             self.x_data[0],
                                                             self.x_data[-1],
                                                             self.n_intervals)
            
            elif self.method == "Simpson":
                n = self.n_intervals if self.n_intervals % 2 == 0 else self.n_intervals + 1
                self.integral_value = NewtonCotes.simpson(spline.evaluate,
                                                         self.x_data[0],
                                                         self.x_data[-1],
                                                         n)
            
            elif self.method == "Adaptive":
                ai = AdaptiveIntegration(tol=1e-6)
                self.integral_value = ai.adaptive_simpson(spline.evaluate,
                                                         self.x_data[0],
                                                         self.x_data[-1])
            
            self.result_label.set_text(f"Integral: {self.integral_value:.6f}")
        
        except Exception as e:
            print(f"Error in integration: {e}")
            self.integral_value = 0.0
    
    def draw(self, surface):
        """Draw screen."""
        surface.fill((10, 10, 20))
        
        self.plot_area.draw(surface)
        
        if self.x_data is not None:
            self.plot_area.plot_points(surface, self.x_data, self.y_data,
                                      color=(255, 100, 100), size=6)
            self.plot_area.plot_line(surface, self.x_data, self.y_data,
                                    color=(100, 200, 100), width=2)
            self.plot_area.fill_under_curve(surface, self.x_data, self.y_data,
                                           color=(100, 200, 100, 80))
            
            self.legend.clear()
            self.legend.add_item("Data", (255, 100, 100))
            self.legend.add_item("Curve", (100, 200, 100))
        
        self.legend.draw(surface)
        
        for component in self.components:
            component.draw(surface)


class CoolingScreen(Screen):
    """Cooling problem visualization screen."""
    
    def __init__(self, width, height, app=None):
        super().__init__(width, height, app)
        
        self.plot_area = PlotArea(300, 20, width - 320, height - 40)
        self.legend = Legend(width - 290, 30)
        
        self._setup_controls()
        
        # State
        self.cooling_problem = None
        self.t_data = None
        self.T_data = None
        self.t_fine = None
        self.T_interp = None
        self.T_model = None
        self.k_value = 0.1
        self.error_value = 0.0
    
    def _setup_controls(self):
        """Setup control panel."""
        x_panel = 10
        y_start = 20
        spacing = 60
        
        # Load cooling data button
        self.components.append(
            Button(x_panel, y_start, 280, 30,
                  "Load Cooling Data", self._load_cooling_data,
                  color=(80, 120, 160))
        )
        
        # k parameter slider
        self.k_slider = Slider(
            x_panel, y_start + spacing, 280,
            min_val=0.01, max_val=0.5, initial_val=0.15,
            label="k (cooling coeff)",
            on_change=self._on_k_changed,
            font=pygame.font.Font(None, 14)
        )
        self.components.append(self.k_slider)
        
        # Find optimal k button
        self.components.append(
            Button(x_panel, y_start + spacing * 2, 280, 30,
                  "Find Optimal k", self._find_optimal_k,
                  color=(100, 150, 100))
        )
        
        # Results label
        self.k_label = Label(x_panel, y_start + spacing * 2 + 50,
                            "k: --", color=(100, 200, 100),
                            font=pygame.font.Font(None, 14))
        self.components.append(self.k_label)
        
        self.error_label = Label(x_panel, y_start + spacing * 2 + 75,
                                "Error: --", color=(100, 200, 100),
                                font=pygame.font.Font(None, 14))
        self.components.append(self.error_label)
        
        # Back button
        self.components.append(
            Button(x_panel, self.height - 40, 280, 30,
                  "Back to Menu", lambda: self.app.switch_mode(Mode.MAIN_MENU),
                  color=(100, 100, 100))
        )
    
    def _load_cooling_data(self):
        """Load cooling problem data."""
        try:
            x_data, y_data = self.app.data_loader.get_dataset("cooling_data")
            
            if x_data is None:
                print("Could not load cooling_data")
                return
            
            from src.applications.cooling import CoolingProblem
            
            self.cooling_problem = CoolingProblem(x_data, y_data, T_ambient=20.0, h_coeff=50.0)
            self.t_data = x_data
            self.T_data = y_data
            
            self.plot_area.auto_fit(self.t_data, self.T_data)
            self._update_cooling_visualization()
        
        except Exception as e:
            print(f"Error loading cooling data: {e}")
    
    def _on_k_changed(self, value):
        """Update k value."""
        self.k_value = value
        self._update_cooling_visualization()
    
    def _find_optimal_k(self):
        """Find optimal k."""
        if self.cooling_problem is None:
            return
        
        try:
            k_opt = self.cooling_problem.estimate_k(k_min=0.01, k_max=0.5, tol=1e-4)
            self.k_slider.value = k_opt
            self.k_value = k_opt
            self._update_cooling_visualization()
        except Exception as e:
            print(f"Error finding optimal k: {e}")
    
    def _update_cooling_visualization(self):
        """Update visualization with current k."""
        if self.cooling_problem is None:
            return
        
        try:
            self.t_fine = np.linspace(self.t_data[0], self.t_data[-1], 100)
            self.T_interp = self.cooling_problem.temperature(self.t_fine)
            self.T_model = self.cooling_problem.exponential_model(self.t_fine, self.k_value)
            self.error_value = self.cooling_problem.model_error(self.k_value)
            
            self.k_label.set_text(f"k: {self.k_value:.6f}")
            self.error_label.set_text(f"Error: {self.error_value:.4f}")
        
        except Exception as e:
            print(f"Error updating visualization: {e}")
    
    def draw(self, surface):
        """Draw screen."""
        surface.fill((10, 10, 20))
        
        self.plot_area.draw(surface)
        
        if self.t_data is not None:
            # Plot data
            self.plot_area.plot_points(surface, self.t_data, self.T_data,
                                      color=(255, 100, 100), size=6)
            self.legend.clear()
            self.legend.add_item("Experimental", (255, 100, 100))
            
            # Plot interpolation
            if self.T_interp is not None:
                self.plot_area.plot_line(surface, self.t_fine, self.T_interp,
                                        color=(100, 200, 100), width=2)
                self.legend.add_item("Spline", (100, 200, 100))
            
            # Plot model
            if self.T_model is not None:
                self.plot_area.plot_line(surface, self.t_fine, self.T_model,
                                        color=(100, 150, 255), width=2)
                self.legend.add_item("Model", (100, 150, 255))
        
        self.legend.draw(surface)
        
        for component in self.components:
            component.draw(surface)


class FlowScreen(Screen):
    """Flow problem visualization screen."""
    
    def __init__(self, width, height, app=None):
        super().__init__(width, height, app)
        
        self.plot_area = PlotArea(300, 20, width - 320, height - 40)
        self.legend = Legend(width - 290, 30)
        
        self._setup_controls()
        
        # State
        self.flow_problem = None
        self.x_data = None
        self.v_data = None
        self.x_fine = None
        self.v_interp = None
        self.flow_rate = 0.0
    
    def _setup_controls(self):
        """Setup control panel."""
        x_panel = 10
        y_start = 20
        spacing = 60
        
        # Load flow data button
        self.components.append(
            Button(x_panel, y_start, 280, 30,
                  "Load Flow Data", self._load_flow_data,
                  color=(80, 120, 160))
        )
        
        # Calculate flow rate button
        self.components.append(
            Button(x_panel, y_start + spacing, 280, 30,
                  "Calculate Flow Rate", self._calculate_flow_rate,
                  color=(100, 150, 100))
        )
        
        # Result label
        self.flow_label = Label(x_panel, y_start + spacing * 2,
                               "Flow Rate: --",
                               color=(100, 200, 100),
                               font=pygame.font.Font(None, 16))
        self.components.append(self.flow_label)
        
        # Back button
        self.components.append(
            Button(x_panel, self.height - 40, 280, 30,
                  "Back to Menu", lambda: self.app.switch_mode(Mode.MAIN_MENU),
                  color=(100, 100, 100))
        )
    
    def _load_flow_data(self):
        """Load flow problem data."""
        try:
            x_data, v_data = self.app.data_loader.get_dataset("flow_data")
            
            if x_data is None:
                print("Could not load flow_data")
                return
            
            from src.applications.flow import FlowProblem
            
            self.flow_problem = FlowProblem(x_data, v_data)
            self.x_data = x_data
            self.v_data = v_data
            
            self.plot_area.auto_fit(self.x_data, self.v_data)
            self._update_visualization()
        
        except Exception as e:
            print(f"Error loading flow data: {e}")
    
    def _calculate_flow_rate(self):
        """Calculate flow rate."""
        if self.flow_problem is None:
            return
        
        try:
            self.flow_rate = self.flow_problem.total_flow_rate(method='adaptive')
            self.flow_label.set_text(f"Flow Rate: {self.flow_rate:.4f} m³/s")
        except Exception as e:
            print(f"Error calculating flow rate: {e}")
    
    def _update_visualization(self):
        """Update visualization."""
        if self.x_data is None:
            return
        
        try:
            self.x_fine = np.linspace(self.x_data[0], self.x_data[-1], 100)
            self.v_interp = self.flow_problem.velocity(self.x_fine)
        except Exception as e:
            print(f"Error updating visualization: {e}")
    
    def draw(self, surface):
        """Draw screen."""
        surface.fill((10, 10, 20))
        
        self.plot_area.draw(surface)
        
        if self.x_data is not None:
            # Plot data
            self.plot_area.plot_points(surface, self.x_data, self.v_data,
                                      color=(255, 100, 100), size=6)
            self.legend.clear()
            self.legend.add_item("Data", (255, 100, 100))
            
            # Plot interpolation
            if self.v_interp is not None:
                self.plot_area.plot_line(surface, self.x_fine, self.v_interp,
                                        color=(100, 200, 100), width=2)
                self.legend.add_item("Spline", (100, 200, 100))
        
        self.legend.draw(surface)
        
        for component in self.components:
            component.draw(surface)
