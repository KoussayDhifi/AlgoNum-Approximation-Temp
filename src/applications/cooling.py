"""
Module : cooling.py
Modélisation du refroidissement d'un composant électronique.

Données expérimentales :
  t (s)  : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
  T (°C) : [90, 85, 72, 63, 58, 52, 48, 45, 43, 41, 40]

Physique du problème :
  Q = ∫₀¹⁰ h·(T(t) − Tamb) dt     avec h = 50 J/°C, Tamb = 20 °C
"""

import numpy as np
import sys
import os

# Assure la résolution des imports relatifs quelle que soit la racine d'exécution
_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC  = os.path.dirname(_HERE)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from interpolation.cubic_spline import CubicSpline
from integration.adaptive import AdaptiveIntegration
from integration.newton_cotes import NewtonCotes


class CoolingProblem:
    """
    Modélise le refroidissement d'un composant électronique.

    Utilise une spline cubique naturelle pour interpoler la température mesurée
    en fonction du temps, puis calcule numériquement la perte de chaleur totale.

    Attributes
    ----------
    t_data : ndarray
        Temps des mesures (secondes).
    T_data : ndarray
        Températures mesurées (°C).
    T_ambient : float
        Température ambiante (°C), par défaut 20.
    h_coeff : float
        Coefficient d'échange thermique (J/°C), par défaut 50.
    """

    def __init__(self, t_data, T_data, T_ambient=20.0, h_coeff=50.0):
        """
        Initialise le problème de refroidissement.

        Parameters
        ----------
        t_data : array-like
            Instants de mesure (s). Doivent être strictement croissants.
        T_data : array-like
            Températures correspondantes (°C).
        T_ambient : float, optional
            Température ambiante Tamb (°C). Par défaut 20.0.
        h_coeff : float, optional
            Coefficient d'échange h (J/°C). Par défaut 50.0.

        Raises
        ------
        ValueError
            Si t_data et T_data n'ont pas la même longueur, ou si t_data n'est
            pas strictement croissant.
        """
        t_data = np.array(t_data, dtype=float)
        T_data = np.array(T_data, dtype=float)

        if len(t_data) != len(T_data):
            raise ValueError("t_data et T_data doivent avoir la même longueur.")
        if np.any(np.diff(t_data) <= 0):
            raise ValueError("t_data doit être strictement croissant.")

        self.t_data    = t_data
        self.T_data    = T_data
        self.T_ambient = T_ambient
        self.h_coeff   = h_coeff
        self._spline   = CubicSpline(self.t_data, self.T_data)

    # ------------------------------------------------------------------
    # Méthodes d'interpolation / calcul physique
    # ------------------------------------------------------------------

    def temperature(self, t_eval):
        """
        Retourne la température interpolée à l'instant t_eval.

        Utilise la spline cubique naturelle ajustée aux données expérimentales.

        Parameters
        ----------
        t_eval : float or array-like
            Instant(s) d'évaluation (s).

        Returns
        -------
        float or ndarray
            Température interpolée T(t) en °C.

        Raises
        ------
        ValueError
            Si t_eval est hors des bornes [t_data[0], t_data[-1]].

        Examples
        --------
        >>> cp = CoolingProblem([0,1,2,3], [90,85,72,63])
        >>> cp.temperature(0.5)
        87.5...
        """
        t_eval = np.asarray(t_eval, dtype=float)
        scalar = t_eval.ndim == 0 #detecte si c est scalaire 
        t_eval = np.atleast_1d(t_eval)

        t_min, t_max = self.t_data[0], self.t_data[-1]
        if np.any(t_eval < t_min) or np.any(t_eval > t_max):
            raise ValueError(
                f"t_eval={t_eval} est hors de l'intervalle [{t_min}, {t_max}]."
            )
