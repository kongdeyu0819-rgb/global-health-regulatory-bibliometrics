# -*- coding: utf-8 -*-
"""文献计量网络分析(Python + networkx + matplotlib), 绕开 R igraph 布局在本环境的崩溃。
数据源: data/processed/paperA_corpus.csv(本地库 + PubMed + Europe PMC 合并, 不依赖 OpenAlex)
产出: figures/authors_network.png, keywords_network.png, top_journals.png, annual_trend.png
      + data/processed/top_authors.csv, top_keywords.csv, top_journals.csv
"""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from collections import Counter

ROOT = "."
PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures")
os.makedirs(FIG, exist_ok=True)

rows = list(csv.DictReader(open(os.path.join(PROC, "paperA_corpus.csv"), encoding="utf-8")))
print("语料行数:", len(rows))

def tokens(s, sep=";"):
    out = []
    for x in (s or "").split(sep):
        x = x.strip()
        if x and x.lower() not in ("et al", "et al."):
            out.append(x)
    return out

def cooc_graph(token_sets):
    G = nx.Graph()
    for ts in token_sets:
        ts = list(dict.fromkeys(ts))  # 去重保序
        if len(ts) < 2:
            continue
        for i in range(len(ts)):
            for j in range(i + 1, len(ts)):
                a, b = ts[i], ts[j]
                if G.has_edge(a, b):
                    G[a][b]["weight"] += 1
                else:
                    G.add_edge(a, b, weight=1)
    return G

# ---------- 1) 作者合作网络 ----------
author_sets = [tokens(r["authors"]) for r in rows]
gA = cooc_graph(author_sets)
print(f"[作者网络] 节点 {gA.number_of_nodes()} 边 {gA.number_of_edges()}")
topA = Counter(dict(gA.degree(weight="weight")))
topA = topA.most_common(15)
with open(os.path.join(PROC, "top_authors.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["author", "collaborations"])
    for a, c in topA: w.writerow([a, c])

plt.figure(figsize=(16, 16))
degA = dict(gA.degree(weight="weight"))
# 仅绘制 Top-K 高合作作者(全量 8166 节点超出绘图内存; 取加权度数前 K 作诱导子图, 标准做法)
K_A = 80
topA_nodes = [n for n, _ in Counter(degA).most_common(K_A)]
gAtop = gA.subgraph(topA_nodes)
posAt = nx.spring_layout(gAtop, k=0.4, iterations=60, seed=42, weight="weight")
nx.draw_networkx_edges(gAtop, posAt, alpha=0.3, edge_color="gray",
                       width=[0.4 + gAtop[u][v]["weight"] * 0.4 for u, v in gAtop.edges()])
nx.draw_networkx_nodes(gAtop, posAt, nodelist=list(gAtop.nodes()),
                       node_size=[30 + degA[n] * 8 for n in gAtop.nodes()],
                       node_color="#1f77b4", alpha=0.9)
topA_labels = dict(Counter(degA).most_common(30))
nx.draw_networkx_labels(gAtop, posAt, labels=topA_labels, font_size=8)
plt.title(f"Top-{K_A} Author Collaboration Network (by weighted collaborations; full corpus {gA.number_of_nodes()} authors)", fontsize=14)
plt.axis("off"); plt.tight_layout()
plt.savefig(os.path.join(FIG, "authors_network.png"), dpi=200)
plt.close()
print("  已存 figures/authors_network.png")

# ---------- 2) 关键词共现网络 ----------
kw_sets = [tokens(r["keywords"]) for r in rows]
gK = cooc_graph(kw_sets)
print(f"[关键词网络] 节点 {gK.number_of_nodes()} 边 {gK.number_of_edges()}")
topK = Counter(dict(gK.degree(weight="weight"))).most_common(20)
with open(os.path.join(PROC, "top_keywords.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["keyword", "co_occ"])
    for k, c in topK: w.writerow([k, c])

plt.figure(figsize=(16, 16))
degK = dict(gK.degree(weight="weight"))
# 仅绘制 Top-K 高频共现关键词(全量 2572+ 节点超出绘图内存; 取加权度数前 K)
K_K = 70
topK_nodes = [n for n, _ in Counter(degK).most_common(K_K)]
gKtop = gK.subgraph(topK_nodes)
posKt = nx.spring_layout(gKtop, k=0.5, iterations=60, seed=42, weight="weight")
nx.draw_networkx_edges(gKtop, posKt, alpha=0.3, edge_color="gray",
                       width=[0.4 + gKtop[u][v]["weight"] * 0.5 for u, v in gKtop.edges()])
nx.draw_networkx_nodes(gKtop, posKt, nodelist=list(gKtop.nodes()),
                       node_size=[20 + degK[n] * 12 for n in gKtop.nodes()],
                       node_color="#d62728", alpha=0.9)
topK_labels = dict(Counter(degK).most_common(30))
nx.draw_networkx_labels(gKtop, posKt, labels=topK_labels, font_size=8)
plt.title(f"Top-{K_K} Keyword Co-occurrence Network (by weighted co-occurrence; full corpus {gK.number_of_nodes()} keywords)", fontsize=14)
plt.axis("off"); plt.tight_layout()
plt.savefig(os.path.join(FIG, "keywords_network.png"), dpi=200)
plt.close()
print("  已存 figures/keywords_network.png")

# ---------- 3) Top 期刊 ----------
jp = Counter(r["journal"] for r in rows if (r.get("journal") or "").strip())
topJ = jp.most_common(15)
with open(os.path.join(PROC, "top_journals.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["journal", "articles"])
    for j, c in topJ: w.writerow([j, c])
plt.figure(figsize=(12, 8))
plt.barh([j for j, _ in topJ][::-1], [c for _, c in topJ][::-1], color="#2ca02c")
plt.xlabel("Articles"); plt.title("Top 15 Sources")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "top_journals.png"), dpi=200); plt.close()
print("  已存 figures/top_journals.png")

# ---------- 4) 年度趋势 ----------
yp = Counter(r["year"] for r in rows if (r.get("year") or "").strip())
for y in list(yp):
    if not y.isdigit(): yp.pop(y, None)
years = sorted(yp)
plt.figure(figsize=(12, 6))
plt.bar(years, [yp[y] for y in years], color="#ff7f0e")
plt.xlabel("Year"); plt.ylabel("Articles"); plt.title("Publications per Year (2000-2025)")
plt.xticks(rotation=90); plt.tight_layout()
plt.savefig(os.path.join(FIG, "annual_trend.png"), dpi=200); plt.close()
print("  已存 figures/annual_trend.png")

print("\n分析完成(Python/networkx)。")
