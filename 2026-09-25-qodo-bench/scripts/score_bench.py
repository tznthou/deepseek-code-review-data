#!/usr/bin/env python3
"""Qodo 評估集評分。兩個子命令：

  candidates <標籤>   產生候選配對與盲標單（rounds/<標籤>/label-sheet.md、pairs.json）
  report <標籤>...    讀 rounds/<標籤>/labels.csv，算 recall 與 finding 端的描述統計

命中分兩層：
  位置命中  finding 定位後的行號落在 GT 錨點 ±3 行內（確定性；「位置準、機制錯」也會算進來 → 上限）
  同一問題  人工盲標：一個改動能同時修掉兩者才算 same（Martian 的判準）；partial = 同處、相關但不是同一個問題

候選配對（要標的）：同檔，且 (a) 定位後的行號在錨點 ±5 行內；或 (b) 定位失敗、模型行號在 ±10 行內；
或 (c) 共用一個有辨識度的識別字且距離 ≤ 40 行（接住「finding 掛呼叫端、GT 掛定義處」）。
"""
import argparse
import collections
import copy
import csv
import json
import pathlib
import re
import sys

EXP = pathlib.Path(__file__).resolve().parents[1]
KIT = EXP.parents[2]
sys.path.insert(0, str(KIT / ".github/scripts"))
import locate  # noqa: E402

IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]{3,}")
STOP = {w.lower() for w in """
this that with from should would could which when where there their other value values false true null none
return returns import export const function class self string number object array list type types data
error errors check checks code line lines file files test tests case cases default using used call calls
called new old missing instead because before after only also into than then while each every some more
""".split()}


def idents(text: str) -> set[str]:
    return {t for t in IDENT.findall(text or "") if t.lower() not in STOP}


def load_round(label: str):
    rdir = EXP / "rounds" / label
    evalset = json.loads((EXP / "evalset.json").read_text(encoding="utf-8"))
    by_pr = collections.defaultdict(list)
    for e in evalset:
        by_pr[e["pr"]].append(e)
    findings = []
    for pr in sorted(by_pr):
        fj = rdir / f"{pr}.json"
        if not fj.exists():
            continue
        index = locate.index_diff((EXP / "prs" / pr / "pr.diff").read_text(encoding="utf-8"))
        for k, f in enumerate(json.loads(fj.read_text(encoding="utf-8")), 1):
            g = copy.deepcopy(f)
            resolved, how = locate.resolve_line(g, index)
            findings.append({"fid": f"{label}:{pr}:{k}", "pr": pr, "path": g.get("path"),
                             "line": resolved, "model_line": f.get("line"), "how": how,
                             "confidence": float(f.get("confidence", 0)), "severity": f.get("severity"),
                             "title": f.get("title", ""), "body": f.get("body", ""),
                             "existing_code": f.get("existing_code", "")})
    return evalset, by_pr, findings


def dist(line: int | None, e: dict) -> int | None:
    if line is None or not isinstance(line, int):
        return None
    return 0 if e["lo"] <= line <= e["hi"] else min(abs(line - e["lo"]), abs(line - e["hi"]))


def pairs_for(findings, by_pr):
    pairs = []
    for f in findings:
        for e in by_pr[f["pr"]]:
            if not e["reachable"] or f["path"] != e["file"]:
                continue
            d = dist(f["line"], e)
            dm = dist(f["model_line"], e) if f["line"] is None else None
            shared = idents(f"{e['title']} {e['snippet']}") & idents(f"{f['title']} {f['body']} {f['existing_code']}")
            via = None
            if d is not None and d <= 5:
                via = "loc"
            elif dm is not None and dm <= 10:
                via = "model_line"
            elif shared and ((d is not None and d <= 40) or (dm is not None and dm <= 40)):
                via = "ident"
            if via:
                pairs.append({"pair": f"{f['fid']}|{e['id']}", "fid": f["fid"], "gid": e["id"], "via": via,
                              "dist": d if d is not None else dm, "loc_hit": d is not None and d <= 3})
    return pairs


