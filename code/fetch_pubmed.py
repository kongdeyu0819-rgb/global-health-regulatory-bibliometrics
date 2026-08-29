# fetch_pubmed.py —— 用 curl --ssl-no-revoke 抓取 PubMed (E-utilities)
# 本机环境 NCBI 默认 TLS 握手因证书吊销检查(0x80092013)失败, 加 --ssl-no-revoke 可通。
# 检索式对齐 search_strategy.md 的 PubMed/MEDLINE 段(已对齐开题报告 v0.5.1)。
# 用法:
#   python fetch_pubmed.py            # 全量抓取 -> data/raw/pubmed_raw.xml + pubmed_records.json
import subprocess, json, time, sys, os, re

RAW = "data/raw"
os.makedirs(RAW, exist_ok=True)
NCBI = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOOL = "paperA_pipeline"; EMAIL = "author@example.com"

# 检索式 v5(高精机制术语; 与 R/01_search_europepmc.R 对齐):
#   仅保留能明确指向"监管依赖/WHO 预认证/联合审评/互认"的特定术语, 剔除泛化词
#   (regulatory harmonization / NRA strengthening / market-shaping / expedited / mutual recognition /
#    benchmarking / National Regulatory Authority 等会引入教育、心理、审计等离题文献)。
#   可及性/LMIC 作为语料内分析透镜(见 build_corpus.py 的 access_lens), 非检索硬过滤。
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
    # ---- 拓宽(精确机制短语, 维持聚焦) ----
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
MECH_Q = " OR ".join(f'"{m}"[Title/Abstract]' for m in MECH)
QUERY = (f"({MECH_Q}) AND "
         f'("2000/01/01"[Date - Publication] : "2025/12/31"[Date - Publication])')

def curl_text(url, tries=6):
    last=None
    for a in range(1, tries+1):
        try:
            r = subprocess.run(
                ["curl", "-s", "--ssl-no-revoke", "--max-time", "90",
                 "--retry", "3", "--retry-all-errors", "--retry-delay", "2", url],
                capture_output=True, text=True)
            if r.returncode != 0 or not r.stdout.strip():
                raise RuntimeError(f"curl rc={r.returncode} empty")
            return r.stdout
        except Exception as e:
            last=e; wait=2**a
            print(f"    [retry {a}/{tries}] {e} | wait {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"curl 最终失败: {last}")

def esearch(query, retmax=100000):
    url = (f"{NCBI}/esearch.fcgi?db=pubmed&retmode=json&retmax={retmax}"
           f"&tool={TOOL}&email={EMAIL}&term=" + requests_quote(query))
    d = json.loads(curl_text(url))
    ids = d.get("esearchresult", {}).get("idlist", [])
    return ids

def requests_quote(s):
    # 简易 URL 编码(避免引入额外依赖)
    import urllib.parse
    return urllib.parse.quote(s)

def efetch_chunk(ids):
    """每批 200 个 PMID 取 XML 摘要记录。"""
    out_records = []
    for i in range(0, len(ids), 200):
        batch = ids[i:i+200]
        url = (f"{NCBI}/efetch.fcgi?db=pubmed&retmode=xml&rettype=abstract"
               f"&tool={TOOL}&email={EMAIL}&id=" + ",".join(batch))
        xml = curl_text(url)
        out_records.append(xml)
        time.sleep(0.34)
    return out_records

if __name__ == "__main__":
    pmid_path = os.path.join(RAW, "pubmed_pmids.json")
    print("== esearch ==")
    if os.path.exists(pmid_path) and os.path.getsize(pmid_path) > 2:
        # 续跑: 已有 PMID 列表则跳过 esearch(esearch 为全量, 结果稳定)
        try:
            ids = json.load(open(pmid_path, encoding="utf-8"))
            print(f"  [续跑] 载入已缓存 PMID {len(ids)} 条, 跳过 esearch")
        except Exception:
            ids = esearch(QUERY)
            json.dump(ids, open(pmid_path, "w", encoding="utf-8"))
    else:
        ids = esearch(QUERY)
        json.dump(ids, open(pmid_path, "w", encoding="utf-8"))
    print(f"PubMed 命中: {len(ids)}")
    print("== efetch (分批, 增量落盘) ==")
    xml_path = os.path.join(RAW, "pubmed_raw.xml")
    done = 0
    with open(xml_path, "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0"?>\n<PubmedArticleSet>\n')
        for i in range(0, len(ids), 200):
            batch = ids[i:i+200]
            xml = curl_text(
                f"{NCBI}/efetch.fcgi?db=pubmed&retmode=xml&rettype=abstract"
                f"&tool={TOOL}&email={EMAIL}&id=" + ",".join(batch))
            for m in re.findall(r"<PubmedArticle>.*?</PubmedArticle>", xml, re.S):
                fh.write(m + "\n")
            done += len(batch)
            fh.flush()
            print(f"  efetch {done}/{len(ids)}")
            time.sleep(0.34)
        fh.write("</PubmedArticleSet>\n")
    print(f"已写出 {xml_path} | PMID 数={len(ids)}")
