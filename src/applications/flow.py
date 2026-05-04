"""
Module : flow.py
Modélisation de l'écoulement dans un canal à section variable.

Données expérimentales :
  x (m)   : [0, 0.5, 1.2, 1.8, 2.5, 3.1, 3.7, 4.2, 4.8, 5.3, 6.0]
  v (m/s) : [0, 2.1, 3.8, 5.2, 6.4, 7.0, 7.3, 7.2, 6.8, 5.9, 4.5]

Physique du problème :
  D = ∫₀⁶ v(x)·w(x) dx     avec w(x) = 0.5 + 0.1·x  (m)
"""

import numpy as np
import sys
import os

# Résolution des imports relatifs
_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC  = os.path.dirname(_HERE)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from interpolation.cubic_spline import CubicSpline
from integration.adaptive import AdaptiveIntegration
from integration.newton_cotes import NewtonCotes


class FlowProblem:
    """
    Modélise l'écoulement dans un canal à largeur variable.

    Utilise une spline cubique naturelle pour interpoler la vitesse mesurée,
    puis calcule le débit volumique total par intégration numérique.

    Attributes
    ----------
    x_data : ndarray
        Positions des mesures (m).
    v_data : ndarray
        Vitesses mesurées (m/s).
    width_func : callable
        Fonction w(x) décrivant la largeur du canal (m).
    """

    def __init__(self, x_data, v_data, width_func=None):
        """
        Initialise le problème d'écoulement.

        Parameters
        ----------
        x_data : array-like
            Positions des mesures (m). Doivent être strictement croissantes.
        v_data : array-like
            Vitesses correspondantes (m/s).
        width_func : callable, optional
            Fonction w(x) décrivant la largeur du canal (m).
            Par défaut : w(x) = 0.5 + 0.1·x.

        Raises
        ------
        ValueError
            Si x_data et v_data n'ont pas la même longueur, ou si x_data
            n'est pas strictement croissant.
        """
        x_data = np.array(x_data, dtype=float)
        v_data = np.array(v_data, dtype=float)

        if len(x_data) != len(v_data):
            raise ValueError("x_data et v_data doivent avoir la même longueur.")
        if np.any(np.diff(x_data) <= 0):
            raise ValueError("x_data doit être strictement croissant.")

        self.x_data    = x_data
        self.v_data    = v_data
        self.width_func = width_func if width_func is not None else (
            lambda x: 0.5 + 0.1 * x
        )
        self._spline = CubicSpline(self.x_data, self.v_data)

    # ------------------------------------------------------------------
    # Méthodes d'interpolation et de calcul physique
    # ------------------------------------------------------------------

    def velocity(self, x_eval):
        """
        Retourne la vitesse interpolée à la position x_eval.

        Utilise la spline cubique naturelle ajustée aux données expérimentales.

        Parameters
        ----------
        x_eval : float or array-like
            Position(s) d'évaluation (m).

        Returns
        -------
        float or ndarray
            Vitesse interpolée v(x) en m/s.

        Raises
        ------
        ValueError
            Si x_eval est hors des bornes [x_data[0], x_data[-1]].

        Examples
        --------
        >>> fp = FlowProblem(x_data, v_data)
        >>> fp.velocity(1.5)
        4.8...
        """
        x_eval = np.asarray(x_eval, dtype=float)
        scalar = x_eval.ndim == 0
        x_eval = np.atleast_1d(x_eval)

        x_min, x_max = self.x_data[0], self.x_data[-1]
        if np.any(x_eval < x_min) or np.any(x_eval > x_max):
            raise ValueError(
                f"x_eval est hors de l'intervalle [{x_min}, {x_max}]."
            )

        result = np.array([self._spline.evaluate(xi) for xi in x_eval])
        return float(result[0]) if scalar else result

    def local_flow_rate(self, x_eval):
        """
        Calcule le débit local q(x) = v(x) · w(x).

        Parameters
        ----------
        x_eval : float or array-like
            Position(s) d'évaluation (m).

        Returns
        -------
        float or ndarray
            Débit local (m²/s).
        """
        x_eval = np.asarray(x_eval, dtype=float)
        scalar = x_eval.ndim == 0
        x_eval = np.atleast_1d(x_eval)

        q = np.array([
            self.velocity(float(xi)) * self.width_func(float(xi))
            for xi in x_eval
        ])
        return float(q[0]) if scalar else q

    def total_flow_rate(self, method='adaptive', n=100):
        """
        Calcule le débit volumique total D sur toute la longueur du canal.

        D = ∫_{x0}^{xn} v(x)·w(x) dx

        Parameters
        ----------
        method : str, optional
            Méthode d'intégration : 'adaptive', 'trapezoid', 'simpson',
            'rectangle'. Par défaut 'adaptive'.
        n : int, optional
            Nombre de sous-intervalles pour les méthodes composées.
            Par défaut 100.

        Returns
        -------
        float
            Débit volumique total D (m³/s).

        Raises
        ------
        ValueError
            Si la méthode spécifiée est inconnue.

        Examples
        --------
        >>> fp = FlowProblem(x_data, v_data)
        >>> D = fp.total_flow_rate(method='adaptive')
        >>> print(f"D = {D:.4f} m³/s")
        """
        a = float(self.x_data[0])
        b = float(self.x_data[-1])

        def f(x):
            return self.local_flow_rate(float(x))

        if method == 'adaptive':
            ai = AdaptiveIntegration(tol=1e-6)
            return ai.adaptive_simpson(f, a, b)
        elif method == 'trapezoid':
            return NewtonCotes.trapezoidal(f, a, b, n)
        elif method == 'simpson':
            n_even = n if n % 2 == 0 else n + 1
            return NewtonCotes.simpson(f, a, b, n_even)
        elif method == 'rectangle':
            return NewtonCotes.rectangle(f, a, b, n)
        else:
            raise ValueError(
                f"Méthode '{method}' inconnue. Choisir parmi : "
                "'adaptive', 'trapezoid', 'simpson', 'rectangle'."
            )

    # ------------------------------------------------------------------
    # Dérivées et travail
    # ------------------------------------------------------------------

    def acceleration(self, x_eval):
        """
        Calcule la dérivée de la vitesse dv/dx à la position x_eval.

        Utilise la dérivée analytique de la spline cubique.

        Parameters
        ----------
        x_eval : float or array-like
            Position(s) d'évaluation (m).

        Returns
        -------
        float or ndarray
            Dérivée de la vitesse dv/dx (m/s par m = s⁻¹).

        Notes
        -----
        Dans le contexte de l'écoulement, dv/dx représente le gradient de
        vitesse longitudinal, lié à la compression/dilatation du fluide.
        """
        x_eval = np.asarray(x_eval, dtype=float)
        scalar = x_eval.ndim == 0
        x_eval = np.atleast_1d(x_eval)

        result = np.array([self._spline.derivative(float(xi), order=1) for xi in x_eval])
        return float(result[0]) if scalar else result

    def work(self, mass=2.0):
        """
        Calcule le travail exercé par le champ de vitesse sur une particule fluide.

        W = ∫_{x0}^{xn} m · (dv/dx)(x) · v(x) dx
          = m · ∫ v · dv/dx dx
          = m/2 · [v(xn)² − v(x0)²]   (par le théorème travail-énergie)

        Parameters
        ----------
        mass : float, optional
            Masse de la particule fluide (kg). Par défaut 2.0.

        Returns
        -------
        tuple (float, float)
            (travail numérique par intégration adaptative, valeur analytique) en J.

        Notes
        -----
        La valeur analytique sert de validation de la méthode numérique.
        """
        a = float(self.x_data[0])
        b = float(self.x_data[-1])

        def integrand(x):
            return mass * self.acceleration(float(x)) * self.velocity(float(x))

        ai = AdaptiveIntegration(tol=1e-6)
        W_numerical = ai.adaptive_simpson(integrand, a, b)

        # Valeur analytique : W = m/2 * (v_b² - v_a²)
        v_a = float(self.velocity(a))
        v_b = float(self.velocity(b))
        W_analytical = 0.5 * mass * (v_b**2 - v_a**2)

        return W_numerical, W_analytical

    # ------------------------------------------------------------------
    # Méthode utilitaire
    # ------------------------------------------------------------------

    def summary(self):
        """
        Affiche un résumé des résultats du problème d'écoulement.
        """
        print("=" * 55)
        print("    PROBLÈME D'ÉCOULEMENT — RÉSUMÉ")
        print("=" * 55)
        print(f"  Plage spatiale : [{self.x_data[0]}, {self.x_data[-1]}] m")
        print(f"  Largeur w(x) = 0.5 + 0.1·x  (m)")
        print()

        # Débit avec différentes méthodes
        methods = ['rectangle', 'trapezoid', 'simpson', 'adaptive']
        print("  Débit volumique total D :")
        for m in methods:
            D = self.total_flow_rate(method=m, n=100)
            print(f"    [{m:>10}] D = {D:.6f} m³/s")

        print()

        # Travail
        W_num, W_ana = self.work(mass=2.0)
        print(f"  Travail (numérique)  : W = {W_num:.6f} J")
        print(f"  Travail (analytique) : W = {W_ana:.6f} J")
        print(f"  Erreur relative      : {abs(W_num - W_ana) / abs(W_ana) * 100:.4f} %")
        print("=" * 55)