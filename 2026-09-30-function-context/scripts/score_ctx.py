#!/usr/bin/env python3
"""函式上下文實驗的計分、混標單與判決（判準見 README「判準」節，跑 API 之前寫定）。$0。

子命令：
  check    計分的正向對照（碰新資料之前）：重現 base-1／base-2 的 L 與 09-25 的配對、S、P／R／F1；
           另印已跑完的新輪次的 L（程式算，不需要標記）
  sheets   混標單：fc-1 與 base-3 的全部候選配對，同一批打亂、編號不透明（blind/，已存在就不覆寫）
  verdict  讀 blind/labels-part*.csv，算 S／P／R／F1 並判決；附記另印；寫 blind/results.json

定位：finding 用「該臂送出去的 diff」建索引重新定位（fc 臂 = fc.diff、基準臂 = Qodo pr.diff）。
GT 錨點（Qodo 的 evalset.json）與候選配對（score_bench.pairs_for）是 09-25 同一份 code。
"""
import argparse
import collections
import copy
import csv
import json
import pathlib
import random
import sys

sys.dont_write_bytecode = True
EXP = pathlib.Path(__file__).resolve().parents[1]
QODO = EXP.parent / "2026-09-25-qodo-bench"
EXIT = EXP.parent / "2026-09-28-v140-exit"
sys.path.insert(0, str(QODO / "scripts"))
sys.path.insert(0, str(EXIT / "scripts"))
import score_bench  # noqa: E402（會再 import kit 的 locate.py）
import make_sheets  # noqa: E402（只借 HEADER 與 block，跟 09-28 同一份標記單格式）

locate = score_bench.locate
BLIND = EXP / "blind"
SEED = 20260930
N_FUNC, N_ALL = 309, 580
VALID = {"same", "partial", "no"}

# 輪次 → (findings 所在目錄, 定位用的 diff)
ROUNDS = {
    "base-1": (QODO / "rounds/base-1", lambda pr: QODO / "prs" / pr / "pr.diff"),
    "base-2": (QODO / "rounds/base-2", lambda pr: QODO / "prs" / pr / "pr.diff"),
    "base-3": (EXP / "arms/base/rounds/base-3", lambda pr: EXP / "arms/base/prs" / pr / "pr.diff"),
    "fc-1": (EXP / "arms/fc/rounds/fc-1", lambda pr: EXP / "arms/fc/prs" / pr / "pr.diff"),
    "fc-2": (EXP / "arms/fc/rounds/fc-2", lambda pr: EXP / "arms/fc/prs" / pr / "pr.diff"),
}
BASE, FC = ("base-1", "base-2", "base-3"), ("fc-1", "fc-2")
LABELED = ("fc-1", "base-3")  # 混標的兩輪


def evalset():
    ev = json.loads((QODO / "evalset.json").read_text(encoding="utf-8"))
    by_pr = collections.defaultdict(list)
    for e in ev:
        by_pr[e["pr"]].append(e)
    return ev, by_pr


def load(label: str, index_of=None):
    """跟 score_bench.load_round 同一套欄位與 fid 格式；差別只在定位用哪份 diff。"""
    rdir, diff_of = ROUNDS[label]
    diff_of = index_of or diff_of
    ev, by_pr = evalset()
    findings = []
    for pr in sorted(by_pr):
        fj = rdir / f"{pr}.json"
        if not fj.exists():
            continue
        index = locate.index_diff(diff_of(pr).read_text(encoding="utf-8"))
        for k, f in enumerate(json.loads(fj.read_text(encoding="utf-8")), 1):
            g = copy.deepcopy(f)
            resolved, how = locate.resolve_line(g, index)
            findings.append({"fid": f"{label}:{pr}:{k}", "pr": pr, "path": g.get("path"),
                             "line": resolved, "model_line": f.get("line"), "how": how,
                             "confidence": float(f.get("confidence", 0)), "severity": f.get("severity"),
                             "title": f.get("title", ""), "body": f.get("body", ""),
                             "existing_code": f.get("existing_code", "")})
    return ev, by_pr, findings


