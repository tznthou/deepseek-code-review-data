#!/usr/bin/env python3
"""v1.4.0 出口的計分與判決（判準見 README「判準」節，跑 API 之前寫定）。$0。

主判準（兩條都成立 → 改回；否則 → 保留）：
  ① S(v131-1) − S(base-1) ≥ 10 則
     S＝有「信心 ≥ 0.7 的 finding × 該 GT」被盲標成 same 的功能性 GT 則數；兩臂用同一批混標的新標籤
  ② min(L(v131-1), L(v131-2)) > max(L(base-1), L(base-2))
     L＝有「信心 ≥ 0.7 的 finding × 該 GT」位置命中（錨點 ±3 行）的功能性 GT 則數；程式算
附記、主 session 抽樣一致率、標記漂移另外印，不影響判決。結果寫進 blind/results.json。
"""
import collections
import csv
import json
import pathlib
import sys

sys.dont_write_bytecode = True
EXIT = pathlib.Path(__file__).resolve().parents[1]
QODO = EXIT.parent / "2026-09-25-qodo-bench"
sys.path.insert(0, str(QODO / "scripts"))
import score_bench  # noqa: E402

B = EXIT / "blind"
VALID = {"same", "partial", "no"}
ROUNDS = ("base-1", "base-2", "v131-1", "v131-2")
NEW, OLD = ("base-1", "base-2"), ("v131-1", "v131-2")
SEV_RANK = {"nit": 0, "minor": 1, "major": 2, "blocker": 3}  # 同 post_review.py


def read_csv(path) -> dict[str, str]:
    with open(path, newline="", encoding="utf-8") as fh:
        return {r["pair"].strip(): r["label"].strip().lower() for r in csv.DictReader(fh)}


