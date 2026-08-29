# -*- coding: utf-8 -*-
"""合并本地文献库(纳入篇) + PubMed 为统一语料, 去重, 产出早期画像。
OpenAlex 因当日预算耗尽暂缺; 待其就绪后(本机R或午夜UTC后)可追加合并。
输出:
  data/processed/paperA_corpus.csv   统一字段语料(source 标记 local/pubmed)
  data/processed/early_profile.json  年度/作者/期刊/来源分布
"""
import csv, json, re, os
import xml.etree.ElementTree as ET

RAW = "data/raw"
PROC = "data/processed"
os.makedirs(PROC, exist_ok=True)

MANUAL_EXCLUDE_LOCAL = ["A Pathologist’s Perspective on Emerging Genomic Tests for Breast Cancer"]
# 用户裁定: 纳入明显相关的待确认篇(许铭N系列/全球卫生治理/国际卫生融资类), 排除离题(如 One Health 译名)
MANUAL_INCLUDE_REVIEW = [
    "Evolution and effectiveness of bilateral and multilateral development assistance for health",
    "Factors associated with the export of traditional",
    "N10外刊全文 2026 1462-8902 28 2 81537052",
    "N1 Enhancing innovative financing",
    "N2 Evaluation WHO integration",
    "N4jogh-16-04145n",
    "N5 CHIKV modeling",
    "N5s12889-026-28110-9 reference",
    "N6中刊全文 2026 R1 93174A 058 003 7203755179",
    "N7resource 2026 07 18 1784350246821",
    "N9 Influenza seasonality",
    "Rethinking international financing for health to better respond to future pandemics",
    "基于全球治理五要素理论的WHO公共卫生产品治理机制分析-杨坚",
]

def norm_title(t):
    t = (t or "").lower()
    t = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", t)
    return t.strip()

# 用户/方法裁定排除: 虽命中机制词, 但属离题体裁的文献。
# (A) 体裁排除: "First Approval"/"Approval Summary" 类单一药品获批公告(Adis/FDA 文体),
#     虽可能提及 Project Orbis 等机制, 但属药品级获批简报而非监管依赖/协调机制系统性研究。
# (B) 特定标题排除: 个别仅以泛化词(如 abbreviated review)命中、实质为临床药理综述的离题文献。
GENRE_EXCLUDE_RE = re.compile(r"first approval|approval summary", re.I)
MANUAL_EXCLUDE_TITLES = [
    "Clinical pharmacology of cancer therapies in older adults",  # 临床药理综述, 仅以 abbreviated review 命中
]

# ---------- 可及性/LMIC 分析透镜(语料内派生标签, 非检索硬过滤) ----------
# 主题另一半"低收入国用药可及性": 在宽口径监管依赖语料中, 标记是否触及可及性/LMIC 维度。
import re as _re
_ACCESS_RE = _re.compile(
    r"access to medicines|medicine access|drug access|medicines access|equitable access|"
    r"affordab|low[- ]income|lower[- ]income|middle[- ]income|developing countr|LMIC|"
    r"low- and middle-income|sub[- ]?saharan|resource[- ]limited|resource[- ]poor|global south|"
    r"essential medicines|pharmaceutical procurement|medicine procurement|drug procurement|"
    r"universal health coverage|\bUHC\b|neglected tropical|availability of medicines|"
    r"supply chain|price|pricing|generic",
    _re.I)
# 政策流(可及性侧)专属宽松过滤: 不要求机制词, 但须明确命中"用药可及性/LMIC"主题短语。
ACCESS_POLICY_RE = _re.compile(
    r"access to medicines|medicine access|drug access|medicines access|equitable access to|"
    r"affordable medicines|medicine affordab|essential medicines|medicine procurement|"
    r"pharmaceutical procurement|local production of|local production pharmaceutical|"
    r"medicine pricing|drug pricing|paediatric formulation|pediatric formulation|"
    r"child-friendly formulation|substandard|falsified|universal health coverage|\bUHC\b|"
    r"neglected tropical|availability of medicines|generic medicines|vaccine access|"
    r"regulatory system strengthening|national medicines regulatory|GAP-f|medicines regulation",
    _re.I)
