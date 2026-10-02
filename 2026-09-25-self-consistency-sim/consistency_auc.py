#!/usr/bin/env python3
"""$0 分析：跨次一致性（self-consistency）當排序訊號，跟模型自評 confidence 比 AUC。

每筆 finding 的一致性 = 同一標的的其他 run 裡，有幾次也報了同一個 item（oracle 分群）。
N=10：用全部 10 次跑的 leave-one-out；N=3：抽 3 次跑，一致性 ∈ {0,1,2}。
另外統計「射程內的組成」：不成立的 finding 裡，有多少屬於「持續性」item（≥50% 的跑都報）。
"""
import random
import sys
from collections import defaultdict

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from vote_sim import load_round  # noqa: E402


def auc(pairs):
    """pairs: [(score, is_pos)]；Mann-Whitney，平手算 0.5。"""
    pos = [s for s, p in pairs if p]
    neg = [s for s, p in pairs if not p]
    if not pos or not neg:
        return float("nan"), len(pos), len(neg)
    win = 0.0
    for a in pos:
        for b in neg:
            win += 1.0 if a > b else 0.5 if a == b else 0.0
    return win / (len(pos) * len(neg)), len(pos), len(neg)


def ok(label, mode):
    return label == "valid" or (mode == "lenient" and label == "disputed")


def analyze(round_labels, n_triplets=400, seed=11):
    rng = random.Random(seed)
    runs = defaultdict(dict)  # target -> run_key -> [findings]
    for lab in round_labels:
        for t, rs in load_round(lab).items():
            for rk, fs in rs.items():
                runs[t][rk] = fs
    print(f"\n######## {' + '.join(round_labels)} ########")

    # ---- N = 全部（leave-one-out）----
    for mode in ("strict", "lenient"):
        rows = []
        for t, rs in runs.items():
            keys = list(rs)
            items_by_run = {rk: {f["item"] for f in fs} for rk, fs in rs.items()}
            for rk, fs in rs.items():
                others = [o for o in keys if o != rk]
                for f in fs:
                    c = sum(1 for o in others if f["item"] in items_by_run[o]) / len(others)
                    rows.append((f["conf"], c, ok(f["label"], mode)))
        a_conf = auc([(r[0], r[2]) for r in rows])
        a_cons = auc([(r[1], r[2]) for r in rows])
        a_prod = auc([(r[0] * r[1], r[2]) for r in rows])
        a_lex = auc([(r[1] * 10 + r[0], r[2]) for r in rows])
        print(f"[N=全部 LOO, {mode}] 成立 {a_conf[1]} / 不成立 {a_conf[2]}")
        print(f"   AUC confidence      {a_conf[0]:.3f}")
        print(f"   AUC 一致性          {a_cons[0]:.3f}")
        print(f"   AUC conf×一致性     {a_prod[0]:.3f}")
        print(f"   AUC 一致性→conf     {a_lex[0]:.3f}")

    # ---- N = 3 ----
    for mode in ("strict", "lenient"):
        rows = []
        for t, rs in runs.items():
            keys = list(rs)
            for _ in range(n_triplets):
                trip = rng.sample(keys, 3)
                items_by_run = {rk: {f["item"] for f in rs[rk]} for rk in trip}
                for rk in trip:
                    for f in rs[rk]:
                        c = sum(1 for o in trip if o != rk and f["item"] in items_by_run[o])
                        rows.append((f["conf"], c, ok(f["label"], mode)))
        a_conf = auc([(r[0], r[2]) for r in rows])
        a_cons = auc([(r[1], r[2]) for r in rows])
        a_lex = auc([(r[1] * 10 + r[0], r[2]) for r in rows])
        print(f"[N=3 抽樣, {mode}]（每標的 {n_triplets} 組，finding 會重複計入）")
        print(f"   AUC confidence      {a_conf[0]:.3f}")
        print(f"   AUC 一致性(0-2)     {a_cons[0]:.3f}")
        print(f"   AUC 一致性→conf     {a_lex[0]:.3f}")

    # ---- 射程內的組成：不成立的 finding 屬於持續性還是零星 item ----
    print("[組成] 不成立（strict）的 finding，依所屬 item 的出現頻率分：")
    for t, rs in runs.items():
        R = len(rs)
        freq = defaultdict(int)
        for fs in rs.values():
            for it in {f["item"] for f in fs}:
                freq[it] += 1
        bad = [f for fs in rs.values() for f in fs if not ok(f["label"], "strict")]
        good = [f for fs in rs.values() for f in fs if ok(f["label"], "strict")]
        pb = sum(1 for f in bad if freq[f["item"]] / R >= 0.5)
        pg = sum(1 for f in good if freq[f["item"]] / R >= 0.5)
        print(f"   {t:<7} 不成立 {len(bad):>2} 筆：持續性(≥50%跑) {pb:>2}／零星 {len(bad)-pb:>2}"
              f"  ｜ 成立 {len(good):>2} 筆：持續性 {pg:>2}／零星 {len(good)-pg:>2}")


if __name__ == "__main__":
    analyze(["v02", "v05"])
    analyze(["v00", "v04"])
