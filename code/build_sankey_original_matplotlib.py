# -*- coding: utf-8 -*-
"""Faithful reconstruction of the ORIGINAL Fig9 (cluster -> keyword -> keyword), but with
the two keyword columns carrying DIFFERENT window frequencies so it is a true thematic
evolution (not a mirrored duplicate):

  - Left column  : 3 thematic clusters (Access & Equity; Vaccines & Quality; Systems & Financing)
  - Middle column: the 20 keywords, height = frequency in 2000-2017 (early)
  - Right column : the 20 keywords, height = frequency in 2018 onward (late)
  - Ribbons      : cluster -> keyword (early) -> keyword (late), coloured by cluster

A keyword absent in the early window (e.g., COVID-19) appears only in the right column,
linked directly from its cluster as an emergent theme.
"""
import json, os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import numpy as np

BASE = "d:/D/我的论文/全球卫生新博士课题/文献计量学论文A"
PROC = os.path.join(BASE, "data/processed")
OUT = os.path.join(BASE, "figures/xt_png")

te = json.load(open(os.path.join(PROC, "thematic_evolution.json"), encoding="utf-8"))
clusters = json.load(open(os.path.join(PROC, "keyword_clusters.json"), encoding="utf-8"))
lbl = {0: "Access & Equity (LMIC)", 1: "Vaccines & Quality", 2: "Systems & Financing"}
color = {"Access & Equity (LMIC)": "#4c9f70", "Vaccines & Quality": "#e06c75", "Systems & Financing": "#5b8fd6"}
kw2c = {}
for cl in clusters:
    for k in cl.get("top_keywords", []):
        kw2c.setdefault(k, lbl[cl["cluster"]])

# early = 2000-2017, late = 2018 onward
data = {}
for kw, cnt in te["keywords"].items():
    early = int(cnt[0]) + int(cnt[1])
    late = int(cnt[2])
    data[kw] = (kw2c.get(kw), early, late)

clusters_order = ["Access & Equity (LMIC)", "Vaccines & Quality", "Systems & Financing"]
# group keywords by cluster, keep cluster's keyword order from json
grouped = {c: [] for c in clusters_order}
for cl in clusters:
    c = lbl[cl["cluster"]]
    for k in cl.get("top_keywords", []):
        if k in data:
            grouped[c].append(k)
# add any leftover keywords
for k in data:
    if not any(k in grouped[c] for c in clusters_order):
        grouped[data[k][0]].append(k)

# Each column normalised to full height, so all keyword labels are readable.
# Within each column, keyword heights = share of that column's total.
cluster_early = {c: sum(data[k][1] for k in grouped[c]) for c in clusters_order}
cluster_late = {c: sum(data[k][2] for k in grouped[c]) for c in clusters_order}
total_early = sum(cluster_early.values())
total_late = sum(cluster_late.values())

fig, ax = plt.subplots(figsize=(11, 9), dpi=600)
ax.set_xlim(0, 11)
ax.set_ylim(0, 1.08)
ax.axis("off")

# ---- y positions per column (stack helper) ----
def stack(items):
    ys, b = [], 0.0
    for h in items:
        ys.append((b, b + h)); b += h
    return ys

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

# column x positions (rectangles)
xL, xM, xR = 0.9, 5.0, 9.1
w = 0.45

# draw cluster rects (left)
for c in clusters_order:
    y0, y1 = left_map[c]
    ax.add_patch(patches.Rectangle((xL, y0), w, y1 - y0, facecolor=color[c],
                                    edgecolor="black", linewidth=0.8))
    label = c.replace(" (LMIC)", "")
    ax.text(xL + w / 2, (y0 + y1) / 2, label, ha="center", va="center",
            fontsize=8.5, fontweight="bold", color="white", rotation=90,
            rotation_mode="anchor")

