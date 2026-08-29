# -*- coding: utf-8 -*-
"""OpenAlex 全量抓取(扩展机制同义词, 与 PubMed/Europe PMC 对齐)。
数据源恢复说明: OpenAlex 已变按请求计费($0.001), 但免费日额度约午夜 UTC 重置;
本次探测 HTTP=200, 额度已恢复, 故可抓全量。
产出: data/raw/openalex_raw.json = {"works":[...]} (含 cited_by_count 供引文分析)
注意: OpenAlex `title_and_abstract.search` 过滤字段稀疏(返回近 0), 故用 `search` 参数(全字段检索, 宽口径)。
"""
import subprocess, json, time, sys, os, urllib.parse

RAW = "data/raw"
os.makedirs(RAW, exist_ok=True)
OA = "https://api.openalex.org/works"
MAILTO = "author@example.com"

MECH = [
    "WHO prequalification", "prequalification of medicines", "vaccine prequalification",
    "regulatory reliance", "shared reliance", "reliance pathway", "work-sharing",
    "joint regulatory assessment", "Collaborative Registration Procedure",
    "ASEAN joint assessment", "stringent regulatory authority", "WHO listed authority",
    "National Regulatory Authority", "NRA strengthening", "regulatory harmonization",
    "abbreviated registration", "abbreviated review", "expedited review",
    "market-shaping", "EU-M4all", "Good Reliance Practices", "mutual recognition",
    "Access Consortium", "Project Orbis", "regulatory benchmarking",
]
SEARCH = " OR ".join(MECH)
DATE_FILTER = "from_publication_date:2000-01-01,to_publication_date:2025-12-31"

def curl(url):
    r = subprocess.run(["curl", "-s", "--ssl-no-revoke", "--max-time", "90",
                        "--retry", "4", "--retry-all-errors", "--retry-delay", "2", url],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError(f"curl rc={r.returncode}")
    return r.stdout

def fetch_all():
    works = []
    cursor = "*"
    page = 0
    while True:
        q = (f"{OA}?search={urllib.parse.quote(SEARCH)}&filter={urllib.parse.quote(DATE_FILTER)}"
             f"&per-page=200&cursor={urllib.parse.quote(cursor)}&mailto={MAILTO}")
        d = json.loads(curl(q))
        batch = d.get("results", [])
        if not batch:
            break
        works.extend(batch)
        page += 1
        nxt = d.get("meta", {}).get("next_cursor")
        print(f"  页 {page}: +{len(batch)} (累计 {len(works)}) | next_cursor: {nxt}")
        if not nxt:
            break
        cursor = nxt
        time.sleep(0.25)
    return works

if __name__ == "__main__":
    print("== OpenAlex 全量抓取(扩展机制 OR, 2000-2025) ==")
    works = fetch_all()
    out = os.path.join(RAW, "openalex_raw.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"works": works}, f, ensure_ascii=False)
    print(f"完成: {len(works)} 篇 -> {out}")
