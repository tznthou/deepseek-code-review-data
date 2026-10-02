#!/usr/bin/env python3
"""對 workflow 副本做變異，確認 selftest [21] 的 workflow 檢查會叫（不是空轉）。不改工作樹。"""
import importlib.util, pathlib, re, sys

KIT = pathlib.Path("<repo>")
spec = importlib.util.spec_from_file_location("selftest_mod", KIT / "tools/selftest.py")
st = importlib.util.module_from_spec(spec)
spec.loader.exec_module(st)

wf = (KIT / ".github/workflows/reusable-ai-review-post.yml").read_text(encoding="utf-8")
N, R, P = "DeepSeek review（唯一跨越信任邊界的是「資料」）", "DeepSeek review（repo 規範）", "貼回 PR（摘要 + inline comments）"


def verdicts(text):
    n, r, p = st.workflow_step(text, N), st.workflow_step(text, R), st.workflow_step(text, P)
    post_if = next((ln for ln in p.splitlines() if ln.strip().startswith("if:")), "")
    return {
        "found": bool(n and r and p),
        "coe": "continue-on-error: true" in r,
        "limits": "timeout-minutes: 6" in r and "--timeout 120 --retries 1" in r,
        "env": st.step_env_keys(n) <= st.step_env_keys(r) and "REVIEW_BLOCKED_TERMS" in st.step_env_keys(r),
        "post_if": "rules_review" not in post_if,
    }


base = verdicts(wf)
print("原版：", base)
assert all(base.values())

mutants = {
    "拿掉規範那步的 REVIEW_BLOCKED_TERMS": ("env", lambda t: t.replace(
        "          REVIEW_BLOCKED_TERMS: ${{ secrets.REVIEW_BLOCKED_TERMS }}\n          RULES_PATH:",
        "          RULES_PATH:")),
    "拿掉 continue-on-error": ("coe", lambda t: t.replace("        continue-on-error: true\n", "")),
    "拿掉 --retries 1": ("limits", lambda t: t.replace("--timeout 120 --retries 1", "--timeout 120")),
    "貼文那步的 if 依賴規範那步": ("post_if", lambda t: t.replace(
        "      - name: 貼回 PR（摘要 + inline comments）\n        if: steps.pr.outputs.number != ''",
        "      - name: 貼回 PR（摘要 + inline comments）\n        if: steps.pr.outputs.number != '' && steps.rules_review.outcome == 'success'")),
}
bad = 0
for label, (key, mutate) in mutants.items():
    text = mutate(wf)
    if text == wf:
        print(f"SKIP {label}：變異沒有套上（替換字串對不到）")
        bad += 1
        continue
    v = verdicts(text)
    caught = not v[key]
    print(f"{'抓到' if caught else '漏掉'} {label} → {key}={v[key]}")
    bad += not caught
sys.exit(1 if bad else 0)