# draw keyword rects (middle = early, right = late)
for k, c in mid_meta:
    y0, y1 = mid_map[k]
    h = y1 - y0
    if h > 0.001:
        ax.add_patch(patches.Rectangle((xM, y0), w, h, facecolor=color[c],
                                        edgecolor="black", linewidth=0.6, alpha=0.92))
    # label only if keyword has early presence; otherwise its right-column label suffices
    if data[k][1] > 0:
        ax.text(xM + w + 0.08, (y0 + y1) / 2, f"{k}", ha="left", va="center",
                fontsize=7.5, color="black")

for k, c in right_meta:
    y0, y1 = right_map[k]
    ax.add_patch(patches.Rectangle((xR, y0), w, y1 - y0, facecolor=color[c],
                                    edgecolor="black", linewidth=0.6, alpha=0.92))
    ax.text(xR + w + 0.08, (y0 + y1) / 2, f"{k}", ha="left", va="center",
            fontsize=8.0, color="black")

# ---- ribbons with vertical alignment matching the keyword's share inside its cluster ----
def ribbon(x0, y0a, y0b, x1, y1a, y1b, col):
    t = np.linspace(0, 1, 80)
    top = (1 - t) ** 3 * y0b + 3 * (1 - t) ** 2 * t * y0b + 3 * (1 - t) * t ** 2 * y1b + t ** 3 * y1b
    bot = (1 - t) ** 3 * y0a + 3 * (1 - t) ** 2 * t * y0a + 3 * (1 - t) * t ** 2 * y1a + t ** 3 * y1a
    xs = x0 + (x1 - x0) * t
    verts = np.column_stack([np.concatenate([xs, xs[::-1]]), np.concatenate([top, bot[::-1]])])
    codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 2) + [Path.CLOSEPOLY]
    ax.add_patch(patches.PathPatch(Path(verts, codes), facecolor=col, edgecolor="none", alpha=0.55))

# helper: position of a keyword inside its cluster band (so cluster->keyword ribbon is aligned)
def keyword_in_cluster_pos(c, k, colmap):
    # find y position of keyword k within cluster c's block in the given column map
    items = [k2 for k2, c2 in mid_meta if c2 == c] if colmap is mid_map else [k2 for k2, c2 in right_meta if c2 == c]
    ys = [colmap[kk] for kk in items]
    return colmap[k] if k in colmap else None

# cluster -> middle keyword (width = keyword early share within cluster)
for c in clusters_order:
    c0, c1 = left_map[c]
    for k in grouped[c]:
        early = data[k][1]
        if early == 0:
            continue
        m0, m1 = mid_map[k]
        ribbon(xL + w, m0, m1, xM, m0, m1, color[c])  # vertical positions match keyword band
# middle keyword -> right keyword (width = keyword late share within cluster)
for c in clusters_order:
    for k in grouped[c]:
        early, late = data[k][1], data[k][2]
        m0, m1 = mid_map[k]
        r0, r1 = right_map[k]
        if early > 0:
            ribbon(xM + w, m0, m1, xR, r0, r1, color[c])
        else:
            # emergent keyword (COVID-19): direct from cluster to right
            c0, c1 = left_map[c]
            ribbon(xL + w, r0, r1, xR, r0, r1, color[c])

# stage headers
ax.text(xL + w / 2, 1.02, "Cluster", ha="center", va="bottom", fontsize=12, fontweight="bold")
ax.text(xM + w / 2, 1.02, "Keywords (2000-2017)", ha="center", va="bottom", fontsize=12, fontweight="bold")
ax.text(xR + w / 2, 1.02, "Keywords (2018 onward)", ha="center", va="bottom", fontsize=12, fontweight="bold")

ax.set_title("Thematic composition and evolution of the three clusters", fontsize=14, fontweight="bold", pad=18)

plt.tight_layout()
fig.savefig(os.path.join(OUT, "sankey_evolution-1.png"), dpi=600, bbox_inches="tight", facecolor="white")
fig.savefig(os.path.join(OUT, "sankey_evolution-1.tif"), dpi=600, bbox_inches="tight", facecolor="white")
print("saved sankey_evolution-1.png/.tif")
