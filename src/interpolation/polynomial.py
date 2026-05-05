"""
Module : polynomial.py
Implémentation de l'interpolation polynomiale.
Méthodes : Lagrange, Newton (différences divisées), interface unifiée.
"""

import numpy as np


class PolynomialInterpolation:
    """
    Interpolation polynomiale par les méthodes de Lagrange et de Newton.

    Étant donnés n+1 points (x_i, y_i) distincts, construit le polynôme
    d'interpolation unique de degré ≤ n passant par tous les points.

    Attributes
    ----------
    x_points : ndarray
        Abscisses des points d'interpolation (doivent être distinctes).
    y_points : ndarray
        Ordonnées des points d'interpolation.
    _dd_coeffs : ndarray or None
        Coefficients de Newton (différences divisées), calculés à la demande.
    """

    def __init__(self, x_points, y_points):
        """
        Initialise l'interpolateur polynomial.

        Parameters
        ----------
        x_points : array-like
            Abscisses des points de données. Doivent être toutes distinctes.
        y_points : array-like
            Ordonnées correspondantes.

        Raises
        ------
        ValueError
            Si x_points et y_points n'ont pas la même longueur.
        ValueError
            Si des abscisses sont répétées (points non distincts).
        ValueError
            Si moins de 2 points sont fournis.

        Examples
        --------
        >>> pi = PolynomialInterpolation([0, 1, 2], [1, 3, 7])
        >>> pi.evaluate(1.5)
        4.75
        """
        x_points = np.array(x_points, dtype=float)
        y_points = np.array(y_points, dtype=float)

        if len(x_points) < 2:
            raise ValueError("Il faut au moins 2 points pour l'interpolation.")
        if len(x_points) != len(y_points):
            raise ValueError(
                f"x_points ({len(x_points)}) et y_points ({len(y_points)}) "
                "doivent avoir la même longueur."
            )
        # Vérification des abscisses distinctes
        if len(np.unique(x_points)) != len(x_points):
            raise ValueError(
                "Les abscisses x_points doivent être toutes distinctes."
            )

        self.x_points = x_points
        self.y_points = y_points
        self._dd_coeffs = None  # calculés à la demande

    # ------------------------------------------------------------------
    # Méthode de Lagrange
    # ------------------------------------------------------------------

    def lagrange(self, x_eval):
        """
        Évalue le polynôme d'interpolation de Lagrange en x_eval.

        Formule :
            P(x) = Σᵢ yᵢ · Lᵢ(x)

        où les polynômes de base de Lagrange sont :
            Lᵢ(x) = Π_{j≠i} (x − xⱼ) / (xᵢ − xⱼ)

        Chaque Lᵢ(x) vaut 1 en xᵢ et 0 en tous les autres nœuds.

        Parameters
        ----------
        x_eval : float or array-like
            Point(s) où évaluer le polynôme.

        Returns
        -------
        float or ndarray
            Valeur(s) du polynôme interpolant en x_eval.

        Notes
        -----
        Complexité : O(n²) par point d'évaluation.
        Pour de nombreux points, préférer newton_eval (O(n) après initialisation).

        Examples
        --------
        >>> pi = PolynomialInterpolation([0, 1, 2], [1, 3, 7])
        >>> pi.lagrange(1.5)
        4.75
        """
        x_eval = np.asarray(x_eval, dtype=float)
        scalar = x_eval.ndim == 0
        x_eval = np.atleast_1d(x_eval)

        n = len(self.x_points)
        result = np.zeros_like(x_eval)

        for i in range(n):
            # Calcul du polynôme de base Lᵢ(x)
            Li = np.ones_like(x_eval)
            for j in range(n):
                if j != i:
                    Li *= (x_eval - self.x_points[j]) / (self.x_points[i] - self.x_points[j])
            result += self.y_points[i] * Li

        return float(result[0]) if scalar else result

    # ------------------------------------------------------------------
    # Méthode de Newton (différences divisées)
    # ------------------------------------------------------------------

    def newton_coefficients(self):
        """
        Calcule les coefficients de Newton par la méthode des différences divisées.

        Algorithme du tableau des différences divisées :
            f[x₀]           = y₀
            f[x₀,x₁]        = (f[x₁] − f[x₀]) / (x₁ − x₀)
            f[x₀,x₁,x₂]     = (f[x₁,x₂] − f[x₀,x₁]) / (x₂ − x₀)
            ...

        Les coefficients de Newton sont la diagonale supérieure :
            c₀ = f[x₀]
            c₁ = f[x₀, x₁]
            c₂ = f[x₀, x₁, x₂]
            ...

        Returns
        -------
        ndarray
            Tableau des n coefficients de Newton c₀, c₁, ..., c_{n-1}.

        Notes
        -----
        Calcul en place sur une copie du tableau, complexité O(n²).
        Les coefficients sont mis en cache dans self._dd_coeffs.

        Examples
        --------
        >>> pi = PolynomialInterpolation([0, 1, 2], [1, 3, 7])
        >>> pi.newton_coefficients()
        array([1., 2., 1.])
        """
        n = len(self.x_points)
        # Tableau de différences divisées (copie pour ne pas modifier y_points)
        dd = self.y_points.copy()

        coeffs = np.zeros(n)
        coeffs[0] = dd[0]

        for j in range(1, n):
            for i in range(n - 1, j - 1, -1):
                dd[i] = (dd[i] - dd[i - 1]) / (self.x_points[i] - self.x_points[i - j])
            coeffs[j] = dd[j]

        self._dd_coeffs = coeffs
        return coeffs

    def newton_eval(self, x_eval):
        """
        Évalue le polynôme de Newton par le schéma de Horner.

        Forme de Newton :
            P(x) = c₀ + c₁(x−x₀) + c₂(x−x₀)(x−x₁) + ...
                 = c₀ + (x−x₀)[c₁ + (x−x₁)[c₂ + ...]]

        Le schéma de Horner évalue ce polynôme emboîté en O(n) opérations :
            b_{n-1} = c_{n-1}
            b_k     = c_k + (x − x_k) · b_{k+1}   pour k = n-2, ..., 0
            P(x)    = b₀

        Parameters
        ----------
        x_eval : float or array-like
            Point(s) où évaluer le polynôme.

        Returns
        -------
        float or ndarray
            Valeur(s) du polynôme de Newton en x_eval.

        Notes
        -----
        Calcule les coefficients si non encore calculés.
        Complexité : O(n) par point après initialisation O(n²).

        Examples
        --------
        >>> pi = PolynomialInterpolation([0, 1, 2], [1, 3, 7])
        >>> pi.newton_eval(1.5)
        4.75
        """
        if self._dd_coeffs is None:
            self.newton_coefficients()

        x_eval = np.asarray(x_eval, dtype=float)
        scalar = x_eval.ndim == 0
        x_eval = np.atleast_1d(x_eval)

        n = len(self.x_points)
        coeffs = self._dd_coeffs

        # Schéma de Horner vectorisé
        result = np.full_like(x_eval, coeffs[n - 1])
        for k in range(n - 2, -1, -1):
            result = coeffs[k] + (x_eval - self.x_points[k]) * result

        return float(result[0]) if scalar else result

    # ------------------------------------------------------------------
    # Interface unifiée
    # ------------------------------------------------------------------

    def evaluate(self, x_eval, method='newton'):
        """
        Interface unifiée pour l'évaluation du polynôme d'interpolation.

        Parameters
        ----------
        x_eval : float or array-like
            Point(s) d'évaluation.
        method : str, optional
            Méthode à utiliser : 'newton' (par défaut) ou 'lagrange'.

        Returns
        -------
        float or ndarray
            Valeur(s) interpolée(s) en x_eval.

        Raises
        ------
        ValueError
            Si la méthode spécifiée est inconnue.

        Examples
        --------
        >>> pi = PolynomialInterpolation([0, 1, 2], [1, 3, 7])
        >>> pi.evaluate(1.5, method='newton')
        4.75
        >>> pi.evaluate(1.5, method='lagrange')
        4.75
        """
        if method == 'newton':
            return self.newton_eval(x_eval)
        elif method == 'lagrange':
            return self.lagrange(x_eval)
        else:
            raise ValueError(
                f"Méthode '{method}' inconnue. Choisir parmi : 'newton', 'lagrange'."
            )

    # ------------------------------------------------------------------
    # Utilitaire : phénomène de Runge
    # ------------------------------------------------------------------

    @staticmethod
    def runge_function(x):
        """
        Fonction de Runge : f(x) = 1 / (1 + 25x²).

        Utilisée pour illustrer le phénomène de Runge : oscillations
        importantes aux extrémités lors d'une interpolation sur points
        équidistants avec un polynôme de haut degré.

        Parameters
        ----------
        x : float or array-like
            Points d'évaluation sur [-1, 1].

        Returns
        -------
        float or ndarray
            Valeur(s) de f(x).
        """
        x = np.asarray(x, dtype=float)
        return 1.0 / (1.0 + 25.0 * x**2)

    @staticmethod
    def chebyshev_nodes(n, a=-1.0, b=1.0):
        """
        Calcule les n nœuds de Tchebychev sur [a, b].

        Formule :
            xₖ = (a+b)/2 + (b−a)/2 · cos((2k+1)π / (2n))   k = 0, ..., n-1

        Les nœuds de Tchebychev sont plus denses aux extrémités de l'intervalle,
        ce qui minimise le phénomène de Runge.

        Parameters
        ----------
        n : int
            Nombre de nœuds.
        a : float, optional
            Borne inférieure (par défaut -1).
        b : float, optional
            Borne supérieure (par défaut 1).

        Returns
        -------
        ndarray
            Tableau des n nœuds de Tchebychev triés par ordre croissant.
        """
        k = np.arange(n)
        nodes = 0.5 * (a + b) + 0.5 * (b - a) * np.cos((2 * k + 1) * np.pi / (2 * n))
        return np.sort(nodes)