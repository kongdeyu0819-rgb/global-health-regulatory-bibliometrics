# fetch_openalex.py —— 用 curl(本环境 TLS 可靠) 全量抓取 OpenAlex
# 逻辑与 R/01_search_openalex.R 一致：单 filter 内 组内'|'OR / 组间逗号 AND
# 健壮性: 小页码(防截断) + 逐页 JSONL 落盘 + 断点续抓 + 失败重试 + 后过滤提升精度
# 用法:
#   python fetch_openalex.py count    # 仅看 abstract 命中数
#   python fetch_openalex.py fetch    # 全量抓取 -> data/raw/openalex_raw.json
#   python fetch_openalex.py resume    # 同 fetch(自动续抓)
import subprocess, json, time, sys, os, re

RAW = "data/raw"
os.makedirs(RAW, exist_ok=True)
MAIL = "author@example.com"
YEAR_FROM, YEAR_TO = "2000-01-01", "2025-12-31"

# Variant G（2026-08-24 广度探针定稿）
reg_terms = ["WHO prequalification", "prequalification", "Collaborative Registration Procedure",
             "ASEAN joint assessment", "regulatory reliance", "work-sharing",
             "stringent regulatory authority", "WHO listed authority", "market-shaping",
             "market shaping", "EU-M4all", "WHOPAR", "two-way regulator",
             "Good Reliance Practices", "PQ4AI"]
acc_terms = ["essential medicines", "medicine procurement", "pharmaceutical procurement", "drug procurement"]

BASE = "https://api.openalex.org/works"

def build_filter(field):
    reg = "|".join(reg_terms)
    acc = "|".join(acc_terms)
    return f"{field}:{reg},{field}:{acc},from_publication_date:{YEAR_FROM},to_publication_date:{YEAR_TO},type:article|review"

def enc(f):
    return f.replace(" ", "%20").replace("|", "%7C")

def curl_json(url, tries=7):
    last_err = None
    for attempt in range(1, tries + 1):
        try:
            r = subprocess.run(
                ["curl", "-s", "--max-time", "60", "--retry", "4", "--retry-all-errors",
                 "--retry-delay", "2", url],
                capture_output=True, text=True)
            out = r.stdout
            if not out.strip():
                raise RuntimeError("empty response")
            return json.loads(out)
        except Exception as e:
            last_err = e
            wait = min(30, 2 ** attempt)
            print(f"    [retry {attempt}/{tries}] {type(e).__name__}: {str(e)[:80]} | 等待 {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"curl_json 最终失败: {last_err} | {url[:100]}")

def count_only(field):
    f = enc(build_filter(field))
    url = f"{BASE}?filter={f}&per_page=1&cursor=*&mailto={MAIL}"
    d = curl_json(url)
    return d.get("meta", {}).get("count", -1)

def fetch_field(field, per_page=25, resume=True):
    """逐页抓取某 field，逐页追加到 JSONL 并写 checkpoint；支持断点续抓。"""
    f = enc(build_filter(field))
    jsonl = os.path.join(RAW, f"_oa_{field}.jsonl")
    cursor_file = os.path.join(RAW, f"_oa_{field}.cursor")
    done = set()
    if resume and os.path.exists(jsonl):
        with open(jsonl, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    w = json.loads(line)
                    k = (w.get("id") or (w.get("doi") or "") or w.get("title") or "")
                    done.add(k)
                except Exception:
                    pass
    start_cursor = "*"
    if resume and os.path.exists(cursor_file):
        with open(cursor_file, "r", encoding="utf-8") as fh:
            start_cursor = fh.read().strip() or "*"
    if start_cursor != "*":
        print(f"  [{field}] 续抓: 已有 {len(done)} 条, 从 cursor={start_cursor[:30]}...", file=sys.stderr)

    cursor = start_cursor
    page = 0
    fetched_this_run = 0
    with open(jsonl, "a", encoding="utf-8") as out:
        while True:
            url = f"{BASE}?filter={f}&per_page={per_page}&cursor={cursor}&mailto={MAIL}"
            d = curl_json(url)
            res = d.get("results", [])
            for w in res:
                k = (w.get("id") or (w.get("doi") or "") or w.get("title") or "")
                if k in done:
                    continue
                done.add(k)
                out.write(json.dumps(w, ensure_ascii=False) + "\n")
                fetched_this_run += 1
            page += 1
            nxt = d.get("meta", {}).get("next_cursor")
            print(f"  [{field}] page {page} +{len(res)} (新{fetched_this_run}) 累计已存{len(done)} next={nxt is not None}", file=sys.stderr)
            if not nxt:
                break
            cursor = nxt
            with open(cursor_file, "w", encoding="utf-8") as cf:
                cf.write(cursor)
            if fetched_this_run > 0 and fetched_this_run % 500 == 0:
                out.flush()
            time.sleep(0.25)
    if os.path.exists(cursor_file):
        os.remove(cursor_file)
    print(f"  [{field}] 完成, 该 field 当前合计 {len(done)} 条", file=sys.stderr)
    return len(done)

def load_jsonl(path):
    rows = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except Exception:
                        pass
    return rows

def reconstruct_abstract(inv):
    if not inv:
        return ""
    pos = []
    for word, idxs in inv.items():
        for i in idxs:
            pos.append((i, word))
    pos.sort()
    return " ".join(w for _, w in pos)

def text_blob(w):
    parts = [w.get("title") or "", w.get("display_name") or ""]
    inv = w.get("abstract_inverted_index")
    if inv:
        parts.append(reconstruct_abstract(inv))
    return " ".join(parts).lower()

def passes_post_filter(w):
    """OpenAlex abstract.search 实际为 token 级匹配，噪声大；后过滤要求至少一个 reg 短语
    与一个 acc 短语作为子串出现在标题/摘要中，确保精度。"""
    blob = text_blob(w)
    reg_hit = any(t.lower() in blob for t in reg_terms)
    acc_hit = any(t.lower() in blob for t in acc_terms)
    return reg_hit and acc_hit

def dedup_key(w):
    doi = (w.get("doi") or "").lower().strip()
    return ("doi", doi) if doi else ("title", (w.get("title") or "").lower().strip())

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "count"
    if mode == "count":
        print("abstract.search 命中:", count_only("abstract.search"))
    elif mode in ("fetch", "resume"):
        fetch_field("abstract.search", per_page=25)
        wa = load_jsonl(os.path.join(RAW, "_oa_abstract.search.jsonl"))
        print(f"\n抓取完成: abstract.search 原始 {len(wa)} 条", file=sys.stderr)
        # 去重 + 后过滤
        seen = {}
        uniq_all = []
        for w in wa:
            k = dedup_key(w)
            if k not in seen:
                seen[k] = True
                uniq_all.append(w)
        filtered = [w for w in uniq_all if passes_post_filter(w)]
        out = {"n_raw": len(wa), "n_dedup": len(uniq_all), "n_filtered": len(filtered),
               "works": filtered}
        with open(os.path.join(RAW, "openalex_raw.json"), "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False)
        print(f"已写出 data/raw/openalex_raw.json | 原始={len(wa)} 去重={len(uniq_all)} 后过滤={len(filtered)}")
    else:
        print("usage: python fetch_openalex.py [count|fetch|resume]")
