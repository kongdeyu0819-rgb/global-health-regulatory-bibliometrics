# -*- coding: utf-8 -*-
"""Build a CLEAN 2-stage Sankey input (Time window -> Thematic cluster) for xiantao sankey_flow.
Fixes the previous degenerate 3-column (cluster->cluster) layout and shortens labels to avoid overflow.
"""
import json, os
import pandas as pd

BASE = "d:/D/我的论文/全球卫生新博士课题/文献计量学论文A"
PROC = os.path.join(BASE, "data/processed")
OUT = os.path.join(BASE, "data/raw/xt_input")

te = json.load(open(os.path.join(PROC, "thematic_evolution.json"), encoding="utf-8"))
clusters = json.load(open(os.path.join(PROC, "keyword_clusters.json"), encoding="utf-8"))

windows = te["windows"]                       # ["2000-2009","2010-2017","2018-2026"]
win_labels = ["2000\u20132009", "2010\u20132017", "2018 onward"]  # match manuscript wording

# keyword -> cluster label
kw2cluster = {}
label_by_cluster = {0: "Access & Equity", 1: "Vaccines & Quality", 2: "Systems & Financing"}
for cl in clusters:
    for k in cl.get("top_keywords", []):
        kw2cluster.setdefault(k, label_by_cluster[cl["cluster"]])

# one row per keyword-window occurrence; rescale to <=900 rows (tool cap) preserving proportions
raw_pairs = []
for kw, counts in te["keywords"].items():
    clbl = kw2cluster.get(kw)
    if clbl is None:
        continue
    for wi, c in enumerate(counts):
        c = int(c)
        if c > 0:
            raw_pairs.extend([(win_labels[wi], clbl)] * c)

total = len(raw_pairs)
factor = max(1.0, total / 900.0)
rows = []
from collections import Counter
cnt = Counter(raw_pairs)
for pair, c in cnt.items():
    n = max(1, round(c / factor))
    rows.extend([pair] * n)

df = pd.DataFrame(rows, columns=["Time window", "Thematic cluster"])
os.makedirs(OUT, exist_ok=True)
df.to_excel(os.path.join(OUT, "sankey_flow.xlsx"), index=False, engine="xlsxwriter")
print("rows:", len(df))
print(df["Time window"].value_counts())
print(df["Thematic cluster"].value_counts())