def complete(label: str) -> int:
    man = ROUNDS[label][0] / "manifest.json"
    if not man.exists():
        return 0
    return sum(r.get("exit") == 0 for r in json.loads(man.read_text(encoding="utf-8"))["results"].values())


# ── 指標（分母固定：功能性 309、全部 580、finding 端 = 該輪全部 finding）──
def L(pairs, fmap, kinds, floor=0.0):
    return {p["gid"] for p in pairs if p["loc_hit"] and p["gid"] in kinds and fmap[p["fid"]]["confidence"] >= floor}


def S(pairs, fmap, kinds, lab, floor=0.0):
    return {p["gid"] for p in pairs
            if lab.get(p["pair"]) == "same" and p["gid"] in kinds and fmap[p["fid"]]["confidence"] >= floor}


def prf(pairs, findings, hit) -> dict:
    """hit(pair) → 這組算不算對上。P = 至少對上一則 GT 的 finding ÷ 全部 finding；R = 被對上的 GT ÷ 580。"""
    f_ok = {p["fid"] for p in pairs if hit(p)}
    g_ok = {p["gid"] for p in pairs if hit(p)}
    p = len(f_ok) / len(findings) if findings else 0.0
    r = len(g_ok) / N_ALL
    return {"P": p, "R": r, "F1": 2 * p * r / (p + r) if p + r else 0.0, "f_ok": len(f_ok), "g_ok": len(g_ok),
            "findings": len(findings)}


def cmd_check() -> None:
    ev, _ = evalset()
    func = {e["id"] for e in ev if e["kind"] == "func"}
    assert len(func) == N_FUNC and len(ev) == N_ALL, (len(func), len(ev))
    print("=== 計分的正向對照（09-25／09-28 公開數字）===")
    expect = {"base-1": (177, 151), "base-2": (178, 149)}
    ok = True
    for r, (e_all, e_07) in expect.items():
        _, by_pr, fs = load(r)
        pairs = score_bench.pairs_for(fs, by_pr)
        fmap = {f["fid"]: f for f in fs}
        la, l7 = len(L(pairs, fmap, func)), len(L(pairs, fmap, func, 0.7))
        ok &= (la, l7) == (e_all, e_07)
        print(f"  {r}：L 全部 {la}（預期 {e_all}）｜L ≥0.7 {l7}（預期 {e_07}）")
        if r == "base-1":
            saved = json.loads((QODO / "rounds/base-1/pairs.json").read_text(encoding="utf-8"))
            same_pairs = sorted(json.dumps(p, sort_keys=True) for p in pairs) == \
                sorted(json.dumps(p, sort_keys=True) for p in saved)
            ok &= same_pairs
            print(f"  base-1 配對 {len(pairs)} 組，與 09-25 存檔逐組相同：{same_pairs}")
            with open(QODO / "rounds/base-1/labels.csv", newline="", encoding="utf-8") as fh:
                old = {row["pair"]: row["label"].strip() for row in csv.DictReader(fh)}
            s = len(S(pairs, fmap, func, old))
            m = prf(pairs, fs, lambda p: old.get(p["pair"]) == "same")
            ok &= (s, m["f_ok"], m["g_ok"], m["findings"]) == (137, 160, 166, 347)
            print(f"  base-1（09-25 舊標籤）：S {s}（預期 137）｜P {m['f_ok']}/{m['findings']}（預期 160/347）"
                  f"｜R {m['g_ok']}/580（預期 166）｜F1 {m['F1']:.3f}（預期 ≈ 0.35）")
    print(f"  → {'全部重現' if ok else '✗ 有數字對不上，先查計分程式'}")
    print("\n=== 新輪次（程式算，不需標記）===")
    for r in ("base-3", "fc-1", "fc-2"):
        n = complete(r)
        if not n:
            print(f"  {r}：還沒跑")
            continue
        _, by_pr, fs = load(r)
        pairs = score_bench.pairs_for(fs, by_pr)
        fmap = {f["fid"]: f for f in fs}
        print(f"  {r}：成功 {n}/100｜finding {len(fs)}｜L 全部 {len(L(pairs, fmap, func))}"
              f"｜L ≥0.7 {len(L(pairs, fmap, func, 0.7))}｜候選配對 {len(pairs)}")
    sys.exit(0 if ok else 1)


