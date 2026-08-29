# -*- coding: utf-8 -*-
"""analyze_bibliometrics.py —— 阶段三: 对 paperA_corpus.csv(2063篇)做描述性文献计量。
产出: 年度趋势、高产期刊、作者合作网络、关键词共现网络+聚类、突现检测、主题演化。
HPP 素净风格: 白底、深细边框、弱饱和、无渐变。
"""
import csv, re, os, json, itertools
from collections import Counter, defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import networkx as nx

CSV = "data/processed/paperA_corpus.csv"
FIG = "figures"
PROC = "data/processed"
os.makedirs(FIG, exist_ok=True)
os.makedirs(PROC, exist_ok=True)

# ---------- HPP 素净风格 ----------
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.edgecolor": "#1f2d3d",
    "axes.labelcolor": "#1f2d3d",
    "text.color": "#1f2d3d",
    "xtick.color": "#1f2d3d",
    "ytick.color": "#1f2d3d",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})
# 弱饱和分类色板(用于社群着色)
PALETTE = ["#4C78A8","#F58518","#54A24B","#E45756","#72B7B2","#EECA3B",
           "#B279A2","#FF9DA6","#9D755D","#BAB0AC","#86BCB6","#8EAADB"]

# ---------- 载入 ----------
def load():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    for r in rows:
        r["year"] = (r.get("year") or "").strip()
    return rows

ROWS = load()
N = len(ROWS)
print(f"载入语料: {N} 篇")

# ---------- 工具 ----------
STOP_KW = {"who","medicines","medicine","drugs","drug","global health","health",
           "review","systematic review","scoping review","bibliometric","analysis",
           "study","studies","united states","china","india","research","policy",
           "the","a","an","of","and","or","in","on","for","to","with","from"}

def split_kw(s):
    if not s: return []
    # 多分隔符: 分号、换行、逗号(谨慎)
    parts = re.split(r"[;\n]|,\s*(?=[A-Z][a-z])", s)  # 逗号仅当后接大写开头词时切, 避免切断短语
    out = []
    for p in parts:
        p = p.strip().strip(".\"';,")
        p = re.sub(r"\s+", " ", p)
        if not p: continue
        pl = p.lower()
        if pl in STOP_KW: continue
        if len(p) < 3: continue
        out.append(p)
    return out

def split_auth(s):
    if not s: return []
    chunks = re.split(r"[;]", s)
    out = []
    for c in chunks:
        c = c.strip().strip(".")
        if not c: continue
        if any(ch.isdigit() for ch in c): continue          # 丢弃含数字的(机构编号等)
        if len(c) < 4: continue
        if len(c) > 60: continue                            # 丢弃整段机构描述
        # 丢弃明显机构串
        if re.search(r"\b(University|Institute|Ministry|Hospital|Department|School|College|WHO|FDA|EMA|WHO)\b", c, re.I):
            continue
        out.append(c)
    return out

