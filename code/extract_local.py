# -*- coding: utf-8 -*-
"""抽取两个本地文献库的 PDF 元数据，并按论文A主题做纳入判定(宽松版)。
策略: 全文本抽取(无txt伴侣则fitz全页, 上限60页/150k字符); 命中任一TOPIC词即纳入,
仅当纯NOISE且无TOPIC时才排除。输出全部判定供用户最终否决。
输出:
  data/raw/local_library_full.csv   所有 PDF + 元数据 + 判定(incl/review/excl) + 理由
  data/raw/local_library_include.csv 判定为 include 的记录(供合并用)
"""
import os, re, csv

DIRS = [
    (r"D:/D/我的论文/全球卫生新博士课题/文献", "lib1_文献"),
    (r"D:/D/许铭论文", "lib2_许铭论文"),
]
OUT_FULL = "data/raw/local_library_full.csv"
OUT_INCL = "data/raw/local_library_include.csv"

# 主题词(命中任一即视为相关候选)
TOPIC = [r"regulatory reliance", r"regulatory harmon", r"prequalif", r"collaborative registration",
       r"work[\-\s]?sharing", r"joint assessment", r"stringent regulatory", r"who listed authority",
       r"marketing authoriz", r"market[\-\s]?shap", r"access consortium", r"reference countr",
       r"mutual recognition", r"good reliance", r"pq4ai", r"eu-m4all", r"whopar", r"two-way regulator",
       r"预认证", r"监管依赖", r"监管协调", r"监管信赖", r"监管", r"上市许可", r"工作分担", r"联合评估",
       r"市场塑造", r"参照国", r"medicine", r"pharmaceutical", r"\bdrug\b", r"vaccine", r"antimalarial",
       r"artemisinin", r"青蒿素", r"抗疟", r"疟疾", r"药品", r"医药", r"疫苗", r"essential medicines",
       r"procurement", r"采购", r"access to medicines", r"可及性", r"出海", r"国际化", r"对外授权",
       r"out-licensing", r"traditional medicine", r"中药", r"biopharma", r"medical product",
       r"health product", r"diagnostic", r"诊断", r"原料药", r"api", r"中国", r"我国", r"许铭",
       r"全球卫生", r"公共产品", r"全球基金", r"非洲", r"东盟", r"\basia\b", r"\bafrica\b", r"china",
       r"brics", r"global health", r"\bwho\b"]
# 纯噪声(仅当无任何TOPIC时才排除)
NOISE = [r"temperature variab", r"\bclimate\b", r"cognitive", r"cardiovascular", r"depress",
         r"sensory", r"asthma", r"weather pattern", r"violent crime", r"macroeconomic burden",
         r"iatrogenic", r"胜任力", r"人才培养", r"公正问题", r"spatiotemporal"]
# 强主题信号: 出现 NOISE 时, 仅当命中以下强信号才保留, 否则判为噪声离题
STRONG = [r"regulatory reliance", r"regulatory harmon", r"prequalif", r"collaborative registration",
       r"work[\-\s]?sharing", r"joint assessment", r"stringent regulatory", r"who listed authority",
       r"marketing authoriz", r"market[\-\s]?shap", r"access consortium", r"reference countr",
       r"mutual recognition", r"good reliance", r"pq4ai", r"eu-m4all", r"whopar", r"two-way regulator",
       r"预认证", r"监管依赖", r"监管协调", r"监管信赖", r"监管", r"上市许可", r"工作分担", r"联合评估",
       r"市场塑造", r"参照国", r"\bmedicine\b", r"pharmaceutical", r"\bvaccine\b", r"antimalarial",
       r"artemisinin", r"青蒿素", r"抗疟", r"疟疾", r"药品", r"医药", r"疫苗", r"essential medicines",
       r"procurement", r"采购", r"access to medicines", r"可及性", r"出海", r"国际化", r"对外授权",
       r"traditional medicine", r"中药", r"biopharma", r"medical product", r"health product",
       r"diagnostic", r"诊断", r"原料药", r"api"]

