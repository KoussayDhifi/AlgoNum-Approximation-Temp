# AlgoNum GUI - Best Practices & Design Patterns

## Architecture Principles

### 1. Separation of Concerns

**GUI Layer** ≠ **Numerical Layer**

```
┌─────────────────────────────────┐
│   GUI (pygame visualization)    │
├─────────────────────────────────┤
│   UI Components & Screens       │
├─────────────────────────────────┤
│   Plotting & Data Management    │
├─────────────────────────────────┤
│   Existing Numerical Classes    │
│   (Interpolation, Integration)  │
└─────────────────────────────────┘
```

**Benefits**:
- GUI can be replaced (e.g., with web UI)
- Numerical code testable independently
- Easy to add new numerical methods
- Reusable across projects

---

### 2. Component-Based Design

Each UI element is **self-contained**:

```python
# Button doesn't know about other buttons
button = Button(10, 10, 100, 40, "Click Me",
               callback=my_function)

# Slider manages its own state
slider = Slider(10, 60, 200,
               min_val=0, max_val=100,
               on_change=my_callback)

# Both follow same interface
button.handle_event(event)
button.update(mouse_pos)
button.draw(surface)
```

**Advantages**:
- Reusability across screens
- Easy testing of individual components
- No hidden dependencies
- Composable

---

### 3. Screen/Mode Pattern

Each screen is **independent state machine**:

```python
class Screen:
    def handle_event(self, event):
        # Route events to components
        for comp in self.components:
            comp.handle_event(event)
    
    def update(self, mouse_pos):
        # Update component states
        for comp in self.components:
            comp.update(mouse_pos)
    
    def draw(self, surface):
        # Render all components
        for comp in self.components:
            comp.draw(surface)
```

**Pattern Flow**:
```
Event Handler → Screen → Components
Screen Update → Components Update State
Screen Draw → Components Draw
```

---

### 4. Observer Pattern (Callbacks)

Components notify listeners of state changes:

```python
# Define callback
def on_value_changed(new_value):
    print(f"New value: {new_value}")
    self._recompute()

# Attach to component
slider = Slider(..., on_change=on_value_changed)

# Component triggers callback
slider.value = new_value
if self.on_change:
    self.on_change(self.value)
```

**Benefits**:
- Loose coupling
- Reactive updates
- Easy to chain actions

---

## Design Patterns Used

### Pattern 1: Factory Pattern (Data Loading)

```python
class DataLoader:
    def get_dataset(self, name):
        """Factory method for data."""
        return self.datasets.get(name)
```

**When to use**: Creating objects based on configuration.

---

### Pattern 2: Strategy Pattern (Integration Methods)

```python
# Different strategies for same problem
strategies = {
    'Rectangle': NewtonCotes.rectangle,
    'Trapezoidal': NewtonCotes.trapezoidal,
    'Simpson': NewtonCotes.simpson,
    'Adaptive': AdaptiveIntegration.adaptive_simpson
}

# Select strategy at runtime
strategy = strategies[method_name]
result = strategy(f, a, b, n)
```

**When to use**: Choosing algorithm implementation at runtime.

---

### Pattern 3: Template Method (Screen Base)

```python
class Screen:
    """Template defines structure."""
    
    def handle_event(self, event):
        for component in self.components:
            component.handle_event(event)
    
    def draw(self, surface):
        surface.fill((10, 10, 20))
        for component in self.components:
            component.draw(surface)

class MyScreen(Screen):
    """Subclass fills in details."""
    
    def __init__(self, ...):
        super().__init__(...)
        self.components = [...]  # Specific components
```

**When to use**: When multiple classes follow same structure.

---

### Pattern 4: Composite Pattern (UI Components)

```python
class UIComponent:
    """Base component."""
    def handle_event(self, event): pass
    def update(self, mouse_pos): pass
    def draw(self, surface): pass

class Container:
    """Composite - contains other components."""
    def __init__(self):
        self.components = []
    
    def handle_event(self, event):
        for comp in self.components:  # Delegate
            comp.handle_event(event)
```

**When to use**: Hierarchical UI structures.

---

### Pattern 5: MVC (Model-View-Controller)

