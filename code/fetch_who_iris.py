# fetch_who_iris.py —— 抓取 WHO IRIS (免费, 免登录, 无预算) 政策文献
# WHO IRIS 是 DSpace 7 实例, REST 搜索: /server/api/discover/search/objects?query=TERM
# 这是替代 Dimensions "policy_documents" 的免费源(监管依赖/WHO预认证/LMIC可及性核心政策文献)。
# 本脚本仅做"收集文献"阶段: 按机制词抓取原始候选 -> data/raw/who_iris_raw.json, 不去噪不分析。
# 用法:  python fetch_who_iris.py
import json, time, sys, os, urllib.parse, urllib.request

RAW = "data/raw"
os.makedirs(RAW, exist_ok=True)
OUT = os.path.join(RAW, "who_iris_raw.json")
BASE = "https://iris.who.int/server/api/discover/search/objects"

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

SIZE = 50
MAX_PAGES_PER_TERM = 8   # 每词最多 8 页 = 400 条候选上限

def get_meta(md, key):
    vals = md.get(key) or []
    return [v.get("value", "") for v in vals if isinstance(v, dict)]

def fetch_json(url, tries=5):
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
    raise RuntimeError(f"WHO IRIS 请求最终失败: {last}")

def main():
    # 增量落盘 + 断点续跑: 启动即载入已有 who_iris_raw.json, 已抓过的(uri/title)跳过
    seen = {}
    if os.path.exists(OUT):
        try:
            with open(OUT, encoding="utf-8") as f:
                for r in json.load(f):
                    k = r.get("url") or r.get("title", "").lower()
                    if k:
                        seen[k] = r
            print(f"  [续跑] 载入已有 {len(seen)} 条")
        except Exception as e:
            print(f"  [续跑] 载入失败, 从头开始: {e}")
    done_terms = set(r.get("term") for r in seen.values())
    for term in MECH:
        if term in done_terms:
            continue
        term_hits = 0
        for page in range(MAX_PAGES_PER_TERM):
            url = (f"{BASE}?query={urllib.parse.quote(term)}"
                   f"&size={SIZE}&page={page}")
            try:
                d = fetch_json(url)
            except Exception as e:
                print(f"  [词中止] {term!r}: {e}", file=sys.stderr)
                break
            sr = d.get("_embedded", {}).get("searchResult", {})
            objs = sr.get("_embedded", {}).get("objects", [])
            if not objs:
                break
            for obj in objs:
                io = obj.get("_embedded", {}).get("indexableObject", {})
                md = io.get("metadata") or {}
                if not md:
                    continue
                title = (get_meta(md, "dc.title") or [""])[0].strip()
                if not title:
                    continue
                uri = (get_meta(md, "dc.identifier.uri") or [""])[0].strip()
                key = uri or title.lower()
                if key in seen:
                    continue
                authors = get_meta(md, "dc.contributor.author")
                year = (get_meta(md, "dc.date.issued") or [""])[0].strip()[:4]
                abstract = (get_meta(md, "dc.description.abstract") or
                            get_meta(md, "dc.description") or [""])[0].strip()
                subjects = get_meta(md, "dc.subject") + get_meta(md, "dc.subject.mesh")
                seen[key] = {
                    "id": uri or title,
                    "doi": "",
                    "title": title,
                    "year": year,
                    "authors": "; ".join(authors[:20]),
                    "journal": "WHO IRIS (WHO)",
                    "abstract": abstract,
                    "keywords": "; ".join(subjects[:15]),
                    "citations": "",
                    "type": "policy_document",
                    "term": term,
                    "url": uri,
                }
                term_hits += 1
            print(f"  [词 {term[:26]:26}] page {page}: +{len(objs)} (累计 {len(seen)})")
            # 末页判断
            pageinfo = sr.get("page", {})
            if pageinfo.get("number", 0) + 1 >= pageinfo.get("totalPages", 1):
                break
            time.sleep(0.3)
        # 每词结束即落盘(防后台被杀丢进度)
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(list(seen.values()), f, ensure_ascii=False, indent=1)
        print(f"  [词完成落盘] {term!r}: 本词 +{term_hits}")
        time.sleep(0.2)

    recs = list(seen.values())
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False, indent=1)
    print(f"\nWHO IRIS 原始候选: {len(recs)} 篇 -> {OUT}")

if __name__ == "__main__":
    main()
