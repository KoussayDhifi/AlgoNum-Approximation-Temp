"""
Package applications
====================
Applications des méthodes numériques aux problèmes physiques :
- CoolingProblem : refroidissement d'un composant électronique
- FlowProblem    : écoulement dans un canal à section variable
"""

from .cooling import CoolingProblem
from .flow import FlowProblem

__all__ = ["CoolingProblem", "FlowProblem"]