def access_lens(r):
    blob = " ".join([r.get("title", ""), r.get("abstract", ""), r.get("keywords", "")])
    return 1 if _ACCESS_RE.search(blob) else 0

# ---------- 主题相关性自动筛选(PRISMA 题摘初筛的自动化等价) ----------
# 宽口径检索会带来离题文献(如 "prequalification training" 医学教育、
# "shared reliance on processing" 心理学、"confidence-building strategies" 护理学等)。
# 故在合并前去噪: 非本地文献须在其 title/abstract/keywords 命中至少一个"高精主题短语",
# 否则视为离题剔除。本地库为用户人工裁定纳入, 不过滤。
HP_TERMS = [
    # ---- 高精机制短语(仅"监管依赖/协调/互认/WHO预认证"文献才会包含的措辞) ----
    "who prequalification", "prequalification of medicines", "vaccine prequalification", "who pqp",
    "collaborative registration procedure", "asean joint assessment",
    "regulatory reliance", "reliance pathway",
    "work-sharing", "work sharing",
    "joint regulatory assessment",
    "stringent regulatory authority", "who listed authority",
    "abbreviated registration", "abbreviated review", "abbreviated approval",
    "eu-m4all", "whopar", "good reliance practices", "pq4ai",
    "access consortium", "project orbis", "two-way regulator",
    "market-shaping", "market shaping",
    "sra reliance", "regulatory reliance index", "reliance practice",
    "african medicines agency", "zazibona",
    # ---- 精确且主题相邻的机制词(监管科学语境, 属"依赖/协调机制"外延, 维持聚焦) ----
    "regulatory harmonization", "regulatory harmonisation", "mutual recognition",
    "nra strengthening", "regulatory cooperation",
    # ---- 扩量批(2026-08-26, 经 diag_expand.py 质量核查, 维持聚焦 ≤1500) ----
    # 仅保留最干净、最贴"监管依赖/趋同/加速与附条件审批"谱系的机制词;
    # 已剔除 vaccine introduction / emergency use authorization 等体量过大(+300+)及宽泛噪声词。
    "regulatory convergence",
    "accelerated approval", "accelerated assessment",
    "conditional approval", "conditional marketing authorization", "conditional registration",
]
HP_RE = _re.compile("|".join(_re.escape(t) for t in HP_TERMS), _re.I)

# 领域语境词: 机制词须与"药品/监管/公共卫生"语境同现, 方能判定为离题误检
# (如 "regulatory reliance on animal models"、"abbreviated registration of trial"、
#  "market shaping of charges" 等均因缺药品语境而被剔除)。
CONTEXT_TERMS = [
    "medicine", "medicines", "drug", "drugs", "vaccine", "vaccines",
    "pharmaceutical", "pharmac", "therapeutic", "clinical trial",
    "marketing authorization", "biologic", "biologics", "generic",
    "procurement", "national regulatory", "prequalification",
    "regulatory authority", "medicinal", "public health", "health product",
]
CONTEXT_RE = _re.compile("|".join(_re.escape(t) for t in CONTEXT_TERMS), _re.I)

def is_relevant(r):
    blob = " ".join([r.get("title", ""), r.get("abstract", ""), r.get("keywords", "")]).lower()
    return bool(HP_RE.search(blob)) and bool(CONTEXT_RE.search(blob))

