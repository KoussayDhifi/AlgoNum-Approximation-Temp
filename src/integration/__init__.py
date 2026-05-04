"""
Package integration
===================
Méthodes d'intégration numérique :
- NewtonCotes  : rectangle, trapèzes, Simpson 1/3, Simpson 3/8
- AdaptiveIntegration : méthode de Simpson adaptative
- GaussQuadrature : quadrature de Gauss-Legendre (bonus)
"""

from .newton_cotes import NewtonCotes
from .adaptive import AdaptiveIntegration
from .gauss import GaussQuadrature

__all__ = ["NewtonCotes", "AdaptiveIntegration", "GaussQuadrature"]