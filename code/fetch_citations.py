# -*- coding: utf-8 -*-
"""按本语料 DOI 定向查 OpenAlex 引文数(cited_by_count), 干净无离题污染。
语料 1835 篇有 DOI, 分批(每批 100)用 filter=doi:A|B|C 查询, 得到 {doi: citations}。
产出: data/raw/openalex_citations.json
"""
import subprocess, json, csv, time, os, urllib.parse, re

RAW = "data/raw"
PROC = "data/processed"
MAILTO = "author@example.com"
OA = "https://api.openalex.org/works"

rows = list(csv.DictReader(open(os.path.join(PROC, "paperA_corpus.csv"), encoding="utf-8")))
dois = []
seen = set()
for r in rows:
    d = (r.get("doi") or "").lower().strip()
    if d and d not in seen:
        seen.add(d); dois.append(d)
print("语料含 DOI 数:", len(dois))

def curl(url):
    r = subprocess.run(["curl", "-s", "--ssl-no-revoke", "--max-time", "90",
                        "--retry", "4", "--retry-all-errors", "--retry-delay", "2", url],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError(f"curl rc={r.returncode}")
    return r.stdout

def norm(d):
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", d)

cit = {}
B = 100
for i in range(0, len(dois), B):
    batch = dois[i:i+B]
    vals = "|".join("https://doi.org/" + urllib.parse.quote(d) for d in batch)
    q = f"{OA}?filter=doi:{vals}&per-page={B}&mailto={MAILTO}"
    try:
        d = json.loads(curl(q))
    except Exception as e:
        print(f"  batch {i//B+1} 失败: {e}")
        continue
    for w in d.get("results", []):
        dd = norm((w.get("doi") or "").lower())
        if dd:
            cit[dd] = str(w.get("cited_by_count") or "")
    print(f"  batch {i//B+1}/{ (len(dois)+B-1)//B }: 本批命中 {len(d.get('results',[]))} | 累计查得 {len(cit)}")
    time.sleep(0.3)

out = os.path.join(RAW, "openalex_citations.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(cit, f, ensure_ascii=False)
print(f"完成: {len(cit)} 条引文数 -> {out}")
