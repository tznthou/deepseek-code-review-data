#!/usr/bin/env python3
"""rules loop 的評分：全部由程式算，$0。

metric「引用命中」：規則類標準答案之中，有 finding 同時滿足下面兩件事的比例（分母 = 切分內全部規則類標準答案）
  (1) 位置命中：定位後的行號在錨點 ±3 行內（直接用 Qodo score_bench.pairs_for 的 loc_hit）
  (2) 引用對：finding 的 title 標的 [Rxx]（title 沒有才看 body）指到的，正是標準答案違反的那條規則

Guard 用的兩個數也在這裡算：
  func_pos_hit          功能性位置命中
  hi_unmatched_per_pr   信心 ≥0.7、定位得到、卻沒跟任何標準答案位置命中的 finding，每個 PR 平均幾筆
                        （Qodo 只列注入的缺陷，所以這不等於誤報；只拿來擋「靠多報刷分」）

標籤 base-1／base-2 讀 Qodo 既有的 rounds（v00：不附規範）；其他標籤讀本實驗的 rounds。
用法：loop_score.py <標籤>... [--split tune|holdout|all] [--only PR ...] [--json 輸出.json]
"""
import argparse
import collections
import copy
import json
import re
import sys

sys.dont_write_bytecode = True
from common import KIT, LOOP, QODO, gt_rule_names, load_rules, norm_rule, pr_repo, rule_ids, split_prs  # noqa: E402

sys.path.insert(0, str(KIT / ".github/scripts"))
sys.path.insert(0, str(QODO / "scripts"))
import locate  # noqa: E402
import score_bench  # noqa: E402

# 引用的寫法不只一種：2026-09-26 smoke 裡，模型把編號寫在 body、用全形括號「（R03）」，不是 title 開頭的 [R03]。
# metric 量的是「有沒有指出違反哪一條」，括號樣式與位置不是重點，所以都接受；但一定要有括號包住，
# 編號也要存在於該 repo 的規則表（cited_rules 會再過濾）。
CITE_RE = re.compile(r"[\[(（【]\s*R(\d{2})\s*[\])）】]")
V00 = ("base-1", "base-2")
HI_CONF = 0.7


def rounds_dir(label: str):
    return (QODO if label in V00 else LOOP) / "rounds" / label


def load_findings(label: str, prs: list[str]) -> tuple[list[dict], list[str]]:
    findings, missing = [], []
    for pr in prs:
        fj = rounds_dir(label) / f"{pr}.json"
        if not fj.exists():
            missing.append(pr)
            continue
        index = locate.index_diff((QODO / "prs" / pr / "pr.diff").read_text(encoding="utf-8"))
        for k, f in enumerate(json.loads(fj.read_text(encoding="utf-8")), 1):
            g = copy.deepcopy(f)
            resolved, _how = locate.resolve_line(g, index)
            findings.append({"fid": f"{label}:{pr}:{k}", "pr": pr, "path": g.get("path"), "line": resolved,
                             "model_line": f.get("line"), "confidence": float(f.get("confidence", 0)),
                             "title": f.get("title") or "", "body": f.get("body") or "",
                             "existing_code": f.get("existing_code") or ""})
    return findings, missing


def cited_rules(f: dict, idmap: dict[str, str]) -> set[str]:
    ids = CITE_RE.findall(f["title"]) or CITE_RE.findall(f["body"])
    return {norm_rule(idmap[f"R{i}"]) for i in ids if f"R{i}" in idmap}


def score(label: str, split: str = "tune", only: list[str] | None = None) -> dict:
    prs = [p for p in split_prs(split) if not only or p in only]
    pset = set(prs)
    evalset = [e for e in json.loads((QODO / "evalset.json").read_text(encoding="utf-8")) if e["pr"] in pset]
    by_pr = collections.defaultdict(list)
    for e in evalset:
        by_pr[e["pr"]].append(e)
    findings, missing = load_findings(label, prs)
    pairs = score_bench.pairs_for(findings, by_pr)
    idmaps = {repo: rule_ids(rs) for repo, rs in load_rules().items()}
    gt_rule = gt_rule_names()
    fmap = {f["fid"]: f for f in findings}

    loc_hit, cited_hit, matched = set(), set(), set()
    for p in pairs:
        if not p["loc_hit"]:
            continue
        loc_hit.add(p["gid"])
        matched.add(p["fid"])
        f = fmap[p["fid"]]
        want = gt_rule.get(p["gid"])
        if want and want in cited_rules(f, idmaps.get(pr_repo(f["pr"]), {})):
            cited_hit.add(p["gid"])

    rule = {e["id"] for e in evalset if e["kind"] == "rule"}
    func = {e["id"] for e in evalset if e["kind"] == "func"}
    done = len(prs) - len(missing)
    hi = [f for f in findings if f["confidence"] >= HI_CONF and f["line"] is not None]
    n_cite = sum(bool(CITE_RE.search(f["title"]) or CITE_RE.search(f["body"])) for f in findings)
    n_valid = sum(bool(cited_rules(f, idmaps.get(pr_repo(f["pr"]), {}))) for f in findings)
    return {
        "label": label, "split": split, "prs": len(prs), "missing": missing,
        "rule_items": len(rule), "func_items": len(func),
        "M_cited_hit": len(cited_hit & rule) / len(rule) if rule else 0.0,
        "cited_hit_n": len(cited_hit & rule),
        "rule_pos_hit": len(loc_hit & rule) / len(rule) if rule else 0.0,
        "func_pos_hit": len(loc_hit & func) / len(func) if func else 0.0,
        "findings": len(findings), "findings_per_pr": len(findings) / done if done else 0.0,
        "hi_conf_located": len(hi),
        "hi_unmatched_per_pr": sum(f["fid"] not in matched for f in hi) / done if done else 0.0,
        "cite_rate": n_cite / len(findings) if findings else 0.0,
        "cite_valid_rate": n_valid / n_cite if n_cite else 0.0,
    }


def line(s: dict) -> str:
    return (f"{s['label']:<12} {s['split']:<7} PR {s['prs'] - len(s['missing'])}/{s['prs']}｜"
            f"引用命中 {s['M_cited_hit']:.3f}（{s['cited_hit_n']}/{s['rule_items']}）｜"
            f"規則位置 {s['rule_pos_hit']:.3f}｜功能位置 {s['func_pos_hit']:.3f}｜"
            f"finding/PR {s['findings_per_pr']:.2f}｜高信心未對上/PR {s['hi_unmatched_per_pr']:.2f}｜"
            f"有標編號 {s['cite_rate']:.2f}（有效 {s['cite_valid_rate']:.2f}）")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("labels", nargs="+")
    ap.add_argument("--split", choices=("tune", "holdout", "all"), default="tune")
    ap.add_argument("--only", nargs="+", default=None)
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    results = [score(l, args.split, args.only) for l in args.labels]
    for s in results:
        print(line(s))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(results, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
