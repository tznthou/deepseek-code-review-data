#!/usr/bin/env python3
"""變異測試：故意組錯 c／d，確認 check_structure 會抓到（它不該對錯的組法也回 PASS）。"""
import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location("cp", pathlib.Path(__file__).with_name("cache_probe.py"))
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

inp = cp.build_inputs()


def pairs_ok():
    return [cp.build_pair(inp, size, structure) for _, size, structure, _ in cp.PLAN]


results = []

# 0. 正常組法 → 應 PASS
results.append(("正常組法", cp.check_structure(inp, pairs_ok()) == []))

# 1. d 格的第一次沒接補充規則（等於 c）→ 應抓到「d 格沒有分岔」
ps = pairs_ok()
ps[1]["u1"] = ps[1]["user_base"]
results.append(("d 格沒分岔", any("沒有分岔" in m for m in cp.check_structure(inp, ps))))

# 2. c 格的第一次多接了補充規則 → 應抓到「不是完整前綴」
ps = pairs_ok()
ps[0]["u1"] = ps[0]["user_base"] + inp["typed_block"]
results.append(("c 格不是完整前綴", any("完整前綴" in m for m in cp.check_structure(inp, ps))))

# 3. d 格把規範區塊放到補充規則後面（分岔點不在 diff 之後，而是整段一般那次都是前綴）→ 應抓到
ps = pairs_ok()
ps[1]["u2"] = ps[1]["u1"] + "\n\n" + inp["rules_block"]
results.append(("d 格分岔點錯", bool(cp.check_structure(inp, ps))))

# 4. nonce 重複 → 應抓到
ps = pairs_ok()
ps[2]["nonce"] = ps[1]["nonce"]
results.append(("nonce 重複", any("nonce" in m for m in cp.check_structure(inp, ps))))

for name, ok in results:
    print(("PASS " if ok else "FAIL ") + name)
print("ALL PASS" if all(ok for _, ok in results) else "有 FAIL")
