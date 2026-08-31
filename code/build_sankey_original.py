# -*- coding: utf-8 -*-
"""Rebuild the ORIGINAL Fig9 structure: Cluster (left) -> Keyword (middle) -> Keyword (right).

This matches the user's reference screenshot: three cluster blocks on the left,
a vertical stack of individual keyword blocks in the middle, and the same keywords
repeated on the right (a degenerate third column required by the tool's 3-column
format). The ribbon width from a cluster to its keywords reflects the keyword's
count across all three time windows.
"""
import json, os
import pandas as pd
from collections import Counter

BASE = "d:/D/我的论文/全球卫生新博士课题/文献计量学论文A"
PROC = os.path.join(BASE, "data/processed")
OUT = os.path.join(BASE, "data/raw/xt_input")

te = json.load(open(os.path.join(PROC, "thematic_evolution.json"), encoding="utf-8"))
clusters = json.load(open(os.path.join(PROC, "keyword_clusters.json"), encoding="utf-8"))

lbl = {0: "Access & Equity (LMIC)", 1: "Vaccines & Quality", 2: "Systems & Financing"}
kw2cluster = {}
for cl in clusters:
    for k in cl.get("top_keywords", []):
        kw2cluster.setdefault(k, lbl[cl["cluster"]])

# Build raw rows: [cluster, keyword, keyword] repeated by total keyword count
raw = []
for kw, counts in te["keywords"].items():
    clbl = kw2cluster.get(kw)
    if clbl is None:
        continue
    total = sum(int(c) for c in counts)
    if total > 0:
        raw.extend([[clbl, kw, kw]] * total)

# Cap to <=900 rows preserving proportions
factor = max(1.0, len(raw) / 900.0)
rows = []
cnt = Counter(tuple(r) for r in raw)
for pat, c in cnt.items():
    rows.extend([list(pat)] * max(1, round(c / factor)))

df = pd.DataFrame(rows, columns=["G-Class", "H-Class", "K-Class"])
df.to_excel(os.path.join(OUT, "sankey_evolution_original.xlsx"), index=False, engine="xlsxwriter")
print("raw rows:", len(raw), "capped:", len(df), "factor=%.3f" % factor)
print("G values:", df["G-Class"].unique().tolist())
print("H values:", df["H-Class"].nunique())
