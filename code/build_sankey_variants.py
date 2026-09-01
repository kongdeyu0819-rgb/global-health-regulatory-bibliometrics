#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fig9 thematic-evolution alluvial — multi-style variants for side-by-side comparison.

Real data structure (matches user's original design):
  Left  : 3 thematic clusters
  Middle: keywords, height = frequency in 2000-2017
  Right : keywords, height = frequency in 2018-2026
  Net-new keywords (early=0) link directly from their cluster to the right column.

Styles reproduce venue typography/palettes OFFLINE (no scienceplots/LaTeX needed):
  --style nature  : Science Figures / Nature & AAAS house style (sans-serif, Okabe-Ito colour-blind palette)
  --style lancet  : K-Dense scientific-writer venue guidance / The Lancet style (serif, Lancet red/teal/navy)
  --style aaas    : Science (AAAS) minimal variant
"""
import json, os, argparse
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import numpy as np

BASE = "d:/D/我的论文/全球卫生新博士课题/文献计量学论文A"
PROC = os.path.join(BASE, "data/processed")
OUT = os.path.join(BASE, "figures/xt_png")

# ---- venue style presets -------------------------------------------------
STYLES = {
    "nature": dict(
        font="Arial", title_weight="bold", kw_size=8, hdr_size=12, title_size=14,
        cluster_label_color="white",
        palette={"Access & Equity (LMIC)": "#0072B2",
                 "Vaccines & Quality": "#D55E00",
                 "Systems & Financing": "#009E73"},
        rect_edge="white", rect_lw=0.0, ribbon_alpha=0.42, grid=False,
        spine_top=False,
    ),
    "lancet": dict(
        font="Times New Roman", title_weight="bold", kw_size=8, hdr_size=12.5, title_size=15,
        cluster_label_color="white",
        palette={"Access & Equity (LMIC)": "#C8102E",
                 "Vaccines & Quality": "#1F7A8C",
                 "Systems & Financing": "#1F3A5F"},
        rect_edge="black", rect_lw=0.6, ribbon_alpha=0.40, grid=False,
    ),
    "aaas": dict(
        font="Arial", title_weight="bold", kw_size=8, hdr_size=12, title_size=14,
        cluster_label_color="white",
        palette={"Access & Equity (LMIC)": "#0072B2",
                 "Vaccines & Quality": "#E69F00",
                 "Systems & Financing": "#009E73"},
        rect_edge="white", rect_lw=0.0, ribbon_alpha=0.45, grid=False,
    ),
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

def ribbon(ax, x0, y0a, y0b, x1, y1a, y1b, col, alpha, eps=0.025):
    # Extend ribbon slightly under the bars it connects; bars will be drawn on top,
    # covering the excess and eliminating anti-aliasing/rounding white slivers.
    t = np.linspace(0, 1, 120)
    top = (1 - t) ** 3 * y0b + 3 * (1 - t) ** 2 * t * y0b + 3 * (1 - t) * t ** 2 * y1b + t ** 3 * y1b
    bot = (1 - t) ** 3 * y0a + 3 * (1 - t) ** 2 * t * y0a + 3 * (1 - t) * t ** 2 * y1a + t ** 3 * y1a
    xs = (x0 - eps) + (x1 - x0 + 2 * eps) * t
    verts = np.column_stack([np.concatenate([xs, xs[::-1]]), np.concatenate([top, bot[::-1]])])
    codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 2) + [Path.CLOSEPOLY]
    ax.add_patch(patches.PathPatch(Path(verts, codes), facecolor=col, edgecolor="none", alpha=alpha))

def draw(style_name, out_png):
    S = STYLES[style_name]
    fig, ax = plt.subplots(figsize=(13, 10), dpi=600)
    ax.set_xlim(0, 13); ax.set_ylim(0, 1.06); ax.axis("off")

    left_ys = stack([cluster_early[c] / total_early for c in clusters_order])
    left_map = {c: left_ys[i] for i, c in enumerate(clusters_order)}

    mid_items, mid_meta = [], []
    for c in clusters_order:
        for k in grouped[c]:
            mid_items.append(data[k][1] / total_early); mid_meta.append((k, c))
    mid_ys = stack(mid_items); mid_map = {k: mid_ys[i] for i, (k, c) in enumerate(mid_meta)}

    right_items, right_meta = [], []
    for c in clusters_order:
        for k in grouped[c]:
            right_items.append(data[k][2] / total_late); right_meta.append((k, c))
    right_ys = stack(right_items); right_map = {k: right_ys[i] for i, (k, c) in enumerate(right_meta)}

    xL, xM, xR = 0.9, 5.4, 9.9
    w = 0.55

    # ---- draw ribbons first, then bars on top (covers anti-aliasing gaps) ----
    for c in clusters_order:
        for k in grouped[c]:
            if data[k][1] == 0:
                continue
            m0, m1 = mid_map[k]
            ribbon(ax, xL + w, m0, m1, xM, m0, m1, S["palette"][c], S["ribbon_alpha"])

    for c in clusters_order:
        for k in grouped[c]:
            early, late = data[k][1], data[k][2]
            m0, m1 = mid_map[k]; r0, r1 = right_map[k]
            if early > 0:
                ribbon(ax, xM + w, m0, m1, xR, r0, r1, S["palette"][c], S["ribbon_alpha"])
            else:
                ribbon(ax, xL + w, r0, r1, xR, r0, r1, S["palette"][c], S["ribbon_alpha"])

    # ---- bars on top of ribbons ------------------------------------------------
    for c in clusters_order:
        y0, y1 = left_map[c]
        ax.add_patch(patches.Rectangle((xL, y0), w, y1 - y0, facecolor=S["palette"][c],
                                       edgecolor=S["rect_edge"], linewidth=S["rect_lw"], zorder=5))
        label = c.replace(" (LMIC)", "")
        ax.text(xL + w / 2, (y0 + y1) / 2, label, ha="center", va="center",
                fontsize=10.5, fontweight="bold", color=S["cluster_label_color"],
                rotation=90, rotation_mode="anchor", fontname=S["font"], zorder=6)

    for k, c in mid_meta:
        y0, y1 = mid_map[k]
        if (y1 - y0) > 0.001:
            ax.add_patch(patches.Rectangle((xM, y0), w, y1 - y0, facecolor=S["palette"][c],
                                           edgecolor=S["rect_edge"], linewidth=S["rect_lw"], alpha=0.92, zorder=5))
        if data[k][1] > 0:
            ax.text(xM + w + 0.10, (y0 + y1) / 2, k, ha="left", va="center",
                    fontsize=S["kw_size"], color="black", fontname=S["font"], zorder=6)
    for k, c in right_meta:
        y0, y1 = right_map[k]
        ax.add_patch(patches.Rectangle((xR, y0), w, y1 - y0, facecolor=S["palette"][c],
                                       edgecolor=S["rect_edge"], linewidth=S["rect_lw"], alpha=0.92, zorder=5))
        ax.text(xR + w + 0.10, (y0 + y1) / 2, k, ha="left", va="center",
                fontsize=S["kw_size"] + 0.5, color="black", fontname=S["font"], zorder=6)

    hy = 1.015
    ax.text(xL + w / 2, hy, "Cluster", ha="center", va="bottom", fontsize=S["hdr_size"],
            fontweight="bold", fontname=S["font"])
    ax.text(xM + w / 2, hy, "Keywords (2000–2017)", ha="center", va="bottom", fontsize=S["hdr_size"],
            fontweight="bold", fontname=S["font"])
    ax.text(xR + w / 2, hy, "Keywords (2018–2026)", ha="center", va="bottom", fontsize=S["hdr_size"],
            fontweight="bold", fontname=S["font"])
    ax.set_title("Thematic composition and evolution of the three clusters",
                 fontsize=S["title_size"], fontweight=S["title_weight"], pad=18, fontname=S["font"])

    plt.tight_layout()
    fig.savefig(out_png, dpi=600, bbox_inches="tight", facecolor="white")
    print("saved", out_png)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--style", choices=list(STYLES.keys()), required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(OUT, f"sankey_v_{a.style}.png")
    draw(a.style, out)
