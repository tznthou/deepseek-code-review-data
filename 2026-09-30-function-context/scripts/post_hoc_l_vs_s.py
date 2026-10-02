#!/usr/bin/env python3
"""【事後探索，不在跑前寫定的判準內】把 L（位置命中）和 S（盲標 same）拆開對照，找 L 落差的來源。$0。

起因：verdict 的 L fc 臂比基準低 12–24，S 卻是 fc-1 +4；post_hoc_locate_stats.py 只解釋得了 4–5 則。
這裡看四件事：
  1. fc-1／base-3 的 L×S 四格：L 少掉的是「位置對、問題也對」還是「位置對、問題不對」
  2. 配對檢定：同一則 GT 在兩輪命中與否（GT 層 McNemar exact、PR 層正負號置換）；臂內兩輪當雜訊對照
  3. 跨輪一致性：基準三輪都命中的 GT，fc 兩輪命中幾輪（反方向當對照）
  4. 一輪命中、另一輪沒命中的 GT，沒命中那輪在同一個檔報了什麼
"""
import collections
import json
import math
import pathlib
import random
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import score_ctx  # noqa: E402

SEED, N_PERM = 20261001, 20000
ROUNDS, BASE, FC, LABELED = score_ctx.ROUNDS, score_ctx.BASE, score_ctx.FC, score_ctx.LABELED

mapping = json.loads((score_ctx.BLIND / "mapping.json").read_text(encoding="utf-8"))
labels = {}
for part in sorted(score_ctx.BLIND.glob("labels-part*.csv")):
    labels.update(score_ctx.read_csv(part))
lab = {m["pair"]: labels[pid] for pid, m in mapping.items()}

ev, _ = score_ctx.evalset()
emap = {e["id"]: e for e in ev}
KIND = {k: {e["id"] for e in ev if e["kind"] == k} for k in ("func", "rule")}

data = {}
for r in ROUNDS:
    _, by_pr, fs = score_ctx.load(r)
    data[r] = {"fs": fs, "pairs": score_ctx.score_bench.pairs_for(fs, by_pr), "fmap": {f["fid"]: f for f in fs}}


def Lset(r, kind):
    return score_ctx.L(data[r]["pairs"], data[r]["fmap"], KIND[kind])


def Sset(r, kind):
    return score_ctx.S(data[r]["pairs"], data[r]["fmap"], KIND[kind], lab)


def mcnemar(a, b):
    """a、b：兩輪命中的 GT 集合 → (只有 a、只有 b、雙尾 exact p)。"""
    oa, ob = len(a - b), len(b - a)
    n, k = oa + ob, min(oa, ob)
    p = min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0
    return oa, ob, p


def perm(a, b):
    """PR 層：每個 PR 的命中數差（a − b）隨機翻正負號。同一 PR 的 GT 不獨立，這個比 McNemar 保守。"""
    per = collections.Counter()
    for g in a:
        per[emap[g]["pr"]] += 1
    for g in b:
        per[emap[g]["pr"]] -= 1
    d = [v for v in per.values() if v]
    t = abs(sum(d))
    rng = random.Random(SEED)
    hit = sum(abs(sum(x if rng.random() < 0.5 else -x for x in d)) >= t for _ in range(N_PERM))
    return (hit + 1) / (N_PERM + 1)


def compare(title, sets, pairs):
    print(f"\n=== {title} ===")
    print(f"  {'a vs b':<16}{'a':>5}{'b':>5}{'差':>6}{'只 a':>6}{'只 b':>6}{'McNemar p':>11}{'置換 p':>9}")
    for a, b in pairs:
        oa, ob, p = mcnemar(sets[a], sets[b])
        print(f"  {a + ' vs ' + b:<16}{len(sets[a]):>5}{len(sets[b]):>5}{len(sets[a]) - len(sets[b]):>+6}"
              f"{oa:>6}{ob:>6}{p:>11.3f}{perm(sets[a], sets[b]):>9.3f}")


# ── 1. L×S 四格 ──
for kind in ("func", "rule"):
    print(f"\n=== L×S 四格（{'功能性 309' if kind == 'func' else '規則類 271'}）===")
    for r in LABELED:
        l, s = Lset(r, kind), Sset(r, kind)
        print(f"  {r:<7} L∧S {len(l & s):>4}｜只有 L（位置對、不是同一問題）{len(l - s):>4}"
              f"｜只有 S（同一問題、位置差 > 3 行）{len(s - l):>4}｜L {len(l)}｜S {len(s)}")

# ── 2. 配對檢定 ──
within = [("base-1", "base-2"), ("base-1", "base-3"), ("base-2", "base-3"), ("fc-1", "fc-2")]
cross = [(f, b) for f in FC for b in BASE]
for kind in ("func", "rule"):
    compare(f"L 配對檢定（{kind}；前四列是臂內兩輪＝雜訊對照）", {r: Lset(r, kind) for r in ROUNDS}, within + cross)
    compare(f"S 配對檢定（{kind}）", {r: Sset(r, kind) for r in LABELED}, [("fc-1", "base-3")])

# ── 3. 跨輪一致性（功能性 L）──
Ls = {r: Lset(r, "func") for r in ROUNDS}
grid = collections.Counter((sum(g in Ls[r] for r in BASE), sum(g in Ls[r] for r in FC)) for g in KIND["func"])
print("\n=== 功能性 L 跨輪一致性：列 = 基準三輪命中幾輪，欄 = fc 兩輪命中幾輪 ===")
print("        fc 0   fc 1   fc 2")
for nb in range(4):
    print(f"  基準 {nb} " + "".join(f"{grid[(nb, nf)]:>7}" for nf in range(3)))
