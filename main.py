"""
Programme principal : main.py
Analyse numérique complète :
  1. Chargement des données expérimentales
  2. Phénomène de Runge
  3. Problème de refroidissement (CoolingProblem)
  4. Problème d'écoulement (FlowProblem)
  5. Convergence des méthodes d'intégration
  6. Affichage des résultats et sauvegarde des graphiques

Exécution : python main.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os
import sys
import csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# ── Résolution des imports relatifs ────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC  = os.path.join(_HERE, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
from applications.cooling import CoolingProblem
from applications.flow    import FlowProblem
from interpolation.polynomial  import PolynomialInterpolation
from interpolation.cubic_spline import CubicSpline
from interpolation.linear_spline import LinearSpline
from integration.newton_cotes   import NewtonCotes
from integration.adaptive        import AdaptiveIntegration

# ── Dossier de sortie pour les graphiques ──────────────────────────────────────
OUTPUT_DIR = os.path.join(_HERE, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# 1. CHARGEMENT DES DONNÉES EXPÉRIMENTALES
# ══════════════════════════════════════════════════════════════════════════════

def load_csv(filepath):
    """Charge un CSV à deux colonnes et retourne deux listes de floats."""
    xs, ys = [], []
    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            keys = list(row.keys())
            xs.append(float(row[keys[0]]))
            ys.append(float(row[keys[1]]))
    return np.array(xs), np.array(ys)


def load_data():
    """Charge les données de refroidissement et d'écoulement."""
    data_dir = os.path.join(_HERE, "data")

    cooling_path = os.path.join(data_dir, "cooling_data.csv")
    flow_path    = os.path.join(data_dir, "flow_data.csv")

    # Données de secours (valeurs du sujet) si les CSV sont absents
    t_data = np.array([0,1,2,3,4,5,6,7,8,9,10], dtype=float)
    T_data = np.array([90,85,72,63,58,52,48,45,43,41,40], dtype=float)
    x_data = np.array([0,0.5,1.2,1.8,2.5,3.1,3.7,4.2,4.8,5.3,6.0], dtype=float)
    v_data = np.array([0,2.1,3.8,5.2,6.4,7.0,7.3,7.2,6.8,5.9,4.5], dtype=float)

    if os.path.exists(cooling_path):
        t_data, T_data = load_csv(cooling_path)
    if os.path.exists(flow_path):
        x_data, v_data = load_csv(flow_path)

    return t_data, T_data, x_data, v_data


# ══════════════════════════════════════════════════════════════════════════════
# 2. PHÉNOMÈNE DE RUNGE
# ══════════════════════════════════════════════════════════════════════════════

