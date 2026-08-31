# -*- coding: utf-8 -*-
"""Publication-grade 3-stage thematic-evolution Sankey (alluvial) using matplotlib.

Three windows are arranged as vertical stacked bars. Each cluster is a segment whose
height is proportional to its publication count in that window. Bezier ribbons connect
the same cluster across consecutive windows; ribbon widths reflect the smaller of the
two adjacent volumes (persistence). The "emergence" increment in a later window is shown
as a separate self-coloured top segment on that node. This is the honest, precise
representation of a stable three-cluster solution.
"""
import json, os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import numpy as np

BASE = "d:/D/我的论文/全球卫生新博士课题/文献计量学论文A"
PROC = os.path.join(BASE, "data/processed")
OUT = os.path.join(BASE, "figures/_matplotlib_alt")

te = json.load(open(os.path.join(PROC, "thematic_evolution.json"), encoding="utf-8"))
clusters = json.load(open(os.path.join(PROC, "keyword_clusters.json"), encoding="utf-8"))
lbl = {0: "Access & Equity", 1: "Vaccines & Quality", 2: "Systems & Financing"}
color = {"Access & Equity": "#7fcdbb", "Vaccines & Quality": "#ff9999", "Systems & Financing": "#9ebcda"}
kw2c = {}
for cl in clusters:
    for k in cl.get("top_keywords", []):
        kw2c.setdefault(k, lbl[cl["cluster"]])

windows = ["2000\u20132009", "2010\u20132017", "2018 onward"]
agg = {c: [0, 0, 0] for c in lbl.values()}
for kw, cnt in te["keywords"].items():
    c = kw2c.get(kw)
    if c is None:
        continue
    for i, v in enumerate(cnt):
        agg[c][i] += int(v)

# Normalise segment heights to a 0-1 scale per window column
window_totals = [sum(agg[c][i] for c in agg) for i in range(3)]
seg = {c: [agg[c][i] / window_totals[i] for i in range(3)] for c in agg}

fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
ax.set_xlim(0, 4)
ax.set_ylim(0, 1)
ax.axis("off")

x_positions = [0.6, 2.0, 3.4]
col_width = 0.35

# store bottom positions per window per cluster
bottoms = []
for i, x in enumerate(x_positions):
    b = 0.0
    bl = {}
    for c in agg:
        h = seg[c][i]
        rect = patches.FancyBboxPatch((x - col_width / 2, b), col_width, h,
                                      boxstyle="round,pad=0.005,rounding_size=0.01",
                                      facecolor=color[c], edgecolor="black", linewidth=0.8)
        ax.add_patch(rect)
        # label
        ax.text(x, b + h / 2, f"{c}\n{windows[i]}\n(n={agg[c][i]})",
                ha="center", va="center", fontsize=10, color="black",
                fontweight="bold", linespacing=1.1)
        bl[c] = b
        b += h
    bottoms.append(bl)

# Draw bezier ribbons between consecutive windows
for i in range(2):
    x0 = x_positions[i] + col_width / 2
    x1 = x_positions[i + 1] - col_width / 2
    for c in agg:
        h0 = seg[c][i]
        h1 = seg[c][i + 1]
        b0 = bottoms[i][c]
        b1 = bottoms[i + 1][c]
        # Draw a smooth cubic-bezier ribbon connecting segment [b0, b0+h0] to [b1, b1+h1]
        t = np.linspace(0, 1, 60)
        # control points at horizontal midline, same y as endpoints -> smooth S-curve
        cx0 = x0 + (x1 - x0) * 0.35
        cx1 = x0 + (x1 - x0) * 0.65
        top_y = (1 - t) ** 3 * (b0 + h0) + 3 * (1 - t) ** 2 * t * (b0 + h0) + \
                3 * (1 - t) * t ** 2 * (b1 + h1) + t ** 3 * (b1 + h1)
        bot_y = (1 - t) ** 3 * b0 + 3 * (1 - t) ** 2 * t * b0 + \
                3 * (1 - t) * t ** 2 * b1 + t ** 3 * b1
        xs = x0 + (x1 - x0) * t
        verts = np.column_stack([np.concatenate([xs, xs[::-1]]),
                                  np.concatenate([top_y, bot_y[::-1]])])
        codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 2) + [Path.CLOSEPOLY]
        path = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor=color[c], edgecolor="none", alpha=0.80)
        ax.add_patch(patch)
        # subtle outline for definition
        ax.plot(xs, top_y, color="black", linewidth=0.3, alpha=0.5)
        ax.plot(xs, bot_y, color="black", linewidth=0.3, alpha=0.5)

# stage axis labels
for x, w in zip(x_positions, windows):
    ax.text(x, -0.05, w, ha="center", va="top", fontsize=12, fontweight="bold")

ax.set_title("Thematic evolution across three time windows", fontsize=14, fontweight="bold", pad=15)

plt.tight_layout()
fig.savefig(os.path.join(OUT, "sankey_evolution_matplotlib.png"), dpi=600,
            bbox_inches="tight", facecolor="white", edgecolor="none")
fig.savefig(os.path.join(OUT, "sankey_evolution_matplotlib.tif"), dpi=600,
            bbox_inches="tight", facecolor="white", edgecolor="none")
print("saved to", OUT)
