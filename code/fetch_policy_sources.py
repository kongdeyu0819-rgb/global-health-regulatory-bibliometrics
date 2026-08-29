# -*- coding: utf-8 -*-
"""fetch_policy_sources.py —— 增厚"可及性/LMIC 用药"侧的政策文献源(收集阶段, 不去噪不分析)。
目的: 论文A 研究问题另一半是 LMIC 用药可及性, 既有 1455 篇机制核心偏"监管依赖机制",
      现补 WHO/UNICEF/GAP-f 政策源以平衡。
源:
  - WHO IRIS (DSpace7 REST, 免费免登录): 可及性/LMIC 主题查询 -> data/raw/who_iris_policy_raw.json
        (GAP-f 由 WHO 托管, 其出版物被 IRIS 收录, 故一并覆盖)
  - Europe PMC (免费免登录): UNICEF/WHO 作者/机构政策文档 -> data/raw/epmc_policy_raw.json (best-effort, 带重试)
过滤: 本脚本只收集原始候选; 最终在 build_corpus.py 用 ACCESS_POLICY_TERMS 宽松过滤(不要求机制词)。
增量落盘 + 断点续跑(防沙箱后台进程被杀)。
"""
import json, time, sys, os, urllib.parse, urllib.request

RAW = "data/raw"
os.makedirs(RAW, exist_ok=True)
OUT_IRIS = os.path.join(RAW, "who_iris_policy_raw.json")
OUT_EPMC = os.path.join(RAW, "epmc_policy_raw.json")

# ---- WHO IRIS 可及性/LMIC 主题查询(均直接面向"用药可及性", 非机制词) ----
IRIS_ACCESS = [
    "access to medicines",
    "essential medicines",
    "medicine procurement",
    "local production pharmaceuticals",
    "medicine pricing",
    "paediatric formulations",
    "substandard falsified medicines",
    "universal health coverage medicines",
    "regulatory system strengthening",
    "GAP-f",
]
IRIS_SIZE = 50
IRIS_MAXPAGES = 4   # 每词 ≤200 条, 控量

BASE = "https://iris.who.int/server/api/discover/search/objects"

def get_meta(md, key):
    vals = md.get(key) or []
    return [v.get("value", "") for v in vals if isinstance(v, dict)]

def iris_fetch(url, tries=5):
    last = None
    for a in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "paperA_pipeline/1.0 (mailto:author@example.com)"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e
            time.sleep(2 ** a)
    raise RuntimeError(f"IRIS 请求失败: {last}")

