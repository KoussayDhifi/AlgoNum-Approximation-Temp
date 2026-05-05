"""
Module : newton_cotes.py
Implémentation des méthodes d'intégration numérique de Newton-Cotes.
Méthodes : rectangle (point médian), trapèzes, Simpson 1/3, Simpson 3/8 (bonus).
"""

import numpy as np


class NewtonCotes:
    """
    Classe regroupant les méthodes d'intégration de Newton-Cotes.
    Toutes les méthodes sont des méthodes statiques : aucune instanciation requise.
    """

    @staticmethod
    def rectangle(f, a, b, n=1):
        """
        Méthode du rectangle (point médian) composée.

        Approxime l'intégrale de f sur [a, b] en utilisant le point médian
        de chaque sous-intervalle comme point d'évaluation.

        Formule composée :
            I ≈ h * Σ f(a + (i + 0.5)*h)   pour i = 0, ..., n-1

        Ordre de convergence : O(h²) (ordre 2 en termes de précision globale).

        Parameters
        ----------
        f : callable
            Fonction à intégrer.
        a : float
            Borne inférieure d'intégration.
        b : float
            Borne supérieure d'intégration.
        n : int, optional
            Nombre de sous-intervalles (par défaut 1).

        Returns
        -------
        float
            Valeur approchée de l'intégrale.

        Raises
        ------
        ValueError
            Si n < 1 ou si a >= b.

        Examples
        --------
        >>> import math
        >>> NewtonCotes.rectangle(math.exp, 0, 1, 100)
        1.7182817...
        """
        if n < 1:
            raise ValueError("Le nombre de sous-intervalles n doit être >= 1.")
        if a >= b:
            raise ValueError("La borne inférieure a doit être strictement < b.")

        h = (b - a) / n
        midpoints = np.array([a + (i + 0.5) * h for i in range(n)])
        return h * np.sum(f(midpoints) if _is_vectorized(f, midpoints) else
                          np.array([f(xi) for xi in midpoints]))

    @staticmethod
    def trapezoidal(f, a, b, n=1):
        """
        Méthode des trapèzes composée.

        Approxime l'intégrale de f sur [a, b] par une interpolation linéaire
        par morceaux entre les points de quadrature.

        Formule composée :
            I ≈ h/2 * [f(a) + 2*Σf(xᵢ) + f(b)]   pour i = 1, ..., n-1

        Ordre de convergence : O(h²).

        Parameters
        ----------
        f : callable
            Fonction à intégrer.
        a : float
            Borne inférieure d'intégration.
        b : float
            Borne supérieure d'intégration.
        n : int, optional
            Nombre de sous-intervalles (par défaut 1).

        Returns
        -------
        float
            Valeur approchée de l'intégrale.

        Raises
        ------
        ValueError
            Si n < 1 ou si a >= b.

        Examples
        --------
        >>> import math
        >>> NewtonCotes.trapezoidal(math.exp, 0, 1, 100)
        1.71828...
        """
        if n < 1:
            raise ValueError("Le nombre de sous-intervalles n doit être >= 1.")
        if a >= b:
            raise ValueError("La borne inférieure a doit être strictement < b.")

        h = (b - a) / n
        x = np.linspace(a, b, n + 1)
        y = _eval_func(f, x)
        return h * (y[0] / 2.0 + np.sum(y[1:-1]) + y[-1] / 2.0)

    @staticmethod
    def simpson(f, a, b, n=2):
        """
        Méthode de Simpson 1/3 composée.

        Utilise une interpolation polynomiale d'ordre 2 (parabole) sur chaque
        paire de sous-intervalles.

        Formule composée (n pair) :
            I ≈ h/3 * [f(x₀) + 4f(x₁) + 2f(x₂) + 4f(x₃) + ... + f(xₙ)]

        Ordre de convergence : O(h⁴).

        Parameters
        ----------
        f : callable
            Fonction à intégrer.
        a : float
            Borne inférieure d'intégration.
        b : float
            Borne supérieure d'intégration.
        n : int, optional
            Nombre de sous-intervalles, DOIT être pair (par défaut 2).

        Returns
        -------
        float
            Valeur approchée de l'intégrale.

        Raises
        ------
        ValueError
            Si n est impair, si n < 2, ou si a >= b.

        Examples
        --------
        >>> import math
        >>> NewtonCotes.simpson(math.exp, 0, 1, 4)
        1.71828...
        """
        if n % 2 != 0:
            raise ValueError(
                f"n doit être pair pour la méthode de Simpson 1/3. Valeur reçue : {n}."
            )
        if n < 2:
            raise ValueError("n doit être >= 2 pour la méthode de Simpson.")
        if a >= b:
            raise ValueError("La borne inférieure a doit être strictement < b.")

        h = (b - a) / n
        x = np.linspace(a, b, n + 1)
        y = _eval_func(f, x)

        result = y[0] + y[-1]
        result += 4.0 * np.sum(y[1:-1:2])   # indices impairs : coefficient 4
        result += 2.0 * np.sum(y[2:-2:2])   # indices pairs intérieurs : coefficient 2
        return (h / 3.0) * result

    @staticmethod
    def simpson_38(f, a, b, n=3):
        """
        Méthode de Simpson 3/8 composée (bonus).

        Utilise une interpolation polynomiale d'ordre 3 (cubique) sur chaque
        groupe de trois sous-intervalles.

        Formule composée (n multiple de 3) :
            I ≈ 3h/8 * [f(x₀) + 3f(x₁) + 3f(x₂) + 2f(x₃) + ... + f(xₙ)]

        Ordre de convergence : O(h⁴).

        Parameters
        ----------
        f : callable
            Fonction à intégrer.
        a : float
            Borne inférieure d'intégration.
        b : float
            Borne supérieure d'intégration.
        n : int, optional
            Nombre de sous-intervalles, DOIT être multiple de 3 (par défaut 3).

        Returns
        -------
        float
            Valeur approchée de l'intégrale.

        Raises
        ------
        ValueError
            Si n n'est pas multiple de 3, si n < 3, ou si a >= b.
        """
        if n % 3 != 0:
            raise ValueError(
                f"n doit être un multiple de 3 pour Simpson 3/8. Valeur reçue : {n}."
            )
        if n < 3:
            raise ValueError("n doit être >= 3 pour Simpson 3/8.")
        if a >= b:
            raise ValueError("La borne inférieure a doit être strictement < b.")

        h = (b - a) / n
        x = np.linspace(a, b, n + 1)
        y = _eval_func(f, x)

        result = y[0] + y[-1]
        for i in range(1, n):
            if i % 3 == 0:
                result += 2.0 * y[i]   # noeuds de jonction : coefficient 2
            else:
                result += 3.0 * y[i]   # noeuds intermédiaires : coefficient 3
        return (3.0 * h / 8.0) * result


# ---------------------------------------------------------------------------
# Fonctions utilitaires internes
# ---------------------------------------------------------------------------

def _is_vectorized(f, x_array):
    """Vérifie si la fonction f accepte un tableau NumPy en entrée."""
    try:
        result = f(x_array)
        return isinstance(result, np.ndarray) and result.shape == x_array.shape
    except Exception:
        return False


def _eval_func(f, x_array):
    """Évalue f sur un tableau, que f soit vectorisée ou non."""
    try:
        result = f(x_array)
        if isinstance(result, np.ndarray) and result.shape == x_array.shape:
            return result
    except Exception:
        pass
    return np.array([f(xi) for xi in x_array], dtype=float)