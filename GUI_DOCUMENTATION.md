# AlgoNum GUI - User & Developer Guide

## Overview

The AlgoNum GUI is a modular, interactive pygame-based application for visualizing and exploring numerical methods including interpolation, integration, and problem-solving applications.

### Architecture Diagram

```
AlgoNumApp (main application loop)
    ├── DataLoader (CSV file management)
    ├── Screens Management
    │   ├── MainMenuScreen
    │   ├── InterpolationScreen
    │   ├── IntegrationScreen
    │   ├── CoolingScreen
    │   └── FlowScreen
    ├── UI Components
    │   ├── Button
    │   ├── Slider
    │   ├── Dropdown
    │   └── Label
    └── Plotting System
        ├── PlotArea (graph rendering)
        └── Legend (display labels)
```

---

## Installation & Setup

### Prerequisites

```bash
pip install -r requirements.txt
```

The following packages are required:
- `pygame>=2.5.2` - GUI framework
- `numpy>=2.4.4` - Numerical computations
- `pandas>=3.0.2` - Data loading
- `matplotlib>=3.10.8` - (Optional, for offline analysis)

### File Structure

```
AlgoNum/
├── data/                          # CSV data files
│   ├── cooling_data.csv
│   └── flow_data.csv
├── src/
│   ├── gui/                       # GUI module
│   │   ├── __init__.py
│   │   ├── app.py                # Main application class
│   │   ├── data_loader.py        # CSV file management
│   │   ├── ui_components.py      # Reusable UI widgets
│   │   ├── plotting.py           # Graph rendering
│   │   └── screens.py            # Screen/mode management
│   ├── interpolation/            # Existing modules
│   ├── integration/
│   ├── applications/
│   └── visualization/
└── gui_main.py                    # Entry point script
```

---

## Running the Application

### Basic Usage

```bash
python3 gui_main.py
```

The application will:
1. Initialize pygame and create window
2. Scan `./data/` folder for CSV files
3. Display main menu with mode options
4. Allow interactive exploration of numerical methods

### CSV Data Format

Each CSV file should have:
- **Header row** with column names
- **Two numerical columns** (x-data, y-data)
- **Sorted x-values** (auto-sorted if needed)

Example (`cooling_data.csv`):
```
t,T
0,90
1,85
2,72
...
```

---

## User Guide

### Main Menu

The main menu provides quick access to five modes:

1. **Interpolation** - Compare interpolation methods
2. **Integration** - Visualize and compute numerical integrals
3. **Cooling** - Analyze exponential cooling model
4. **Flow** - Visualize fluid flow problems
5. **Exit** - Close application

### Mode: Interpolation

**Purpose**: Compare different interpolation methods on the same dataset.

**Controls**:
- **Dataset Dropdown** - Select which CSV file to load
- **Method Dropdown** - Choose interpolation method:
  - `Lagrange` - Polynomial interpolation (Lagrange form)
  - `Newton` - Polynomial interpolation (Newton form)
  - `LinearSpline` - Piecewise linear (C⁰ continuous)
  - `CubicSpline` - Cubic splines (C² continuous)

**Display**:
- Red dots: Original data points
- Colored curve: Interpolated function
- Legend: Shows which method is displayed
- Grid & axes: For reference

**Real-time Updates**: Changes to method/dataset immediately update the plot.

### Mode: Integration

**Purpose**: Visualize and compare numerical integration methods.

**Controls**:
- **Dataset Dropdown** - Select data to integrate
- **Method Dropdown** - Choose integration method:
  - `Rectangle` - Midpoint rectangle rule
  - `Trapezoidal` - Trapezoidal rule
  - `Simpson` - Simpson's 1/3 rule
  - `Adaptive` - Adaptive Simpson (recommended)
- **Intervals Slider** - Adjust number of intervals (2-200)

**Display**:
- Red dots: Discrete data points
- Green curve: Interpolated function
- Green shaded area: Area under curve
- Result display: Computed integral value

**Formula**: Approximates $\int f(x) dx$ over the domain.

### Mode: Cooling

**Purpose**: Analyze the Newton cooling model inverse problem.

**Controls**:
- **Load Cooling Data** - Load experimental cooling data
- **k Slider** - Adjust cooling coefficient (0.01-0.5 s⁻¹)
- **Find Optimal k** - Auto-compute k that minimizes error
- Result display: Current k and error values

**Model**: $T(t) = T_{amb} + (T_0 - T_{amb}) e^{-kt}$