def fetch_iris():
    seen = {}
    if os.path.exists(OUT_IRIS):
        try:
            for r in json.load(open(OUT_IRIS, encoding="utf-8")):
                k = r.get("url") or r.get("title", "").lower()
                if k: seen[k] = r
            print(f"  [IRIS 续跑] 载入 {len(seen)} 条")
        except Exception as e:
            print(f"  [IRIS 续跑失败] {e}")
    done = set(r.get("term") for r in seen.values())
    for term in IRIS_ACCESS:
        if term in done:
            continue
        hits = 0
        for page in range(IRIS_MAXPAGES):
            url = f"{BASE}?query={urllib.parse.quote(term)}&size={IRIS_SIZE}&page={page}"
            try:
                d = iris_fetch(url)
            except Exception as e:
                print(f"  [IRIS 词中止] {term!r}: {e}", file=sys.stderr)
                break
            sr = d.get("_embedded", {}).get("searchResult", {})
            objs = sr.get("_embedded", {}).get("objects", [])
            if not objs: break
            for obj in objs:
                io = obj.get("_embedded", {}).get("indexableObject", {})
                md = io.get("metadata") or {}
                if not md: continue
                title = (get_meta(md, "dc.title") or [""])[0].strip()
                if not title: continue
                uri = (get_meta(md, "dc.identifier.uri") or [""])[0].strip()
                key = uri or title.lower()
                if key in seen: continue
                authors = get_meta(md, "dc.contributor.author")
                year = (get_meta(md, "dc.date.issued") or [""])[0].strip()[:4]
                abstract = (get_meta(md, "dc.description.abstract") or get_meta(md, "dc.description") or [""])[0].strip()
                subjects = get_meta(md, "dc.subject") + get_meta(md, "dc.subject.mesh")
                seen[key] = {
                    "id": uri or title, "doi": "", "title": title, "year": year,
                    "authors": "; ".join(authors[:20]), "journal": "WHO IRIS (WHO)",
                    "abstract": abstract, "keywords": "; ".join(subjects[:15]),
                    "citations": "", "type": "policy_document", "term": term, "url": uri,
                    "stream": "access_policy",
                }
                hits += 1
            print(f"  [IRIS {term[:24]:24}] page {page}: +{len(objs)} (累计 {len(seen)})")
            pi = sr.get("page", {})
            if pi.get("number", 0) + 1 >= pi.get("totalPages", 1): break
            time.sleep(0.3)
        json.dump(list(seen.values()), open(OUT_IRIS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"  [IRIS 词落盘] {term!r}: +{hits}")
        time.sleep(0.2)
    recs = list(seen.values())
    json.dump(recs, open(OUT_IRIS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\nWHO IRIS 政策候选: {len(recs)} -> {OUT_IRIS}")

# ---- Europe PMC: UNICEF/WHO 政策文档(best-effort) ----
EPMC_Q = [
    "UNICEF AND (access to medicines OR essential medicines OR medicine procurement OR vaccine procurement)",
    "WHO AND (medicine procurement OR local production pharmaceuticals OR equitable access medicines)",
]
EPMC_SIZE = 50
EPMC_MAXPAGES = 8
EPMC_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

def epmc_fetch(url, tries=6):
    last = None
    for a in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "paperA_pipeline/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e
            time.sleep(min(2 ** a, 30))
    raise RuntimeError(f"EPMC 请求失败: {last}")

def fetch_epmc():
    recs = []
    if os.path.exists(OUT_EPMC):
        try:
            recs = json.load(open(OUT_EPMC, encoding="utf-8"))
            print(f"  [EPMC 续跑] 载入 {len(recs)} 条")
        except Exception:
            recs = []
    seen_keys = set((r.get("doi") or "").lower() or r.get("title", "").lower() for r in recs)
    for q in EPMC_Q:
        for page in range(EPMC_MAXPAGES):
            url = (f"{EPMC_BASE}?query={urllib.parse.quote(q)}"
                   f"&format=json&pageSize={EPMC_SIZE}&cursor={page*EPMC_SIZE}")
            try:
                d = epmc_fetch(url)
            except Exception as e:
                print(f"  [EPMC 查询中止] {q!r}: {e}", file=sys.stderr)
                break
            res = (d.get("resultList") or {}).get("result", [])
            if not res: break
            for it in res:
                title = (it.get("title") or "").strip()
                if not title: continue
                doi = (it.get("doi") or "").lower().strip()
                key = doi or title.lower()
                if key in seen_keys: continue
                ji = it.get("journalInfo") or {}
                kw = []
                for kl in (it.get("keywordList") or {}).get("keyword", []) or []:
                    if isinstance(kl, dict) and kl.get("value"): kw.append(kl["value"])
                recs.append({
                    "id": doi or title, "doi": doi,
                    "title": title, "year": str(it.get("pubYear", "")),
                    "authors": (it.get("authorString") or "").strip(),
                    "journal": (ji.get("journal") or {}).get("title", "") if ji else "",
                    "abstract": (it.get("abstractText") or "").strip(),
                    "keywords": "; ".join(kw), "citations": "",
                    "type": "policy_document", "term": q[:40], "url": "",
                    "stream": "access_policy",
                })
                seen_keys.add(key)
            print(f"  [EPMC {q[:30]:30}] cursor {page}: +{len(res)} (累计 {len(recs)})")
            if len(res) < EPMC_SIZE: break
            time.sleep(0.3)
    json.dump(recs, open(OUT_EPMC, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\nEurope PMC 政策候选: {len(recs)} -> {OUT_EPMC}")

if __name__ == "__main__":
    print("=== WHO IRIS 可及性政策源 ===")
    fetch_iris()
    print("\n=== Europe PMC UNICEF/WHO 政策源(best-effort) ===")
    fetch_epmc()
    print("\n完成。下一步: 在 build_corpus.py 并入并施加 ACCESS_POLICY_TERMS 过滤。")
