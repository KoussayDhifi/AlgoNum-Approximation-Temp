# AlgoNum GUI - Quick Reference

## Launching the Application

```bash
python3 gui_main.py
```

## Main Menu

```
┌─────────────────────────────┐
│     AlgoNum - GUI           │
├─────────────────────────────┤
│  [  Interpolation   ]       │
│  [  Integration     ]       │
│  [  Cooling         ]       │
│  [  Flow            ]       │
│  [  Exit            ]       │
└─────────────────────────────┘
```

## Mode: Interpolation

**Goal**: Visualize different interpolation methods

| Control | Function |
|---------|----------|
| Dataset Dropdown | Select CSV file to interpolate |
| Method Dropdown | Choose: Lagrange, Newton, LinearSpline, CubicSpline |
| Plot Area | Shows data (red dots) and interpolated curve |
| Legend | Identifies which method is active |

**Methods**:
- **Lagrange**: $P_n(x) = \sum_{i=0}^{n} y_i \prod_{j \neq i} \frac{x - x_j}{x_i - x_j}$
- **Newton**: Divided differences form
- **LinearSpline**: Piecewise linear (C⁰)
- **CubicSpline**: Cubic polynomials (C²)

---

## Mode: Integration

**Goal**: Compute integrals and visualize methods

| Control | Function |
|---------|----------|
| Dataset Dropdown | Select function to integrate |
| Method Dropdown | Choose: Rectangle, Trapezoidal, Simpson, Adaptive |
| Intervals Slider | Number of subintervals (2-200) |
| Result Display | Computed integral value |

**Methods Formula**:
- **Rectangle**: $I \approx h \sum f(x_i + h/2)$ — O(h²)
- **Trapezoidal**: $I \approx \frac{h}{2}[f(x_0) + 2\sum f(x_i) + f(x_n)]$ — O(h²)
- **Simpson**: $I \approx \frac{h}{3}[f(x_0) + 4f(x_1) + 2f(x_2) + ...]$ — O(h⁴)
- **Adaptive**: Simpson with automatic refinement — O(h⁶)

---

## Mode: Cooling

**Goal**: Analyze Newton cooling and solve inverse problem

| Control | Function |
|---------|----------|
| Load Button | Import cooling_data.csv |
| k Slider | Adjust cooling coefficient (0.01-0.5) |
| Find Optimal k | Auto-compute k minimizing error |
| Result Labels | Show current k and error |

**Model**:
$$T(t) = T_{amb} + (T_0 - T_{amb}) e^{-kt}$$

**Inverse Problem**: Find k* that minimizes
$$E(k) = \int_0^{t_{max}} |T_{exp}(t) - T_{model}(t,k)| dt$$

**Algorithm**: Golden Section Search (bisection-like, no derivatives)

**Display**:
- Red dots: Experimental measurements
- Green curve: Cubic spline interpolation
- Blue curve: Exponential model with current k

---

## Mode: Flow

**Goal**: Analyze flow rate through variable-width channel

| Control | Function |
|---------|----------|
| Load Button | Import flow_data.csv |
| Calculate Button | Compute volumetric flow rate |
| Result Display | Total flow in m³/s |

**Model**:
$$D = \int_0^L v(x) \cdot w(x) \, dx$$

where:
- $v(x)$ = velocity (from data interpolation)
- $w(x) = 0.5 + 0.1x$ = channel width
- $D$ = volumetric flow rate

---

## UI Component Reference

### Button
```python
button = Button(x, y, width, height, "Label", callback=func)
```
- Click to trigger action
- Color changes on hover
- Border indicates state

### Slider
```python
slider = Slider(x, y, width, min_val, max_val, initial, 
               label="Name", on_change=callback)
```
- Drag circle to adjust value
- Real-time callback
- Display current value

### Dropdown
```python
dropdown = Dropdown(x, y, width, ["Option A", "Option B"],
                   label="Select", on_change=callback)
```
- Click to expand
- Select option
- Display selected value

### Label
```python
label = Label(x, y, "Text", color=(R,G,B))
label.set_text("New text")
```
- Static text display
- Update dynamically in real-time