def analyse_runge():
    """
    Illustre le phénomène de Runge sur f(x) = 1/(1+25x²).
    Compare interpolation sur nœuds équidistants vs nœuds de Tchebychev
    pour n = 5, 10, 15, 20.
    Sauvegarde : runge_comparison.png
    """
    print("\n" + "="*60)
    print("  2. PHÉNOMÈNE DE RUNGE")
    print("="*60)

    x_fine = np.linspace(-1, 1, 500)
    y_true = PolynomialInterpolation.runge_function(x_fine)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Phénomène de Runge : f(x) = 1/(1+25x²)\n"
                 "Nœuds équidistants vs Tchebychev", fontsize=14, fontweight='bold')

    ns = [5, 10, 15, 20]
    errors = {'equidistant': [], 'chebyshev': []}

    for idx, n in enumerate(ns):
        ax = axes[idx // 2][idx % 2]

        # ── Nœuds équidistants ──────────────────────────────────────────
        x_eq = np.linspace(-1, 1, n)
        y_eq = PolynomialInterpolation.runge_function(x_eq)
        pi_eq = PolynomialInterpolation(x_eq, y_eq)
        y_interp_eq = pi_eq.evaluate(x_fine, method='newton')

        # ── Nœuds de Tchebychev ────────────────────────────────────────
        x_ch = PolynomialInterpolation.chebyshev_nodes(n)
        y_ch = PolynomialInterpolation.runge_function(x_ch)
        pi_ch = PolynomialInterpolation(x_ch, y_ch)
        y_interp_ch = pi_ch.evaluate(x_fine, method='newton')

        # ── Erreurs max ────────────────────────────────────────────────
        err_eq = np.max(np.abs(y_interp_eq - y_true))
        err_ch = np.max(np.abs(y_interp_ch - y_true))
        errors['equidistant'].append(err_eq)
        errors['chebyshev'].append(err_ch)

        print(f"  n={n:2d} | Err équidistant = {err_eq:.4f} | Err Tchebychev = {err_ch:.6f}")

        # ── Tracé ──────────────────────────────────────────────────────
        ax.plot(x_fine, y_true,        'k-',  lw=2,   label='f(x) exacte')
        ax.plot(x_fine, y_interp_eq,   'r--', lw=1.5, label=f'Équidistant (err={err_eq:.3f})')
        ax.plot(x_fine, y_interp_ch,   'b-',  lw=1.5, label=f'Tchebychev  (err={err_ch:.4f})')
        ax.scatter(x_eq, y_eq, color='red',  s=30, zorder=5)
        ax.scatter(x_ch, y_ch, color='blue', s=30, zorder=5)
        ax.set_ylim(-0.5, 1.5)
        ax.set_title(f'n = {n} points', fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('x')
        ax.set_ylabel('f(x)')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "runge_comparison.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n  → Graphique sauvegardé : {path}")
    return errors


# ══════════════════════════════════════════════════════════════════════════════
# 3. ANALYSE DU PROBLÈME DE REFROIDISSEMENT
# ══════════════════════════════════════════════════════════════════════════════

def analyse_cooling(t_data, T_data):
    """
    Analyse complète du refroidissement :
      - Comparaison des méthodes d'interpolation
      - Calcul de Q par 4 méthodes
      - Estimation de k*
    Sauvegarde : cooling_interpolations.png, cooling_heat_loss.png
    """
    print("\n" + "="*60)
    print("  3. PROBLÈME DE REFROIDISSEMENT")
    print("="*60)

    cp = CoolingProblem(t_data, T_data)
    t_fine = np.linspace(t_data[0], t_data[-1], 500)

    # ── Interpolations ──────────────────────────────────────────────────────
    # 1) Spline cubique (via CoolingProblem)
    T_cubic = np.array([cp.temperature(ti) for ti in t_fine])

    # 2) Spline linéaire
    ls = LinearSpline(t_data, T_data)
    T_linear = np.array([ls.evaluate(ti) for ti in t_fine])

    # 3) Polynôme de Newton
    pi = PolynomialInterpolation(t_data, T_data)
    T_newton = pi.evaluate(t_fine, method='newton')

    # 4) Polynôme de Lagrange
    T_lagrange = pi.evaluate(t_fine, method='lagrange')

    # ── Températures aux instants demandés ────────────────────────────────
    print("\n  Températures interpolées :")
    print(f"  {'Méthode':<18} {'T(2.5 s)':>12} {'T(7.3 s)':>12}")
    print(f"  {'-'*44}")
    for label, interp_obj, method in [
        ("Spline cubique",   cp,   None),
        ("Spline linéaire",  ls,   None),
        ("Newton",           pi,   'newton'),
        ("Lagrange",         pi,   'lagrange'),
    ]:
        if method is None and label == "Spline cubique":
            v1 = cp.temperature(2.5)
            v2 = cp.temperature(7.3)
        elif method is None:
            v1 = ls.evaluate(2.5)
            v2 = ls.evaluate(7.3)
        else:
            v1 = pi.evaluate(2.5, method=method)
            v2 = pi.evaluate(7.3, method=method)
        print(f"  {label:<18} {v1:>12.4f} °C {v2:>10.4f} °C")

    # ── Perte de chaleur totale ────────────────────────────────────────────
    print("\n  Perte de chaleur totale Q :")
    methods_int = ['rectangle', 'trapezoid', 'simpson', 'adaptive']
    Q_values = {}
    for m in methods_int:
        Q = cp.total_heat_loss(method=m, n=100)
        Q_values[m] = Q
        print(f"    [{m:>10}]  Q = {Q:.4f} J")

    # ── Estimation de k* ──────────────────────────────────────────────────
    print("\n  Estimation de k* (section dorée) :")
    k_opt = cp.estimate_k()
    E_opt = cp.model_error(k_opt)
    print(f"    k* = {k_opt:.6f} s⁻¹")
    print(f"    E(k*) = {E_opt:.6f}")

    T_model = cp.exponential_model(t_fine, k_opt)

    # ── Graphique 1 : comparaison des interpolations ──────────────────────
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(t_data, T_data, s=60, color='black', zorder=5, label='Données expérimentales')
    ax.plot(t_fine, T_cubic,   'b-',  lw=2,   label='Spline cubique')
    ax.plot(t_fine, T_linear,  'g--', lw=1.5, label='Spline linéaire')
    ax.plot(t_fine, T_newton,  'r-',  lw=1.5, label='Newton (degré 10)')
    ax.plot(t_fine, T_model,   'm:',  lw=2,   label=f'Modèle exp. k*={k_opt:.4f}')
    ax.set_xlabel('Temps t (s)', fontsize=12)
    ax.set_ylabel('Température T (°C)', fontsize=12)
    ax.set_title('Refroidissement — Comparaison des méthodes d\'interpolation', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    path1 = os.path.join(OUTPUT_DIR, "cooling_interpolations.png")
    plt.savefig(path1, dpi=150, bbox_inches='tight')
    plt.close()

    # ── Graphique 2 : perte de chaleur par méthode ────────────────────────
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ['#E74C3C', '#3498DB', '#2ECC71', '#9B59B6']
    bars = ax.bar(list(Q_values.keys()), list(Q_values.values()), color=colors, width=0.5)
    ax.bar_label(bars, fmt='%.2f J', padding=3, fontsize=10)
    ax.set_ylabel('Perte de chaleur Q (J)', fontsize=12)
    ax.set_title('Perte de chaleur totale selon la méthode d\'intégration', fontsize=12, fontweight='bold')
    ax.set_ylim(0, max(Q_values.values()) * 1.15)
    ax.grid(True, axis='y', alpha=0.3)
    path2 = os.path.join(OUTPUT_DIR, "cooling_heat_loss.png")
    plt.savefig(path2, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"\n  → Graphiques sauvegardés : {path1}\n                              {path2}")
    return cp, k_opt


# ══════════════════════════════════════════════════════════════════════════════
# 4. ANALYSE DU PROBLÈME D'ÉCOULEMENT
# ══════════════════════════════════════════════════════════════════════════════

def analyse_flow(x_data, v_data):
    """
    Analyse complète de l'écoulement :
      - Débit total par 4 méthodes
      - Accélération dv/dx
      - Travail numérique vs analytique
    Sauvegarde : flow_analysis.png
    """
    print("\n" + "="*60)
    print("  4. PROBLÈME D'ÉCOULEMENT")
    print("="*60)

    fp = FlowProblem(x_data, v_data)
    x_fine = np.linspace(x_data[0], x_data[-1], 500)

    # Débit total
    print("\n  Débit volumique total D :")
    D_values = {}
    for m in ['rectangle', 'trapezoid', 'simpson', 'adaptive']:
        D = fp.total_flow_rate(method=m, n=100)
        D_values[m] = D
        print(f"    [{m:>10}]  D = {D:.6f} m³/s")

    # Travail
    W_num, W_ana = fp.work(mass=2.0)
    err_rel = abs(W_num - W_ana) / abs(W_ana) * 100
    print(f"\n  Travail (numérique)  : W = {W_num:.6f} J")
    print(f"  Travail (analytique) : W = {W_ana:.6f} J")
    print(f"  Erreur relative      : {err_rel:.4f} %")

    # Vitesse, débit local, accélération
    v_interp = np.array([fp.velocity(xi) for xi in x_fine])
    q_interp = np.array([fp.local_flow_rate(xi) for xi in x_fine])
    a_interp = np.array([fp.acceleration(xi) for xi in x_fine])
    w_interp = np.array([0.5 + 0.1 * xi for xi in x_fine])

    # ── Graphique ──────────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle("Problème d'écoulement — Analyse complète", fontsize=14, fontweight='bold')

    # v(x)
    ax = axes[0][0]
    ax.scatter(x_data, v_data, s=50, color='black', zorder=5, label='Mesures')
    ax.plot(x_fine, v_interp, 'b-', lw=2, label='Spline cubique v(x)')
    ax.set_xlabel('x (m)'); ax.set_ylabel('v (m/s)')
    ax.set_title('Vitesse interpolée v(x)'); ax.legend(); ax.grid(True, alpha=0.3)

    # w(x)
    ax = axes[0][1]
    ax.plot(x_fine, w_interp, 'g-', lw=2)
    ax.set_xlabel('x (m)'); ax.set_ylabel('w (m)')
    ax.set_title('Largeur w(x) = 0.5 + 0.1x'); ax.grid(True, alpha=0.3)

    # q(x) = v·w
    ax = axes[1][0]
    ax.plot(x_fine, q_interp, 'r-', lw=2)
    ax.fill_between(x_fine, q_interp, alpha=0.2, color='red')
    ax.set_xlabel('x (m)'); ax.set_ylabel('q (m²/s)')
    ax.set_title(f'Débit local q(x) = v·w   →   D = {D_values["adaptive"]:.4f} m³/s')
    ax.grid(True, alpha=0.3)

    # dv/dx
    ax = axes[1][1]
    ax.plot(x_fine, a_interp, 'm-', lw=2)
    ax.axhline(0, color='black', lw=0.8, linestyle='--')
    ax.set_xlabel('x (m)'); ax.set_ylabel('dv/dx (s⁻¹)')
    ax.set_title('Gradient de vitesse dv/dx'); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "flow_analysis.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n  → Graphique sauvegardé : {path}")
    return fp


# ══════════════════════════════════════════════════════════════════════════════
# 5. CONVERGENCE DES MÉTHODES D'INTÉGRATION
# ══════════════════════════════════════════════════════════════════════════════

def analyse_convergence():
    """
    Étudie la convergence des méthodes Newton-Cotes sur ∫₀¹ exp(x) dx = e-1.
    Sauvegarde : convergence.png
    """
    print("\n" + "="*60)
    print("  5. CONVERGENCE DES MÉTHODES D'INTÉGRATION")
    print("="*60)

    f       = np.exp
    a, b    = 0.0, 1.0
    exact   = np.e - 1.0
    ns      = [2, 4, 8, 16, 32, 64, 128, 256, 512]

    errors = {'rectangle': [], 'trapezoid': [], 'simpson': []}

    for n in ns:
        n_even = n if n % 2 == 0 else n + 1
        errors['rectangle'].append(abs(NewtonCotes.rectangle(f, a, b, n)  - exact))
        errors['trapezoid'].append(abs(NewtonCotes.trapezoidal(f, a, b, n) - exact))
        errors['simpson'].append(abs(NewtonCotes.simpson(f, a, b, n_even)  - exact))

    hs = [(b - a) / n for n in ns]

    # Lignes de référence O(h²) et O(h⁴)
    h_ref   = np.array(hs)
    ref_h2  = 1e-2 * h_ref**2
    ref_h4  = 5e-5 * h_ref**4

    print(f"\n  {'n':>5}  {'Rect':>12}  {'Trap':>12}  {'Simpson':>12}")
    print(f"  {'-'*50}")
    for i, n in enumerate(ns):
        print(f"  {n:>5}  {errors['rectangle'][i]:>12.2e}  "
              f"{errors['trapezoid'][i]:>12.2e}  {errors['simpson'][i]:>12.2e}")

    # ── Graphique ──────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.loglog(hs, errors['rectangle'], 'r-o', lw=2, ms=6, label='Rectangle (O(h²))')
    ax.loglog(hs, errors['trapezoid'], 'b-s', lw=2, ms=6, label='Trapèzes  (O(h²))')
    ax.loglog(hs, errors['simpson'],   'g-^', lw=2, ms=6, label='Simpson   (O(h⁴))')
    ax.loglog(hs, ref_h2, 'k--', lw=1, alpha=0.5, label='Référence O(h²)')
    ax.loglog(hs, ref_h4, 'k:',  lw=1, alpha=0.5, label='Référence O(h⁴)')
    ax.set_xlabel('h = (b-a)/n  (pas)', fontsize=12)
    ax.set_ylabel('Erreur absolue', fontsize=12)
    ax.set_title('Convergence des méthodes d\'intégration\n∫₀¹ eˣ dx = e − 1', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, which='both', alpha=0.3)
    path = os.path.join(OUTPUT_DIR, "convergence.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n  → Graphique sauvegardé : {path}")
    return errors


# ══════════════════════════════════════════════════════════════════════════════
# 6. RÉSUMÉ GLOBAL
# ══════════════════════════════════════════════════════════════════════════════

def print_summary(cp, fp, k_opt):
    print("\n" + "="*60)
    print("  6. RÉSUMÉ GLOBAL")
    print("="*60)
    cp.summary()
    print()
    fp.summary()


# ══════════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "█"*60)
    print("  ANALYSE NUMÉRIQUE — PROGRAMME PRINCIPAL")
    print("█"*60)

    # 1. Chargement
    print("\n  1. Chargement des données ...")
    t_data, T_data, x_data, v_data = load_data()
    print(f"     Refroidissement : {len(t_data)} points  t ∈ [{t_data[0]}, {t_data[-1]}] s")
    print(f"     Écoulement      : {len(x_data)} points  x ∈ [{x_data[0]}, {x_data[-1]}] m")

    # 2. Runge
    analyse_runge()

    # 3. Refroidissement
    cp, k_opt = analyse_cooling(t_data, T_data)

    # 4. Écoulement
    fp = analyse_flow(x_data, v_data)

    # 5. Convergence
    analyse_convergence()

    # 6. Résumé
    print_summary(cp, fp, k_opt)

    print("\n" + "█"*60)
    print(f"  Tous les graphiques sont dans : {OUTPUT_DIR}")
    print("█"*60 + "\n")
