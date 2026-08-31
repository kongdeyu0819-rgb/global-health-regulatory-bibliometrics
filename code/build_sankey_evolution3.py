# -*- coding: utf-8 -*-
"""Build a clean 3-stage thematic-evolution Sankey at the theme (cluster) level.

Three columns = three time windows; three clusters = stable nodes in each window.
Ribbon width = total theme publications; the three themes persist and grow across the
windows (exact per-window counts are annotated in the nodes and reported in Fig. 8).
"""
import json, os
import pandas as pd

BASE = "d:/D/我的论文/全球卫生新博士课题/文献计量学论文A"
PROC = os.path.join(BASE, "data/processed")
OUT = os.path.join(BASE, "data/raw/xt_input")

te = json.load(open(os.path.join(PROC, "thematic_evolution.json"), encoding="utf-8"))
clusters = json.load(open(os.path.join(PROC, "keyword_clusters.json"), encoding="utf-8"))
lbl = {0: "Access & Equity", 1: "Vaccines & Quality", 2: "Systems & Financing"}
kw2c = {}
for cl in clusters:
    for k in cl.get("top_keywords", []):
        kw2c.setdefault(k, lbl[cl["cluster"]])

win = ["2000\u20132009", "2010\u20132017", "2018 onward"]
agg = {c: [0, 0, 0] for c in lbl.values()}
for kw, cnt in te["keywords"].items():
    c = kw2c.get(kw)
    if c is None:
        continue
    for i, v in enumerate(cnt):
        agg[c][i] += int(v)

# Build 3-column chains (G/H/K = the 3 windows), one per cluster.
# Use total theme publications as chain weight for visibility.
raw = []
for c, (n1, n2, n3) in agg.items():
    total = n1 + n2 + n3
    g = f"{c}\n{win[0]}\n(n={n1})"
    h = f"{c}\n{win[1]}\n(n={n2})"
    k = f"{c}\n{win[2]}\n(n={n3})"
    raw.extend([[g, h, k]] * total)

# Cap rows to the tool limit (<=900) while preserving proportions.
from collections import Counter
factor = max(1.0, len(raw) / 900.0)
rows = []
cnt = Counter(tuple(r) for r in raw)
for pat, c in cnt.items():
    rows.extend([list(pat)] * max(1, round(c / factor)))

df = pd.DataFrame(rows, columns=["G-Class", "H-Class", "K-Class"])
df.to_excel(os.path.join(OUT, "sankey_evolution3.xlsx"), index=False, engine="xlsxwriter")
print("cluster volumes:", agg)
print("raw rows:", len(raw), "capped:", len(df), "factor=%.3f" % factor)