**Display**:
- Red dots: Experimental temperature measurements
- Green curve: Cubic spline interpolation
- Blue curve: Exponential model with current k

**Algorithm**: Uses golden section search to minimize:
$$E(k) = \int_0^{t_{max}} |T_{exp}(t) - T_{model}(t, k)| dt$$

### Mode: Flow

**Purpose**: Analyze fluid flow through a channel with variable width.

**Controls**:
- **Load Flow Data** - Load velocity measurements
- **Calculate Flow Rate** - Compute total volumetric flow

**Model**: $D = \int v(x) \cdot w(x) dx$

where $w(x) = 0.5 + 0.1x$ is the channel width.

**Display**:
- Red dots: Measured velocity at positions
- Green curve: Interpolated velocity profile
- Result: Total flow rate in m³/s

---

## Developer Guide

### Architecture

#### 1. DataLoader (data_loader.py)

Manages CSV file loading and caching.

```python
from src.gui.data_loader import DataLoader

loader = DataLoader(data_dir='./data')
x_data, y_data = loader.get_dataset('cooling_data')
datasets = loader.get_available_datasets()
```

**Methods**:
- `get_dataset(name)` - Retrieve data by filename (without .csv)
- `get_available_datasets()` - List all loaded datasets
- `reload()` - Refresh file list from disk

#### 2. UI Components (ui_components.py)

Reusable, self-contained UI widgets.

**Button**
```python
button = Button(x, y, width, height, "Click Me",
                callback=my_function,
                color=(100, 100, 100),
                text_color=(255, 255, 255),
                font=pygame.font.Font(None, 24))

button.handle_event(event)
button.update(mouse_pos)
button.draw(surface)
```

**Slider**
```python
slider = Slider(x, y, width,
                min_val=0, max_val=100, initial_val=50,
                label="Parameter",
                on_change=lambda val: print(f"New value: {val}"),
                font=pygame.font.Font(None, 16))
```

**Dropdown**
```python
dropdown = Dropdown(x, y, width,
                   options=["Option A", "Option B", "Option C"],
                   initial_index=0,
                   label="Select",
                   on_change=lambda idx, val: print(val))
```

**Label**
```python
label = Label(x, y, "Text", color=(200, 200, 200))
label.set_text("New text")
```

#### 3. Plotting System (plotting.py)

Graph rendering with axes, grid, and data visualization.

```python
# Create plot area
plot = PlotArea(x, y, width, height)
plot.auto_fit(x_data, y_data)  # Auto-scale to data

# Plot elements
plot.plot_points(surface, x_data, y_data, color=(255, 0, 0), size=5)
plot.plot_line(surface, x_fine, y_fine, color=(0, 255, 0), width=2)
plot.fill_under_curve(surface, x_data, y_data)
plot.draw_rectangles(surface, x_intervals, y_intervals)

# Legend
legend = Legend(x, y)
legend.add_item("Data", (255, 0, 0))
legend.add_item("Fit", (0, 255, 0))
legend.draw(surface)
```

#### 4. Screen Management (screens.py)

Base `Screen` class with six concrete implementations.

```python
class MyScreen(Screen):
    def __init__(self, width, height, app=None):
        super().__init__(width, height, app)
        self.plot_area = PlotArea(...)
        self.components = [Button(...), Slider(...), ...]
    
    def handle_event(self, event):
        super().handle_event(event)  # Propagate to components
    
    def update(self, mouse_pos):
        super().update(mouse_pos)
    
    def draw(self, surface):
        super().draw(surface)
        # Custom drawing here
```

#### 5. Main Application (app.py)

Coordinates all components, manages main loop.

```python
from src.gui.app import AlgoNumApp

app = AlgoNumApp(width=1400, height=700,
                title="My App")
app.run()
```

---

### Adding a New Mode/Screen

**Step 1**: Create new screen class in `screens.py`

```python
class MyNewScreen(Screen):
    def __init__(self, width, height, app=None):
        super().__init__(width, height, app)
        self.plot_area = PlotArea(300, 20, width - 320, height - 40)
        self._setup_controls()
    
    def _setup_controls(self):
        # Add buttons, sliders, etc. to self.components
        pass
    
    def handle_event(self, event):
        super().handle_event(event)
    
    def draw(self, surface):
        surface.fill((10, 10, 20))
        self.plot_area.draw(surface)
        for component in self.components:
            component.draw(surface)
```

**Step 2**: Add Mode enum value in `screens.py`

```python
class Mode(Enum):
    ...
    MY_NEW_MODE = 6
```

