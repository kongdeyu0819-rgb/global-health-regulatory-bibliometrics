# -*- coding: utf-8 -*-
"""构造仙桃(xt)绘图所需的本地 xlsx 输入文件（基于 paperA 真实数据）"""
import csv, json, os
import pandas as pd
from collections import Counter, defaultdict

BASE = "d:/D/我的论文/全球卫生新博士课题/文献计量学论文A"
PROC = os.path.join(BASE, "data/processed")
OUT = os.path.join(BASE, "data/raw/xt_input")
os.makedirs(OUT, exist_ok=True)

rows = list(csv.DictReader(open(os.path.join(PROC, "paperA_corpus.csv"), encoding="utf-8")))

# ---------- 1) 条形图：高产同行评审期刊（剔除 WHO IRIS 灰色文献占位名） ----------
jc = pd.read_csv(os.path.join(PROC, "top_journals.csv"))
jc = jc[~jc["journal"].str.contains("IRIS|WHO IRIS|undefined", case=False, na=False)]
jc = jc.head(15).copy()
jc.columns = ["x", "y"]
jc = jc.sort_values("y", ascending=True).reset_index(drop=True)  # 升序，is_rev=true 后最高在顶
jc.to_excel(os.path.join(OUT, "bar_journals.xlsx"), index=False, engine="xlsxwriter")
print("bar_journals:", len(jc), jc["x"].tolist()[:5])

# ---------- 2) 条形图：高产作者 Top15 ----------
ac = pd.read_csv(os.path.join(PROC, "top_authors.csv")).head(15).copy()
ac.columns = ["x", "y"]
ac = ac.sort_values("y", ascending=True).reset_index(drop=True)
ac.to_excel(os.path.join(OUT, "bar_authors.xlsx"), index=False, engine="xlsxwriter")
print("bar_authors:", len(ac))

# ---------- 3) 条形图：国家频次 Top15 ----------
cf = json.load(open(os.path.join(PROC, "country_freq.json"), encoding="utf-8"))
cf_items = [k for k, v in sorted(cf.items(), key=lambda x: -x[1]) if k not in ("WHO (multilateral)",)][:15]
df_c = pd.DataFrame({"x": cf_items, "y": [cf[k] for k in cf_items]})
df_c = df_c.sort_values("y", ascending=True).reset_index(drop=True)
df_c.to_excel(os.path.join(OUT, "bar_countries.xlsx"), index=False, engine="xlsxwriter")
print("bar_countries:", len(df_c))

# ---------- 4) 折线图：年度趋势 ----------
acnt = json.load(open(os.path.join(PROC, "annual_counts.json"), encoding="utf-8"))
years = [str(y) for y in range(2000, 2027) if str(y) in acnt]
vals = [acnt[y] for y in years]
df_line = pd.DataFrame([{"trt": "Publications", **{yr: v for yr, v in zip(years, vals)}}])
df_line.to_excel(os.path.join(OUT, "line_trend.xlsx"), index=False, engine="xlsxwriter")
print("line_trend years:", years[0], "-", years[-1], "n=", len(years))

# ---------- 5) 热图：Top25 关键词共现矩阵 ----------
def split_kw(s):
    s = (s or "").strip()
    if not s:
        return []
    # 兼容 ; 与 , 分隔，去引号/多余空格
    parts = []
    for p in s.replace(";", "|").replace(",", "|").split("|"):
        p = p.strip().strip("'\"")
        if p:
            parts.append(p)
    return parts

kw_counter = Counter()
paper_kws = []
for r in rows:
    kws = split_kw(r.get("keywords"))
    if kws:
        paper_kws.append(kws)
        kw_counter.update(kws)

top25 = [k for k, _ in kw_counter.most_common(25)]
idx = {k: i for i, k in enumerate(top25)}
M = [[0] * 25 for _ in range(25)]
for kws in paper_kws:
    seen = set()
    for a in kws:
        if a not in idx:
            continue
        for b in kws:
            if b not in idx or b == a or b in seen:
                continue
            M[idx[a]][idx[b]] += 1
            M[idx[b]][idx[a]] += 1
        seen.add(a)
# 对角线填自身频次
for k in top25:
    M[idx[k]][idx[k]] = kw_counter[k]

df_hm = pd.DataFrame(M, columns=top25)
df_hm.insert(0, "id", top25)
df_hm.to_excel(os.path.join(OUT, "heatmap_keywords.xlsx"), index=False, engine="xlsxwriter")
print("heatmap_keywords top25:", top25[:6])

# ---------- 6) 桑基图：主题演化（时间窗 -> 主题簇 -> 关键词） ----------
te = json.load(open(os.path.join(PROC, "thematic_evolution.json"), encoding="utf-8"))
windows = te["windows"]
kw_counts = te["keywords"]
clusters = json.load(open(os.path.join(PROC, "keyword_clusters.json"), encoding="utf-8"))
kw2cluster = {}
for cl in clusters:
    lbl = {0: "Access & Equity (LMIC)", 1: "Vaccines & Quality", 2: "Systems & Financing"}[cl["cluster"]]
    for k in cl.get("top_keywords", []):
        kw2cluster.setdefault(k, lbl)
# 兜底：未命中簇的关键词归入其最高频窗口对应主题（用频次最高的窗口的通用簇）
sankey_rows = []
raw = []
# 2 阶段桑基：时间窗 -> 主题簇；避免右侧关键词标签重叠
for kw, counts in kw_counts.items():
    clbl = kw2cluster.get(kw, "Systems & Financing")
    for wi, w in enumerate(windows):
        c = int(counts[wi])
        if c > 0:
            raw.append((w, clbl, c))
agg = {}
for w, clbl, c in raw:
    agg[(w, clbl)] = agg.get((w, clbl), 0) + c
# 桑基 3 列（工具强制），用簇名占位作为 K-Class
sankey_rows = []
total = sum(agg.values())
factor = max(1.0, total / 900.0)  # 保持<=900
for (w, clbl), c in agg.items():
    n = max(1, round(c / factor))
    for _ in range(n):
        sankey_rows.append([w, clbl, clbl])
df_sk = pd.DataFrame(sankey_rows, columns=["G-Class", "H-Class", "K-Class"])
# 堆叠条形图（更清晰的 HPP 风格主题演化）：x=时间窗，group=簇，y=计数
stack_rows = []
for (w, clbl), c in agg.items():
    stack_rows.append([w, clbl, int(c)])
df_stack = pd.DataFrame(stack_rows, columns=["x", "group", "y"])
df_stack.to_excel(os.path.join(OUT, "bar_stack_thematic.xlsx"), index=False, engine="xlsxwriter")
print("bar_stack_thematic rows:", len(df_stack))
df_sk.to_excel(os.path.join(OUT, "sankey_evolution.xlsx"), index=False, engine="xlsxwriter")
print("sankey_evolution rows:", len(df_sk), "windows:", windows)

print("\n全部 xlsx 已写入:", OUT)
