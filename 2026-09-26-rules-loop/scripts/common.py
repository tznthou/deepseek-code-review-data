"""rules loop 共用的路徑與小工具。"""
import json
import pathlib
import re

LOOP = pathlib.Path(__file__).resolve().parents[1]
QODO = LOOP.parent / "2026-09-25-qodo-bench"
KIT = LOOP.parents[2]
SPLIT = LOOP / "split.json"


def pr_repo(pr: str) -> str:
    return pr.rsplit("-", 1)[0]


def load_rules() -> dict[str, list[dict]]:
    rows = [json.loads(l) for l in (QODO / "data/rules_for_repo.jsonl").read_text(encoding="utf-8").splitlines()
            if l.strip()]
    return {r["repo"]: r["extracted_rules"] for r in rows}


def rule_ids(rules: list[dict]) -> dict[str, str]:
    """照規則檔原本的順序編成 R01、R02…；編號跟呈現設定無關，評分才對得回去。"""
    return {f"R{i:02d}": r["title"] for i, r in enumerate(rules, 1)}


def norm_rule(name: str) -> str:
    """GT 的 rule_name 有些帶「Rule 19: 」前綴；去掉之後 271/271 對得上規則檔的 title（2026-09-26 實測）。"""
    name = re.sub(r"^rule\s*\d+\s*:\s*", "", name or "", flags=re.I)
    return re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()


def gt_rule_names() -> dict[str, str]:
    """evalset 的 id（<pr>#<issue 序號>）→ 標準答案違反的規則名稱（已正規化）。"""
    out = {}
    for line in (QODO / "data/bench.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        parts = r["pr_url_to_review"].rstrip("/").split("/")
        pr = f"{parts[-3]}-{parts[-1]}"
        for i, it in enumerate(r["issues"]):
            if it.get("rule_name"):
                out[f"{pr}#{i}"] = norm_rule(it["rule_name"])
    return out


def load_split() -> dict:
    return json.loads(SPLIT.read_text(encoding="utf-8"))


def split_prs(name: str) -> list[str]:
    if name == "all":
        s = load_split()
        return sorted(s["tune"] + s["holdout"])
    return list(load_split()[name])