#le spline cubique naturelle est défini sur l'intervalle [t_data[0], t_data[-1]], donc on vérifie que les instants d'évaluation sont bien dans cette plage. Si ce n'est pas le cas, une exception est levée pour éviter des extrapolations non fiables.
        result = np.array([self._spline.evaluate(ti) for ti in t_eval])
        return float(result[0]) if scalar else result

    def heat_loss_rate(self, t_eval):
        """
        Calcule le taux instantané de perte de chaleur Q'(t).

        Q'(t) = h × (T(t) − Tamb)

        Parameters
        ----------
        t_eval : float or array-like
            Instant(s) d'évaluation (s).

        Returns
        -------
        float or ndarray
            Taux de perte de chaleur (W = J/s).
        """
        T = self.temperature(t_eval)
        return self.h_coeff * (T - self.T_ambient)

    def total_heat_loss(self, method='adaptive', n=100):
        """
        Calcule la perte de chaleur totale sur [t₀, tₙ].

        Q = ∫_{t0}^{tn} h·(T(t) − Tamb) dt

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
            Perte de chaleur totale Q (J).

        Raises
        ------
        ValueError
            Si la méthode spécifiée est inconnue.

        Examples
        --------
        >>> cp = CoolingProblem(t_data, T_data)
        >>> Q = cp.total_heat_loss(method='adaptive')
        >>> print(f"Q = {Q:.2f} J")
        """
        a = float(self.t_data[0])
        b = float(self.t_data[-1])

        def f(t):
            return self.heat_loss_rate(float(t))

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
    # Modèle exponentiel et problème inverse
    # ------------------------------------------------------------------

    def exponential_model(self, t_eval, k):
        """
        Modèle de refroidissement exponentiel (loi de Newton).

        T_model(t) = Tamb + (T₀ − Tamb) × exp(−k × t)

        Parameters
        ----------
        t_eval : float or array-like
            Instant(s) d'évaluation (s).
        k : float
            Constante de refroidissement (s⁻¹), k > 0.

        Returns
        -------
        float or ndarray
            Température du modèle en °C.

        Raises
        ------
        ValueError
            Si k ≤ 0.
        """
        if k <= 0:
            raise ValueError("La constante de refroidissement k doit être > 0.")
        T0 = float(self.T_data[0])
        t_eval = np.asarray(t_eval, dtype=float)
        return self.T_ambient + (T0 - self.T_ambient) * np.exp(-k * t_eval)

    def model_error(self, k):
        """
        Calcule l'erreur intégrale entre les données et le modèle exponentiel.

        E(k) = ∫_{t0}^{tn} |T_exp(t) − T_model(t, k)| dt

        Parameters
        ----------
        k : float
            Constante de refroidissement à évaluer.

        Returns
        -------
        float
            Erreur intégrale E(k) ≥ 0.
        """
        a = float(self.t_data[0])
        b = float(self.t_data[-1])

        def integrand(t):
            T_exp   = self.temperature(float(t))
            T_model = float(self.exponential_model(float(t), k))
            return abs(T_exp - T_model)

        ai = AdaptiveIntegration(tol=1e-6)
        return ai.adaptive_simpson(integrand, a, b)

    def estimate_k(self, k_min=0.01, k_max=0.5, tol=1e-4):
        """
        Estime la constante optimale k minimisant l'erreur E(k).

        Utilise la recherche par section dorée (Golden Section Search),
        une méthode d'optimisation sans dérivée pour fonctions unimodales.

        Parameters
        ----------
        k_min : float, optional
            Borne inférieure de recherche (par défaut 0.01).
        k_max : float, optional
            Borne supérieure de recherche (par défaut 0.5).
        tol : float, optional
            Tolérance de convergence (par défaut 1e-4).

        Returns
        -------
        float
            Valeur optimale k* minimisant E(k) sur [k_min, k_max].

        Notes
        -----
        La section dorée divise l'intervalle par le rapport φ = (√5-1)/2 ≈ 0.618
        à chaque itération, garantissant la convergence en O(log(1/tol)) étapes.
        """
        golden_ratio = (np.sqrt(5) - 1) / 2.0
        a, b = k_min, k_max

        c = b - golden_ratio * (b - a)
        d = a + golden_ratio * (b - a)

        while abs(b - a) > tol:
            Ec = self.model_error(c)
            Ed = self.model_error(d)

            if Ec < Ed:
                b = d
            else:
                a = c

            # Recalcul des points intérieurs
            c = b - golden_ratio * (b - a)
            d = a + golden_ratio * (b - a)

        k_opt = (a + b) / 2.0
        return k_opt

    # ------------------------------------------------------------------
    # Méthode utilitaire
    # ------------------------------------------------------------------

    def summary(self):
        """
        Affiche un résumé des résultats du problème de refroidissement.
        """
        print("=" * 55)
        print("    PROBLÈME DE REFROIDISSEMENT — RÉSUMÉ")
        print("=" * 55)
        print(f"  Tamb = {self.T_ambient} °C  |  h = {self.h_coeff} J/°C")
        print(f"  Plage temporelle : [{self.t_data[0]}, {self.t_data[-1]}] s")
        print()

        # Températures interpolées aux instants demandés
        for t_eval in [2.5, 7.3]:
            T_val = self.temperature(t_eval)
            print(f"  T(t={t_eval} s) = {T_val:.4f} °C")

        print()

        # Perte de chaleur avec différentes méthodes
        methods = ['rectangle', 'trapezoid', 'simpson', 'adaptive']
        print("  Perte de chaleur totale Q :")
        for m in methods:
            Q = self.total_heat_loss(method=m, n=100)
            print(f"    [{m:>10}] Q = {Q:.4f} J")

        print()

        # k optimal
        k_opt = self.estimate_k()
        print(f"  Constante de refroidissement optimale k* = {k_opt:.6f} s⁻¹")
        print(f"  Erreur E(k*) = {self.model_error(k_opt):.6f}")
        print("=" * 55)