def main() -> None:
    mapping = json.loads((B / "mapping.json").read_text(encoding="utf-8"))
    labels, dup = {}, []
    for part in sorted(B.glob("labels-part*.csv")):
        for pid, lab in read_csv(part).items():
            if pid in labels:
                dup.append(pid)
            labels[pid] = lab
    missing = sorted(set(mapping) - set(labels))
    extra = sorted(set(labels) - set(mapping))
    invalid = sorted(p for p, l in labels.items() if l not in VALID)
    print(f"標籤 {len(labels)} / 配對 {len(mapping)}｜缺 {len(missing)}｜多 {len(extra)}｜重複 {len(dup)}｜不合法 {len(invalid)}")
    for run in ("v131-1", "base-1"):
        print(f"  {run} 分佈：", dict(collections.Counter(labels[p] for p, m in mapping.items() if m["run"] == run)))
    if missing or extra or dup or invalid:
        sys.exit(f"[stop] 標籤不完整或不合法（缺 {missing[:10]}、不合法 {invalid[:10]}），補齊再判決")

    evalset = json.loads((QODO / "evalset.json").read_text(encoding="utf-8"))
    func = {e["id"] for e in evalset if e["kind"] == "func"}
    n_func = len(func)

    rounds = {}
    for r in ROUNDS:
        _, by_pr, findings = score_bench.load_round(r)
        prs = {f["pr"] for f in findings}
        rounds[r] = (findings, score_bench.pairs_for(findings, by_pr), prs)
    fdata = {f["fid"]: f for r in ROUNDS for f in rounds[r][0]}

    def inline_like(f: dict) -> bool:  # 仿 post_review.py：嚴重度 ≥ minor、定位得到（不套可留言範圍與前 8 則）
        return SEV_RANK.get(f.get("severity") or "nit", 0) >= 1 and f.get("line") is not None

    def L(r: str, floor: float = 0.7, pred=None) -> set:
        return {p["gid"] for p in rounds[r][1]
                if p["loc_hit"] and p["gid"] in func and fdata[p["fid"]]["confidence"] >= floor
                and (pred is None or pred(fdata[p["fid"]]))}

    def S(r: str, floor: float = 0.7, pred=None) -> set:
        return {m["gid"] for pid, m in mapping.items()
                if m["run"] == r and m["gid"] in func and labels[pid] == "same" and m["conf"] >= floor
                and (pred is None or pred(fdata[m["fid"]]))}

    res = {"n_func": n_func}
    # ── 主判準 ──
    s = {r: S(r) for r in ("base-1", "v131-1")}
    l = {r: L(r) for r in ROUNDS}
    d1 = len(s["v131-1"]) - len(s["base-1"])
    c1 = d1 >= 10
    lo_old, hi_new = min(len(l[r]) for r in OLD), max(len(l[r]) for r in NEW)
    c2 = lo_old > hi_new
    verdict = "改回" if (c1 and c2) else "保留"
    print(f"\n=== 主判準（功能性 GT {n_func} 則；行內那層 = 信心 ≥ 0.7）===")
    print(f"  S：v1.3.1 {len(s['v131-1'])}（{len(s['v131-1']) / n_func:.3f}）｜v1.4.0 {len(s['base-1'])}"
          f"（{len(s['base-1']) / n_func:.3f}）｜差 {d1:+d} 則 → ① {'成立' if c1 else '不成立'}（門檻 +10）")
    print(f"  L：" + "｜".join(f"{r} {len(l[r])}（{len(l[r]) / n_func:.3f}）" for r in ROUNDS))
    print(f"     v1.3.1 最低 {lo_old} vs v1.4.0 最高 {hi_new} → ② {'成立' if c2 else '不成立'}")
    print(f"  判決：{verdict}")
    res["main"] = {"S": {r: len(v) for r, v in s.items()}, "L": {r: len(v) for r, v in l.items()},
                   "d1": d1, "c1": c1, "c2": c2, "verdict": verdict}

    # ── 附記（只記錄）──
    print("\n=== 附記（不影響判決）===")
    s6 = {r: S(r, 0.6) for r in ("base-1", "v131-1")}
    l6 = {r: L(r, 0.6) for r in ROUNDS}
    print(f"  信心 ≥ 0.6：S v1.3.1 {len(s6['v131-1'])}、v1.4.0 {len(s6['base-1'])}｜L "
          + "、".join(f"{r} {len(l6[r])}" for r in ROUNDS))
    si = {r: S(r, 0.7, inline_like) for r in ("base-1", "v131-1")}
    li = {r: L(r, 0.7, inline_like) for r in ROUNDS}
    print(f"  仿 post_review 門檻：S v1.3.1 {len(si['v131-1'])}、v1.4.0 {len(si['base-1'])}｜L "
          + "、".join(f"{r} {len(li[r])}" for r in ROUNDS))

    old_lab = read_csv(QODO / "rounds/base-1/labels.csv")
    b1_pairs = rounds["base-1"][1]
    cover = sum(p["pair"] in old_lab for p in b1_pairs)
    same_all = {p["gid"] for p in b1_pairs if p["gid"] in func and old_lab.get(p["pair"]) == "same"}
    same_ge6 = {p["gid"] for p in b1_pairs if p["gid"] in func and old_lab.get(p["pair"]) == "same"
                and fdata[p["fid"]]["confidence"] >= 0.6}
    print(f"  v1.4.0 低於 0.6 多撈到的（09-25 舊標籤；配對覆蓋 {cover}/{len(b1_pairs)}）：{len(same_all - same_ge6)} 則"
          f"（全部 same {len(same_all)}、≥ 0.6 的 same {len(same_ge6)}）")

    # 未預先登記（README 附記沒有這一項），只為了把總量講完整：v131-1 全部信心的同一問題 vs base-1
    s_all_old = S("v131-1", 0.0)
    print(f"  〔未預先登記〕全部信心層級的同一問題：v1.3.1 {len(s_all_old)}（新標籤）｜v1.4.0 "
          f"{len(s6['base-1'] | (same_all - same_ge6))}（≥ 0.6 用新標籤、< 0.6 用 09-25 舊標籤，兩批混用）")
    print("  每輪 finding 數／信心 ≥ 0.7／高信心未對上（÷ 100 個 PR）：")
    res["notes"] = {"S_ge06": {r: len(v) for r, v in s6.items()}, "L_ge06": {r: len(v) for r, v in l6.items()},
                    "S_inline_like": {r: len(v) for r, v in si.items()},
                    "L_inline_like": {r: len(v) for r, v in li.items()},
                    "v140_below06_extra": len(same_all - same_ge6), "rounds": {}}
    for r in ROUNDS:
        findings, pairs, prs = rounds[r]
        hit_fids = {p["fid"] for p in pairs if p["loc_hit"]}
        hi = [f for f in findings if f["confidence"] >= 0.7]
        unmatched = [f for f in hi if f["fid"] not in hit_fids]
        per_pr = len(unmatched) / 100  # README 定義是 ÷ 100（沒有 finding 的 PR 也算在分母）
        print(f"    {r:<7} finding {len(findings)}｜≥0.7 {len(hi)}｜高信心未對上 {len(unmatched)}（{per_pr:.2f}／PR）"
              f"｜有 finding 的 PR {len(prs)}")
        res["notes"]["rounds"][r] = {"findings": len(findings), "ge07": len(hi), "hi_unmatched": len(unmatched),
                                     "prs": len(prs)}

    # ── 主 session 抽樣 vs 標記員 ──
    spot_path = B / "spot-main.csv"
    if spot_path.exists():
        spot = read_csv(spot_path)
        both = [p for p in spot if p in labels]
        exact = sum(spot[p] == labels[p] for p in both)
        same_agree = sum((spot[p] == "same") == (labels[p] == "same") for p in both)
        print(f"\n主 session 抽樣 vs 標記員：三類一致 {exact}/{len(both)}｜same 與否一致 {same_agree}/{len(both)}")
        for p in both:
            if spot[p] != labels[p]:
                print(f"  分歧 {p}：主 session {spot[p]}、標記員 {labels[p]}（{mapping[p]['run']}）")
        res["spot"] = {"n": len(both), "exact": exact, "same_agree": same_agree}
    else:
        print("\n[注意] 沒有 spot-main.csv（主 session 抽樣沒做）")

    # ── 漂移：base-1 新標籤 vs 09-25 舊標籤 ──
    pairs = [(p, m["qodo_pair"]) for p, m in mapping.items() if m["run"] == "base-1" and m["qodo_pair"] in old_lab]
    ex = sum(labels[p] == old_lab[q] for p, q in pairs)
    sa = sum((labels[p] == "same") == (old_lab[q] == "same") for p, q in pairs)
    print(f"漂移（base-1 新 vs 09-25 舊，同一組配對）：三類一致 {ex}/{len(pairs)}｜same 與否一致 {sa}/{len(pairs)}")
    res["drift"] = {"n": len(pairs), "exact": ex, "same_agree": sa}

    (B / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
