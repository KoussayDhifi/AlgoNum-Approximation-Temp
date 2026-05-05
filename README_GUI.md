# AlgoNum GUI - Interactive Numerical Analysis Visualization

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the GUI
python3 gui_main.py
```

## Features

### 🎯 5 Interactive Modes

1. **Interpolation** - Compare Lagrange, Newton, LinearSpline, and CubicSpline methods
2. **Integration** - Visualize Rectangle, Trapezoidal, Simpson, and Adaptive methods
3. **Cooling** - Analyze exponential cooling with inverse problem solving
4. **Flow** - Study fluid flow with variable channel width
5. **Exit** - Close application

### 🖱️ Real-Time Interaction

- **Buttons**: Navigate modes and trigger computations
- **Sliders**: Adjust parameters (n, k, tolerance) with instant updates
- **Dropdowns**: Select datasets and numerical methods
- **Labels**: Display computed results

### 📊 Advanced Plotting

- Interactive graph area with automatic scaling
- Grid and axes with labeled ticks
- Multiple curves on same plot
- Shaded area under curves
- Rectangle visualization for integration
- Legend for curve identification

## Data Format

Place CSV files in `./data/` folder with format:

```csv
x,y
0,10
1,15
2,20
```

Current datasets:
- `cooling_data.csv` - Temperature vs time
- `flow_data.csv` - Velocity vs position

## Architecture

```
src/gui/
├── app.py              # Main application & loop
├── data_loader.py      # CSV management
├── ui_components.py    # Buttons, sliders, dropdowns
├── plotting.py         # Graph rendering
└── screens.py          # Mode screens

+ existing modules:
  ├── src/interpolation/
  ├── src/integration/
  ├── src/applications/
  └── src/visualization/
```

## Code Examples

### Load and Plot Data
```python
from src.gui.data_loader import DataLoader
from src.gui.plotting import PlotArea
import pygame

loader = DataLoader('./data')
x, y = loader.get_dataset('cooling_data')

plot = PlotArea(50, 50, 700, 500)
plot.auto_fit(x, y)
plot.plot_points(surface, x, y)
plot.draw(surface)
```

### Create Custom UI
```python
from src.gui.ui_components import Slider, Button

slider = Slider(10, 10, 200, 0, 100, 50, 
               label="Value",
               on_change=lambda v: print(f"Value: {v}"))

button = Button(10, 50, 100, 40, "Click",
               callback=my_function)
```

### Custom Screen
```python
from src.gui.screens import Screen

class MyScreen(Screen):
    def __init__(self, width, height, app=None):
        super().__init__(width, height, app)
        self.plot_area = PlotArea(...)
        self.components = [...]
    
    def draw(self, surface):
        super().draw(surface)
        # Custom drawing
```

## Advanced Features

### Golden Section Search
Automatically finds optimal cooling coefficient (k) that minimizes error integral.

### Adaptive Integration
Simpson's rule with automatic refinement - guarantees specified precision with minimal function evaluations.

### Cubic Spline Interpolation
C² continuous interpolation with natural boundary conditions - no oscillations (Runge phenomenon).

### Real-Time Parameter Adjustment
All visualizations update instantly as you drag sliders or change dropdowns.

## Documentation

- **GUI_DOCUMENTATION.md** - Complete developer guide
- **examples_gui.py** - 6 detailed usage examples
- **src/gui/** - Inline code documentation

## Performance

- Handles 100+ data points smoothly
- Real-time updates at 60 FPS
- Efficient screen redraws using pygame
- Numpy vectorization for fast computations

## Requirements

- Python 3.8+
- pygame 2.5.2
- numpy 2.4.4
- pandas 3.0.2

## Troubleshooting

**"Could not load dataset"**
- Ensure CSV files are in `./data/` folder
- Check CSV has exactly 2 columns with headers

**Slow performance**
- Reduce number of data points
- Use LinearSpline instead of Polynomial

**UI not responding**
- Check components are added to `self.components` list
- Verify `handle_event()` is called in main loop

## File Structure

```
AlgoNum/
├── gui_main.py                    # Entry point
├── examples_gui.py                # Usage examples
├── GUI_DOCUMENTATION.md           # Full guide
├── data/
│   ├── cooling_data.csv
│   └── flow_data.csv
└── src/gui/
    ├── app.py                     # Main app class
    ├── data_loader.py             # CSV loading
    ├── ui_components.py           # UI widgets
    ├── plotting.py                # Graph rendering
    └── screens.py                 # Screen manager
```

## Future Enhancements

- [ ] Export graphs as PNG/PDF
- [ ] Save/load analysis sessions
- [ ] Zoom/pan on graphs
- [ ] Keyboard shortcuts
- [ ] Dark/light themes
- [ ] 3D surface visualization
- [ ] ODE solver animations

## Example Workflows

### Workflow 1: Compare Interpolation Methods
1. Start GUI → Interpolation mode
2. Select dataset (cooling_data)
3. Try each method (Lagrange, Newton, LinearSpline, CubicSpline)
4. Observe differences in accuracy and stability

### Workflow 2: Study Convergence
1. Integration mode
2. Select dataset
3. Adjust intervals slider (2-200)
4. Observe how rectangle/trapezoidal/Simpson errors decrease
5. Notice Simpson's O(h⁴) much faster than O(h²)

### Workflow 3: Find Optimal Model
1. Cooling mode → Load data
2. Manually adjust k slider to understand model behavior
3. Click "Find Optimal k" to auto-optimize
4. Observe residual error between model and data

### Workflow 4: Analyze Physical Problem
1. Flow mode → Load data
2. Visualize velocity interpolation
3. Calculate flow rate using different integration methods
4. Interpret physical meaning of results

## Citation

If you use AlgoNum in research, please cite:

```bibtex
@software{algonum2026,
  title={AlgoNum: Interactive Numerical Analysis GUI},
  author={AlgoNum Team},
  year={2026},
  url={https://github.com/...}
}
```

---

**Version**: 1.0.0  
**Last Updated**: May 2026  
**License**: MIT

For more information, see [GUI_DOCUMENTATION.md](GUI_DOCUMENTATION.md)
