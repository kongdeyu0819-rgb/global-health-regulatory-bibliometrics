#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Zenodo 归档上传工具（论文A：监管依赖与中低收入国家药品可及性文献计量学）

用法
----
1) 仅打包、不上传（检查归档内容）：
   python zenodo_deposit.py --dry-run

2) 真实上传并发布（需要 Zenodo Personal Access Token）：
   python zenodo_deposit.py --token <TOKEN>
   或设置环境变量 ZENODO_TOKEN

3) 已在 Zenodo 网页端发布过、只想把 DOI 回填进稿件：
   python zenodo_deposit.py --only-backfill --doi 10.5281/zenodo.XXXXXXX

4) 查询 Zenodo 上是否已有本项目记录（无需令牌）：
   python zenodo_deposit.py --check-existing

说明
----
- 归档包排除 .git / __pycache__ / 中间版本 docx / 超大 TIF，控制在 ~15 MB。
- 元数据来自 github_repo/.zenodo.json。
- 成功后 DOI 写入 zenodo_doi.txt，并自动回填 manuscript/manuscript.md 的
  TODO_DOI 占位符（会同步到 github_repo/manuscript/manuscript.md）。
- 令牌若通过 --token 传入，会缓存到 .workbuddy/zenodo_token（项目私有目录，
  不进 git），下次无需再问用户索取。
