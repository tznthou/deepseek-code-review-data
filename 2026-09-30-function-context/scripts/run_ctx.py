#!/usr/bin/env python3
"""跑一輪：直接呼叫 09-25 的 run_bench.main()，只把它的資料根目錄換成本實驗的 arms/<臂>/。

為什麼不另寫一支：兩個入口的參數會無聲分岔（[[dual-entry-config-drift]]）。run_bench 的
呼叫參數、key 驗形狀、續跑、manifest、估價全部沿用；它讀 `EXP/prs/<key>/pr.diff` 與 `meta.json`、
寫 `EXP/rounds/<標籤>/`、讀 `EXP/data/`，所以只要讓 EXP 指到下面這個結構：

  arms/<臂>/data  → ../2026-09-25-qodo-bench/data（symlink）
  arms/<臂>/prs/<key>/pr.diff   base 臂 → Qodo 的 pr.diff；fc 臂 → 本實驗 prs/<key>/fc.diff（symlink）
  arms/<臂>/prs/<key>/meta.json → Qodo 的 meta.json（symlink）
  arms/<臂>/rounds/<標籤>/      輸出

用法：run_ctx.py --arm base|fc <標籤> [run_bench 的其他參數，例如 --limit 1]
"""
import argparse
import pathlib
import sys

sys.dont_write_bytecode = True
EXP = pathlib.Path(__file__).resolve().parents[1]
QODO = EXP.parent / "2026-09-25-qodo-bench"
sys.path.insert(0, str(QODO / "scripts"))
import run_bench  # noqa: E402


def stage(arm: str) -> pathlib.Path:
    root = EXP / "arms" / arm
    (root / "rounds").mkdir(parents=True, exist_ok=True)
    if not (root / "data").exists():
        (root / "data").symlink_to(QODO / "data")
    for key in run_bench_keys():
        d = root / "prs" / key
        d.mkdir(parents=True, exist_ok=True)
        diff = QODO / "prs" / key / "pr.diff" if arm == "base" else EXP / "prs" / key / "fc.diff"
        if not diff.exists():
            sys.exit(f"[stop] 缺 {diff}")
        for name, target in (("pr.diff", diff), ("meta.json", QODO / "prs" / key / "meta.json")):
            link = d / name
            if link.is_symlink() and link.resolve() != target.resolve():
                sys.exit(f"[stop] {link} 指向 {link.resolve()}，不是 {target}")
            if not link.exists():
                link.symlink_to(target)
    return root


def run_bench_keys() -> list[str]:
    saved = run_bench.EXP
    run_bench.EXP = QODO
    try:
        return run_bench.pr_keys()
    finally:
        run_bench.EXP = saved


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["base", "fc"], required=True)
    ap.add_argument("--stage-only", action="store_true", help="只建 arms/<臂>/ 結構，不呼叫 API")
    args, rest = ap.parse_known_args()
    root = stage(args.arm)
    if args.stage_only:
        print(f"{root}：{len(list((root / 'prs').iterdir()))} 個 PR")
        return
    run_bench.EXP = root
    sys.argv = ["run_bench.py", *rest]
    run_bench.main()


if __name__ == "__main__":
    main()
