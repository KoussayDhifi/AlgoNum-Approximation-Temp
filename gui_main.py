#!/usr/bin/env python3
"""
gui_main.py - Entry point for AlgoNum GUI application

Usage:
    python3 gui_main.py
"""

import sys
import os

# Ensure proper path resolution
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_HERE)

if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.gui.app import AlgoNumApp


def main():
    """Run the GUI application."""
    print("=" * 70)
    print("AlgoNum - Interactive GUI for Numerical Analysis")
    print("=" * 70)
    print()
    print("Controls:")
    print("  - Click buttons to navigate and change parameters")
    print("  - Drag sliders to adjust values in real-time")
    print("  - Use dropdowns to select datasets and methods")
    print("  - Press ESC or close window to exit")
    print()
    
    app = AlgoNumApp(width=1400, height=700)
    app.run()


if __name__ == '__main__':
    main()