hb = sum(nb * c for (nb, _), c in grid.items()) / 3
hf = sum(nf * c for (_, nf), c in grid.items()) / 2
print(f"  每輪平均命中：基準 {hb:.1f}、fc {hf:.1f}")


# ── 4. 一輪命中、另一輪沒命中：沒命中那輪在同一個檔報了什麼 ──
def classify(gid, r):
    e = emap[gid]
    ps = [p for p in data[r]["pairs"] if p["gid"] == gid]
    if ps:
        if any(lab.get(p["pair"]) == "same" for p in ps):
            return "同一問題、位置差 > 3 行"
        return "有候選配對、標成非 same" if r in LABELED else "有候選配對（這輪沒標）"
    same_file = [f for f in data[r]["fs"] if f["pr"] == e["pr"] and f["path"] == e["file"]]
    if not same_file:
        return "同一個檔沒有 finding"
    if any(f["line"] is None for f in same_file):
        return "同檔有定位不到的 finding"
    return "同檔有 finding、距離太遠"


def winner_same(gid, r):
    """命中那輪的位置命中配對有沒有被標成 same。"""
    return any(lab.get(p["pair"]) == "same" for p in data[r]["pairs"] if p["gid"] == gid and p["loc_hit"])


def breakdown(title, gids, loser, winner):
    print(f"\n=== {title}：{len(gids)} 則 ===")
    c = collections.Counter(classify(g, loser) for g in gids)
    for k, v in c.most_common():
        print(f"  {loser} 那邊：{k} {v}")
    if winner in LABELED:
        w = sum(winner_same(g, winner) for g in gids)
        print(f"  {winner} 那邊的位置命中被標成 same：{w}／{len(gids)}（其餘 = 位置對、問題不對）")
    ext = collections.Counter(pathlib.Path(emap[g]["file"]).suffix or "(無)" for g in gids)
    print(f"  副檔名：{dict(ext.most_common())}")


breakdown("base-3 位置命中、fc-1 沒有", Ls["base-3"] - Ls["fc-1"], "fc-1", "base-3")
breakdown("fc-1 位置命中、base-3 沒有（反方向）", Ls["fc-1"] - Ls["base-3"], "base-3", "fc-1")
lost = {g for g in KIND["func"] if all(g in Ls[r] for r in BASE) and not any(g in Ls[r] for r in FC)}
gained = {g for g in KIND["func"] if all(g in Ls[r] for r in FC) and not any(g in Ls[r] for r in BASE)}
breakdown("基準三輪都命中、fc 兩輪都沒有", lost, "fc-1", "base-3")
breakdown("fc 兩輪都命中、基準三輪都沒有（反方向）", gained, "base-3", "fc-1")

# 規則類：配對數與標籤分布（S 37 → 23 是 finding 變少，還是同樣的配對標得比較嚴）
print("\n=== 規則類候選配對的標籤分布 ===")
for r in LABELED:
    ps = [p for p in data[r]["pairs"] if p["gid"] in KIND["rule"]]
    c = collections.Counter(lab.get(p["pair"]) for p in ps)
    print(f"  {r:<7} 配對 {len(ps)}｜same {c['same']}、partial {c['partial']}、no {c['no']}"
          f"｜涉及 finding {len({p['fid'] for p in ps})}")

# ── 5. 「只有 S」（同一問題、位置差 > 3 行）逐筆：位置偏在哪 ──
print("\n=== 只有 S 的 GT：same 配對的候選管道、距離、定位方式 ===")
for r in LABELED:
    only_s = Sset(r, "func") - Lset(r, "func")
    print(f"  {r}：{len(only_s)} 則")
    for g in sorted(only_s):
        for p in data[r]["pairs"]:
            if p["gid"] == g and lab.get(p["pair"]) == "same":
                f = data[r]["fmap"][p["fid"]]
                print(f"    {g:<16} via {p['via']:<10} 距離 {p['dist']:>3}｜定位 {f['how'][:24]}")

# ── 6. 基準臂內的 S 對照：base-1 用 09-25 舊標籤（不同批標記；09-28 量過新舊標籤 same 與否一致 98.5%）──
old = score_ctx.read_csv(score_ctx.QODO / "rounds/base-1/labels.csv")
b1 = data["base-1"]
for kind in ("func", "rule"):
    s1 = score_ctx.S(b1["pairs"], b1["fmap"], KIND[kind], old)
    sets = {"base-1": s1, **{r: Sset(r, kind) for r in LABELED}}
    compare(f"S 對照（{kind}；base-1 = 09-25 舊標籤）", sets,
            [("base-1", "base-3"), ("fc-1", "base-1"), ("fc-1", "base-3")])

# ── 7. 多重命中的代價：locate 遇到多重命中直接放棄（不退回模型行號）。
#       把「多重命中、模型行號落在錨點 ±3」也算位置命中，看 L 的落差剩多少 ──
def L_mm(r):
    fmap = data[r]["fmap"]
    return {p["gid"] for p in data[r]["pairs"] if p["gid"] in KIND["func"] and (
        p["loc_hit"] or (p["via"] == "model_line" and p["dist"] <= 3 and "多重命中" in fmap[p["fid"]]["how"]))}


print("\n=== 功能性 L，多重命中改用模型行號（±3）===")
lm = {r: L_mm(r) for r in ROUNDS}
print("  " + "｜".join(f"{r} {len(Ls[r])} → {len(lm[r])}（+{len(lm[r]) - len(Ls[r])}）" for r in ROUNDS))
print(f"  每輪平均：基準 {sum(len(lm[r]) for r in BASE) / 3:.1f}、fc {sum(len(lm[r]) for r in FC) / 2:.1f}")
compare("L（多重命中改用模型行號）配對檢定", lm, within + cross)