# ---------- 1. 年度趋势 ----------
def annual_trend():
    c = Counter()
    for r in ROWS:
        y = r["year"]
        if y.isdigit():
            c[int(y)] += 1
    years = sorted(c)
    fig, ax = plt.subplots(figsize=(10,4.2))
    ys = [str(y) for y in years]
    vals = [c[y] for y in years]
    ax.bar(ys, vals, color="#4C78A8", edgecolor="#1f2d3d", linewidth=0.6)
    # 仅标出部分年份, 避免拥挤
    step = max(1, len(ys)//12)
    ax.set_xticks(range(0, len(ys), step))
    ax.set_xticklabels([ys[i] for i in range(0, len(ys), step)], rotation=45, ha="right")
    ax.set_ylabel("Publications")
    ax.set_title("Annual publications on regulatory reliance & medicine access (2000–2026)\n(2025–2026 include online-first / in-press records)",
                 fontsize=10.5, fontweight="bold")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    plt.tight_layout(); plt.savefig(f"{FIG}/trend.png", dpi=300); plt.close()
    # 2000 后逐年存表
    post = {str(y): c[y] for y in years if y >= 2000}
    json.dump(post, open(f"{PROC}/annual_counts.json","w"), ensure_ascii=False, indent=2)
    print("  [1] 年度趋势 -> figures/trend.png ; 2000+ 计数 -> annual_counts.json")
    return c

# ---------- 2. 高产期刊 ----------
def top_journals():
    c = Counter()
    grey = 0  # WHO IRIS 等灰色文献/政策文件(非真实期刊)
    for r in ROWS:
        j = (r.get("journal") or "").strip()
        if not j:
            continue
        if "IRIS" in j or j.lower() in ("", "who", "unknown"):
            grey += 1
            continue
        c[j] += 1
    top = c.most_common(15)
    fig, ax = plt.subplots(figsize=(8,5.2))
    names = [t[0][:42] for t in top][::-1]
    vals = [t[1] for t in top][::-1]
    # 末尾追加一行灰色文献标注, 透明展示其体量(非期刊)
    names.append("WHO IRIS grey literature / policy docs*")
    vals.append(grey)
    colors = ["#54A24B"]*len(top) + ["#BAB0AC"]
    ax.barh(names, vals, color=colors, edgecolor="#1f2d3d", linewidth=0.6)
    ax.set_xlabel("Publications")
    ax.set_title("Top 15 most productive peer-reviewed journals\n(*WHO IRIS grey literature shown separately; retained in corpus & all other analyses)",
                 fontsize=9.5, fontweight="bold")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    plt.tight_layout(); plt.savefig(f"{FIG}/journals_top.png", dpi=300); plt.close()
    json.dump({"peer_reviewed_top": top, "grey_literature_count": grey},
              open(f"{PROC}/top_journals.json","w"), ensure_ascii=False, indent=2)
    print(f"  [2] 高产期刊 -> figures/journals_top.png (真实期刊榜首: {top[0]}; 灰色文献 {grey} 篇已排除)")
    return c

# ---------- 3. 作者合作网络 ----------
def author_network(min_occ=3, topK=60):
    occ = Counter()
    pairs = Counter()
    for r in ROWS:
        auths = split_auth(r.get("authors"))
        if len(auths) < 1: continue
        occ.update(auths)
        for a, b in itertools.combinations(sorted(set(auths)), 2):
            pairs[(a, b)] += 1
    keep = {a for a, n in occ.items() if n >= min_occ}
    # 取出现频次最高的 topK 个节点(限边规模)
    top_nodes = [a for a, _ in occ.most_common(topK) if a in keep]
    G = nx.Graph()
    for (a, b), w in pairs.items():
        if a in set(top_nodes) and b in set(top_nodes):
            G.add_edge(a, b, weight=w)
    for n in top_nodes:
        if n in G: G.nodes[n]["weight"] = occ[n]
    # 清理孤立点
    G.remove_nodes_from([n for n in G if G.degree(n)==0])
    if G.number_of_nodes() == 0:
        print("  [3] 作者网络空(数据噪声), 跳过"); return occ, None
    comms = nx.community.greedy_modularity_communities(G)
    cmap = {n: i for i, com in enumerate(comms) for n in com}
    fig, ax = plt.subplots(figsize=(10,9))
    pos = nx.spring_layout(G, k=0.5, seed=42, weight="weight")
    degs = dict(G.degree())
    for i, com in enumerate(comms):
        ns = [n for n in com if n in G]
        if not ns: continue
        nx.draw_networkx_nodes(G, pos, nodelist=ns, node_color=PALETTE[i % len(PALETTE)],
                               node_size=[80 + 6*degs[n] for n in ns],
                               edgecolors="#1f2d3d", linewidths=0.4, alpha=0.9)
    nx.draw_networkx_edges(G, pos, alpha=0.25, edge_color="#888888", width=0.5)
    # 仅标注度最高的 15 个作者
    lbl = {n: (n[:18] + "." if len(n) > 18 else n) for n, d in
           sorted(degs.items(), key=lambda x: -x[1])[:15]}
    nx.draw_networkx_labels(G, pos, labels=lbl, font_size=7, font_color="#1f2d3d")
    ax.set_title(f"Author co-authorship network (nodes≥{min_occ} occurrences, top {len(top_nodes)})",
                 fontsize=11, fontweight="bold")
    ax.axis("off")
    plt.tight_layout(); plt.savefig(f"{FIG}/author_network.png", dpi=300); plt.close()
    # 输出社群
    comm_out = [{"community": i, "size": len(com),
                 "top_authors": [n for n in sorted(com, key=lambda x:-occ[x])[:8]]}
                for i, com in enumerate(comms)]
    json.dump(comm_out, open(f"{PROC}/author_communities.json","w"), ensure_ascii=False, indent=2)
    print(f"  [3] 作者合作网络 -> figures/author_network.png ; {G.number_of_nodes()} 节点 / {G.number_of_edges()} 边 / {len(comms)} 社群")
    return occ, comm_out

# ---------- 4. 关键词共现网络 + 聚类 ----------
def keyword_network(min_occ=4, topK=80):
    occ = Counter()
    pairs = Counter()
    for r in ROWS:
        kws = split_kw(r.get("keywords"))
        if len(kws) < 1: continue
        occ.update(kws)
        for a, b in itertools.combinations(sorted(set(kws)), 2):
            pairs[(a, b)] += 1
    top_nodes = [k for k, _ in occ.most_common(topK) if k in occ and occ[k] >= min_occ]
    G = nx.Graph()
    for (a, b), w in pairs.items():
        if a in set(top_nodes) and b in set(top_nodes):
            G.add_edge(a, b, weight=w)
    for n in top_nodes:
        if n in G: G.nodes[n]["weight"] = occ[n]
    G.remove_nodes_from([n for n in G if G.degree(n)==0])
    if G.number_of_nodes() == 0:
        print("  [4] 关键词网络空, 跳过"); return occ, None
    comms = nx.community.greedy_modularity_communities(G)
    cmap = {n: i for i, com in enumerate(comms) for n in com}
    fig, ax = plt.subplots(figsize=(11,10))
    pos = nx.spring_layout(G, k=0.4, seed=7, weight="weight")
    degs = dict(G.degree())
    for i, com in enumerate(comms):
        ns = [n for n in com if n in G]
        if not ns: continue
        nx.draw_networkx_nodes(G, pos, nodelist=ns, node_color=PALETTE[i % len(PALETTE)],
                               node_size=[70 + 5*degs[n] for n in ns],
                               edgecolors="#1f2d3d", linewidths=0.4, alpha=0.9)
    nx.draw_networkx_edges(G, pos, alpha=0.22, edge_color="#888888", width=0.5)
    lbl = {n: (n[:20] + "." if len(n) > 20 else n) for n, d in
           sorted(degs.items(), key=lambda x: -x[1])[:25]}
    nx.draw_networkx_labels(G, pos, labels=lbl, font_size=7, font_color="#1f2d3d")
    ax.set_title(f"Keyword co-occurrence network (≥{min_occ} occurrences, top {len(top_nodes)})",
                 fontsize=11, fontweight="bold")
    ax.axis("off")
    plt.tight_layout(); plt.savefig(f"{FIG}/keyword_network.png", dpi=300); plt.close()
    # 社群关键词表
    comm_out = []
    for i, com in enumerate(comms):
        members = sorted(com, key=lambda x:-occ[x])
        comm_out.append({"cluster": i, "size": len(members),
                         "top_keywords": members[:12],
                         "hub": members[0] if members else ""})
    comm_out.sort(key=lambda x: -x["size"])
    json.dump(comm_out, open(f"{PROC}/keyword_clusters.json","w"), ensure_ascii=False, indent=2)
    # CSV 便于论文使用
    with open(f"{PROC}/keyword_clusters.csv","w",encoding="utf-8",newline="") as f:
        w = csv.writer(f); w.writerow(["cluster","size","hub","top_keywords"])
        for c in comm_out:
            w.writerow([c["cluster"], c["size"], c["hub"], " | ".join(c["top_keywords"])])
    print(f"  [4] 关键词共现网络 -> figures/keyword_network.png ; {G.number_of_nodes()} 节点 / {len(comms)} 主题簇")
    return occ, comm_out

# ---------- 5. 突现检测 + 主题演化 ----------
def burst_and_evolution():
    # 关键词逐年计数
    kw_year = defaultdict(lambda: Counter())
    for r in ROWS:
        y = r["year"]
        if not y.isdigit(): continue
        y = int(y)
        for k in split_kw(r.get("keywords")):
            kw_year[k][y] += 1
    # 仅考虑出现>=5次的关键词
    candidates = [k for k, c in Counter({k: sum(v.values()) for k, v in kw_year.items()}).items() if c >= 5]
    rec = []
    for k in candidates:
        yrs = kw_year[k]
        early = sum(v for y, v in yrs.items() if y <= 2014)
        late = sum(v for y, v in yrs.items() if y >= 2015)
        tot = early + late
        if tot == 0: continue
        late_share = late / tot
        # 突现分数: 近期占比 - 总体均衡基准(0.5) * 频次, 取近期主导且总量大者
        score = (late_share - 0.5) * tot
        rec.append((k, tot, early, late, round(late_share, 2), round(score, 2)))
    rec.sort(key=lambda x: -x[5])
    burst = rec[:30]
    with open(f"{PROC}/burst_keywords.csv","w",encoding="utf-8",newline="") as f:
        w = csv.writer(f); w.writerow(["keyword","total","early(<=2014)","late(>=2015)","late_share","burst_score"])
        for row in burst: w.writerow(row)
    print(f"  [5a] 突现关键词(近期主导) -> burst_keywords.csv (top: {burst[0][0] if burst else '-'})")

    # 主题演化: 把关键词归入前面聚类(若已算), 看各簇在三个时间窗的占比
    evo = {}
    windows = [(2000,2009,"2000-2009"),(2010,2017,"2010-2017"),(2018,2026,"2018-2026")]
    # 用关键词频次最高的 40 个按年份统计(不依赖聚类, 直接展示热点词时间分布)
    top_kw = [k for k, _ in Counter({k: sum(v.values()) for k, v in kw_year.items()}).most_common(20)]
    evo = {"windows": [w[2] for w in windows],
           "keywords": {}}
    for k in top_kw:
        evo["keywords"][k] = [sum(kw_year[k][y] for y in range(ws, we+1)) for ws, we, _ in windows]
    json.dump(evo, open(f"{PROC}/thematic_evolution.json","w"), ensure_ascii=False, indent=2)
    # 演化堆叠图
    fig, ax = plt.subplots(figsize=(9,5))
    bottom = [0]*len(windows)
    for k in top_kw:
        vals = evo["keywords"][k]
        ax.bar([w[2] for w in windows], vals, bottom=bottom, label=k[:18],
               edgecolor="white", linewidth=0.4)
        bottom = [b+v for b, v in zip(bottom, vals)]
    ax.set_ylabel("Publications (keyword mentions)")
    ax.set_title("Thematic evolution of top keywords across time windows", fontsize=11, fontweight="bold")
    ax.legend(fontsize=6, loc="upper left", ncol=2)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    plt.tight_layout(); plt.savefig(f"{FIG}/thematic_evolution.png", dpi=300); plt.close()
    print("  [5b] 主题演化 -> figures/thematic_evolution.png ; thematic_evolution.json")

# ---------- 主流程 ----------
if __name__ == "__main__":
    try: annual_trend()
    except Exception as e: print("  [1] 失败:", e)
    try: top_journals()
    except Exception as e: print("  [2] 失败:", e)
    try: author_network()
    except Exception as e: print("  [3] 失败:", e)
    try: keyword_network()
    except Exception as e: print("  [4] 失败:", e)
    try: burst_and_evolution()
    except Exception as e: print("  [5] 失败:", e)
    print("阶段三分析完成。")
