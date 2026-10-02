#!/usr/bin/env python3
"""PR #47 AI review 第二次 run（G1–G5）的實跑驗證。G1 在 09c2b05 修掉之後，這支會顯示修好的結果。"""
import importlib.util, pathlib, sys

KIT = pathlib.Path("<repo>")
sys.path.insert(0, str(KIT / ".github/scripts"))
spec = importlib.util.spec_from_file_location("dr", KIT / ".github/scripts/deepseek_review.py")
dr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dr)

print("G1：條目那一行就開 code block")
for r in dr.parse_repo_rules('- ```python\n  print("hello")\n  ```\n- 下一條\n- 再下一條\n'):
    print("  ", (r["head"], r["rest"]))
print("  （修正前：只有 1 條，'- 下一條'、'- 再下一條' 都在 R01 的 rest 裡）")
print("G4：空行後的縮排續行", [(r["head"], r["rest"]) for r in dr.parse_repo_rules("- 條目一\n\n  續行一\n")])
print("G3：最壞耗時", 2 * 120 + 2, "秒")
src = (KIT / ".github/scripts/deepseek_review.py").read_text(encoding="utf-8").splitlines()
print("G2：return 0 與寫 findings-out 的行", [i + 1 for i, l in enumerate(src) if "return 0" in l or "args.findings_out" in l])
