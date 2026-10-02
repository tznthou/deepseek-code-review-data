#!/usr/bin/env python3
"""產生 A／B 兩組 prompt：A＝repo 現行的逐位元組副本，B＝三個改動。

每個改動都斷言「剛好命中一次」，改不到就停；最後印出 A→B 的 diff 供目視確認。
用法：python3 scripts/make_variants.py
"""

import difflib
import filecmp
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
KIT = HERE.parents[2]
RUBRIC = KIT / "prompts/review-rubric.md"
RULES = KIT / "prompts/rules"
OUT = HERE / "variants"

ITEM6_OLD = "6. **可測試性與可觀測性**：新增分支沒有對應測試、錯誤被吞掉、失敗時無足夠 log/context。"
ITEM6_NEW = "6. **可觀測性**：錯誤被吞掉、失敗時無足夠 log/context。"
PY_LINE = "- 不要報「缺少測試」——你看不到測試檔案是否存在於這次 diff 之外。"


def die(msg: str) -> None:
    sys.exit(f"[停] {msg}")


def make_rubric_b(text: str) -> str:
    lines = text.split("\n")
    quote = [i for i, ln in enumerate(lines) if ln.startswith(">")]
    if not quote or quote != list(range(quote[0], quote[0] + len(quote))):
        die(f"blockquote 不是連續的一段：{quote}")
    if len(quote) != 5 or quote[0] != 2:
        die(f"blockquote 預期是第 3–7 行共 5 行，實際 {quote[0] + 1} 起 {len(quote)} 行")
    if lines[quote[0] - 1] != "" or lines[quote[-1] + 1] != "":
        die("blockquote 前後不是空行")
    del lines[quote[0]:quote[-1] + 2]  # 連同後面那個空行
    out = "\n".join(lines)
    if out.count(ITEM6_OLD) != 1:
        die(f"第 6 條原文命中 {out.count(ITEM6_OLD)} 次")
    return out.replace(ITEM6_OLD, ITEM6_NEW)


def make_python_b(text: str) -> str:
    target = PY_LINE + "\n"
    if text.count(target) != 1:
        die(f"python.md 那一行命中 {text.count(target)} 次")
    return text.replace(target, "")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "rules-A").mkdir(parents=True)
    (OUT / "rules-B").mkdir(parents=True)

    rubric = RUBRIC.read_text(encoding="utf-8")
    (OUT / "rubric-A.md").write_text(rubric, encoding="utf-8")
    rubric_b = make_rubric_b(rubric)
    (OUT / "rubric-B.md").write_text(rubric_b, encoding="utf-8")

    for src in sorted(RULES.glob("*.md")):
        shutil.copyfile(src, OUT / "rules-A" / src.name)
        body = src.read_text(encoding="utf-8")
        if src.name == "python.md":
            body = make_python_b(body)
        (OUT / "rules-B" / src.name).write_text(body, encoding="utf-8")

    # A 必須跟 repo 逐位元組相同
    same = filecmp.cmp(RUBRIC, OUT / "rubric-A.md", shallow=False)
    match, mismatch, errors = filecmp.cmpfiles(RULES, OUT / "rules-A",
                                                [p.name for p in RULES.glob("*.md")], shallow=False)
    if not same or mismatch or errors:
        die(f"A 跟 repo 不一致：rubric={same} mismatch={mismatch} errors={errors}")
    print(f"A 跟 repo 逐位元組相同：rubric + {len(match)} 份 rules")

    for name, a, b in (("rubric", OUT / "rubric-A.md", OUT / "rubric-B.md"),
                       ("python.md", OUT / "rules-A/python.md", OUT / "rules-B/python.md")):
        diff = difflib.unified_diff(a.read_text(encoding="utf-8").splitlines(),
                                    b.read_text(encoding="utf-8").splitlines(),
                                    f"A/{name}", f"B/{name}", lineterm="", n=1)
        print("\n".join(diff))
    others = [p.name for p in RULES.glob("*.md") if p.name != "python.md"]
    for name in others:
        if not filecmp.cmp(OUT / "rules-A" / name, OUT / "rules-B" / name, shallow=False):
            die(f"{name} 在 B 不該有變動")
    print(f"其他 rules 在 A／B 相同：{others}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
