#!/usr/bin/env python3
"""算出報告要用的數字（values.json），全部從資料重算，不手填。

依賴：rounds/base-1/labels.csv（4 份標記合併）、spot-main.csv、兩輪的 manifest。
用法：make_values.py <輸出 values.json>
"""
import collections
import csv
import json
import pathlib
import statistics
import subprocess
import sys

EXP = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXP / "scripts"))
from score_bench import load_round  # noqa: E402

R1 = EXP / "rounds/base-1"


def read_labels(path: pathlib.Path) -> dict[str, str]:
    with open(path, newline="", encoding="utf-8") as fh:
        return {row["pair"]: row["label"].strip() for row in csv.DictReader(fh)}


def recall_table(label: str, lab: dict[str, str]):
    evalset, _, _ = load_round(label)
    pairs = json.loads((EXP / "rounds" / label / "pairs.json").read_text(encoding="utf-8"))
    loc, same, part = set(), set(), set()
    for p in pairs:
        if p["loc_hit"]:
            loc.add(p["gid"])
        if lab.get(p["pair"]) == "same":
            same.add(p["gid"])
        if lab.get(p["pair"]) in ("same", "partial"):
            part.add(p["gid"])
    rows = {}
    for kind in ("func", "rule"):
        for scope in ("all", "reach"):
            ids = [e["id"] for e in evalset if e["kind"] == kind and (scope == "all" or e["reachable"])]
            rows[(kind, scope)] = (len(ids), len(loc & set(ids)) / len(ids), len(same & set(ids)) / len(ids),
                                   len(part & set(ids)) / len(ids), len((loc - same) & set(ids)))
    return rows


def cost(label: str) -> float:
    m = json.loads((EXP / "rounds" / label / "manifest.json").read_text(encoding="utf-8"))
    tin = sum(r["prompt_tokens"] or 0 for r in m["results"].values())
    hit = sum(r["cache_hit"] or 0 for r in m["results"].values())
    out = sum(r["completion_tokens"] or 0 for r in m["results"].values())
    return ((tin - hit) * 0.66 + hit * 0.022 + out * 1.98) / 1e6


def main() -> None:
    lab = read_labels(R1 / "labels.csv")
    pairs = json.loads((R1 / "pairs.json").read_text(encoding="utf-8"))
    missing = [p["pair"] for p in pairs if p["pair"] not in lab]
    if missing:
        sys.exit(f"labels.csv 缺 {len(missing)} 組，例如 {missing[:3]}")
    t1 = recall_table("base-1", lab)
    loc2 = recall_table("base-2", {})[("func", "all")][1]

    spot = read_labels(R1 / "spot-main.csv")
    agree = sum(spot[k] == lab[k] for k in spot)
    agree_same = sum((spot[k] == "same") == (lab[k] == "same") for k in spot)

    rel = subprocess.run([sys.executable, str(EXP / "scripts/reliability.py"), "base-1", "base-2"],
                         capture_output=True, text=True, check=True).stdout
    relj = json.loads(rel.split("JSON ", 1)[1])

    names = {("func", "all"): "功能性缺陷（全部）", ("func", "reach"): "功能性缺陷（diff 內定得到錨點）",
             ("rule", "all"): "違反 repo 規則（全部，未給規則）", ("rule", "reach"): "違反 repo 規則（diff 內定得到錨點）"}
    rows_html = []
    for key, name in names.items():
        n, l, s, p, _ = t1[key]
        em = ' class="rp-row-em"' if key == ("func", "all") else ""
        rows_html.append(
            f'                <tr{em}>\n                  <td>{name}</td>\n'
            f'                  <td class="num">{n}</td>\n                  <td class="num">{l:.1%}</td>\n'
            f'                  <td class="num">{s:.1%}</td>\n                  <td class="num">{p:.1%}</td>\n'
            f'                </tr>')
    values = {
        "Q_RECALL_SAME": f"{t1[('func', 'all')][2]:.0%}",
        "Q_RECALL_LOC": f"{t1[('func', 'all')][1]:.0%}",
        "Q_TABLE_ROWS": "\n".join(rows_html),
        "Q_JACCARD": f"{relj['median']:.2f}",
        "Q_JACCARD_MEAN": f"{relj['mean']:.2f}",
        "Q_JACCARD_IQR": f"{relj['q1']:.2f}–{relj['q3']:.2f}",
        "Q_OVERLAP": f"{relj['overlap_a']:.0%}",
        "Q_COST": f"${cost('base-1') + cost('base-2'):.2f}",
        "Q_NOISE": f"{abs(loc2 - t1[('func', 'all')][1]) * 100:.1f} 個百分點",
        "Q_LOC_NOT_SAME": f"{t1[('func', 'all')][4]} 則",
        "Q_AGREE": f"{agree}/{len(spot)}",
    }
    pathlib.Path(sys.argv[1]).write_text(json.dumps(values, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in values.items():
        if k != "Q_TABLE_ROWS":
            print(f"{k} = {v}")
    print(f"抽查：四類完全一致 {agree}/{len(spot)}；只看 same 與否 {agree_same}/{len(spot)}")
    for k in spot:
        if spot[k] != lab[k]:
            print(f"  不一致 {k}：主 session {spot[k]} ／ 標記員 {lab[k]}")
    print("label 分布：", dict(collections.Counter(lab.values())))


if __name__ == "__main__":
    main()
