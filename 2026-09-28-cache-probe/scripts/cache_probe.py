#!/usr/bin/env python3
"""規範那次沒吃到快取的 2×2 實驗（長度 × 前綴結構）。設計與判定見 ../README.md，跑之前定稿。

  python3 cache_probe.py --dry-run   # 只組 prompt、驗結構、估花費，不送出
  python3 cache_probe.py --run       # 真的送（key 從 keychain 讀，先驗形狀，不印、不寫檔）

prompt 用 kit 自己的 USER_TEMPLATE／render_repo_rules／select_rules 組，跟 production 的 main() 同順序。
"""
import argparse
import json
import os
import pathlib
import re
import secrets
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

EXP = pathlib.Path(__file__).resolve().parents[1]
KIT = EXP.parents[2]
sys.path.insert(0, str(KIT / ".github/scripts"))
import deepseek_review as dr  # noqa: E402

MODEL = "deepseek-v4-pro"
URL = "https://api.deepseek.com/chat/completions"
MAX_TOKENS = 200
L_MAX_CHARS = 8766  # #50 run 1 的 diff 長度
# 尖峰價（USD / 1M tokens；README「模型費用估算」離峰價 ×2）
PRICE_MISS, PRICE_HIT, PRICE_OUT = 1.32, 0.044, 3.96
BUDGET = 0.15
PLAN = [  # (對, 長度, 結構, 第一次回應後隔幾秒送第二次)
    (1, "S", "c", 0.1),
    (2, "L", "d", 0.1),
    (3, "S", "d", 0.1),
    (4, "L", "c", 0.1),
    (5, "L", "c", 0.1),
    (6, "S", "d", 0.1),
    (7, "L", "d", 0.1),
    (8, "S", "c", 0.1),
    (9, "L", "d", 15.0),
]