```
┌──────────────┐
│  MODEL       │  (Numerical computation)
│  CoolingProb │  Stores state, computes results
└────┬─────────┘
     │ notify changes
     ↓
┌──────────────┐
│  VIEW        │  (Visual representation)
│  Screen      │  Plots curves, displays values
└────┬─────────┘
     │ user input
     ↓
┌──────────────┐
│  CONTROLLER  │  (Event handling)
│  Button/Sli  │  Updates model, refreshes view
└──────────────┘
```

**Implementation**:
```python
# Model
self.cooling = CoolingProblem(...)

# View
self.plot_area = PlotArea(...)

# Controller
self.k_slider = Slider(
    ...,
    on_change=lambda k: self._update_model(k)
)
```

---

## Code Organization Best Practices

### 1. File Structure

```
gui/
├── __init__.py                  # Package marker
├── app.py                       # Main (largest file)
├── data_loader.py               # Utilities
├── ui_components.py             # UI widgets
├── plotting.py                  # Plotting
└── screens.py                   # Screen logic
```

**Guideline**: Files <500 lines, classes <400 lines, methods <50 lines

---

### 2. Naming Conventions

```python
# Classes: PascalCase
class MainMenuScreen: pass
class DataLoader: pass

# Functions/methods: snake_case
def load_dataset(name): pass
def on_slider_changed(value): pass

# Constants: UPPER_SNAKE_CASE
DEFAULT_WIDTH = 1400
MAX_INTERVALS = 200

# Private: _leading_underscore
def _internal_method(self): pass
self._private_state = None
```

---

### 3. Documentation

```python
def plot_points(self, surface, x_data, y_data, 
               color=(200, 100, 100), size=5):
    """
    Plot discrete data points on the graph.
    
    Parameters
    ----------
    surface : pygame.Surface
        Target drawing surface
    x_data : ndarray
        X coordinates of points
    y_data : ndarray
        Y coordinates of points
    color : tuple, optional
        RGB color (default: red)
    size : int, optional
        Point radius in pixels (default: 5)
    
    Examples
    --------
    >>> plot.plot_points(surface, [0, 1, 2], [1, 2, 3])
    """
```

---

### 4. Error Handling

```python
# Don't crash - handle gracefully
def _on_dataset_changed(self, index, name):
    try:
        x_data, y_data = self.app.data_loader.get_dataset(name)
        
        if x_data is None:
            print(f"Warning: Could not load {name}")
            return
        
        self.x_data = x_data
        self._update_plot()
    
    except Exception as e:
        print(f"Error loading dataset: {e}")
        import traceback
        traceback.print_exc()
```

---

## Performance Optimization Tips

### 1. Minimize Redraws

```python
# BAD: Redraw everything every frame
def draw(self, surface):
    for x in range(1000):
        for y in range(1000):
            pygame.draw.pixel(...)

# GOOD: Only draw changed regions
def draw(self, surface):
    if self.needs_redraw:
        self._render_to_cache()
        self.needs_redraw = False
    surface.blit(self.cache, (0, 0))
```

---

### 2. Vectorize Computations

```python
# BAD: Loop through arrays
y = []
for x_val in x_array:
    y.append(f(x_val))

# GOOD: Use NumPy vectorization
y = f(x_array)  # Much faster
```

---

### 3. Lazy Evaluation

```python
# Only compute when needed
self.interpolated_y = None  # Don't compute yet

def draw(self, surface):
    if self.interpolated_y is None:
        self._compute_interpolation()  # Compute on demand
    
    plot.plot_line(surface, ..., self.interpolated_y)
```

---

### 4. Cache Results

```python
class Screen:
    def __init__(self, ...):
        self._cached_results = {}
    
    def compute(self, parameters):
        key = hash(parameters)
        
        if key not in self._cached_results:
            self._cached_results[key] = self._do_compute(parameters)
        
        return self._cached_results[key]
```

---

## Testing Strategies

### Unit Testing (Components)

```python
import pytest

def test_button_click():
    clicked = False
    def callback():
        nonlocal clicked
        clicked = True
    
    button = Button(0, 0, 100, 40, "Test", callback=callback)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (50, 20)})
    button.handle_event(event)
    
    assert clicked == True
```

### Integration Testing (Screens)

```python
def test_interpolation_screen():
    screen = InterpolationScreen(800, 600, app=app)
    
    # Simulate dataset selection
    screen._on_dataset_changed(0, 'cooling_data')
    
    # Check state updated
    assert screen.x_data is not None
    assert screen.y_data is not None
```

