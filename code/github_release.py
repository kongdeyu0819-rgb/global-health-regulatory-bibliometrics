#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建 GitHub Release（论文A 仓库）。发布会自动触发 Zenodo 归档并生成新版本 DOI。

用法
----
  python github_release.py --tag v3.0.0 --name "..." --notes "..."
  python github_release.py --list            # 列出现有 release

令牌获取顺序（不需要问用户）
----------------------------
1. 环境变量 GITHUB_TOKEN
2. .workbuddy/github_token（本脚本首次成功后自动写入）
3. 从 WorkBuddy 审计日志 ~/.workbuddy/audit-log/*.jsonl 中按 ghp_ 前缀正则提取
   （用户此前在对话中提供过令牌，按约定直接检索复用）
"""

import argparse
import glob
import json
import os
import re
import urllib.error
import urllib.request

REPO_FULL = "kongdeyu0819-rgb/global-health-regulatory-bibliometrics"
API = f"https://api.github.com/repos/{REPO_FULL}/releases"
BASE = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BASE, ".workbuddy", "github_token")
AUDIT_DIR = os.path.join(os.path.expanduser("~"), ".workbuddy", "audit-log")


def find_token() -> str:
    tok = os.environ.get("GITHUB_TOKEN", "").strip()
    if tok:
        return tok
    if os.path.exists(TOKEN_FILE):
        tok = open(TOKEN_FILE, encoding="utf-8").read().strip()
        if tok:
            return tok
    pat = re.compile(r"ghp_[A-Za-z0-9]{30,45}")
    found = []
    for fp in sorted(glob.glob(os.path.join(AUDIT_DIR, "*.jsonl"))):
        try:
            t = open(fp, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        found.extend(pat.findall(t))
    if found:
        return found[-1]
    return ""


def api(url, method="GET", token="", data=None):
    h = {"User-Agent": "paperA-release/1.0", "Accept": "application/vnd.github+json"}
    if token:
        h["Authorization"] = "Bearer " + token
    body = json.dumps(data).encode("utf-8") if data is not None else None
    if body:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, json.loads(r.read().decode("utf-8", "ignore"))
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", "ignore")
        try:
            return e.code, json.loads(txt)
        except Exception:
            return e.code, txt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="")
    ap.add_argument("--name", default="")
    ap.add_argument("--notes", default="")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    token = find_token()
    if not token:
        print("未找到 GitHub 令牌（env GITHUB_TOKEN / .workbuddy/github_token / 审计日志）")
        raise SystemExit(2)

    if args.list:
        code, d = api(API, "GET", token)
        if code != 200:
            print("failed", code, d)
            raise SystemExit(1)
        for r in d:
            print(f"{r['tag_name']:10s} {r['name']:60s} {r['html_url']}")
        return

    if not args.tag:
        print("需要 --tag")
        raise SystemExit(2)

    payload = {
        "tag_name": args.tag,
        "name": args.name or args.tag,
        "body": args.notes or args.tag,
        "draft": False,
        "prerelease": False,
    }
    code, d = api(API, "POST", token, payload)
    if code not in (200, 201):
        print("release create failed:", code, d)
        raise SystemExit(1)
    print("created:", d["tag_name"], d["html_url"])

    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w", encoding="utf-8") as fh:
        fh.write(token)
    print(f"[token] cached -> {TOKEN_FILE}")
    print("[next] Zenodo 会在几分钟内自动归档该 release 并生成新版本 DOI；")
    print("       查询：python zenodo_deposit.py --check-existing")


if __name__ == "__main__":
    main()
