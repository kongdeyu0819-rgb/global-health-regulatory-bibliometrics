# fetch_europepmc.py —— 用 Europe PMC REST 抓取(免费, 免登录, 无 IP 额度墙)
# 复用 fetch_pubmed.py 的拓宽机制词, 逐词以 (ABSTRACT:"t" OR TITLE:"t") 检索, cursor 分页。
# 输出 data/raw/europepmc_records.csv (字段对齐 build_corpus.py: title,year,authors,journal,doi,pmid,abstract,keywords)
# 本脚本仅做"收集文献"阶段, 不去噪不分析。
# 用法:  python fetch_europepmc.py
import csv, json, time, sys, os, urllib.parse, urllib.request

RAW = "data/raw"
os.makedirs(RAW, exist_ok=True)
OUT = os.path.join(RAW, "europepmc_records.csv")
BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

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
    "regulatory cooperation", "regulatory convergence", "joint review", "joint assessment",
    "mutual recognition of", "functional linkage", "SRA reliance", "stringent regulatory",
    "conditional approval", "emergency use authorization", "vaccine introduction",
    "medicine registration", "medicines registration", "marketing authorization",
    "regulatory system strengthening", "reliance practice", "bioequivalence",
    "generic medicine", "generic medicines", "pharmaceutical regulation", "drug regulation",
    "regulatory approval pathway", "expedited programme", "priority review",
    "fast-track approval", "regulatory reliance index", "African Medicines Agency",
    "Zazibona", "medicine authorization", "vaccine authorization", "therapeutic equivalence",
    "pharmaceutical assessment", "regulatory peer review", "regulatory networking",
    "abbreviated new drug application", "waivered approval",
]

PER_PAGE = 100
MAX_PER_TERM = 250   # 每词最多 250 条候选上限
SLEEP = 0.25

def fetch_json(url, tries=5):
    last = None
    for a in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "paperA_pipeline/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e
            wait = 2 ** a
            print(f"    [retry {a}/{tries}] {e} | wait {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"EuropePMC 请求最终失败: {last}")

def main():
    seen = {}   # (doi or pmid or normtitle) -> row
    for term in MECH:
        q = f'(ABSTRACT:"{term}" OR TITLE:"{term}")'
        cursor = "*"
        cnt = 0
        while cnt < MAX_PER_TERM:
            url = (f"{BASE}?query={urllib.parse.quote(q)}"
                   f"&format=json&pageSize={PER_PAGE}&cursorMark={urllib.parse.quote(cursor)}"
                   f"&resultType=core&sort=P_PDATE_D%20desc")
            try:
                d = fetch_json(url)
            except Exception as e:
                print(f"  [词中止] {term!r}: {e}", file=sys.stderr)
                break
            res = d.get("resultList", {}).get("result", [])
            if not res:
                break
            for it in res:
                title = (it.get("title") or "").strip()
                if not title:
                    continue
                doi = (it.get("doi") or "").lower().strip()
                pmid = (it.get("pmid") or "").strip()
                key = doi or pmid or title.lower()
                if key in seen:
                    continue
                authors = it.get("authorString") or ""
                if not authors and "authorList" in it:
                    al = it["authorList"].get("author", [])
                    authors = "; ".join(
                        (a.get("firstName", "") + " " + a.get("lastName", "")).strip()
                        for a in al if a.get("firstName") or a.get("lastName"))
                journal = it.get("journalInfo", {}).get("journal", {}).get("title", "") or ""
                year = ""
                pd = it.get("pubYear") or (it.get("journalInfo", {}).get("yearOfPublication") or "")
                year = str(pd).strip()
                abstract = it.get("abstractText") or ""
                kw = it.get("keywordList", {}).get("keyword", []) or []
                if isinstance(kw, str):
                    kw = [kw]
                keywords = "; ".join(k for k in kw if k)
                seen[key] = {
                    "title": title, "year": year, "authors": authors,
                    "journal": journal, "doi": doi, "pmid": pmid,
                    "abstract": abstract, "keywords": keywords,
                }
                cnt += 1
            nxt = d.get("nextCursorMark")
            if not nxt or nxt == cursor:
                break
            cursor = nxt
            if cnt >= MAX_PER_TERM:
                break
            time.sleep(SLEEP)
        print(f"  [词 {term[:26]:26}] +{cnt} (累计 {len(seen)})")
        time.sleep(SLEEP)

    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["title", "year", "authors", "journal", "doi", "pmid", "abstract", "keywords"])
        w.writeheader()
        for r in seen.values():
            w.writerow(r)
    print(f"\nEuropePMC 原始候选: {len(seen)} 篇 -> {OUT}")

if __name__ == "__main__":
    main()
