"""
Module : visualizer.py
Implémentation de la classe Visualizer pour la visualisation des résultats.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


class Visualizer:
    """
    Classe de visualisation pour afficher les résultats d'interpolation,
    d'intégration et d'analyse.

    Attributes
    ----------
    style : str
        Style matplotlib à utiliser.
    figsize : tuple
        Taille des figures (largeur, hauteur) en pouces.
    """

    def __init__(self, style='seaborn-v0_8-darkgrid', figsize=(10, 6)):
        """
        Initialise le visualiseur.

        Parameters
        ----------
        style : str, optional
            Style matplotlib (défaut : 'seaborn-v0_8-darkgrid').
        figsize : tuple, optional
            Taille des figures (défaut : (10, 6)).
        """
        try:
            plt.style.use(style)
        except OSError:
            # Fallback si le style n'existe pas
            plt.style.use('default')

        self.style = style
        self.figsize = figsize

    def plot_interpolation_comparison(self, x_data, y_data, interpolators,
                                      x_fine, title, save_path=None):
        """
        Compare plusieurs interpolations sur un même graphique.

        Parameters
        ----------
        x_data : ndarray
            Données d'entraînement (abscisses).
        y_data : ndarray
            Données d'entraînement (ordonnées).
        interpolators : dict
            Dictionnaire {nom: objet_interpolateur} où chaque objet
            a une méthode evaluate(x).
        x_fine : ndarray
            Points fins pour l'évaluation.
        title : str
            Titre du graphique.
        save_path : str, optional
            Chemin pour sauvegarder la figure.

        Returns
        -------
        fig : Figure
            Figure matplotlib créée.
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # Affiche les points de données
        ax.scatter(x_data, y_data, color='red', s=100, label='Données',
                   zorder=5, edgecolors='darkred', linewidth=1.5)

        # Affiche chaque interpolation
        colors = plt.cm.viridis(np.linspace(0, 1, len(interpolators)))
        for (name, interpolator), color in zip(interpolators.items(), colors):
            y_fine = interpolator.evaluate(x_fine)
            ax.plot(x_fine, y_fine, label=name, linewidth=2, color=color)

        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('y', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3)

        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        return fig

    def plot_runge_phenomenon(self, x_fine, y_true, interpolations,
                             title='Phénomène de Runge', save_path=None):
        """
        Affiche le phénomène de Runge : oscillations aux extrémités
        avec interpolation polynomiale uniforme.

        Parameters
        ----------
        x_fine : ndarray
            Points fins pour la vraie fonction.
        y_true : ndarray
            Valeurs vraies.
        interpolations : dict
            Dictionnaire {description: (x_data, y_interp)} pour chaque
            nombre de points.
        title : str, optional
            Titre du graphique.
        save_path : str, optional
            Chemin pour sauvegarder la figure.

        Returns
        -------
        fig : Figure
            Figure matplotlib créée.
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # Fonction vraie
        ax.plot(x_fine, y_true, 'k-', linewidth=2.5, label='Vraie fonction')

        # Interpolations
        colors = plt.cm.rainbow(np.linspace(0, 1, len(interpolations)))
        for (desc, (x_data, y_interp)), color in zip(interpolations.items(), colors):
            ax.plot(x_data, y_interp, 'o-', label=desc, linewidth=1.5,
                   markersize=6, color=color)

        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('y', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=10, loc='best')
        ax.grid(True, alpha=0.3)

        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        return fig

    def plot_convergence(self, n_values, errors, methods, 
                        title='Convergence des méthodes d\'intégration',
                        save_path=None):
        """
        Affiche la convergence (en échelle log-log) de plusieurs méthodes.

        Parameters
        ----------
        n_values : ndarray
            Nombres d'intervalles testés.
        errors : dict
            Dictionnaire {méthode: array_d'erreurs} de même longueur que n_values.
        methods : list, optional
            Liste des noms des méthodes (pour la légende).
        title : str, optional
            Titre du graphique.
        save_path : str, optional
            Chemin pour sauvegarder la figure.

        Returns
        -------
        fig : Figure
            Figure matplotlib créée.
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        colors = plt.cm.tab10(np.linspace(0, 1, len(errors)))
        for (method_name, error_array), color in zip(errors.items(), colors):
            ax.loglog(n_values, np.abs(error_array), 'o-', 
                     label=method_name, linewidth=2, markersize=6, color=color)

        ax.set_xlabel('Nombre d\'intervalles (n)', fontsize=12)
        ax.set_ylabel('Erreur absolue (log scale)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3, which='both')

        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        return fig

    def plot_cooling_analysis(self, t_data, T_data, t_fine, T_interp,
                             k_opt, T_model, save_path=None):
        """
        Affiche l'analyse du problème de refroidissement.

        Affiche sur un même graphique :
        - Les données expérimentales (points)
        - L'interpolation spline (courbe lisse)
        - Le modèle exponentiel optimal (courbe lisse)

        Parameters
        ----------
        t_data : ndarray
            Temps mesurés.
        T_data : ndarray
            Températures mesurées.
        t_fine : ndarray
            Temps fins pour l'interpolation.
        T_interp : ndarray
            Températures interpolées (spline).
        k_opt : float
            Coefficient k optimal du modèle exponentiel.
        T_model : ndarray
            Modèle exponentiel avec k_opt évalué sur t_fine.
        save_path : str, optional
            Chemin pour sauvegarder la figure.

        Returns
        -------
        fig : Figure
            Figure matplotlib créée.
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        ax.scatter(t_data, T_data, color='red', s=120, label='Données expérimentales',
                  zorder=5, edgecolors='darkred', linewidth=1.5)
        ax.plot(t_fine, T_interp, 'b-', linewidth=2.5, label='Spline cubique')
        ax.plot(t_fine, T_model, 'g--', linewidth=2.5, 
               label=f'Modèle exponentiel (k={k_opt:.4f})')

        ax.set_xlabel('Temps (s)', fontsize=12)
        ax.set_ylabel('Température (°C)', fontsize=12)
        ax.set_title('Analyse du refroidissement', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3)

        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        return fig

    def plot_flow_analysis(self, x_data, v_data, x_fine, v_interp,
                          w_function, save_path=None):
        """
        Affiche l'analyse du problème d'écoulement.

        Affiche sur un même graphique :
        - Les données expérimentales (points)
        - L'interpolation spline (courbe lisse)
        - La fonction modèle de vitesse (courbe lisse)

        Parameters
        ----------
        x_data : ndarray
            Positions mesurées.
        v_data : ndarray
            Vitesses mesurées.
        x_fine : ndarray
            Positions fines pour l'interpolation.
        v_interp : ndarray
            Vitesses interpolées (spline).
        w_function : callable or ndarray
            Fonction w(x) ou tableau w(x_fine).
        save_path : str, optional
            Chemin pour sauvegarder la figure.

        Returns
        -------
        fig : Figure
            Figure matplotlib créée.
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        ax.scatter(x_data, v_data, color='red', s=120, label='Données expérimentales',
                  zorder=5, edgecolors='darkred', linewidth=1.5)
        ax.plot(x_fine, v_interp, 'b-', linewidth=2.5, label='Spline cubique')

        # Évalue w(x) si c'est un callable
        if callable(w_function):
            w_vals = w_function(x_fine)
        else:
            w_vals = w_function

        ax.plot(x_fine, w_vals, 'g--', linewidth=2.5, label='Fonction modèle w(x)')

        ax.set_xlabel('Position (m)', fontsize=12)
        ax.set_ylabel('Vitesse (m/s)', fontsize=12)
        ax.set_title('Analyse de l\'écoulement', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3)

        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        return fig

    def plot_error_function(self, k_values, E_values, k_opt, E_opt,
                           title='Fonction d\'erreur E(k)',
                           save_path=None):
        """
        Affiche la fonction d'erreur E(k) et son minimum.

        Parameters
        ----------
        k_values : ndarray
            Valeurs de k.
        E_values : ndarray
            Valeurs de E(k).
        k_opt : float
            Valeur optimale de k.
        E_opt : float
            Valeur minimale de E(k).
        title : str, optional
            Titre du graphique.
        save_path : str, optional
            Chemin pour sauvegarder la figure.

        Returns
        -------
        fig : Figure
            Figure matplotlib créée.
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        ax.plot(k_values, E_values, 'b-', linewidth=2.5, label='E(k)')
        ax.scatter([k_opt], [E_opt], color='red', s=150, zorder=5,
                  label=f'Minimum : k={k_opt:.6f}, E={E_opt:.6e}',
                  edgecolors='darkred', linewidth=2)

        ax.set_xlabel('Coefficient k', fontsize=12)
        ax.set_ylabel('Erreur E(k)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3)

        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        return fig
