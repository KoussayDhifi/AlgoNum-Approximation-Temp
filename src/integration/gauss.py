"""
Module : gauss.py
Implémentation de la quadrature de Gauss-Legendre (bonus).
Méthodes à 2 et 3 points sur un intervalle général [a, b].
"""

import numpy as np


class GaussQuadrature:
    """
    Quadrature de Gauss-Legendre pour l'intégration numérique.

    La quadrature de Gauss-Legendre à n points est exacte pour les polynômes
    de degré ≤ 2n-1. Elle utilise des abscisses et des poids optimalement
    choisis sur l'intervalle de référence [-1, 1], puis les transforme sur [a, b].

    Transformation affine : x = (a+b)/2 + t*(b-a)/2,  t ∈ [-1, 1]
    """

    # Abscisses et poids de Gauss-Legendre sur [-1, 1]
    # Source : formules analytiques exactes
    _NODES_WEIGHTS = {
        2: (
            np.array([-1.0 / np.sqrt(3), 1.0 / np.sqrt(3)]),
            np.array([1.0, 1.0])
        ),
        3: (
            np.array([-np.sqrt(3.0 / 5.0), 0.0, np.sqrt(3.0 / 5.0)]),
            np.array([5.0 / 9.0, 8.0 / 9.0, 5.0 / 9.0])
        ),
        4: (
            np.array([
                -np.sqrt((3 + 2 * np.sqrt(6.0 / 5.0)) / 7.0),
                -np.sqrt((3 - 2 * np.sqrt(6.0 / 5.0)) / 7.0),
                 np.sqrt((3 - 2 * np.sqrt(6.0 / 5.0)) / 7.0),
                 np.sqrt((3 + 2 * np.sqrt(6.0 / 5.0)) / 7.0)
            ]),
            np.array([
                (18 - np.sqrt(30)) / 36.0,
                (18 + np.sqrt(30)) / 36.0,
                (18 + np.sqrt(30)) / 36.0,
                (18 - np.sqrt(30)) / 36.0
            ])
        ),
        5: (
            np.array([
                -np.sqrt(5 + 2 * np.sqrt(10.0 / 7.0)) / 3.0,
                -np.sqrt(5 - 2 * np.sqrt(10.0 / 7.0)) / 3.0,
                 0.0,
                 np.sqrt(5 - 2 * np.sqrt(10.0 / 7.0)) / 3.0,
                 np.sqrt(5 + 2 * np.sqrt(10.0 / 7.0)) / 3.0
            ]),
            np.array([
                (322 - 13 * np.sqrt(70)) / 900.0,
                (322 + 13 * np.sqrt(70)) / 900.0,
                128.0 / 225.0,
                (322 + 13 * np.sqrt(70)) / 900.0,
                (322 - 13 * np.sqrt(70)) / 900.0
            ])
        )
    }

    @classmethod
    def _gauss(cls, f, a, b, n_points):
        """
        Méthode générique de quadrature de Gauss-Legendre à n points.

        Parameters
        ----------
        f : callable
            Fonction à intégrer.
        a : float
            Borne inférieure.
        b : float
            Borne supérieure.
        n_points : int
            Nombre de points de quadrature (2, 3, 4 ou 5).

        Returns
        -------
        float
            Valeur approchée de l'intégrale.
        """
        if n_points not in cls._NODES_WEIGHTS:
            raise ValueError(f"Nombre de points {n_points} non supporté. Choisir parmi {list(cls._NODES_WEIGHTS.keys())}.")

        nodes, weights = cls._NODES_WEIGHTS[n_points]

        # Transformation affine de [-1,1] vers [a,b]
        mid   = (a + b) / 2.0
        half  = (b - a) / 2.0
        x_mapped = mid + half * nodes

        # Évaluation et somme pondérée
        y_values = np.array([f(xi) for xi in x_mapped])
        return half * np.dot(weights, y_values)

    @classmethod
    def gauss_legendre_2(cls, f, a, b):
        """
        Quadrature de Gauss-Legendre à 2 points.

        Exacte pour les polynômes de degré ≤ 3.

        Abscisses : t₁ = -1/√3,  t₂ = +1/√3
        Poids     : w₁ = w₂ = 1

        Parameters
        ----------
        f : callable
            Fonction à intégrer.
        a : float
            Borne inférieure.
        b : float
            Borne supérieure.

        Returns
        -------
        float
            Valeur approchée de l'intégrale.

        Examples
        --------
        >>> import math
        >>> GaussQuadrature.gauss_legendre_2(math.exp, 0, 1)
        1.71828...
        """
        return cls._gauss(f, a, b, 2)

    @classmethod
    def gauss_legendre_3(cls, f, a, b):
        """
        Quadrature de Gauss-Legendre à 3 points.

        Exacte pour les polynômes de degré ≤ 5.

        Abscisses : t₁ = -√(3/5),  t₂ = 0,  t₃ = +√(3/5)
        Poids     : w₁ = w₃ = 5/9,  w₂ = 8/9

        Parameters
        ----------
        f : callable
            Fonction à intégrer.
        a : float
            Borne inférieure.
        b : float
            Borne supérieure.

        Returns
        -------
        float
            Valeur approchée de l'intégrale.
        """
        return cls._gauss(f, a, b, 3)

    @classmethod
    def gauss_legendre_4(cls, f, a, b):
        """Quadrature de Gauss-Legendre à 4 points. Exacte pour deg ≤ 7."""
        return cls._gauss(f, a, b, 4)

    @classmethod
    def gauss_legendre_5(cls, f, a, b):
        """Quadrature de Gauss-Legendre à 5 points. Exacte pour deg ≤ 9."""
        return cls._gauss(f, a, b, 5)

    @classmethod
    def composite_gauss(cls, f, a, b, n_intervals, n_points=3):
        """
        Quadrature de Gauss composite : applique la quadrature de Gauss
        sur n_intervals sous-intervalles égaux.

        Parameters
        ----------
        f : callable
            Fonction à intégrer.
        a : float
            Borne inférieure.
        b : float
            Borne supérieure.
        n_intervals : int
            Nombre de sous-intervalles.
        n_points : int, optional
            Nombre de points de Gauss par intervalle (par défaut 3).

        Returns
        -------
        float
            Valeur approchée de l'intégrale.
        """
        h = (b - a) / n_intervals
        total = 0.0
        for i in range(n_intervals):
            ai = a + i * h
            bi = ai + h
            total += cls._gauss(f, ai, bi, n_points)
        return total