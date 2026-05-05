"""
Module : adaptive.py
Implémentation de l'intégration adaptative par la méthode de Simpson adaptative.
"""

import numpy as np


class AdaptiveIntegration:
    """
    Intégration numérique adaptative basée sur la règle de Simpson.

    L'algorithme raffine récursivement les intervalles dont l'erreur estimée
    dépasse la tolérance, concentrant ainsi les points d'évaluation là où
    la fonction varie rapidement.

    Attributes
    ----------
    tol : float
        Tolérance d'erreur globale par défaut.
    max_depth : int
        Profondeur de récursion maximale pour éviter les boucles infinies.
    eval_count : int
        Compteur d'évaluations de la fonction (mis à jour à chaque appel).
    """

    def __init__(self, tol=1e-6, max_depth=20):
        """
        Initialise l'intégrateur adaptatif.

        Parameters
        ----------
        tol : float, optional
            Tolérance d'erreur globale (par défaut 1e-6).
        max_depth : int, optional
            Profondeur maximale de récursion (par défaut 20).
        """
        if tol <= 0:
            raise ValueError("La tolérance tol doit être strictement positive.")
        if max_depth < 1:
            raise ValueError("max_depth doit être >= 1.")

        self.tol = tol
        self.max_depth = max_depth
        self.eval_count = 0

    def _simpson_rule(self, f, a, b):
        """
        Applique la règle de Simpson simple sur l'intervalle [a, b].

        Formule : I ≈ (b-a)/6 * [f(a) + 4*f((a+b)/2) + f(b)]

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
            Approximation de l'intégrale sur [a, b].
        """
        c = (a + b) / 2.0
        fa, fc, fb = f(a), f(c), f(b)
        self.eval_count += 3
        return (b - a) / 6.0 * (fa + 4.0 * fc + fb)

    def adaptive_simpson(self, f, a, b, tol=None, depth=0):
        """
        Intégration de Simpson adaptative récursive.

        Algorithme :
        1. Calcule Simpson sur [a, b] → S_entier
        2. Divise en deux sous-intervalles [a, c] et [c, b]
        3. Calcule Simpson sur chaque demi-intervalle → S_gauche + S_droite
        4. Estime l'erreur : |S_gauche + S_droite - S_entier|
        5. Si erreur ≤ 15*tol → accepte avec correction de Richardson
        6. Sinon → raffine récursivement chaque moitié

        La correction de Richardson améliore l'ordre de convergence à O(h⁶).

        Parameters
        ----------
        f : callable
            Fonction à intégrer.
        a : float
            Borne inférieure d'intégration.
        b : float
            Borne supérieure d'intégration.
        tol : float, optional
            Tolérance locale (par défaut : self.tol).
        depth : int, optional
            Profondeur de récursion courante (par défaut 0).

        Returns
        -------
        float
            Valeur approchée de l'intégrale avec la précision demandée.

        Notes
        -----
        Le facteur 15 dans le critère d'arrêt provient de l'extrapolation
        de Richardson : l'erreur réelle est ≈ (S_g + S_d - S) / 15.
        """
        if tol is None:
            tol = self.tol

        c = (a + b) / 2.0

        # Simpson simple sur l'intervalle entier
        fa, fc, fb = f(a), f(c), f(b)
        self.eval_count += 3
        S_whole = (b - a) / 6.0 * (fa + 4.0 * fc + fb)

        # Simpson sur les deux moitiés
        lc = (a + c) / 2.0
        rc = (c + b) / 2.0
        flc, frc = f(lc), f(rc)
        self.eval_count += 2
        S_left  = (c - a) / 6.0 * (fa + 4.0 * flc + fc)
        S_right = (b - c) / 6.0 * (fc + 4.0 * frc + fb)

        error = abs(S_left + S_right - S_whole)

        # Critère d'arrêt : convergence ou profondeur maximale atteinte
        if depth >= self.max_depth or error <= 15.0 * tol:
            # Correction de Richardson d'ordre 4→6
            return S_left + S_right + (S_left + S_right - S_whole) / 15.0

        # Raffinement récursif sur chaque moitié
        half_tol = tol / 2.0
        left_result  = self._recursive(f, a, c, fa, flc, fc, half_tol, depth + 1)
        right_result = self._recursive(f, c, b, fc, frc, fb, half_tol, depth + 1)
        return left_result + right_result

    def _recursive(self, f, a, b, fa, fm, fb, tol, depth):
        """
        Version interne de l'intégration adaptative réutilisant les évaluations
        déjà calculées pour éviter les appels redondants à f.

        Parameters
        ----------
        f : callable
            Fonction à intégrer.
        a, b : float
            Bornes de l'intervalle courant.
        fa, fm, fb : float
            Valeurs de f aux points a, (a+b)/2, b (déjà calculées).
        tol : float
            Tolérance locale.
        depth : int
            Profondeur de récursion courante.

        Returns
        -------
        float
            Approximation raffinée de l'intégrale sur [a, b].
        """
        c = (a + b) / 2.0
        S_whole = (b - a) / 6.0 * (fa + 4.0 * fm + fb)

        lc = (a + c) / 2.0
        rc = (c + b) / 2.0
        flc = f(lc)
        frc = f(rc)
        self.eval_count += 2

        S_left  = (c - a) / 6.0 * (fa + 4.0 * flc + fm)
        S_right = (b - c) / 6.0 * (fm + 4.0 * frc + fb)

        error = abs(S_left + S_right - S_whole)

        if depth >= self.max_depth or error <= 15.0 * tol:
            return S_left + S_right + (S_left + S_right - S_whole) / 15.0

        half_tol = tol / 2.0
        return (self._recursive(f, a, c, fa, flc, fm, half_tol, depth + 1) +
                self._recursive(f, c, b, fm, frc, fb, half_tol, depth + 1))

    def reset_counter(self):
        """Remet le compteur d'évaluations à zéro."""
        self.eval_count = 0

    def integrate(self, f, a, b, tol=None):
        """
        Interface simplifiée : intègre f sur [a, b] et retourne (résultat, nb_évaluations).

        Parameters
        ----------
        f : callable
            Fonction à intégrer.
        a : float
            Borne inférieure.
        b : float
            Borne supérieure.
        tol : float, optional
            Tolérance (par défaut self.tol).

        Returns
        -------
        tuple (float, int)
            (valeur de l'intégrale, nombre d'évaluations de f).
        """
        self.reset_counter()
        result = self.adaptive_simpson(f, a, b, tol=tol)
        return result, self.eval_count