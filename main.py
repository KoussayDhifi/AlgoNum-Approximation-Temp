#!/usr/bin/env python3
"""
Script principal : AlgoNum - Approximation et Analyse Numérique

Ce script exécute les trois applications principales du projet :
1. Analyse d'interpolation (spline linéaire vs cubique)
2. Problème de refroidissement (Section 4.2)
3. Problème d'écoulement (bonus)

Génère les figures dans le dossier outputs/figures/
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Configuration des chemins
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, 'src'))

from interpolation.linear_spline import LinearSpline
from interpolation.cubic_spline import CubicSpline
from visualization.visualizer import Visualizer
from applications.cooling import CoolingProblem
from applications.flow import FlowProblem
from integration.newton_cotes import NewtonCotes
from integration.adaptive import AdaptiveIntegration


def load_data(filename):
    """Charge un fichier CSV."""
    data = np.loadtxt(filename, delimiter=',', skiprows=1)
    return data[:, 0], data[:, 1]


def section_interpolation():
    """
    Section 3.2 : Démonstration des classes LinearSpline et CubicSpline.
    """
    print("\n" + "="*70)
    print("SECTION 3.2 : INTERPOLATION PAR SPLINES")
    print("="*70)

    # Données de test
    x_data = np.array([0, 1, 2, 3, 4, 5])
    y_data = np.array([0, 1, 1.5, 2.8, 3.2, 3.0])

    # Crée les interpolateurs
    lin_spline = LinearSpline(x_data, y_data)
    cub_spline = CubicSpline(x_data, y_data, boundary='natural')

    # Points fins pour évaluation
    x_fine = np.linspace(x_data[0], x_data[-1], 300)
    y_lin = lin_spline.evaluate(x_fine)
    y_cub = cub_spline.evaluate(x_fine)

    # Visualisation
    viz = Visualizer(figsize=(12, 6))
    fig = viz.plot_interpolation_comparison(
        x_data, y_data,
        {
            'Linear Spline': lin_spline,
            'Cubic Spline': cub_spline
        },
        x_fine,
        'Comparaison : Spline Linéaire vs Cubique'
    )
    output_path = os.path.join(_HERE, 'outputs', 'figures', 'interpolation_comparison.png')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Figure sauvegardée : {output_path}")

    # Affiche des valeurs
    print("\nÉvaluations de la spline cubique :")
    for x_val in [0.5, 1.5, 2.5, 3.5, 4.5]:
        y_val = cub_spline.evaluate(x_val)
        dy_val = cub_spline.derivative(x_val, order=1)
        d2y_val = cub_spline.derivative(x_val, order=2)
        print(f"  x = {x_val:4.1f} : y = {y_val:7.4f}, y' = {dy_val:7.4f}, y'' = {d2y_val:7.4f}")

    plt.close('all')


def section_cooling():
    """
    Section 4.2 : Problème inverse du refroidissement.
    Détermine k optimal et affiche les résultats.
    """
    print("\n" + "="*70)
    print("SECTION 4.2 : PROBLÈME DE REFROIDISSEMENT")
    print("="*70)

    # Données expérimentales
    t_data = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=float)
    T_data = np.array([90, 85, 72, 63, 58, 52, 48, 45, 43, 41, 40], dtype=float)

    # Crée le problème
    cooling = CoolingProblem(t_data, T_data, T_ambient=20.0, h_coeff=50.0)

    print("\n1. Température interpolée :")
    for t_test in [2.5, 5.0, 7.5]:
        T_interp = cooling.temperature(t_test)
        print(f"   T({t_test:4.1f} s) = {T_interp:6.2f} °C")

    print("\n2. Perte de chaleur totale :")
    Q_adaptive = cooling.total_heat_loss(method='adaptive', n=100)
    Q_simpson = cooling.total_heat_loss(method='simpson', n=100)
    Q_trapez = cooling.total_heat_loss(method='trapezoid', n=100)
    print(f"   (Adaptative) Q = {Q_adaptive:10.2f} J")
    print(f"   (Simpson)    Q = {Q_simpson:10.2f} J")
    print(f"   (Trapézoid)  Q = {Q_trapez:10.2f} J")

    print("\n3. Recherche du coefficient optimal k* :")
    print("   Minimisation de E(k) = ∫ |T_exp(t) - T_modèle(t, k)| dt")
    print("   sur [0.01, 0.5] ...")

    k_opt = cooling.estimate_k(k_min=0.01, k_max=0.5, tol=1e-5)
    E_opt = cooling.model_error(k_opt)
    print(f"   k* = {k_opt:.6f} s⁻¹")
    print(f"   E(k*) = {E_opt:.6e}")

    # Calcule E(k) pour la visualisation
    k_values = np.linspace(0.01, 0.5, 100)
    E_values = np.array([cooling.model_error(k) for k in k_values])

    viz = Visualizer(figsize=(12, 5))

    # Figure 1 : Fonction d'erreur E(k)
    fig1 = viz.plot_error_function(k_values, E_values, k_opt, E_opt)
    error_func_path = os.path.join(_HERE, 'outputs', 'figures', 'cooling_error_function.png')
    os.makedirs(os.path.dirname(error_func_path), exist_ok=True)
    fig1.savefig(error_func_path, dpi=150, bbox_inches='tight')
    print(f"\n   ✓ Figure sauvegardée : {error_func_path}")

    # Figure 2 : Comparaison spline vs modèle optimal
    t_fine = np.linspace(t_data[0], t_data[-1], 200)
    T_interp = cooling.temperature(t_fine)
    T_model = cooling.exponential_model(t_fine, k_opt)

    fig2 = viz.plot_cooling_analysis(t_data, T_data, t_fine, T_interp, k_opt, T_model)
    cooling_analysis_path = os.path.join(_HERE, 'outputs', 'figures', 'cooling_analysis.png')
    fig2.savefig(cooling_analysis_path, dpi=150, bbox_inches='tight')
    print(f"   ✓ Figure sauvegardée : {cooling_analysis_path}")

    # Erreurs de précision du modèle
    print("\n4. Erreurs du modèle avec k* optimal :")
    errors = np.abs(T_interp - T_model)
    error_max = np.max(errors)
    error_mean = np.mean(errors)
    print(f"   Erreur maximale   : {error_max:.4f} °C")
    print(f"   Erreur moyenne    : {error_mean:.4f} °C")

    plt.close('all')

    return k_opt, E_opt


def section_flow():
    """
    Section 4.3 (Bonus) : Problème d'écoulement.
    """
    print("\n" + "="*70)
    print("SECTION 4.3 : PROBLÈME D'ÉCOULEMENT (BONUS)")
    print("="*70)

    # Données expérimentales
    x_data = np.array([0, 0.5, 1.2, 1.8, 2.5, 3.1, 3.7, 4.2, 4.8, 5.3, 6.0], dtype=float)
    v_data = np.array([0, 2.1, 3.8, 5.2, 6.4, 7.0, 7.3, 7.2, 6.8, 5.9, 4.5], dtype=float)

    # Crée le problème avec la largeur w(x) = 0.5 + 0.1*x
    flow = FlowProblem(x_data, v_data)

    print("\n1. Vitesse interpolée :")
    for x_test in [1.5, 3.0, 4.5]:
        v_interp = flow.velocity(x_test)
        print(f"   v({x_test:4.1f} m) = {v_interp:6.2f} m/s")

    print("\n2. Débit volumique :")
    D_adaptive = flow.total_flow_rate(method='adaptive', n=100)
    D_simpson = flow.total_flow_rate(method='simpson', n=100)
    print(f"   (Adaptative) D = {D_adaptive:10.4f} m³/s")
    print(f"   (Simpson)    D = {D_simpson:10.4f} m³/s")

    # Visualisation
    x_fine = np.linspace(x_data[0], x_data[-1], 200)
    v_interp = flow.velocity(x_fine)

    viz = Visualizer(figsize=(12, 6))
    fig = viz.plot_flow_analysis(x_data, v_data, x_fine, v_interp, flow.width_func)
    output_path = os.path.join(_HERE, 'outputs', 'figures', 'flow_analysis.png')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n   ✓ Figure sauvegardée : {output_path}")

    plt.close('all')


def section_numerical_integration():
    """
    Section 2.3 : Démonstration des méthodes d'intégration numérique.
    """
    print("\n" + "="*70)
    print("SECTION 2.3 : INTÉGRATION NUMÉRIQUE")
    print("="*70)

    # Fonction de test : e^(-x²) sur [0, 1]
    def f(x):
        return np.exp(-x**2)

    # Valeur approchée de l'intégrale (obtenue avec haute précision)
    exact = 0.7468241328670857

    print("\n1. Intégration de f(x) = exp(-x²) sur [0, 1] :")
    print(f"   Valeur de référence : {exact:.10f}")

    n_values = [2, 4, 8, 16, 32, 64, 128]
    methods = {
        'Rectangle': NewtonCotes.rectangle,
        'Trapézoïdal': NewtonCotes.trapezoidal,
        'Simpson': NewtonCotes.simpson,
    }

    results = {}
    print("\n2. Convergence des méthodes :")
    for method_name, method_func in methods.items():
        print(f"\n   {method_name} :")
        errors = []
        approx_values = []
        for n in n_values:
            if method_name == 'Simpson' and n % 2 == 1:
                n += 1
            approx = method_func(f, 0, 1, n)
            error = abs(approx - exact)
            errors.append(error)
            approx_values.append(approx)
            print(f"      n={n:3d} : I ≈ {approx:.10f}, erreur = {error:.2e}")
        results[method_name] = np.array(errors)

    # Intégration adaptative
    print(f"\n   Adaptative :")
    ai = AdaptiveIntegration(tol=1e-8)
    approx_adapt = ai.adaptive_simpson(f, 0, 1)
    error_adapt = abs(approx_adapt - exact)
    print(f"      I ≈ {approx_adapt:.10f}, erreur = {error_adapt:.2e}")

    # Visualisation
    viz = Visualizer(figsize=(10, 6))
    fig = viz.plot_convergence(
        np.array(n_values),
        results,
        list(methods.keys()),
        title='Convergence des méthodes d\'intégration'
    )
    output_path = os.path.join(_HERE, 'outputs', 'figures', 'integration_convergence.png')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n   ✓ Figure sauvegardée : {output_path}")

    plt.close('all')


def main():
    """Fonction principale."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "AlgoNum - Analyse Numérique : Interpolation et Intégration".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")

    try:
        # Exécute les sections
        section_interpolation()
        section_numerical_integration()
        section_cooling()
        section_flow()

        print("\n" + "="*70)
        print("✓ TOUS LES CALCULS COMPLÉTÉS AVEC SUCCÈS")
        print("="*70)
        print("\nFigures générées dans : ./outputs/figures/")

    except Exception as e:
        print(f"\n✗ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
