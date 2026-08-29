# -*- coding: utf-8 -*-
"""build_country_data.py —— 从本地 pubmed_raw.xml 的 Affiliation 提取国家,
回填到 paperA_corpus.csv(按 pmid 映射), 构建国家合作网络。
无需联网(数据已在本地 XML)。
覆盖: 仅 PubMed 来源(含 Affiliation)的文献; WHO IRIS/EPMC-only/本地库缺此字段, 标注覆盖率。
"""
import csv, re, os, json, itertools
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

RAW = "data/raw/pubmed_raw.xml"
CSV = "data/processed/paperA_corpus.csv"
PROC = "data/processed"
FIG = "figures"
os.makedirs(PROC, exist_ok=True); os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({
    "font.family":"sans-serif","font.size":10,
    "axes.edgecolor":"#1f2d3d","text.color":"#1f2d3d",
    "xtick.color":"#1f2d3d","ytick.color":"#1f2d3d",
    "figure.facecolor":"white","axes.facecolor":"white"})

# 国家别名 -> 规范名
COUNTRY = {
 "United States":"United States","USA":"United States","U.S.A":"United States","US":"United States",
 "United Kingdom":"United Kingdom","UK":"United Kingdom","England":"United Kingdom","Scotland":"United Kingdom","Wales":"United Kingdom",
 "China":"China","PR China":"China","People's Republic of China":"China",
 "India":"India","Japan":"Japan","Germany":"Germany","France":"France","Brazil":"Brazil","Canada":"Canada",
 "Australia":"Australia","Italy":"Italy","Spain":"Spain","Netherlands":"Netherlands","Switzerland":"Switzerland",
 "South Africa":"South Africa","Sweden":"Sweden","Belgium":"Belgium","Denmark":"Denmark","Norway":"Norway",
 "Finland":"Finland","Austria":"Austria","Ireland":"Ireland","Portugal":"Portugal","Poland":"Poland",
 "Russia":"Russia","Russian Federation":"Russia","Turkey":"Turkey","Iran":"Iran","Israel":"Israel",
 "Mexico":"Mexico","Argentina":"Argentina","Chile":"Chile","Colombia":"Colombia","Peru":"Peru",
 "Thailand":"Thailand","Malaysia":"Malaysia","Singapore":"Singapore","Indonesia":"Indonesia","Philippines":"Philippines",
 "Vietnam":"Vietnam","Pakistan":"Pakistan","Bangladesh":"Bangladesh","Nepal":"Nepal","Sri Lanka":"Sri Lanka",
 "Kenya":"Kenya","Nigeria":"Nigeria","Ethiopia":"Ethiopia","Ghana":"Ghana","Uganda":"Uganda","Tanzania":"Tanzania",
 "Egypt":"Egypt","Morocco":"Morocco","Tunisia":"Tunisia","Senegal":"Senegal","Zimbabwe":"Zimbabwe",
 "New Zealand":"New Zealand","South Korea":"South Korea","Republic of Korea":"South Korea","Korea":"South Korea",
 "Taiwan":"Taiwan","Hong Kong":"China","Macau":"China",
 "Saudi Arabia":"Saudi Arabia","United Arab Emirates":"United Arab Emirates","Qatar":"Qatar",
 "Greece":"Greece","Czech Republic":"Czech Republic","Hungary":"Hungary","Romania":"Romania",
 "Ukraine":"Ukraine","Croatia":"Croatia","Serbia":"Serbia","Slovenia":"Slovenia",
 "Ireland":"Ireland","Luxembourg":"Luxembourg","Iceland":"Iceland",
 "WHO":"WHO (multilateral)","World Health Organization":"WHO (multilateral)",
}
COUNTRY_RE = re.compile(r"\b(" + "|".join(re.escape(k) for k in COUNTRY.keys()) + r")\b", re.I)
COUNTRY_LC = {k.lower(): v for k, v in COUNTRY.items()}

def extract_countries(affil_text):
    found = set()
    for m in COUNTRY_RE.finditer(affil_text or ""):
        found.add(COUNTRY_LC[m.group(1).lower()])
    return found

# ---- 解析 PubMed XML ----
tree = ET.parse(RAW)
pmid_countries = {}
total_aff = 0
for art in tree.getroot().iter("PubmedArticle"):
    pmid = ""
    for el in art.iter("PMID"):
        pmid = (el.text or "").strip(); break
    if not pmid:
        for el in art.iter("ArticleId"):
            if el.get("IdType")=="pmid": pmid=(el.text or "").strip(); break
    if not pmid: continue
    countries = set()
    for aff in art.iter("Affiliation"):
        if aff.text:
            total_aff += 1
            countries |= extract_countries(aff.text)
    if countries:
        pmid_countries[pmid] = countries

print(f"PubMed XML 解析: {len(pmid_countries)} 篇含国家信息; 扫描 Affiliation 段 {total_aff}")