**Step 3**: Register in `AlgoNumApp.__init__()` in `app.py`

```python
self.screens = {
    ...
    Mode.MY_NEW_MODE: MyNewScreen(width, height, app=self),
}
```

**Step 4**: Add menu button in `MainMenuScreen`

```python
self.components.append(
    Button(..., "My New Mode", 
          lambda: self._switch_mode(Mode.MY_NEW_MODE))
)
```

---

### Adding a New UI Component

Create a subclass of `UIComponent`:

```python
class MyWidget(UIComponent):
    def __init__(self, x, y, width, height, custom_param=None):
        super().__init__(x, y, width, height)
        self.custom_param = custom_param
        self.value = None
    
    def update(self, mouse_pos):
        super().update(mouse_pos)
        # Custom logic
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                # Handle click
                pass
    
    def draw(self, surface):
        # Draw custom widget
        pygame.draw.rect(surface, (100, 100, 100), self.rect)
```

---

## Code Examples

### Example 1: Load Data and Plot

```python
from src.gui.data_loader import DataLoader
from src.gui.plotting import PlotArea
import pygame

# Initialize pygame and surface
pygame.init()
surface = pygame.display.set_mode((800, 600))

# Load data
loader = DataLoader('./data')
x_data, y_data = loader.get_dataset('cooling_data')

# Create plot
plot = PlotArea(50, 50, 700, 500)
plot.auto_fit(x_data, y_data)

# Render
plot.draw(surface)
plot.plot_points(surface, x_data, y_data)

pygame.display.flip()
pygame.time.wait(3000)
pygame.quit()
```

### Example 2: Real-time Interpolation

```python
from src.gui.ui_components import Slider
from src.interpolation.cubic_spline import CubicSpline

# Create slider
slider = Slider(10, 10, 200, min_val=1, max_val=10, 
               label="Smoothing")

# Create spline
spline = CubicSpline(x_data, y_data)

# In main loop:
while running:
    slider.handle_event(event)
    smooth_y = spline.evaluate(x_eval)
    # Use smooth_y with current slider value
```

### Example 3: Cooling Problem Integration

```python
from src.applications.cooling import CoolingProblem

# Load data
cooling = CoolingProblem(t_data, T_data, T_ambient=20, h_coeff=50)

# Estimate optimal k
k_opt = cooling.estimate_k(k_min=0.01, k_max=0.5)
error = cooling.model_error(k_opt)

# Get model prediction
t_eval = np.linspace(0, 10, 100)
T_model = cooling.exponential_model(t_eval, k_opt)
```

---

## Performance Optimization

### Data Handling

- CSV files are loaded once at startup
- Use `reload()` method if files change
- For large datasets, downsample for real-time plotting

### Plotting

- Limit plot point density to ~500 points for smooth performance
- Use numpy vectorized operations
- Cache interpolated curves when parameters don't change

### Event Handling

- Don't process every mouse motion event unnecessarily
- Use component-level bounding box checks before expensive operations

---

## Troubleshooting

### "Could not load dataset"
- Check CSV file is in `./data/` folder
- Verify CSV has exactly 2 columns with headers
- Ensure x-values are numeric and distinct

### Slow plotting
- Reduce number of interpolation points
- Use simpler interpolation methods (LinearSpline vs Polynomial)
- Check for outliers in data

### UI elements not responding
- Verify component is added to `self.components` list
- Check that `handle_event()` and `update()` are called
- Ensure callback functions are not blocking

---

## Future Enhancements

1. **Data Management**
   - Save/export computed results to CSV
   - Real-time CSV file monitoring
   - Data validation and cleaning tools

2. **Visualization**
   - Zoom/pan on graphs
   - Multiple curves per plot
   - 3D surface rendering for bivariate functions

3. **Numerical Methods**
   - Gauss quadrature visualization
   - Spline fitting with smoothness control
   - ODE solver animations

4. **UI/UX**
   - Keyboard shortcuts
   - Configuration file for saved settings
   - Dark/light theme toggle
   - Tooltips and help text

5. **Performance**
   - Multi-threading for long computations
   - GPU-accelerated plotting
   - Caching of expensive calculations

---

## References

- **Pygame Documentation**: https://www.pygame.org/docs/
- **NumPy Guide**: https://numpy.org/doc/
- **Pandas I/O**: https://pandas.pydata.org/docs/user_guide/io.html
- **UI/UX Best Practices**: https://material.io/design

---

**Last Updated**: May 2026  
**Version**: 1.0.0  
**License**: MIT
