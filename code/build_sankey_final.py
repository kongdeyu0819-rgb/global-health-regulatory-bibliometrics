#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publication-quality thematic-evolution alluvial diagram (Fig9).

Structure matches the user's original design:
  Left  : 3 thematic clusters
  Middle: keywords, height = frequency in 2000-2017
  Right : keywords, height = frequency in 2018-2026
  Ribbons connect cluster -> keyword (early) and keyword (early) -> keyword (late).
  Net-new keywords (early=0) are drawn directly from their cluster to the right column.

Rendered with matplotlib at 600 DPI.  This is used instead of Xiantao's native
sankey tool because Xiantao's sankey enforces flow-conserving vertical internal
labels, which overlap for 20 keywords; the alluvial/riverplot style required
here needs external horizontal labels and asymmetric bands.
"""
import json, os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import numpy as np

BASE = "d:/D/我的论文/全球卫生新博士课题/文献计量学论文A"
PROC = os.path.join(BASE, "data/processed")
OUT = os.path.join(BASE, "figures/xt_png")

# Publication-friendly palette (ColourBrewer Set2-ish, cluster-distinguishable)
COLOR = {
    "Access & Equity (LMIC)": "#66c2a5",
    "Vaccines & Quality": "#fc8d62",
    "Systems & Financing": "#8da0cb",
}

te = json.load(open(os.path.join(PROC, "thematic_evolution.json"), encoding="utf-8"))
clusters = json.load(open(os.path.join(PROC, "keyword_clusters.json"), encoding="utf-8"))
LBL = {0: "Access & Equity (LMIC)", 1: "Vaccines & Quality", 2: "Systems & Financing"}
kw2c = {}
for cl in clusters:
    for k in cl.get("top_keywords", []):
        kw2c.setdefault(k, LBL[cl["cluster"]])

data = {}
for kw, cnt in te["keywords"].items():
    early = int(cnt[0]) + int(cnt[1])
    late = int(cnt[2])
    data[kw] = (kw2c.get(kw), early, late)

clusters_order = ["Access & Equity (LMIC)", "Vaccines & Quality", "Systems & Financing"]
grouped = {c: [] for c in clusters_order}
for cl in clusters:
    c = LBL[cl["cluster"]]
    for k in cl.get("top_keywords", []):
        if k in data:
            grouped[c].append(k)
for k in data:
    if not any(k in grouped[c] for c in clusters_order):
        grouped[data[k][0]].append(k)

cluster_early = {c: sum(data[k][1] for k in grouped[c]) for c in clusters_order}
cluster_late = {c: sum(data[k][2] for k in grouped[c]) for c in clusters_order}
total_early = sum(cluster_early.values())
total_late = sum(cluster_late.values())

def stack(items):
    ys, b = [], 0.0
    for h in items:
        ys.append((b, b + h)); b += h
    return ys

fig, ax = plt.subplots(figsize=(13, 10), dpi=600)
ax.set_xlim(0, 13)
ax.set_ylim(0, 1.06)
ax.axis("off")

# left column: clusters scaled by early totals
left_ys = stack([cluster_early[c] / total_early for c in clusters_order])
left_map = {c: left_ys[i] for i, c in enumerate(clusters_order)}

# middle (early) and right (late) keyword columns grouped by cluster
mid_items, mid_meta = [], []
for c in clusters_order:
    for k in grouped[c]:
        h = data[k][1] / total_early
        mid_items.append(h); mid_meta.append((k, c))
mid_ys = stack(mid_items)
mid_map = {k: mid_ys[i] for i, (k, c) in enumerate(mid_meta)}

right_items, right_meta = [], []
for c in clusters_order:
    for k in grouped[c]:
        h = data[k][2] / total_late
        right_items.append(h); right_meta.append((k, c))
right_ys = stack(right_items)
right_map = {k: right_ys[i] for i, (k, c) in enumerate(right_meta)}

xL, xM, xR = 0.9, 5.4, 9.9
w = 0.55

# draw cluster rects
for c in clusters_order:
    y0, y1 = left_map[c]
    ax.add_patch(patches.Rectangle((xL, y0), w, y1 - y0, facecolor=COLOR[c],
                                    edgecolor="black", linewidth=1.0))
    label = c.replace(" (LMIC)", "")
    ax.text(xL + w / 2, (y0 + y1) / 2, label, ha="center", va="center",
            fontsize=10, fontweight="bold", color="white", rotation=90,
            rotation_mode="anchor", fontfamily="Arial")

# draw keyword rects and horizontal labels
kw_label_size = 7.5
for k, c in mid_meta:
    y0, y1 = mid_map[k]
    h = y1 - y0
    if h > 0.001:
        ax.add_patch(patches.Rectangle((xM, y0), w, h, facecolor=COLOR[c],
                                        edgecolor="black", linewidth=0.6, alpha=0.92))
    if data[k][1] > 0:
        ax.text(xM + w + 0.10, (y0 + y1) / 2, k, ha="left", va="center",
                fontsize=kw_label_size, color="black", fontfamily="Arial")

for k, c in right_meta:
    y0, y1 = right_map[k]
    ax.add_patch(patches.Rectangle((xR, y0), w, h, facecolor=COLOR[c],
                                    edgecolor="black", linewidth=0.6, alpha=0.92))
    ax.text(xR + w + 0.10, (y0 + y1) / 2, k, ha="left", va="center",
            fontsize=kw_label_size + 0.5, color="black", fontfamily="Arial")

def ribbon(x0, y0a, y0b, x1, y1a, y1b, col):
    t = np.linspace(0, 1, 100)
    # cubic Bezier with control points maintaining y at start/end -> smooth S-shape
    top = (1 - t) ** 3 * y0b + 3 * (1 - t) ** 2 * t * y0b + 3 * (1 - t) * t ** 2 * y1b + t ** 3 * y1b
    bot = (1 - t) ** 3 * y0a + 3 * (1 - t) ** 2 * t * y0a + 3 * (1 - t) * t ** 2 * y1a + t ** 3 * y1a
    xs = x0 + (x1 - x0) * t
    verts = np.column_stack([np.concatenate([xs, xs[::-1]]), np.concatenate([top, bot[::-1]])])
    codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 2) + [Path.CLOSEPOLY]
    ax.add_patch(patches.PathPatch(Path(verts, codes), facecolor=col, edgecolor="none", alpha=0.45))

# cluster -> middle keyword
for c in clusters_order:
    for k in grouped[c]:
        early = data[k][1]
        if early == 0:
            continue
        m0, m1 = mid_map[k]
        ribbon(xL + w, m0, m1, xM, m0, m1, COLOR[c])

# middle keyword -> right keyword (or cluster -> right for net-new)
for c in clusters_order:
    for k in grouped[c]:
        early, late = data[k][1], data[k][2]
        m0, m1 = mid_map[k]
        r0, r1 = right_map[k]
        if early > 0:
            ribbon(xM + w, m0, m1, xR, r0, r1, COLOR[c])
        else:
            ribbon(xL + w, r0, r1, xR, r0, r1, COLOR[c])

# stage headers
header_y = 1.015
ax.text(xL + w / 2, header_y, "Cluster", ha="center", va="bottom", fontsize=12, fontweight="bold", fontfamily="Arial")
ax.text(xM + w / 2, header_y, "Keywords (2000-2017)", ha="center", va="bottom", fontsize=12, fontweight="bold", fontfamily="Arial")
ax.text(xR + w / 2, header_y, "Keywords (2018-2026)", ha="center", va="bottom", fontsize=12, fontweight="bold", fontfamily="Arial")

ax.set_title("Thematic composition and evolution of the three clusters", fontsize=14, fontweight="bold", pad=18, fontfamily="Arial")

plt.tight_layout()
fig.savefig(os.path.join(OUT, "sankey_evolution-1.png"), dpi=600, bbox_inches="tight", facecolor="white")
fig.savefig(os.path.join(OUT, "sankey_evolution-1.tif"), dpi=600, bbox_inches="tight", facecolor="white")
print("saved", os.path.join(OUT, "sankey_evolution-1.png/.tif"))