def cmd_sheets(per_part: int) -> None:
    if BLIND.exists():
        sys.exit(f"[stop] {BLIND} 已存在，不覆寫（標記單產生一次就定了）")
    items = []
    for r in LABELED:
        if complete(r) != 100:
            sys.exit(f"[stop] {r} 只有 {complete(r)}/100 個 PR 成功（README：重跑一次仍失敗才記 0 筆，先處理）")
        ev, by_pr, fs = load(r)
        fmap, emap = {f["fid"]: f for f in fs}, {e["id"]: e for e in ev}
        items += [(r, p, fmap[p["fid"]], emap[p["gid"]]) for p in score_bench.pairs_for(fs, by_pr)]
    random.Random(SEED).shuffle(items)
    BLIND.mkdir()
    mapping, blocks = {}, []
    for i, (r, p, f, e) in enumerate(items, 1):
        pid = f"P{i:04d}"
        mapping[pid] = {"run": r, "pair": p["pair"], "fid": p["fid"], "gid": p["gid"], "kind": e["kind"],
                        "via": p["via"], "dist": p["dist"], "loc_hit": p["loc_hit"], "conf": f["confidence"]}
        blocks.append((pid, make_sheets.block(pid, e, f, p)))
    (BLIND / "mapping.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=1), encoding="utf-8")
    parts = -(-len(blocks) // per_part)
    size = -(-len(blocks) // parts)
    for k in range(parts):
        chunk = blocks[k * size:(k + 1) * size]
        text = make_sheets.HEADER.format(part=k + 1, csv=BLIND / f"labels-part{k + 1}.csv") + "\n".join(b for _, b in chunk)
        (BLIND / f"sheet-part{k + 1}.md").write_text(text, encoding="utf-8")
        print(f"sheet-part{k + 1}.md：{len(chunk)} 組、{len(text.encode()):,} bytes")
    loc = [pid for pid, m in mapping.items() if m["loc_hit"]]
    other = [pid for pid, m in mapping.items() if not m["loc_hit"]]
    spot = sorted(random.Random(SEED + 1).sample(loc, 20) + random.Random(SEED + 2).sample(other, 10))
    bmap = dict(blocks)
    (BLIND / "spot-sheet.md").write_text(
        make_sheets.HEADER.format(part="（主 session 抽樣）", csv=BLIND / "spot-main.csv")
        + "\n".join(bmap[p] for p in spot), encoding="utf-8")
    c = collections.Counter((m["run"], m["kind"]) for m in mapping.values())
    print(f"共 {len(blocks)} 組：{dict(c)}｜主 session 抽樣 30 組（位置命中 20、其他 10）")


def read_csv(path) -> dict[str, str]:
    with open(path, newline="", encoding="utf-8") as fh:
        return {r["pair"].strip(): r["label"].strip().lower() for r in csv.DictReader(fh)}


def cmd_verdict() -> None:
    mapping = json.loads((BLIND / "mapping.json").read_text(encoding="utf-8"))
    labels, dup = {}, []
    for part in sorted(BLIND.glob("labels-part*.csv")):
        for pid, lab in read_csv(part).items():
            dup += [pid] if pid in labels else []
            labels[pid] = lab
    missing = sorted(set(mapping) - set(labels))
    invalid = sorted(p for p, l in labels.items() if l not in VALID)
    extra = sorted(set(labels) - set(mapping))
    print(f"標籤 {len(labels)} / 配對 {len(mapping)}｜缺 {len(missing)}｜多 {len(extra)}｜重複 {len(dup)}｜不合法 {len(invalid)}")
    if missing or invalid or extra or dup:
        sys.exit("[stop] 標籤不完整或不合法，補齊再判決")
    lab = {m["pair"]: labels[pid] for pid, m in mapping.items()}  # score_bench 的配對編號 → 標籤

    ev, _ = evalset()
    func = {e["id"] for e in ev if e["kind"] == "func"}
    rule = {e["id"] for e in ev if e["kind"] == "rule"}
    data = {}
    for r in ROUNDS:
        _, by_pr, fs = load(r)
        data[r] = (fs, score_bench.pairs_for(fs, by_pr), {f["fid"]: f for f in fs})
    res = {}

    # ── 主判準 ──
    s = {r: len(S(data[r][1], data[r][2], func, lab)) for r in LABELED}
    l_ = {r: len(L(data[r][1], data[r][2], func)) for r in ROUNDS}
    m = {r: prf(data[r][1], data[r][0], lambda p: lab.get(p["pair"]) == "same") for r in LABELED}
    d1 = s["fc-1"] - s["base-3"]
    better = d1 >= 10 and min(l_[r] for r in FC) > max(l_[r] for r in BASE)
    worse = d1 <= -10 and max(l_[r] for r in FC) < min(l_[r] for r in BASE)
    verdict = "函式上下文較好" if better else "函式上下文較差" if worse else "分不出來"
    if better and m["fc-1"]["F1"] <= m["base-3"]["F1"]:
        verdict = "recall 換 precision"
    print(f"\n=== 主判準（功能性 GT {N_FUNC} 則，全部信心層級）===")
    print(f"  S：fc-1 {s['fc-1']}（{s['fc-1'] / N_FUNC:.3f}）｜base-3 {s['base-3']}（{s['base-3'] / N_FUNC:.3f}）｜差 {d1:+d}（門檻 ±10）")
    print("  L：" + "｜".join(f"{r} {l_[r]}" for r in ROUNDS))
    print(f"     fc 最低 {min(l_[r] for r in FC)}／最高 {max(l_[r] for r in FC)} vs 基準最低 {min(l_[r] for r in BASE)}"
          f"／最高 {max(l_[r] for r in BASE)}")
    for r in LABELED:
        print(f"  {r}：P {m[r]['f_ok']}/{m[r]['findings']} = {m[r]['P']:.3f}｜R {m[r]['g_ok']}/580 = {m[r]['R']:.3f}"
              f"｜F1 {m[r]['F1']:.3f}")
    print(f"  ΔF1 = {m['fc-1']['F1'] - m['base-3']['F1']:+.3f}（讀法：跟「prompt 改動 2–4 點」比，不當閘門）")
    print(f"  判決：{verdict}")
    res["main"] = {"S": s, "L": l_, "d1": d1, "PRF": m, "verdict": verdict}

    # ── 附記（只記錄）──
    print("\n=== 附記（不影響判決）===")
    notes = {}
    s7 = {r: len(S(data[r][1], data[r][2], func, lab, 0.7)) for r in LABELED}
    l7 = {r: len(L(data[r][1], data[r][2], func, 0.7)) for r in ROUNDS}
    print(f"  信心 ≥ 0.7：S fc-1 {s7['fc-1']}、base-3 {s7['base-3']}｜L " + "、".join(f"{r} {l7[r]}" for r in ROUNDS))
    sr = {r: len(S(data[r][1], data[r][2], rule, lab)) for r in LABELED}
    lr = {r: len(L(data[r][1], data[r][2], rule)) for r in ROUNDS}
    print(f"  規則類 271 則：S fc-1 {sr['fc-1']}、base-3 {sr['base-3']}｜L " + "、".join(f"{r} {lr[r]}" for r in ROUNDS))
    fb = {r["key"] for r in json.loads((EXP / "prs/fc-manifest.json").read_text(encoding="utf-8")) if r["fallback"]}
    func95 = {e["id"] for e in ev if e["kind"] == "func" and e["pr"] not in fb}
    print(f"  排除 5 個 fallback PR（功能性 {len(func95)} 則）：S fc-1 {len(S(data['fc-1'][1], data['fc-1'][2], func95, lab))}"
          f"、base-3 {len(S(data['base-3'][1], data['base-3'][2], func95, lab))}｜L "
          + "、".join(f"{r} {len(L(data[r][1], data[r][2], func95))}" for r in ROUNDS))
    notes.update({"S07": s7, "L07": l7, "S_rule": sr, "L_rule": lr})

    # fc 臂落在擴出來的行（定位後行號不在 Qodo pr.diff 的索引裡）
    for r in FC:
        fs = data[r][0]
        idx = {pr: locate.index_diff((QODO / "prs" / pr / "pr.diff").read_text(encoding="utf-8"))
               for pr in {f["pr"] for f in fs}}
        outside = [f for f in fs if f["line"] is not None and f["line"] not in idx[f["pr"]].get(f["path"], {})]
        same_out = [f for f in outside if any(lab.get(p["pair"]) == "same" for p in data[r][1] if p["fid"] == f["fid"])]
        unloc = sum(f["line"] is None for f in fs)
        print(f"  {r}：finding {len(fs)}｜落在擴出來的行 {len(outside)}（其中標 same {len(same_out) if r == 'fc-1' else '—'}）"
              f"｜定位不到 {unloc}")
        notes[f"outside_{r}"] = {"outside": len(outside), "same": len(same_out), "unlocated": unloc}
        # 另一種定位設計：fc 的 finding 改用 Qodo pr.diff 定位（正式環境 inline 只能掛在 PR diff 的行上）
        _, by_pr, fs_alt = load(r, index_of=lambda pr: QODO / "prs" / pr / "pr.diff")
        pa = score_bench.pairs_for(fs_alt, by_pr)
        print(f"    改用 Qodo diff 定位的 L：{len(L(pa, {f['fid']: f for f in fs_alt}, func))}")

    for r in ROUNDS:
        fs, pairs, _ = data[r]
        loc = prf(pairs, fs, lambda p: p["loc_hit"])
        tok = json.loads((ROUNDS[r][0] / "manifest.json").read_text(encoding="utf-8"))["results"]
        pt = sum(v.get("prompt_tokens") or 0 for v in tok.values())
        print(f"  {r:<7} finding {len(fs)}｜≥0.7 {sum(f['confidence'] >= 0.7 for f in fs)}｜位置命中版 P {loc['P']:.3f}"
              f" R {loc['R']:.3f} F1 {loc['F1']:.3f}｜prompt token {pt:,}")
        notes[f"round_{r}"] = {"findings": len(fs), "loc_prf": loc, "prompt_tokens": pt}

    per_repo = collections.defaultdict(dict)
    for r in ROUNDS:
        for gid in L(data[r][1], data[r][2], func):
            repo = gid.split("#")[0].rsplit("-", 1)[0]
            per_repo[repo][r] = per_repo[repo].get(r, 0) + 1
    print("  各 repo 的 L（只描述）：")
    for repo in sorted(per_repo):
        print(f"    {repo:<12} " + "｜".join(f"{r} {per_repo[repo].get(r, 0)}" for r in ROUNDS))
    notes["per_repo_L"] = per_repo
    res["notes"] = notes

    # ── 主 session 抽樣 vs 標記員 ──
    sp = BLIND / "spot-main.csv"
    if sp.exists():
        spot = read_csv(sp)
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
    (BLIND / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    a = sub.add_parser("sheets")
    a.add_argument("per_part", type=int, nargs="?", default=100)
    sub.add_parser("verdict")
    args = ap.parse_args()
    {"check": cmd_check, "sheets": lambda: cmd_sheets(args.per_part), "verdict": cmd_verdict}[args.cmd]()


if __name__ == "__main__":
    main()