# ---------- 本地 PDF 旁路 .txt 侧车解析(补作者/摘要, 因本地库清单 authors_hint 为空) ----------
LIB_DIRS = {
    "lib1_文献": "D:/D/我的论文/全球卫生新博士课题/文献",
    "lib2_许铭论文": "D:/D/许铭论文",
}
def parse_sidecar(txt_path):
    """从 PDF 同名 .txt 提取 (作者行, 摘要)。失败返回 ('', ')。"""
    try:
        with open(txt_path, encoding="utf-8", errors="ignore") as fh:
            lines = [l.strip() for l in fh if l.strip()]
    except (FileNotFoundError, OSError):
        return "", ""
    # 定位摘要起始行
    abs_idx = None
    for i, l in enumerate(lines):
        if l.startswith("摘要") or l.lower().startswith("abstract"):
            abs_idx = i
            break
    authors = ""
    if abs_idx and abs_idx >= 1:
        cand = lines[abs_idx - 1]
        cand = re.sub(r"[（(][^）)]*[）)]", "", cand).strip(" ,;*")
        # 像作者行: 含逗号分隔的中文名, 或英文 "名 姓," 模式
        if (re.search(r"[，,].*[一-龥A-Za-z]", cand)
                or re.match(r"([A-Z][a-z]+ [A-Z][a-z]+[,，])", cand)):
            authors = cand
    abstract = ""
    if abs_idx is not None:
        end = len(lines)
        for j in range(abs_idx + 1, len(lines)):
            if lines[j].startswith("关键词") or lines[j].lower().startswith("keywords"):
                end = j
                break
        abstract = " ".join(lines[abs_idx + 1:end])
        abstract = re.sub(r"^(摘要|Abstract)[：: ]*", "", abstract).strip()
    return authors, abstract

# ---------- 1. 本地库纳入篇 (include + 用户裁定纳入的 review) ----------
def _nkey(s):
    return s.lower().replace("_", " ").replace("-", " ").strip()