### Visual Testing

```python
# Run app and manually verify:
# - Button colors change on hover
# - Slider follows mouse
# - Curves update in real-time
# - Menu transitions work
```

---

## Common Pitfalls to Avoid

### ❌ Pitfall 1: Tight Coupling

```python
# BAD: Component knows about Screen
class Button:
    def __init__(self, ..., screen):
        self.screen = screen
        self.callback = lambda: screen.update_plot()

# GOOD: Generic callback
class Button:
    def __init__(self, ..., callback=None):
        self.callback = callback
```

---

### ❌ Pitfall 2: Mutable Default Arguments

```python
# BAD: Shared mutable default
def plot_points(x_data, y_data, color=[255, 0, 0]):
    color[0] = 100  # Modifies shared default!

# GOOD: None sentinel
def plot_points(x_data, y_data, color=None):
    if color is None:
        color = [255, 0, 0]
```

---

### ❌ Pitfall 3: Missing Error Checks

```python
# BAD: Assumes data exists
x = data[0]  # Crash if empty

# GOOD: Validate first
if not data:
    print("No data")
    return
x = data[0]
```

---

### ❌ Pitfall 4: Global State

```python
# BAD: Global variables
global current_screen
current_screen = None

# GOOD: Pass through constructor
class App:
    def __init__(self):
        self.current_screen = None
```

---

## Refactoring Examples

### Before: Monolithic Screen

```python
class CoolingScreen(Screen):
    def __init__(self, ...):
        # 200 lines of setup
        self.button1 = Button(...)
        self.button2 = Button(...)
        # ... many more components
```

### After: Organized Setup

```python
class CoolingScreen(Screen):
    def __init__(self, ...):
        super().__init__(...)
        self.plot_area = PlotArea(...)
        self._setup_controls()
        self._setup_callbacks()
    
    def _setup_controls(self):
        """Create UI components."""
        self.components.append(Button(...))
    
    def _setup_callbacks(self):
        """Wire up event handlers."""
        self.button.callback = self._on_button_click
```

---

## Debugging Tips

### 1. Print Debugging

```python
# Quick debug output
print(f"DEBUG: state={self.state}, value={value}")

# With timestamps
import time
print(f"[{time.time():.2f}] Event fired")
```

### 2. Visual Debugging

```python
# Draw debug info on screen
font = pygame.font.Font(None, 16)
text = font.render(f"FPS: {self.clock.get_fps():.0f}", True, (255,0,0))
surface.blit(text, (10, 10))
```

### 3. Breakpoints

```python
# In PyCharm, VS Code: click line number to set breakpoint
# In terminal: use pdb
import pdb; pdb.set_trace()
```

---

## Documentation Best Practices

### Module-Level Docstring

```python
"""
screens.py - Screen/Mode management for GUI application

This module contains the base Screen class and all concrete screen
implementations (MainMenu, Interpolation, Integration, etc).

Classes:
    Screen - Base class for all screens
    MainMenuScreen - Main menu with mode selection
    InterpolationScreen - Interpolation visualization
    ... (list others)

Example:
    >>> screen = InterpolationScreen(800, 600, app=app)
    >>> screen.handle_event(event)
    >>> screen.draw(surface)
"""
```

### Class-Level Docstring

```python
class DataLoader:
    """
    Manages CSV file loading and caching.
    
    Attributes
    ----------
    datasets : dict
        Cached datasets {name: (x_data, y_data)}
    """
```

### Method Docstring

```python
def get_dataset(self, name):
    """
    Retrieve dataset by name.
    
    Parameters
    ----------
    name : str
        Dataset name (filename without .csv)
    
    Returns
    -------
    tuple
        (x_array, y_array) or (None, None) if not found
    """
```

---

## Summary of Best Practices

| Practice | Why | How |
|----------|-----|-----|
| Modular design | Easy to test and extend | Separate concerns |
| Clear naming | Self-documenting code | Descriptive names |
| DRY principle | Less bugs, easier maintenance | Extract repetition |
| Error handling | Graceful degradation | Try-except, validation |
| Documentation | Easy to use and maintain | Docstrings + comments |
| Performance | Good UX | Profile and optimize |
| Testing | Reliable code | Unit + integration tests |

---

**Version**: 1.0  
**Last Updated**: May 2026
