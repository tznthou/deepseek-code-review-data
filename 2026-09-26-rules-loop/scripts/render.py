"""把一個 repo 的規則照「呈現設定」渲染成 prompt 片段。

loop 每一輪只改設定檔（iterations/vNN.json），設定只能從 OPTIONS 列舉的值裡選——搜尋空間在這裡封死：
- 規則文字一律逐字取自 rules_for_repo.jsonl，標準答案的任何內容都進不來
- 開頭說明只能選 HEADERS 三句之一，三句都只提供資訊，不含「確定才報」這類要求自我約束的話
  （README §4.7：要求自律的改法實測無效，v1.4.0 那輪的定錨版 AUC 還掉到 0.773）
- 引用編號的要求（CITE）每個版本都一樣，不在搜尋範圍內：metric 靠它判斷 finding 引用的是哪條規則
"""
import json

from common import load_rules, rule_ids

OPTIONS = {
    "placement": ("after_diff", "before_diff"),
    "fields": ("title", "title_objective", "full"),
    "format": ("list", "sections", "json"),
    "header": ("h1", "h2", "h3"),
}
HEADERS = {
    "h1": "## 這個 repo 的規範\n\n以下是這個 repo 自己訂的規範，和上面的通用要求一起適用於這次改動。",
    "h2": "## 專案規範（取自這個 repo 的規範檔）\n\n這些規範描述這個專案的慣例與限制；改動違反其中任何一條，也是要報的問題。",
    "h3": "## Repository rules\n\nThe maintainers of this repository defined the following rules for all changes.",
}
CITE = ("如果某個 finding 是違反上面的某一條規範，請在它的 `title` 開頭標出規範編號，"
        "例如 `[R03] …`；一個 finding 只標一條。")
FIELD_KEYS = {"title": (), "title_objective": ("objective",),
              "full": ("objective", "success_criteria", "failure_criteria")}
LABELS = {"objective": "目的", "success_criteria": "符合", "failure_criteria": "違反"}


def check(cfg: dict) -> dict:
    extra = set(cfg) - set(OPTIONS)
    if extra:
        raise ValueError(f"不認得的設定：{sorted(extra)}")
    for key, allowed in OPTIONS.items():
        if cfg.get(key) not in allowed:
            raise ValueError(f"{key} 必須是 {allowed} 之一，拿到 {cfg.get(key)!r}")
    return cfg


def _text(v) -> str:
    return v.strip() if isinstance(v, str) else json.dumps(v, ensure_ascii=False)


def render(repo: str, cfg: dict) -> tuple[str, dict[str, str]]:
    """回傳 (要附進 user message 的整段文字, {規則編號: 規則 title})。"""
    check(cfg)
    rules = load_rules()[repo]
    ids = rule_ids(rules)
    keys = FIELD_KEYS[cfg["fields"]]
    parts = [HEADERS[cfg["header"]], ""]
    if cfg["format"] == "json":
        items = [{"id": rid, "title": r["title"], **{k: _text(r[k]) for k in keys if r.get(k)}}
                 for rid, r in zip(ids, rules)]
        parts.append("```json\n" + json.dumps(items, ensure_ascii=False, indent=1) + "\n```")
    elif cfg["format"] == "list":
        for rid, r in zip(ids, rules):
            tail = "；".join(f"{LABELS[k]}：{_text(r[k])}" for k in keys if r.get(k))
            parts.append(f"- [{rid}] **{r['title']}**" + (f" — {tail}" if tail else ""))
    else:  # sections
        for rid, r in zip(ids, rules):
            parts.append(f"### [{rid}] {r['title']}")
            parts += [f"{LABELS[k]}：{_text(r[k])}" for k in keys if r.get(k)]
            parts.append("")
    parts += ["", CITE]
    return "\n".join(parts).strip() + "\n", ids