local_rows = []
with open(os.path.join(RAW, "local_library_full.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        base = r["filename"][:-4]
        if base in MANUAL_EXCLUDE_LOCAL:
            continue
        keep = (r["decision"] == "include")
        if not keep and r["decision"] == "review":
            bk = _nkey(base)
            if any(_nkey(m) in bk or bk in _nkey(m) for m in MANUAL_INCLUDE_REVIEW):
                keep = True
        if not keep:
            continue
        # 尝试从 PDF 同名 .txt 侧车补作者/摘要(本地库清单 authors_hint 为空)
        base = r["filename"][:-4]
        sidecar = os.path.join(LIB_DIRS.get(r["source_dir"], ""), base + ".txt")
        au, ab = parse_sidecar(sidecar)
        local_rows.append({
            "title": r["title"], "year": r["year"],
            "authors": au or (r["authors_hint"] or ""),
            "journal": "", "doi": r["doi"], "pmid": "",
            "source": "local", "source_detail": r["source_dir"], "abstract": ab,
            "keywords": "", "citations": "", "norm": norm_title(r["title"]),
        })

# ---------- 2. PubMed ----------
ns = ""  # PubMed XML 无命名空间
tree = ET.parse(os.path.join(RAW, "pubmed_raw.xml"))
root = tree.getroot()
pub_rows = []
for art in root.iter("PubmedArticle"):
    def txt(tag):
        e = art.find(f".//{tag}")
        return e.text if e is not None else ""
    pmid = txt("PMID")
    title = txt("ArticleTitle")
    if not title:
        continue
    # 作者
    authors = []
    for a in art.iter("Author"):
        ln = a.findtext("LastName") or ""
        fn = a.findtext("ForeName") or ""
        cn = a.findtext("CollectiveName") or ""
        if cn:
            authors.append(cn)
        elif ln or fn:
            authors.append((fn + " " + ln).strip())
    authors = [x for x in authors if x][:20]
    # 期刊
    journal = txt("Title")
    # DOI
    doi = ""
    for el in art.iter("ELocationID"):
        if el.get("EIdType") == "doi":
            doi = el.text or ""
    if not doi:
        for el in art.iter("ArticleId"):
            if el.get("IdType") == "doi":
                doi = el.text or ""
    # 年份
    year = ""
    for tag in ("DateCompleted", "DateRevised", "PubDate"):
        e = art.find(f".//{tag}/Year")
        if e is not None and e.text:
            year = e.text; break
    if not year:
        e = art.find(".//PubDate/Year")
        if e is not None:
            year = e.text
    # 摘要
    abs_parts = [a.text or "" for a in art.iter("AbstractText")]
    abstract = " ".join(abs_parts)
    # 作者关键词(DE 字段, 共现分析核心)
    kw_set = []
    for kl in art.iter("KeywordList"):
        for kw in kl.iter("Keyword"):
            if kw.text and kw.text.strip():
                kw_set.append(kw.text.strip())
    keywords = "; ".join(dict.fromkeys(kw_set))  # 保序去重
    pub_rows.append({
        "title": title, "year": year, "authors": "; ".join(authors),
        "journal": journal, "doi": doi, "pmid": pmid,
        "source": "pubmed", "source_detail": "PubMed/MEDLINE", "abstract": abstract,
        "keywords": keywords, "citations": "", "norm": norm_title(title),
    })

# ---------- 2b. Europe PMC (免费主源替代 OpenAlex; 见 R/01_search_europepmc.R) ----------
epmc_path = os.path.join(RAW, "europepmc_records.csv")
epmc_rows = []
if os.path.exists(epmc_path):
    with open(epmc_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t = (r.get("title") or "").strip()
            if not t:
                continue
            epmc_rows.append({
                "title": t,
                "year": (r.get("year") or "").strip(),
                "authors": (r.get("authors") or "").strip(),
                "journal": (r.get("journal") or "").strip(),
                "doi": (r.get("doi") or "").lower().strip(),
                "pmid": (r.get("pmid") or "").strip(),
                "source": "europepmc", "source_detail": "EuropePMC",
                "abstract": (r.get("abstract") or "").strip(),
                "keywords": (r.get("keywords") or "").strip(),
                "citations": "", "norm": norm_title(t),
            })
    print(f"[EuropePMC] 载入 {len(epmc_rows)} 条")
else:
    print("[EuropePMC] 未找到 europepmc_records.csv (请先跑 fetch_europepmc.py)")

# ---------- 2d. WHO IRIS (免费政策文献, DSpace REST 抓取, 替代 Dimensions policy_documents) ----------
who_path = os.path.join(RAW, "who_iris_raw.json")
who_rows = []
if os.path.exists(who_path):
    with open(who_path, encoding="utf-8") as f:
        for r in json.load(f):
            t = (r.get("title") or "").strip()
            if not t:
                continue
            who_rows.append({
                "title": t, "year": (r.get("year") or "").strip(),
                "authors": (r.get("authors") or "").strip(),
                "journal": (r.get("journal") or "").strip(),
                "doi": (r.get("doi") or "").lower().strip(),
                "pmid": "", "source": "who_iris", "source_detail": "WHO IRIS",
                "abstract": (r.get("abstract") or "").strip(),
                "keywords": (r.get("keywords") or "").strip(),
                "citations": "", "norm": norm_title(t),
            })
    print(f"[WHO IRIS] 载入 {len(who_rows)} 条")
else:
    print("[WHO IRIS] 未找到 who_iris_raw.json (请先跑 fetch_who_iris.py)")

# ---------- 2e. 可及性政策流(增厚 LMIC 用药可及性侧): WHO IRIS 扩展查询 + Europe PMC UNICEF/WHO ----------
# 这些文档不要求命中监管依赖机制词, 但须经 ACCESS_POLICY_RE 宽松过滤(明确在"用药可及性/LMIC"主题),
# 并强制标记 access_lens=1。机制核心(1455)保持不变, 仅叠加此流以平衡研究问题两半。
_exc = set(norm_title(t) for t in MANUAL_EXCLUDE_TITLES)
policy_rows = []
for _pf, _src, _det in [
    (os.path.join(RAW, "who_iris_policy_raw.json"), "who_iris_policy", "WHO IRIS (access)"),
    (os.path.join(RAW, "epmc_policy_raw.json"), "epmc_policy", "EuropePMC (UNICEF/WHO)"),
]:
    if os.path.exists(_pf):
        with open(_pf, encoding="utf-8") as f:
            for r in json.load(f):
                t = (r.get("title") or "").strip()
                if not t:
                    continue
                blob = " ".join([t, (r.get("abstract") or ""), (r.get("keywords") or "")]).lower()
                if not ACCESS_POLICY_RE.search(blob):
                    continue  # 非可及性主题, 剔除
                if GENRE_EXCLUDE_RE.search(t) or norm_title(t) in _exc:
                    continue
                policy_rows.append({
                    "title": t, "year": (r.get("year") or "").strip(),
                    "authors": (r.get("authors") or "").strip(),
                    "journal": (r.get("journal") or "").strip(),
                    "doi": (r.get("doi") or "").lower().strip(),
                    "pmid": (r.get("pmid") or "").strip(),
                    "source": _src, "source_detail": _det,
                    "abstract": (r.get("abstract") or "").strip(),
                    "keywords": (r.get("keywords") or "").strip(),
                    "citations": "", "norm": norm_title(t),
                    "_access_policy": True,
                })
        print(f"[{_det}] 政策流载入并过滤后: 累计 {len(policy_rows)} 条")
    else:
        print(f"[{_det}] 未找到 {_pf} (请先跑 fetch_policy_sources.py)")

# ---------- 2a/2b 后处理: 主题相关性自动筛选(剔除宽检索离题文献, PRISMA 题摘初筛等价) ----------
pub_before, epmc_before = len(pub_rows), len(epmc_rows)
pub_rows = [r for r in pub_rows if is_relevant(r)]
epmc_rows = [r for r in epmc_rows if is_relevant(r)]
print(f"[筛选] PubMed {pub_before} -> {len(pub_rows)} 保留; EuropePMC {epmc_before} -> {len(epmc_rows)} 保留 (本地库不筛选)")
# 方法裁定排除(离题体裁, 见 MANUAL_EXCLUDE_TITLES / GENRE_EXCLUDE_RE)
_exc = set(norm_title(t) for t in MANUAL_EXCLUDE_TITLES)
pub_rows = [r for r in pub_rows
            if norm_title(r["title"]) not in _exc and not GENRE_EXCLUDE_RE.search(r["title"])]
epmc_rows = [r for r in epmc_rows
             if norm_title(r["title"]) not in _exc and not GENRE_EXCLUDE_RE.search(r["title"])]
# WHO IRIS 同样施加主题筛选 + 体裁排除
who_before = len(who_rows)
who_rows = [r for r in who_rows
            if is_relevant(r)
            and norm_title(r["title"]) not in _exc
            and not GENRE_EXCLUDE_RE.search(r["title"])]
print(f"[筛选] WHO IRIS {who_before} -> {len(who_rows)} 保留")
# 方法裁定排除(离题体裁, 见 MANUAL_EXCLUDE_TITLES / GENRE_EXCLUDE_RE)
_exc = set(norm_title(t) for t in MANUAL_EXCLUDE_TITLES)
pub_rows = [r for r in pub_rows
            if norm_title(r["title"]) not in _exc and not GENRE_EXCLUDE_RE.search(r["title"])]
epmc_rows = [r for r in epmc_rows
             if norm_title(r["title"]) not in _exc and not GENRE_EXCLUDE_RE.search(r["title"])]

# ---------- 2c. OpenAlex: 仅作"引文数查表"(按 DOI 关联), 不并入全文(避免宽 search 引入离题噪声) ----------
# 说明: OpenAlex 宽 search 会把 "regulation/reliance/market-shaping" 等泛词匹配到创业、审计、环境政策等
#       离题文献, 直接并入会污染语料(实测 7546 篇中大量离题)。故改为: 用已抓取的 openalex_raw.json
#       构建 DOI -> cited_by_count 映射, 仅为已有(PubMed/EPMC/本地)文献补全引文数, 语料规模与纯净度不变。
oa_path = os.path.join(RAW, "openalex_citations.json")
OA_CIT = {}
if os.path.exists(oa_path):
    try:
        with open(oa_path, encoding="utf-8") as f:
            OA_CIT = {str(k).lower(): str(v) for k, v in json.load(f).items()}
        print(f"[OpenAlex] 引文查表载入 {len(OA_CIT)} 条 (来自 {oa_path}, 按 DOI 关联引文数)")
    except Exception as e:
        print(f"[OpenAlex] 引文查表载入失败: {e}")
else:
    print("[OpenAlex] 未找到 openalex_citations.json (跳过引文关联)")

# ---------- 3. 合并去重(本地 + PubMed + Europe PMC + WHO IRIS + 可及性政策流) ----------
all_rows = local_rows + pub_rows + epmc_rows + who_rows + policy_rows
seen = {}
merged = []
for r in all_rows:
    key = ("doi", r["doi"].lower()) if r["doi"] else ("norm", r["norm"])
    if key[1] == "":
        key = ("norm", r["norm"])
    if key in seen:
        # 合并来源标记
        prev = merged[seen[key]]
        src = prev["source"]
        if r["source"] not in src.split("|"):
            prev["source"] = src + "|" + r["source"]
        # 补全缺失字段
        for fld in ("authors", "journal", "doi", "pmid", "year", "abstract", "keywords"):
            if not prev[fld] and r[fld]:
                prev[fld] = r[fld]
        continue
    seen[key] = len(merged)
    merged.append(dict(r))

# ---------- 4. 写出 ----------
# 语料内派生可及性/LMIC 标签(基于 title/abstract/keywords)
for r in merged:
    if r.get("_access_policy"):
        r["access_lens"] = 1  # 政策流强制标记可及性侧
    else:
        r["access_lens"] = access_lens(r)
    # 引文数: 若本行尚无且 DOI 命中 OpenAlex 查表, 则补全
    if not (r.get("citations") or "").strip() and r.get("doi"):
        c = OA_CIT.get(r["doi"].lower())
        if c:
            r["citations"] = c

fields = ["title", "year", "authors", "journal", "doi", "pmid", "source", "source_detail", "abstract", "keywords", "access_lens", "citations", "norm"]
with open(os.path.join(PROC, "paperA_corpus.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in merged:
        w.writerow({k: r.get(k, "") for k in fields})

# ---------- 5. 早期画像 ----------
from collections import Counter
years = Counter()
authors = Counter()
journals = Counter()
keywords = Counter()
src = Counter()
for r in merged:
    if r["year"]:
        years[r["year"]] += 1
    for a in re.split(r"[;,]|\band\b", r["authors"]):
        a = a.strip()
        if len(a) > 1 and a.lower() not in ("et al", "et al."):
            authors[a] += 1
    if r["journal"]:
        journals[r["journal"]] += 1
    for k in re.split(r"[;,]| and ", (r.get("keywords") or "")):
        k = k.strip().lower()
        if len(k) > 2:
            keywords[k] += 1
    src[r["source"]] += 1

profile = {
    "total": len(merged),
    "by_source": dict(src),
    "in_local_flagged": sum(1 for r in merged if "local" in r["source"]),
    "access_lens_count": sum(1 for r in merged if str(r.get("access_lens")) == "1"),
    "year_hist": dict(sorted(years.items())),
    "top_authors": authors.most_common(15),
    "top_journals": journals.most_common(15),
    "top_keywords": keywords.most_common(20),
}
with open(os.path.join(PROC, "early_profile.json"), "w", encoding="utf-8") as f:
    json.dump(profile, f, ensure_ascii=False, indent=2)

print(f"合并去重后语料总数: {len(merged)}")
print("来源分布:", dict(src))
print("可及性/LMIC 透镜命中:", sum(1 for r in merged if str(r.get("access_lens")) == "1"))
print("\n年度分布(前20):")
for y, c in list(sorted(years.items()))[:20]:
    print(f"  {y}: {c}")
print("\nTop 作者:")
for a, c in authors.most_common(12):
    print(f"  {a}: {c}")
print("\nTop 期刊:")
for j, c in journals.most_common(12):
    print(f"  {j}: {c}")
