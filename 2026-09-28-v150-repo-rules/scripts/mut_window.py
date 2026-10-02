#!/usr/bin/env python3
"""把 MERGE_WINDOW 改成指定值（在副本上），看 merge_into 的邊界測試會不會叫。"""
import importlib.util, pathlib, re, sys

KIT = pathlib.Path("<repo>")
SCRATCH = pathlib.Path(__file__).parent
sys.path.insert(0, str(KIT / ".github/scripts"))

for w in (0, 2, 3, 4, 10):
    src = (KIT / ".github/scripts/post_review.py").read_text(encoding="utf-8")
    mutated, n = re.subn(r"^MERGE_WINDOW = 3$", f"MERGE_WINDOW = {w}", src, flags=re.M)
    assert n == 1, "變異沒有套上"
    path = SCRATCH / f"post_mut_{w}.py"
    path.write_text(mutated, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"pm{w}", path)
    pm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pm)
    hosts = [{"path": "a.py", "line": 10}, {"path": "a.py", "line": 20}]
    extras = [{"path": "a.py", "line": 13, "title": "距離 3"}, {"path": "a.py", "line": 14, "title": "距離 4"},
              {"path": "a.py", "line": 7, "title": "往上距離 3"}, {"path": "b.py", "line": 10, "title": "別的檔案"},
              {"path": "a.py", "line": 17, "title": "選近的"}]
    alone = [e["title"] for e in pm.merge_into(hosts, extras)]
    ok = alone == ["距離 4", "別的檔案"]
    print(f"MERGE_WINDOW={pm.MERGE_WINDOW} → alone={alone} → 測試{'通過' if ok else '會叫'}")
