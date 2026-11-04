"""Draw the figures of docs/figures/ from results/resultados_tfm.json.

Same palette as the defence slides. Run from the repository root:
    python scripts/generar_figuras.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "docs" / "figures"
DATA = json.load(open(ROOT / "results" / "resultados_tfm.json", encoding="utf-8"))

BLUE, TEAL, GRAY, LGRAY = "#219BC3", "#00566C", "#858591", "#C0C0C8"
QUANT, TINT_Q, TINT_B, TINT_G = "#7D3C98", "#F3EAF7", "#E8F5FA", "#F1F2F4"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": LGRAY,
                     "axes.labelcolor": "#333333", "xtick.color": "#555555", "ytick.color": "#555555",
                     "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    fig.savefig(FIG / name, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  ·", name)


def box(ax, x, y, w, h, title, sub="", fc=TINT_B, tc=TEAL, sc=GRAY, fs=11):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec="none"))
    ax.text(x + w / 2, y + h * (0.62 if sub else 0.5), title, ha="center", va="center",
            color=tc, fontsize=fs, fontweight="bold")
    if sub:
        ax.text(x + w / 2, y + h * 0.3, sub, ha="center", va="center", color=sc, fontsize=fs - 2.5)


def arrow(ax, x0, y0, x1, y1, c=GRAY):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=c, lw=1.4))


# ── 1. Architecture ─────────────────────────────────────────────────────────
def fig_arquitectura():
    fig, ax = plt.subplots(figsize=(13, 3.9)); ax.set_xlim(0, 13); ax.set_ylim(0, 3.9); ax.axis("off")
    steps = [("Secuencia", "L aminoácidos", TINT_B, TEAL, GRAY),
             ("ESM-2 (35M)", "embeddings + atención", TINT_B, TEAL, GRAY),
             ("Vector de par", "1201 = 480+480+1+240", TINT_B, TEAL, GRAY),
             ("Embudo MLP", "1201 → 32 → 12 ángulos", TINT_B, TEAL, GRAY),
             ("Circuito MERA", "12 qubits · 312 parám.\n27 valores medidos", QUANT, "white", "white"),
             ("Capas clásicas", "39 → 64 → 32\ndistancia + 2 ángulos", TINT_B, TEAL, GRAY)]
    w, g, y = 1.85, 0.32, 2.15
    for i, (t, s, fc, tc, sc) in enumerate(steps):
        x = 0.1 + i * (w + g)
        box(ax, x, y, w, 1.4, t, s, fc, tc, sc)
        if i:
            arrow(ax, x - g + 0.03, y + 0.7, x - 0.03, y + 0.7)
    xs = [0.1 + k * (w + g) for k in (5, 4, 3)]
    row = [("Distancias", "mapa L × L"), ("Reconstrucción", "MDS + refinamiento"),
           ("Estructura 3D", "trazado Cα")]
    arrow(ax, xs[0] + w / 2, y - 0.05, xs[0] + w / 2, 1.5)
    for k, (t, s) in enumerate(row):
        box(ax, xs[k], 0.35, w, 1.1, t, s, TINT_G, TEAL, GRAY, fs=10.5)
        if k:
            arrow(ax, xs[k - 1] - 0.03, 0.9, xs[k] + w + 0.03, 0.9)
    ax.text(0.1, 0.9, "45 103 parámetros\n312 en el circuito", color=TEAL, fontsize=12, fontweight="bold", va="center")
    save(fig, "arquitectura.png")


# ── 2. MERA schedule (exactly the one in the code) ──────────────────────────
SCHEDULE = [
    (list(range(12)), [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (1, 2), (3, 4), (5, 6), (7, 8), (9, 10)],
     [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11)]),
    ([0, 2, 4, 6, 8, 10], [(0, 2), (4, 6), (8, 10)], [(0, 2), (4, 6), (8, 10)]),
    ([0, 4, 8], [(0, 4), (4, 8)], [(0, 4)]),
    ([0, 8], [], [(0, 8)]),
]


def fig_mera():
    fig, ax = plt.subplots(figsize=(12.5, 7.6)); ax.set_xlim(-1.4, 12); ax.set_ylim(0.2, 16.6); ax.axis("off")
    X = lambda q: q * 0.95
    y = 16.0
    nb = 0
    for lvl, (wires, dpairs, ipairs) in enumerate(SCHEDULE):
        ax.text(-1.35, y - 0.35, f"Nivel {lvl}", color=BLUE, fontsize=11, fontweight="bold", va="center")
        for q in wires:                                            # data re-upload
            ax.add_patch(FancyBboxPatch((X(q) - 0.36, y - 0.1), 0.72, 0.36, boxstyle="round,pad=0.01,rounding_size=0.06", fc=BLUE, ec="none"))
            ax.text(X(q), y + 0.08, r"$R_Y(x)$", ha="center", va="center", color="white", fontsize=7.5, fontweight="bold")
        y -= 0.75
        for q in wires:
            ax.add_patch(Circle((X(q), y), 0.27, fc=TINT_G, ec=LGRAY, lw=1.2))
            ax.text(X(q), y, str(q), ha="center", va="center", color=TEAL, fontsize=9, fontweight="bold")
        y -= 0.75
        rows = []                                                  # disentanglers split in non-overlapping rows
        for p in dpairs:
            for r in rows:
                if all(max(p) < min(o) or min(p) > max(o) for o in r):
                    r.append(p); break
            else:
                rows.append([p])
        for r in rows:
            for a, b in r:
                ax.add_patch(FancyBboxPatch((X(a) - 0.3, y - 0.2), X(b) - X(a) + 0.6, 0.4, boxstyle="round,pad=0.01,rounding_size=0.05", fc="#A569BD", ec="none"))
                ax.text((X(a) + X(b)) / 2, y, "D", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
                nb += 1
            y -= 0.6
        for a, b in ipairs:
            ax.add_patch(FancyBboxPatch((X(a) - 0.3, y - 0.22), X(b) - X(a) + 0.6, 0.44, boxstyle="round,pad=0.01,rounding_size=0.05", fc=TINT_Q, ec=QUANT, lw=1.2))
            ax.text((X(a) + X(b)) / 2, y, "B", ha="center", va="center", color=QUANT, fontsize=9, fontweight="bold")
            nb += 1
        y -= 1.0
    ax.add_patch(FancyBboxPatch((-0.3, y - 0.05), 11.0, 0.55, boxstyle="round,pad=0.01,rounding_size=0.05", fc=TEAL, ec="none"))
    ax.text(5.2, y + 0.22, "Medición: 12 ⟨Z⟩ + 9 ⟨ZZ⟩ + 3 ⟨X⟩ + 3 ⟨Y⟩ = 27 valores", ha="center", va="center", color="white", fontsize=11, fontweight="bold")
    ax.text(5.2, y - 0.55, f"{nb} bloques × 8 parámetros (U3 ⊗ U3 + RYY·RZZ) = 216  ·  recarga de datos entrenable = 96  ·  total 312",
            ha="center", va="center", color=GRAY, fontsize=10, style="italic")
    ax.text(5.2, y - 0.95, r"$R_Y(x)$: recarga de datos   ·   D: disentangler   ·   B: isometría (reduce a la mitad los qubits activos)",
            ha="center", va="center", color=GRAY, fontsize=10, style="italic")
    assert nb == 27
    save(fig, "circuito_mera.png")


# ── 3. Contact precision by range (memoria, Table 5.1) ──────────────────────
def fig_contactos():
    t = DATA["resultados_memoria"]["contactos_tabla_5_1"]
    rng = ["corto_6_11", "medio_12_23", "largo_24"]
    lab = ["Corto (6–11)", "Medio (12–23)", "Largo (≥ 24)"]
    series = [("Sistema propuesto", [t["sistema_propuesto"][r]["P@L/5"] * 100 for r in rng], BLUE),
              ("ESM-2 nativo", [t["esm2_referencia"][r]["P@L/5"] * 100 for r in rng], TEAL),
              ("Azar (densidad)", [t["densidad_contactos"][r] * 100 for r in rng], LGRAY)]
    fig, ax = plt.subplots(figsize=(9, 4.6))
    w = 0.26
    for k, (name, vals, c) in enumerate(series):
        xs = [i + (k - 1) * w for i in range(3)]
        ax.bar(xs, vals, w * 0.92, color=c, label=name)
        for x, v in zip(xs, vals):
            ax.text(x, v + 1.2, f"{v:.1f}".replace(".", ","), ha="center", fontsize=9.5, color="#444")
    ax.set_xticks(range(3)); ax.set_xticklabels(lab); ax.set_ylabel("P@L/5 (%)"); ax.set_ylim(0, 100)
    ax.legend(frameon=False, ncol=3, loc="upper right")
    ax.set_title("Precisión de contactos por rango de separación (224 proteínas, CASP11)", color=TEAL, fontweight="bold", loc="left")
    save(fig, "contactos.png")


# ── 4. Ablation (memoria, Table 5.4) ────────────────────────────────────────
def fig_ablacion():
    t = DATA["resultados_memoria"]["ablacion_tabla_5_4"]
    reps = [("Réplica 1\ntraining_30", t["replica_1_training_30"]), ("Réplica 2\ntraining_100", t["replica_2_training_100"])]
    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    w = 0.34
    for i, (name, r) in enumerate(reps):
        for k, (key, c, lab) in enumerate((("MERA", QUANT, "Circuito MERA (312 parám.)"), ("lineal", GRAY, "Capa lineal 12→27 (351 parám.)"))):
            x = i + (k - 0.5) * w
            ax.bar(x, r[key] * 100, w * 0.9, color=c, label=lab if i == 0 else None)
            ax.text(x, r[key] * 100 + 0.2, f"{r[key]:.4f}".replace(".", ","), ha="center", fontsize=9.5, color="#444")
        ax.text(i, 11.9, f"Δ = {r['diferencia']:+.4f}".replace(".", ","), ha="center", color=QUANT, fontweight="bold")
    ax.set_xticks(range(2)); ax.set_xticklabels([n for n, _ in reps]); ax.set_ylim(0, 15.5)
    ax.set_ylabel("P@L/5 largo alcance (%)"); ax.legend(frameon=False, loc="upper center", ncol=2, fontsize=9)
    ax.set_title("Ablación: circuito cuántico frente a capa lineal", color=TEAL, fontweight="bold", loc="left")
    save(fig, "ablacion.png")


# ── 5. CASP11 context (memoria, Table 5.3) ──────────────────────────────────
def fig_casp():
    t = DATA["resultados_memoria"]["casp_tabla_5_3"]
    rows = [("CONSIP2 / MetaPSICOV (CASP11, con MSA)", t["CONSIP2_MetaPSICOV_CASP11"]["P@L/5"], TEAL),
            ("Mejor grupo CASP10 (≈, con MSA)", t["mejor_grupo_CASP10"]["P@L/5"], GRAY),
            ("Este trabajo (sin MSA)", t["este_trabajo"]["P@L/5"], BLUE),
            ("ESM-2 nativo (sin MSA)", t["esm2_referencia"]["P@L/5"], LGRAY),
            ("Predictor aleatorio", t["predictor_aleatorio"]["P@L/5"], "#DADAE0")]
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    for i, (n, v, c) in enumerate(rows[::-1]):
        ax.barh(i, v * 100, color=c, height=0.66)
        ax.text(v * 100 + 0.4, i, f"{v * 100:.1f} %".replace(".", ","), va="center", fontsize=10, color="#333")
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]])
    ax.set_xlabel("P@L/5, contactos de largo alcance (%)"); ax.set_xlim(0, 31)
    ax.set_title("Contexto: experimento CASP11", color=TEAL, fontweight="bold", loc="left")
    save(fig, "casp11.png")


# ── 6. Quantum gradient norm (notebook run) ─────────────────────────────────
def fig_gradiente():
    h = DATA["ejecucion_notebook"]["entrenamiento"]["historial"]
    ep = [r["epoca"] for r in h]
    fig, ax1 = plt.subplots(figsize=(8.2, 3.9))
    ax1.plot(ep, [r["norma_grad_cuantico"] for r in h], "-o", color=QUANT, lw=2, ms=4, label="‖∇q‖ circuito")
    ax1.axhline(0.01, color="#C0392B", ls="--", lw=1, alpha=0.6, label="umbral de meseta (~0,01)")
    ax1.set_yscale("log"); ax1.set_xlabel("Época"); ax1.set_ylabel("Norma del gradiente cuántico", color=QUANT)
    ax2 = ax1.twinx(); ax2.spines["right"].set_visible(True)
    ax2.plot(ep, [r["loss_val"] for r in h], "-", color=TEAL, lw=1.6, label="pérdida de monitorización")
    ax2.set_ylabel("Pérdida de monitorización", color=TEAL)
    lines = ax1.get_lines() + ax2.get_lines()
    ax1.legend(lines, [l.get_label() for l in lines], frameon=False, fontsize=9, loc="upper right")
    ax1.set_title("El gradiente del circuito se apaga durante el entrenamiento", color=TEAL, fontweight="bold", loc="left")
    save(fig, "gradiente_cuantico.png")


# ── 7. 3D quality vs chain length (notebook run) ────────────────────────────
def fig_longitud():
    per = DATA["ejecucion_notebook"]["estructura_3d"]["Modelo híbrido"]["por_proteina"]
    fig, ax = plt.subplots(figsize=(8.2, 3.9))
    ax.scatter([p["L"] for p in per], [p["GDT_TS"] for p in per], s=46, color=BLUE, alpha=0.85, edgecolor="white")
    for p in per:
        if "2KJI" in p["id"] or "3PBT" in p["id"]:
            ax.annotate(p["id"].split("#")[1][:4], (p["L"], p["GDT_TS"]), xytext=(8, 6), textcoords="offset points", color=TEAL, fontweight="bold")
    ax.set_xlabel("Longitud de la cadena (residuos)"); ax.set_ylabel("GDT_TS")
    ax.set_title("Calidad de la reconstrucción 3D frente a la longitud (30 proteínas)", color=TEAL, fontweight="bold", loc="left")
    save(fig, "estructura_vs_longitud.png")


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    print("Figuras en docs/figures/:")
    for f in (fig_arquitectura, fig_mera, fig_contactos, fig_ablacion, fig_casp, fig_gradiente, fig_longitud):
        f()
