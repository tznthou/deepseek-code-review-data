#!/usr/bin/env python3
"""2026-10-03 寫公開頁時的獨立重算（不 import 本目錄或 loop 的分析腳本，自己讀標記檔）。

算：兩個標記版本 × 嚴格／寬鬆 precision、只看補跑四輪、各標的、probe 的真缺陷命中、單輪與兩兩合併的嚴格 AUC、
第一批套用殘差檢查之後的數字、抽查推翻的分布。
版本 (i)＝跑前定稿的流程（labels-manual 裡被殘差檢查改過的那 20 筆不套）；(ii)＝全部套用。
"""
import csv
import itertools
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent.parent
ROUNDS = HERE.parent / "2026-09-24-confidence-loop" / "rounds"
ARMS = {"A": [f"ph-A{i}" for i in range(1, 5)], "B": [f"ph-B{i}" for i in range(1, 5)]}
b3_map = json.loads((HERE / "blind3" / "blind-map.json").read_text(encoding="utf-8"))
changed_ids = {b3_map[r["code"]] for r in csv.DictReader((HERE / "blind3" / "blind-labels.csv").open(encoding="utf-8"))}


def load(version):
    rows = []  # (arm, round, target, run, conf, label, item)
    for arm, labs in ARMS.items():
        for lab in labs:
            d = ROUNDS / lab
            key = json.loads((d / "key.json").read_text(encoding="utf-8"))
            lab_of = {r["id"]: (r["label"], r["item"]) for r in csv.DictReader((d / "labels-auto.csv").open(encoding="utf-8"))}
            for r in csv.DictReader((d / "labels-manual.csv").open(encoding="utf-8")):
                if version == "i" and r["id"] in changed_ids:
                    continue
                lab_of[r["id"]] = (r["label"], r["item"])
            for fid, meta in key.items():
                _, target, run, _ = fid.split(":")
                label, item = lab_of[fid]
                rows.append((arm, lab, target, int(run), meta["confidence"], label, item))
    return rows


def prec(rows, lenient=False):
    ok = {"valid", "disputed"} if lenient else {"valid"}
    return 100 * sum(1 for r in rows if r[5] in ok) / len(rows)


def auc(rows):
    pos = [r[4] for r in rows if r[5] == "valid"]
    neg = [r[4] for r in rows if r[5] != "valid"]
    s = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return s / (len(pos) * len(neg))


for v in ("i", "ii"):
    R = load(v)
    A = [r for r in R if r[0] == "A"]
    B = [r for r in R if r[0] == "B"]
    cnt = lambda rows, lb: sum(1 for r in rows if r[5] == lb)
    print(f"== 版本 ({v})")
    print(f"  嚴格 A {cnt(A,'valid')}/{len(A)}={prec(A):.2f}  B {cnt(B,'valid')}/{len(B)}={prec(B):.2f}  差 {prec(B)-prec(A):+.2f}")
    print(f"  寬鬆 A {prec(A,True):.2f}  B {prec(B,True):.2f}  差 {prec(B,True)-prec(A,True):+.2f}")
    print(f"  有爭議 A {cnt(A,'disputed')}  B {cnt(B,'disputed')}｜不成立 A {cnt(A,'invalid')} ({100*cnt(A,'invalid')/len(A):.1f}%)  B {cnt(B,'invalid')} ({100*cnt(B,'invalid')/len(B):.1f}%)")
    b1 = lambda rows: [r for r in rows if r[1][-1] in "12"]
    b2 = lambda rows: [r for r in rows if r[1][-1] in "34"]
    print(f"  第一批 A {prec(b1(A)):.1f} B {prec(b1(B)):.1f}｜補跑 A {prec(b2(A)):.1f} B {prec(b2(B)):.1f} 差 {prec(b2(B))-prec(b2(A)):+.2f}")
    print(f"  第一批 AUC A {auc(b1(A)):.3f} B {auc(b1(B)):.3f}｜四輪 AUC A {auc(A):.3f} B {auc(B):.3f}")
    for t in ("probe", "python", "shell"):
        ta = [r for r in A if r[2] == t]
        tb = [r for r in B if r[2] == t]
        print(f"  {t:6s} A {cnt(ta,'valid')}/{len(ta)}={prec(ta):.2f}  B {cnt(tb,'valid')}/{len(tb)}={prec(tb):.2f}  差 {prec(tb)-prec(ta):+.2f}")
    # probe 的真缺陷：每次跑抓到幾個（item 以 PR-A 開頭、成立），20 次加總
    for arm, rows in (("A", A), ("B", B)):
        runs = {(r[1], r[3]) for r in rows if r[2] == "probe"}
        hits = {(r[1], r[3], r[6]) for r in rows if r[2] == "probe" and r[5] == "valid" and r[6].startswith("PR-A")}
        per_item = {}
        for _, _, it in hits:
            per_item[it] = per_item.get(it, 0) + 1
        print(f"  probe 真缺陷 {arm}：{len(hits)} 次／{len(runs)} 次跑  {dict(sorted(per_item.items()))}")
    print("  單輪 AUC（嚴格）：" + "  ".join(f"{lab} {auc([r for r in R if r[1]==lab]):.2f}" for lab in ARMS["A"] + ARMS["B"]))
    a12 = [r for r in A if r[1] in ("ph-A1", "ph-A2")]
    a34 = [r for r in A if r[1] in ("ph-A3", "ph-A4")]
    print(f"  A1+A2 {auc(a12):.3f}  A3+A4 {auc(a34):.3f}  差 {auc(a34)-auc(a12):+.3f}")
    # Shell 那個方向相反的項目（SH-B2）：自動標記、沒人工覆蓋的筆數
    sh_b2 = {arm: sum(1 for r in rows if r[6] == "SH-B2" and r[5] == "invalid") for arm, rows in (("A", A), ("B", B))}
    need = next(x for x in range(0, 99) if 100 * (cnt(B, "valid") + x) / len(B) - prec(A) >= -3)
    print(f"  SH-B2 標成陷阱的 A {sh_b2['A']}  B {sh_b2['B']}｜B 組要幾筆改成成立才過 −3pp：{need}")
print("== 殘差檢查改了幾筆：", len(changed_ids), "；其中第一批（輪次 1、2）：",
      sum(1 for i in changed_ids if i.split(":")[0][-1] in "12"))