---

## Plotting Functions

### Create Plot Area
```python
plot = PlotArea(x, y, width, height)
plot.auto_fit(x_data, y_data)  # Auto-scale
plot.set_data_limits(x_min, x_max, y_min, y_max)  # Manual
```

### Plot Methods
```python
plot.plot_points(surface, x, y, color=(R,G,B), size=5)
plot.plot_line(surface, x, y, color=(R,G,B), width=2)
plot.fill_under_curve(surface, x, y, color=(R,G,B,A))
plot.draw_rectangles(surface, x, y, color=(R,G,B))
plot.draw(surface)  # Draw axes and grid
```

### Legend
```python
legend = Legend(x, y)
legend.add_item("Label", (R,G,B))
legend.draw(surface)
```

---

## Data File Format

### CSV Requirements
- First row: column headers (any names)
- Columns: exactly 2 (x-data, y-data)
- Values: numeric
- X-values: sorted (auto-sorted if not)

### Example: cooling_data.csv
```csv
t,T
0,90
1,85
2,72
3,63
...
```

### Location
```
data/
├── cooling_data.csv
├── flow_data.csv
└── (any other .csv files)
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| ESC | Return to menu or exit |
| Mouse Drag | Slide sliders |
| Click | Buttons and dropdowns |

---

## Performance Tips

1. **Faster Plotting**: Use LinearSpline instead of Polynomial
2. **Smoother Interaction**: Close other applications
3. **Less Lag**: Reduce number of intervals slider
4. **Better Colors**: Use distinct RGB values in legend

---

## Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| Dataset not loading | Check file in `./data/` folder |
| Slow UI | Reduce data points or intervals |
| Curves not showing | Check dropdown selection |
| Results all zeros | Load data first with button |

---

## Mathematical Reference

### Interpolation Error
- **Polynomial**: $E = \frac{(x-x_0)...(x-x_n)}{(n+1)!} f^{(n+1)}(\xi)$
- **Spline**: $E = O(h^4)$ for cubic, $O(h^2)$ for linear

### Integration Error
- **Rectangle**: $E = -\frac{(b-a)h^2}{24} f''(\xi)$ → O(h²)
- **Simpson**: $E = -\frac{(b-a)h^4}{180} f^{(4)}(\xi)$ → O(h⁴)

### Golden Section Search
Iterations needed: $\approx -\log_{φ}(\epsilon)$ where $\phi = (1+\sqrt{5})/2 \approx 1.618$

---

## Code Snippets

### Integrate Custom Function
```python
from src.integration.newton_cotes import NewtonCotes
import math

result = NewtonCotes.simpson(math.exp, 0, 1, n=100)
```

### Interpolate with Spline
```python
from src.interpolation.cubic_spline import CubicSpline
import numpy as np

spline = CubicSpline(x_data, y_data)
y_interp = spline.evaluate(x_eval)
y_deriv = spline.derivative(x_eval, order=1)
```

### Run GUI
```python
from src.gui.app import AlgoNumApp

app = AlgoNumApp()
app.run()
```

---

## File Structure

```
AlgoNum/
├── gui_main.py                   ← Entry point
├── examples_gui.py               ← Usage examples
├── README_GUI.md                 ← This file
├── GUI_DOCUMENTATION.md          ← Detailed guide
├── data/
│   ├── cooling_data.csv
│   └── flow_data.csv
├── src/
│   ├── gui/
│   │   ├── app.py               ← Main app
│   │   ├── data_loader.py       ← CSV loading
│   │   ├── ui_components.py     ← UI widgets
│   │   ├── plotting.py          ← Plotting
│   │   └── screens.py           ← Screens
│   ├── interpolation/
│   ├── integration/
│   ├── applications/
│   └── visualization/
└── requirements.txt
```

---

## Getting Help

1. Read **GUI_DOCUMENTATION.md** for complete reference
2. Check **examples_gui.py** for code samples
3. Review docstrings in source files
4. Examine existing screen implementations

---

**Version**: 1.0.0  
**Updated**: May 2026
