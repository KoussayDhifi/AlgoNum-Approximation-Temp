"""
Module : linear_spline.py
Implémentation de l'interpolation par spline linéaire.
"""

import numpy as np


class LinearSpline:
    """
    Interpolation linéaire par morceaux (spline linéaire).

    Connecte les points de données consécutifs par des segments de droite.
    Simple, mais C⁰ seulement (continuité de position, pas de dérivée).

    Attributes
    ----------
    x_points : ndarray
        Points d'abscisse (doivent être triés en ordre croissant).
    y_points : ndarray
        Valeurs de la fonction aux points x_points.
    n : int
        Nombre de points.
    """

    def __init__(self, x_points, y_points):
        """
        Initialise la spline linéaire.

        Parameters
        ----------
        x_points : array-like
            Abscisses des points d'interpolation.
        y_points : array-like
            Ordonnées des points d'interpolation.

        Raises
        ------
        ValueError
            Si les tableaux n'ont pas la même longueur ou si x_points
            n'est pas strictement croissant.
        """
        self.x_points = np.asarray(x_points, dtype=float)
        self.y_points = np.asarray(y_points, dtype=float)

        if len(self.x_points) != len(self.y_points):
            raise ValueError("x_points et y_points doivent avoir la même longueur.")

        if len(self.x_points) < 2:
            raise ValueError("Au moins 2 points sont nécessaires pour une interpolation.")

        if not np.all(np.diff(self.x_points) > 0):
            raise ValueError("Les x_points doivent être strictement croissants.")

        self.n = len(self.x_points)

    def _find_interval(self, x):
        """
        Trouve l'indice i tel que x_points[i] <= x < x_points[i+1].

        Utilise une dichotomie pour une recherche O(log n).

        Parameters
        ----------
        x : float
            Valeur à rechercher.

        Returns
        -------
        int
            Indice i du sous-intervalle contenant x.
            Retourne n-2 si x >= x_points[-1] (dernier intervalle).

        Raises
        ------
        ValueError
            Si x < x_points[0].
        """
        if x < self.x_points[0]:
            raise ValueError(
                f"x = {x} est en dehors du domaine d'interpolation "
                f"[{self.x_points[0]}, {self.x_points[-1]}]."
            )

        # Si x dépasse le dernier point, retourne le dernier intervalle
        if x >= self.x_points[-1]:
            return self.n - 2

        # Dichotomie
        left, right = 0, self.n - 1
        while left < right - 1:
            mid = (left + right) // 2
            if self.x_points[mid] <= x:
                left = mid
            else:
                right = mid

        return left

    def evaluate(self, x_eval):
        """
        Évalue la spline linéaire aux points x_eval.

        Parameters
        ----------
        x_eval : float or array-like
            Point(s) d'évaluation.

        Returns
        -------
        float or ndarray
            Valeur(s) interpolée(s).

        Examples
        --------
        >>> x = [0, 1, 2]
        >>> y = [0, 1, 0]
        >>> spline = LinearSpline(x, y)
        >>> spline.evaluate(0.5)
        0.5
        >>> spline.evaluate([0.5, 1.5])
        array([0.5, 0.5])
        """
        scalar_input = np.isscalar(x_eval)
        x_eval = np.atleast_1d(x_eval).astype(float)

        result = np.zeros_like(x_eval)

        for k, x in enumerate(x_eval):
            i = self._find_interval(x)
            x0, x1 = self.x_points[i], self.x_points[i + 1]
            y0, y1 = self.y_points[i], self.y_points[i + 1]

            # Interpolation linéaire : y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
            result[k] = y0 + (y1 - y0) * (x - x0) / (x1 - x0)

        return result[0] if scalar_input else result