def cmd_candidates(label: str) -> None:
    evalset, by_pr, findings = load_round(label)
    pairs = pairs_for(findings, by_pr)
    rdir = EXP / "rounds" / label
    (rdir / "pairs.json").write_text(json.dumps(pairs, ensure_ascii=False, indent=1), encoding="utf-8")
    fmap = {f["fid"]: f for f in findings}
    emap = {e["id"]: e for e in evalset}
    out = ["# 盲標單：finding 跟 GT 是不是同一個問題", "",
           "判準（Martian）：**一個 code change 能同時修掉兩者**才算 `same`；同處、相關但講的是別的問題算 `partial`；否則 `no`。",
           "本單刻意不含 confidence、severity。標在 `labels.csv`：`pair,label,note`。", ""]
    for p in pairs:
        f, e = fmap[p["fid"]], emap[p["gid"]]
        snip = [l.strip() for l in (e["snippet"] or "").splitlines() if l.strip()][:4]
        out += [f"## {p['pair']}", "",
                f"**GT**（{e['kind']}）{e['title']}", "", f"> {e['description']}", "",
                "GT 片段：`" + " ⏎ ".join(snip)[:300] + "`", "",
                f"**finding**（`{f['path']}:{f['line'] or f['model_line']}`，距錨點 {p['dist']} 行，候選管道 {p['via']}）"
                f"{f['title']}", "", f"> {f['body'][:900]}", "",
                "finding 片段：`" + " ⏎ ".join(l.strip() for l in (f['existing_code'] or '').splitlines()[:4])[:300] + "`",
                ""]
    (rdir / "label-sheet.md").write_text("\n".join(out), encoding="utf-8")
    c = collections.Counter(p["via"] for p in pairs)
    print(f"finding {len(findings)}｜候選配對 {len(pairs)}（{dict(c)}）｜位置命中 {sum(p['loc_hit'] for p in pairs)}")
    print(f"定位結果：{dict(collections.Counter(re.sub(r'（.*', '', f['how']) for f in findings))}")


def cmd_report(labels: list[str]) -> None:
    for label in labels:
        evalset, by_pr, findings = load_round(label)
        rdir = EXP / "rounds" / label
        pairs = json.loads((rdir / "pairs.json").read_text(encoding="utf-8"))
        lab = {}
        lp = rdir / "labels.csv"
        if lp.exists():
            with open(lp, newline="", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    lab[row["pair"]] = row["label"].strip()
        unlabeled = [p for p in pairs if p["pair"] not in lab]
        print(f"\n######## {label} ########  finding {len(findings)}｜配對 {len(pairs)}｜未標 {len(unlabeled)}")
        hit_loc = collections.defaultdict(bool)
        hit_same = collections.defaultdict(bool)
        hit_part = collections.defaultdict(bool)
        f_same = collections.defaultdict(bool)
        for p in pairs:
            if p["loc_hit"]:
                hit_loc[p["gid"]] = True
            if lab.get(p["pair"]) == "same":
                hit_same[p["gid"]] = True
                f_same[p["fid"]] = True
            if lab.get(p["pair"]) in ("same", "partial"):
                hit_part[p["gid"]] = True
        for kind in ("func", "rule"):
            for scope in ("全部", "diff 內可定錨"):
                sub = [e for e in evalset if e["kind"] == kind and (scope == "全部" or e["reachable"])]
                n = len(sub)
                print(f"  {kind} {scope:<8} n={n:<4} 位置命中 {sum(hit_loc[e['id']] for e in sub)/n:.3f}"
                      f"｜同一問題 {sum(hit_same[e['id']] for e in sub)/n:.3f}"
                      f"｜含 partial {sum(hit_part[e['id']] for e in sub)/n:.3f}")
        same_f = [f for f in findings if f_same[f["fid"]]]
        other_f = [f for f in findings if not f_same[f["fid"]]]
        print(f"  finding 端：對上 GT（same）{len(same_f)}／其他 {len(other_f)}"
              f"（其他不等於誤報：Qodo 只列注入的缺陷）")
        for name, fs in (("對上 GT", same_f), ("其他", other_f)):
            if fs:
                print(f"    {name}：confidence ≥0.7 佔 {sum(f['confidence'] >= 0.7 for f in fs)/len(fs):.2f}")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("candidates")
    a.add_argument("label")
    b = sub.add_parser("report")
    b.add_argument("labels", nargs="+")
    args = ap.parse_args()
    if args.cmd == "candidates":
        cmd_candidates(args.label)
    else:
        cmd_report(args.labels)


if __name__ == "__main__":
    main()
