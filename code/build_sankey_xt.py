#!/usr/bin/env python3
"""Build Xiantao sankey_plot input: Cluster -> Keyword -> Time-window.

Real data sources:
  data/processed/thematic_evolution.json  (20 keywords x 3 windows)
  data/processed/keyword_clusters.json    (3 clusters, top_keywords)

Model: 3-layer grouped Sankey (header row + one row per paper-keyword occurrence).
  col1 = Cluster label
  col2 = Keyword label
  col3 = Time window label
Node heights are driven by row frequency, so each (keyword, window) pair is
repeated by its occurrence count. This is conserved and honestly shows
evolution incl. net-new topics (COVID-19: 0 -> 28 in 2018-2026).

If the render rejects >~900 rows, pass --scale 0.65 to shrink proportionally.
"""
import json
import argparse
import openpyxl

PROJ = "d:/D/我的论文/全球卫生新博士课题/文献计量学论文A"

CLUSTER_NAMES = {0: "Access & Equity (LMIC)", 1: "Vaccines & Quality", 2: "Systems & Financing"}
WINDOW_LABELS = ["2000-2009", "2010-2017", "2018-2026"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1.0, help="proportional shrink of row counts")
    ap.add_argument("--out", default="data/raw/xt_input/sankey_evolution_xt.xlsx")
    args = ap.parse_args()

    te = json.load(open(f"{PROJ}/data/processed/thematic_evolution.json", encoding="utf-8"))
    kc = json.load(open(f"{PROJ}/data/processed/keyword_clusters.json", encoding="utf-8"))

    kw2cluster = {}
    for c in kc:
        for kw in c["top_keywords"]:
            kw2cluster.setdefault(kw, c["cluster"])

    counts = te["keywords"]  # keyword -> [w0, w1, w2]
    windows = te["windows"]

    rows = []  # (cluster_label, keyword, window_label)
    total = 0
    for kw, vals in counts.items():
        cid = kw2cluster[kw]
        clabel = CLUSTER_NAMES[cid]
        for wi, v in enumerate(vals):
            n = int(round(v * args.scale))
            for _ in range(n):
                rows.append((clabel, kw, WINDOW_LABELS[wi]))
            total += n

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sankey"
    ws.append(["Cluster", "Keyword", "Time window"])
    for r in rows:
        ws.append(list(r))
    wb.save(args.out)
    print(f"Wrote {args.out}: {len(rows)} data rows (scale={args.scale}, total~={total})")


if __name__ == "__main__":
    main()