# ---- 映射到语料 ----
rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
fieldnames = list(rows[0].keys())
if "countries" not in fieldnames: fieldnames.append("countries")
if "country_count" not in fieldnames: fieldnames.append("country_count")

matched = 0
for r in rows:
    pmid = (r.get("pmid") or "").strip()
    cs = pmid_countries.get(pmid, set())
    if cs:
        matched += 1
        r["countries"] = "; ".join(sorted(cs))
        r["country_count"] = str(len(cs))
    else:
        r["countries"] = ""
        r["country_count"] = "0"

out = os.path.join(PROC, "paperA_corpus_geo.csv")
with open(out, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames); w.writeheader(); w.writerows(rows)
print(f"已回填国家并写出: {out} (语料 {len(rows)} 篇中 {matched} 篇匹配到国家, 覆盖 {100*matched/len(rows):.1f}%)")

# ---- 国家频次 + 合作网络 ----
cfreq = {}
edges = {}
for r in rows:
    cs = [c for c in (r.get("countries") or "").split(";") if c.strip()]
    cs = list(dict.fromkeys(c.strip() for c in cs))  # 去重保序
    if not cs: continue
    for c in cs: cfreq[c] = cfreq.get(c,0)+1
    for a,b in itertools.combinations(sorted(set(cs)),2):
        edges[(a,b)] = edges.get((a,b),0)+1

json.dump(cfreq, open(os.path.join(PROC,"country_freq.json"),"w"), ensure_ascii=False, indent=2)
with open(os.path.join(PROC,"country_edges.csv"),"w",encoding="utf-8",newline="") as f:
    w=csv.writer(f); w.writerow(["country_a","country_b","weight"])
    for (a,b),wt in sorted(edges.items(), key=lambda x:-x[1]):
        w.writerow([a,b,wt])
print(f"国家数: {len(cfreq)}; 跨国合作边数: {len(edges)}")

# 国家频次 Top20 条形
top = sorted(cfreq.items(), key=lambda x:-x[1])[:20][::-1]
fig, ax = plt.subplots(figsize=(8,5.2))
ax.barh([t[0] for t in top], [t[1] for t in top], color="#4C78A8", edgecolor="#1f2d3d", linewidth=0.6)
ax.set_xlabel("Publications (with at least one affiliation in that country)")
ax.set_title("Top 20 countries by publication count (PubMed-sourced subset, n=%d)"%matched,
             fontsize=10.5, fontweight="bold")
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
plt.tight_layout(); plt.savefig(os.path.join(FIG,"country_freq.png"), dpi=300); plt.close()

# 国家合作网络(仅保留权重>=2的边, 避免过密)
G = nx.Graph()
for (a,b),wt in edges.items():
    if wt >= 2:
        G.add_edge(a,b,weight=wt)
for c, n in cfreq.items():
    if c in G: G.nodes[c]["weight"]=n
G.remove_nodes_from([n for n in G if G.degree(n)==0])
if G.number_of_nodes()>0:
    comms = nx.community.greedy_modularity_communities(G)
    PALETTE=["#4C78A8","#F58518","#54A24B","#E45756","#72B7B2","#EECA3B","#B279A2"]
    fig, ax = plt.subplots(figsize=(11,10))
    pos = nx.spring_layout(G, k=0.5, seed=11, weight="weight")
    degs = dict(G.degree())
    for i, com in enumerate(comms):
        ns=[n for n in com if n in G]
        if not ns: continue
        nx.draw_networkx_nodes(G,pos,nodelist=ns,node_color=PALETTE[i%len(PALETTE)],
            node_size=[120+8*degs[n] for n in ns],edgecolors="#1f2d3d",linewidths=0.4,alpha=0.9)
    nx.draw_networkx_edges(G,pos,alpha=0.25,edge_color="#888888",width=0.6)
    lbl={n:(n if degs[n]>=6 else "") for n in G}
    nx.draw_networkx_labels(G,pos,labels=lbl,font_size=7,font_color="#1f2d3d")
    ax.set_title("Country co-authorship network (edges ≥2 collaborations, PubMed subset)",
                 fontsize=11, fontweight="bold")
    ax.axis("off")
    plt.tight_layout(); plt.savefig(os.path.join(FIG,"country_network.png"), dpi=300); plt.close()
    comm_out=[{"community":i,"size":len(com),"countries":sorted(com,key=lambda x:-cfreq[x])[:10]}
              for i,com in enumerate(comms)]
    json.dump(comm_out, open(os.path.join(PROC,"country_communities.json"),"w"), ensure_ascii=False, indent=2)
    print(f"国家合作网络 -> figures/country_network.png ; {G.number_of_nodes()} 节点 / {G.number_of_edges()} 边 / {len(comms)} 社群")
else:
    print("国家合作网络空(边均<2), 跳过")

print("国家回填完成。")
