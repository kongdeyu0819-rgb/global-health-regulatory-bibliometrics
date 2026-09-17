# -*- coding: utf-8 -*-
"""
audit_manuscript_hpp.py —— 用 HPP 写作 DNA 的同一套指标审计我们的稿件。
指标定义与 distill_step2_style.py / distill_step8_blindtest.py 完全一致，
保证"语料基线"与"稿件实测"可比。
"""
import os, re, sys, statistics as st

MAN = sys.argv[1] if len(sys.argv) > 1 else "manuscript/manuscript.md"

# ---- 基線（25 篇 HPP 论文 / 171,353 词实测） ----
BASE = {
    "em_dash": 2.28,     # 每千词
    "sent_med": 26.0,    # 句中位词数
    "hedge_strong": 1.60,
    "first_I": 0.74,     # 每千词（写作 DNA 要求 0）
    "caption_med": 10.0, # 图注中位词数
    "policy_per_paper": 40,
}

HEDGE = re.compile(r"\b(may|might|could|potential(ly)?|suggest(s|ing|ed)?|likely|possible|possibly|"
                   r"appears?|seems?|relatively|generally|largely|partially|unclear)\b", re.I)
STRONG = re.compile(r"\b(significantly?|key|novel|crucial|first(ly)?|importantly|robust|"
                    r"clearly|demonstrate[sd]?|conclusive(ly)?|undoubtedly|central|twofold)\b", re.I)

# 正文中用于审计的部分：剔除参考文献与代码块
txt = open(MAN, encoding="utf-8").read()
txt = re.sub(r"```.*?```", " ", txt, flags=re.S)
ref_start = txt.find("## References")
body = txt[:ref_start] if ref_start > 0 else txt

words = len(body.split())
sents = [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(\[])", body) if 3 < len(s.split()) < 120]
sent_med = st.median([len(s.split()) for s in sents]) if sents else 0
em = body.count("—") / max(words, 1) * 1000
first_I = len(re.findall(r"\bI\b", body)) / max(words, 1) * 1000
h, s = len(HEDGE.findall(body)), len(STRONG.findall(body))
hs = h / max(s, 1)

# 图注
caps = re.findall(r"\*(Figure\s+\d+\..*?)\[\s*figures/.*?\]\*", txt, flags=re.S)
cap_words = []
for c in caps:
    w = re.sub(r"\[\s*figures/.*", "", c, flags=re.S)
    w = re.sub(r"^Figure\s+\d+\.\s*", "", w).strip()
    cap_words.append((c.split(".")[0], len(w.split()), w.rstrip().endswith(".")))

policy_n = len(re.findall(r"\bpolic(y|ies)\b", body, re.I))
pm = len(re.findall(r"\b(policymaker|policy maker|policy-maker|decision-maker|decision maker)\w*\b",
                    body, re.I))
m = re.search(r"^##\s+\d+\.\s*(.+)$", body, re.M)
first_head = m.group(1).strip() if m else "(未找到编号一级章节)"

def verdict(got, target, tol=0.35, lower=False):
    if lower:
        ok = got <= target * (1 + tol)
    else:
        ok = abs(got - target) <= abs(target) * tol
    return f"{got:.2f}{'' if ok else '  [FAIL]'}", f"{'≤' if lower else ''}{target:.2f}"

rows = [
    ("em dash / 千词", *verdict(em, BASE["em_dash"], lower=True)),
    ("句中位词数", *verdict(sent_med, BASE["sent_med"])),
    ("hedge : strong", *verdict(hs, BASE["hedge_strong"])),
    ("第一人称 I / 千词", *verdict(first_I, 0.0, lower=True)),
    ("policy 词频（全篇）", f"{policy_n}", f"≈{BASE['policy_per_paper']}"),
    ("policymaker/decision-maker", f"{pm}", f"≥1（17/25 篇有）"),
    ("首节标题", first_head, "Background"),
]

print("=" * 68)
print("稿件 × HPP 写作 DNA 审计")
print("=" * 68)
print(f"正文字数（剔除参考文献/代码块）: {words}")
print(f"HEDGE 计数 {h} / STRONG 计数 {s}")
print("-" * 68)
for n, g, t in rows:
    print(f"  {n:<28} 实测 {g:<12} 目标 {t}")
print("-" * 68)
print(f"图注 {len(cap_words)} 条（HPP 中位 {BASE['caption_med']:.0f} 词）:")
for name, w, dot in cap_words:
    flag = "" if w <= 15 else "   <== 过长"
    print(f"    {name:<10} {w:>3} 词 | 句号={dot}{flag}")
print("-" * 68)
print(f"用 'Fig.' 缩写        : {bool(re.search(r'Fig\.\s*\d', body))}")
print(f"含 'Policy implications' 小标题: {bool(re.search(r'^#+.*Policy implications', body, re.M))}")
print(f"含 Background 首节    : {bool(re.search(r'^##\s+(\d+\.\s*)?Background', body, re.M))}")
print(f"含 Limitations        : {bool(re.search(r'imitations', body))}")
print(f"含 Conclusion         : {bool(re.search(r'^##\s+(\d+\.\s*)?Conclusion', body, re.M))}")
print("=" * 68)
