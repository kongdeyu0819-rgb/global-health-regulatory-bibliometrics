# fetch_openalex_works.py —— 全量检索 OpenAlex (免费, 免登录)
# 复用 fetch_pubmed.py 的 35 机制词策略, 在 OpenAlex 上以 title_and_abstract.search 逐词抓取,
# 收集 2000-01-01 ~ 2025-12-31 的 works, 直接带 cited_by_count 引文数, 免去单独引文查表。
# 本脚本仅做"收集文献"阶段: 抓原始候选 -> data/raw/openalex_works.json, 不去噪不分析。
# 用法:  python fetch_openalex_works.py            # 全量抓取
import json, time, sys, os, re, urllib.parse, urllib.request

RAW = "data/raw"
os.makedirs(RAW, exist_ok=True)
OUT = os.path.join(RAW, "openalex_works.json")

MECH = [
    "WHO prequalification", "prequalification of medicines", "vaccine prequalification",
    "WHO PQP", "prequalification", "regulatory reliance", "shared reliance",
    "reliance pathway", "work-sharing", "work sharing", "joint regulatory assessment",
    "Collaborative Registration Procedure", "ASEAN joint assessment",
    "stringent regulatory authority", "WHO listed authority", "National Regulatory Authority",
    "NRA strengthening", "regulatory harmonization", "regulatory harmonisation",
    "abbreviated registration", "abbreviated review", "abbreviated approval",
    "expedited review", "expedited approval", "market-shaping", "market shaping",
    "EU-M4all", "WHOPAR", "Good Reliance Practices", "PQ4AI", "mutual recognition",
    "confidence-building", "Access Consortium", "Project Orbis",
    "regulatory benchmarking", "WHO benchmarking",
]

PER_PAGE = 200
MAX_PAGES_PER_TERM = 4   # 每词最多抓 4 页 = 800 条候选上限, 避免长尾离题无限扩张
BASE = "https://api.openalex.org/works"

def reconstruct_abstract(inv):
    """OpenAlex 摘要为倒排索引, 还原为文本"""
    if not inv:
        return ""
    try:
        max_idx = max(max(pos) for pos in inv.values()) if inv else -1
        words = [""] * (max_idx + 1)
        for w, pos in inv.items():
            for p in pos:
                words[p] = w
        return " ".join(words).strip()
    except Exception:
        return ""

def fetch_url(url, tries=5):
    last = None
    for a in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "paperA_pipeline/1.0 (mailto:author@example.com)"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e
            wait = 2 ** a
            print(f"    [retry {a}/{tries}] {e} | wait {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"OpenAlex 请求最终失败: {last}")

def main():
    seen = {}   # id -> record (去重)
    for term in MECH:
        f = (f"title_and_abstract.search:{urllib.parse.quote(term)},"
             f"from_publication_date:2000-01-01,to_publication_date:2025-12-31")
        for page in range(1, MAX_PAGES_PER_TERM + 1):
            url = (f"{BASE}?filter={f}&per_page={PER_PAGE}&page={page}"
                       f"&select=id,doi,title,abstract_inverted_index,publication_year,"
                       f"authorships,cited_by_count,type,primary_location")
            try:
                d = fetch_url(url)
            except Exception as e:
                print(f"  [词中止] {term!r}: {e}", file=sys.stderr)
                break
            results = d.get("results", [])
            if not results:
                break
            for w in results:
                wid = w.get("id")
                if not wid or wid in seen:
                    continue
                title = (w.get("title") or "").strip()
                if not title:
                    continue
                authors = []
                for a in w.get("authorships", []) or []:
                    nm = a.get("author", {}).get("display_name")
                    if nm:
                        authors.append(nm)
                venue = ""
                pl = w.get("primary_location") or {}
                sv = pl.get("source") or {}
                venue = (sv.get("display_name") or "") if isinstance(sv, dict) else ""
                seen[wid] = {
                    "id": wid,
                    "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
                    "title": title,
                    "year": w.get("publication_year") or "",
                    "authors": "; ".join(authors[:20]),
                    "journal": venue,
                    "abstract": reconstruct_abstract(w.get("abstract_inverted_index")),
                    "citations": w.get("cited_by_count") or 0,
                    "type": w.get("type") or "",
                    "term": term,
                }
            meta = d.get("meta", {})
            print(f"  [词 {term[:28]:28}] page {page}: +{len(results)} (累计 {len(seen)}) meta_count={meta.get('count')}")
            if len(results) < PER_PAGE:
                break
            time.sleep(0.3)   # 礼貌限速
        time.sleep(0.2)

    recs = list(seen.values())
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False, indent=1)
    print(f"\nOpenAlex 原始候选: {len(recs)} 篇 -> {OUT}")

if __name__ == "__main__":
    main()