"""

import argparse
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(BASE, "github_repo")
MD_SRC = os.path.join(BASE, "manuscript", "manuscript.md")
MD_REPO = os.path.join(REPO, "manuscript", "manuscript.md")
DOI_FILE = os.path.join(BASE, "zenodo_doi.txt")
TOKEN_FILE = os.path.join(BASE, ".workbuddy", "zenodo_token")
ZIP_PATH = os.path.join(BASE, "build", "global-health-regulatory-bibliometrics.zip")

ZENODO_API = "https://zenodo.org/api/deposit/depositions"

EXCLUDE_DIRS = {".git", "__pycache__", ".ipynb_checkpoints", ".workbuddy"}
EXCLUDE_FILES = {"paper_HPP_new.docx", ".DS_Store"}
EXCLUDE_SUFFIX = {".tif", ".pyc", ".tmp"}


# --------------------------------------------------------------------------
# 归档打包
# --------------------------------------------------------------------------
def build_zip() -> str:
    os.makedirs(os.path.dirname(ZIP_PATH), exist_ok=True)
    n_files = 0
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for root, dirs, files in os.walk(REPO):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for f in sorted(files):
                if f in EXCLUDE_FILES or os.path.splitext(f)[1].lower() in EXCLUDE_SUFFIX:
                    continue
                full = os.path.join(root, f)
                rel = os.path.relpath(full, REPO)
                z.write(full, os.path.join("global-health-regulatory-bibliometrics", rel))
                n_files += 1
    size_mb = os.path.getsize(ZIP_PATH) / 1024 / 1024
    print(f"[zip] {n_files} files -> {ZIP_PATH} ({size_mb:.1f} MB)")
    return ZIP_PATH


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------
def _req(url, method="GET", token=None, data=None, headers=None, raw=None):
    h = {"User-Agent": "paperA-zenodo-deposit/1.0"}
    if token:
        h["Authorization"] = "Bearer " + token
    if headers:
        h.update(headers)
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        h["Content-Type"] = "application/json"
    if raw is not None:
        body = raw
    r = urllib.request.Request(url, data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=180) as resp:
            txt = resp.read().decode("utf-8", "ignore")
            return resp.status, (json.loads(txt) if txt.strip().startswith(("{", "[")) else txt)
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", "ignore")
        try:
            payload = json.loads(txt)
        except Exception:
            payload = txt
        return e.code, payload


def check_existing():
    queries = [
        'creators.person.name:"Kong, Deyu"',
        'creators.person.orcid:"0009-0002-3621-5719"',
        '"regulatory reliance" AND "bibliometric"',
    ]
    for q in queries:
        url = "https://zenodo.org/api/records?size=10&q=" + urllib.parse.quote(q)
        code, d = _req(url)
        if code != 200:
            print(f"[check] {q} -> HTTP {code}")
            continue
        total = d.get("hits", {}).get("total", 0)
        print(f"[check] {q} -> {total} hit(s)")
        for h in d.get("hits", {}).get("hits", [])[:10]:
            md = h.get("metadata", {})
            print("        ", h.get("doi"), "|", md.get("title", "")[:80])


# --------------------------------------------------------------------------
# 上传
# --------------------------------------------------------------------------
def deposit(token, publish=True):
    code, d = _req(ZENODO_API, "POST", token=token, data={})
    if code not in (200, 201):
        print("[deposit] create failed:", code, d)
        return None
    dep_id = d["id"]
    bucket = d["links"]["bucket"]
    print(f"[deposit] created id={dep_id}")

    zip_path = build_zip()
    fname = os.path.basename(zip_path)
    with open(zip_path, "rb") as fh:
        raw = fh.read()
    code2, up = _req(
        f"{bucket}/{fname}", "PUT", token=token, raw=raw,
        headers={"Content-Type": "application/zip"},
    )
    if code2 not in (200, 201):
        print("[deposit] upload failed:", code2, up)
        return None
    print(f"[deposit] uploaded {fname} ({len(raw)/1024/1024:.1f} MB)")

    with open(os.path.join(REPO, ".zenodo.json"), encoding="utf-8") as fh:
        meta = json.load(fh)
    meta["upload_type"] = meta.get("upload_type", "software")
    meta["prereserve_doi"] = True
    code3, m = _req(f"{ZENODO_API}/{dep_id}", "PUT", token=token, data={"metadata": meta})
    if code3 != 200:
        print("[deposit] metadata failed:", code3, m)
        return None
    prereserved = (m.get("metadata") or {}).get("prereserve_doi", {})
    print("[deposit] metadata set; prereserved DOI:", prereserved.get("doi"))

    if not publish:
        print(f"[deposit] NOT published. Edit here: https://zenodo.org/deposit/{dep_id}")
        return prereserved.get("doi")

    code4, p = _req(f"{ZENODO_API}/{dep_id}/actions/publish", "POST", token=token)
    if code4 not in (200, 201, 202):
        print("[deposit] publish failed:", code4, p)
        return None
    doi = p.get("doi")
    print("[deposit] PUBLISHED. DOI:", doi, "|", p.get("links", {}).get("record_html"))
    return doi


# --------------------------------------------------------------------------
# 回填稿件
# --------------------------------------------------------------------------
def backfill(doi: str) -> None:
    with open(DOI_FILE, "w", encoding="utf-8") as fh:
        fh.write(doi + "\n")
    url = f"https://doi.org/{doi}"
    changed = 0
    for path in (MD_SRC, MD_REPO):
        if not os.path.exists(path):
            continue
        t = open(path, encoding="utf-8").read()
        if "TODO_DOI" in t:
            t = t.replace("Zenodo: TODO_DOI", f"Zenodo: {url}")
            t = t.replace("TODO_DOI", url)
            open(path, "w", encoding="utf-8").write(t)
            changed += 1
            print(f"[backfill] {path}: TODO_DOI -> {url}")
        else:
            print(f"[backfill] {path}: no placeholder (already set?)")
    if changed == 0:
        print("[backfill] 没有文件被修改，请检查稿件中的占位符写法")
    print("[backfill] 下一步：重新生成 docx  -> python manuscript/build_docx.py")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", default=os.environ.get("ZENODO_TOKEN", ""))
    ap.add_argument("--dry-run", action="store_true", help="只打包不上传")
    ap.add_argument("--no-publish", action="store_true", help="上传但不发布（先在网页检查）")
    ap.add_argument("--only-backfill", action="store_true")
    ap.add_argument("--doi", default="")
    ap.add_argument("--check-existing", action="store_true")
    args = ap.parse_args()

    if args.check_existing:
        check_existing()
        return

    if args.only_backfill:
        doi = args.doi or (open(DOI_FILE, encoding="utf-8").read().strip() if os.path.exists(DOI_FILE) else "")
        if not doi:
            print("需要 --doi 10.5281/zenodo.XXXXXXX")
            sys.exit(1)
        backfill(doi)
        return

    if args.dry_run:
        build_zip()
        return

    token = args.token
    if not token and os.path.exists(TOKEN_FILE):
        token = open(TOKEN_FILE, encoding="utf-8").read().strip()
    if not token:
        print("缺少 Zenodo 令牌。获取方式：登录 zenodo.org -> 右上角账户名 -> "
              "Applications -> Personal access tokens -> New token，勾选 "
              "deposit:actions 与 deposit:write。")
        sys.exit(2)

    doi = deposit(token, publish=not args.no_publish)
    if not doi:
        sys.exit(3)

    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w", encoding="utf-8") as fh:
        fh.write(token)
    print(f"[token] 已缓存到 {TOKEN_FILE}（项目私有目录，不进 git），下次无需再索取")

    backfill(doi)


if __name__ == "__main__":
    main()