def api_key() -> str:
    try:
        key = subprocess.run(
            ["security", "find-generic-password", "-w", "-s", "deepseek-api-key"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except subprocess.CalledProcessError:
        sys.exit("keychain 裡沒有 deepseek-api-key")
    # 形狀不對就不送（避免把存錯的值當成 key 送出去），錯誤訊息不帶值本身。
    if not re.fullmatch(r"sk-[A-Za-z0-9]{20,}", key):
        sys.exit(f"keychain 裡的 deepseek-api-key 不像 DeepSeek key（長度 {len(key)}、"
                 f"sk- 開頭：{key.startswith('sk-')}），不送出")
    return key


def cut_at_line(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: text.rfind("\n", 0, limit) + 1]


def build_inputs() -> dict:
    diffs = {
        "S": (EXP / "inputs/pr51.diff").read_text(encoding="utf-8"),
        "L": cut_at_line((EXP / "inputs/pr50.diff").read_text(encoding="utf-8"), L_MAX_CHARS),
    }
    rubric = dr.load_text(str(KIT / "prompts/review-rubric.md"))
    system_prompt = rubric or "你是嚴謹的資深程式碼審查者，只輸出 JSON。"
    rules = dr.parse_repo_rules(dr.load_text(str(KIT / ".github/review-rules.md")))
    rules_block, rule_ids = dr.render_repo_rules(rules)
    extra_rules, used = dr.select_rules(
        (EXP / "inputs/pr50.diff").read_text(encoding="utf-8"), str(KIT / "prompts/rules")
    )
    typed_block = (
        "\n\n## 這次改動涉及的檔案型態，有以下補充規則\n\n"
        "這些規則補充上面的通用要求，不取代它們。\n\n" + extra_rules + "\n"
    )
    return {
        "diffs": diffs, "system": system_prompt, "rules_block": rules_block,
        "rule_count": len(rule_ids), "typed_block": typed_block, "typed_used": used,
    }


def build_pair(inp: dict, size: str, structure: str) -> dict:
    nonce = secrets.token_hex(6)
    meta = {"nonce": nonce, "title": "cache probe", "base_ref": "main", "head_sha": nonce + "0" * 28}
    user_base = dr.USER_TEMPLATE.format(
        meta=json.dumps(meta, ensure_ascii=False, indent=2)[:4000],
        base_ref=meta["base_ref"],
        head_sha=meta["head_sha"][:12],
        diff=inp["diffs"][size],
    )
    # 同 production main()：規範那次先 rstrip 再接規範區塊；補充規則在兩次都接在最後
    rules_user = user_base.rstrip("\n") + "\n\n" + inp["rules_block"]
    if structure == "d":
        u1, u2 = user_base + inp["typed_block"], rules_user + inp["typed_block"]
    else:
        u1, u2 = user_base, rules_user
    return {"nonce": nonce, "user_base": user_base, "u1": u1, "u2": u2}


def payload(system: str, user: str) -> dict:
    return {
        "model": MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "response_format": {"type": "json_object"},
        "max_tokens": MAX_TOKENS,
        "temperature": 0.2,
        "stream": False,
        "thinking": {"type": "disabled"},
    }


def check_structure(inp: dict, pairs: list[dict]) -> list[str]:
    problems = []
    nonces = [p["nonce"] for p in pairs]
    if len(set(nonces)) != len(nonces):
        problems.append("nonce 重複")
    for (no, size, structure, _), p in zip(PLAN, pairs):
        common = os.path.commonprefix([p["u1"], p["u2"]])
        if structure == "c" and not p["u2"].startswith(p["u1"]):
            problems.append(f"對 {no}：c 格的第一次不是第二次的完整前綴")
        if structure == "d":
            if p["u2"].startswith(p["u1"]):
                problems.append(f"對 {no}：d 格沒有分岔")
            if not common.startswith(p["user_base"].rstrip("\n")):
                problems.append(f"對 {no}：d 格的共同前綴沒有涵蓋到 diff 結尾")
            if len(common) > len(p["user_base"].rstrip("\n")) + 2:
                problems.append(f"對 {no}：d 格分岔點不在 diff 之後")
    if not inp["typed_used"]:
        problems.append("select_rules 沒選到任何補充規則")
    return problems


def send(key: str, body: dict) -> tuple[dict, float, float]:
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}", "Accept": "application/json"},
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        if err.code in (401, 403):
            sys.exit(f"HTTP {err.code}：認證失敗，全停（不印 body）")
        detail = err.read().decode("utf-8", errors="replace")[:200]
        sys.exit(f"HTTP {err.code}：{detail}（全停）")
    except (urllib.error.URLError, TimeoutError) as err:
        sys.exit(f"{type(err).__name__}：{err}（全停）")
    return data, t0, time.time()


def usage_row(data: dict) -> dict:
    u = data.get("usage", {})
    return {
        "prompt_tokens": u.get("prompt_tokens"),
        "cached": (u.get("prompt_tokens_details") or {}).get("cached_tokens"),
        "hit": u.get("prompt_cache_hit_tokens"),
        "miss": u.get("prompt_cache_miss_tokens"),
        "completion_tokens": u.get("completion_tokens"),
        "finish_reason": (data.get("choices") or [{}])[0].get("finish_reason"),
    }


def cost(row: dict) -> float:
    hit = row["hit"] if row["hit"] is not None else (row["cached"] or 0)
    miss = row["prompt_tokens"] - hit
    return (miss * PRICE_MISS + hit * PRICE_HIT + (row["completion_tokens"] or 0) * PRICE_OUT) / 1e6


def classify(rows: list[dict]) -> list[dict]:
    c_prompt = {}
    for size in ("S", "L"):
        vals = [r["call1"]["prompt_tokens"] for r in rows if r["size"] == size and r["structure"] == "c"]
        c_prompt[size] = sum(vals) / len(vals) if vals else None
    for r in rows:
        p = r["call1"]["prompt_tokens"] if r["structure"] == "c" else c_prompt[r["size"]]
        r["P"] = p
        cached2 = r["call2"]["cached"] or 0
        if p is not None and cached2 >= int(p) // 64 * 64 - 64:
            r["class"] = "full"
        elif cached2 <= (r["call1"]["cached"] or 0) + 64:
            r["class"] = "baseline"
        else:
            r["class"] = "partial"
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    args = ap.parse_args()

    inp = build_inputs()
    pairs = [build_pair(inp, size, structure) for _, size, structure, _ in PLAN]
    problems = check_structure(inp, pairs)
    print(f"system {len(inp['system'])} 字元；規範 {inp['rule_count']} 條、{len(inp['rules_block'])} 字元；"
          f"補充規則 {inp['typed_used']}、{len(inp['typed_block'])} 字元")
    print(f"diff：S {len(inp['diffs']['S'])} 字元、L {len(inp['diffs']['L'])} 字元")
    for (no, size, structure, gap), p in zip(PLAN, pairs):
        print(f"  對 {no} {size}-{structure} gap={gap}s：第一次 user {len(p['u1'])} 字元、第二次 {len(p['u2'])} 字元")
    if problems:
        print("結構檢查 FAIL：", problems)
        return 1
    print("結構檢查 PASS")
    if args.dry_run:
        return 0

    key = api_key()
    out = EXP / "results" / f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.jsonl"
    rows, spent = [], 0.0
    for (no, size, structure, gap), p in zip(PLAN, pairs):
        d1, s1, e1 = send(key, payload(inp["system"], p["u1"]))
        time.sleep(gap)
        d2, s2, e2 = send(key, payload(inp["system"], p["u2"]))
        r = {
            "pair": no, "size": size, "structure": structure, "gap_planned": gap,
            "gap_end_to_start": round(s2 - e1, 3), "dur1": round(e1 - s1, 2), "dur2": round(e2 - s2, 2),
            "t1_start_utc": datetime.fromtimestamp(s1, timezone.utc).isoformat(timespec="milliseconds"),
            "call1": usage_row(d1), "call2": usage_row(d2),
        }
        rows.append(r)
        spent += cost(r["call1"]) + cost(r["call2"])
        with out.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"對 {no} {size}-{structure}：一般 {r['call1']['prompt_tokens']}/{r['call1']['cached']}（{r['dur1']}s）"
              f" → 隔 {r['gap_end_to_start']}s → 規範 {r['call2']['prompt_tokens']}/{r['call2']['cached']}"
              f"（{r['dur2']}s）｜累計 ${spent:.4f}", flush=True)
        if spent > BUDGET:
            print(f"累計 ${spent:.4f} 超過預算 ${BUDGET}，停止")
            break
        time.sleep(2)

    print(f"\n結果：{out}")
    for r in classify(rows):
        p_text = f"{r['P']:.0f}" if r["P"] is not None else "?"
        print(f"  對 {r['pair']} {r['size']}-{r['structure']} gap={r['gap_planned']}s："
              f"P={p_text} 第二次 cached={r['call2']['cached']}（第一次 cached={r['call1']['cached']}）→ {r['class']}")
    cells = {}
    for r in rows:
        if r["gap_planned"] < 1:
            cells.setdefault(f"{r['size']}-{r['structure']}", []).append(r["class"])
    print("格：")
    for cell in ("S-c", "S-d", "L-c", "L-d"):
        got = cells.get(cell, [])
        verdict = got[0] if got and len(set(got)) == 1 else "mixed"
        print(f"  {cell}：{got} → {verdict}")
    print(f"估算花費（尖峰價）：${spent:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