TOPIC_RE = re.compile("|".join(TOPIC), re.I)
NOISE_RE = re.compile("|".join(NOISE), re.I)
STRONG_RE = re.compile("|".join(STRONG), re.I)
YEAR_RE = re.compile(r"(19|20)\d{2}")
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"'<>]+")

def get_text(pdf_path):
    base = pdf_path[:-4]
    txt = base + ".txt"
    if os.path.exists(txt):
        try:
            with open(txt, encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            pass
    try:
        import fitz
        doc = fitz.open(pdf_path)
        chunks, n = [], min(doc.page_count, 60)
        for i in range(n):
            chunks.append(doc[i].get_text())
        doc.close()
        return "\n".join(chunks)[:150000]
    except Exception as e:
        return ""

def norm_title(t):
    t = (t or "").lower()
    t = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", t)
    return t.strip()

def decide(text, fname):
    blob = text + "\n" + fname
    has_topic = bool(TOPIC_RE.search(blob))
    has_noise = bool(NOISE_RE.search(blob))
    has_strong = bool(STRONG_RE.search(blob))
    if has_noise and not has_strong:
        return "exclude", "含噪声词且无强监管/药品信号"
    if has_topic:
        return "include", "命中主题词"
    return "review", "无明确主题词,需人工确认"

def extract_meta(text, fname):
    year_m = YEAR_RE.search(fname)
    if not year_m:
        year_m = YEAR_RE.search(text[:6000])
    year = year_m.group(0) if year_m else ""
    doi_m = DOI_RE.search(text)
    doi = doi_m.group(0).rstrip(".") if doi_m else ""
    am = re.match(r"([\u4e00-\u9fff]{2,4})\s*(\d{4})", os.path.basename(fname))
    author = am.group(1) if am else ""
    title = os.path.basename(fname)[:-4]
    title = re.sub(r"^[\u4e00-\u9fff]{2,4}\s*\d{4}\s*[_-]?", "", title)
    title = title.replace("_", " ").strip()
    if not title:
        for line in text.splitlines():
            line = line.strip()
            if 10 < len(line) < 200:
                title = line; break
    return year, doi, author, title

rows = []
for dpath, dlabel in DIRS:
    if not os.path.isdir(dpath):
        print("WARN dir missing:", dpath); continue
    for f in sorted(os.listdir(dpath)):
        if not f.lower().endswith(".pdf"):
            continue
        fp = os.path.join(dpath, f)
        try:
            text = get_text(fp)
        except Exception as e:
            text = ""; print("ERR read", f, e)
        year, doi, author, title = extract_meta(text, f)
        dec, reason = decide(text, f)
        rows.append({
            "source_dir": dlabel, "filename": f, "title": title, "year": year,
            "authors_hint": author, "doi": doi, "decision": dec, "reason": reason,
            "norm_title": norm_title(title),
        })

with open(OUT_FULL, "w", encoding="utf-8", newline="") as g:
    w = csv.DictWriter(g, fieldnames=["source_dir","filename","title","year","authors_hint","doi","decision","reason","norm_title"])
    w.writeheader(); w.writerows(rows)

incl = [r for r in rows if r["decision"] == "include"]
rev = [r for r in rows if r["decision"] == "review"]
exc = [r for r in rows if r["decision"] == "exclude"]
with open(OUT_INCL, "w", encoding="utf-8", newline="") as g:
    w = csv.DictWriter(g, fieldnames=["source_dir","filename","title","year","authors_hint","doi","decision","reason","norm_title"])
    w.writeheader(); w.writerows(incl)

print(f"TOTAL PDF={len(rows)}  include={len(incl)}  review={len(rev)}  exclude={len(exc)}")
print("\n===== INCLUDE (纳入) =====")
for r in incl:
    print(f"  [{r['year']}] {r['title'][:82]}")
print("\n===== REVIEW (待你确认) =====")
for r in rev:
    print(f"  [{r['year']}] {r['title'][:82]}")
print("\n===== EXCLUDE (离题, 不纳) =====")
for r in exc:
    print(f"  {r['title'][:72]}")
