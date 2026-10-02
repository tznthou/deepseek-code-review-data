<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在複製到 replica 時會移除 field TTL 的問題，改為複製成 HSETEX 並加上 KEEPTTL 旗標。主要風險在於新增的 shared 物件（hsetex、fields）未在所有初始化路徑中建立，可能導致 null pointer dereference；此外，測試中對 TTL 的斷言使用固定範圍，可能因時間誤差而 flaky。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/server.c:2130` | 新增 shared.hsetex 與 shared.fields 可能未在所有初始化路徑建立 | 0.80 |
| ⚠️ | Major | `src/t_hash.c:2571` | rewriteClientCommandVector 參數數量與格式需確認 | 0.75 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1980` | 測試中 TTL 斷言使用固定範圍可能導致 flaky | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:2130</code> 新增 shared.hsetex 與 shared.fields 可能未在所有初始化路徑建立</summary>

在 `createSharedObjects()` 中新增了 `shared.hsetex` 和 `shared.fields`，但需確認所有會建立 shared objects 的程式路徑（例如 `main()` 中的初始化、測試中的特殊初始化）都有呼叫到這個函式。若某路徑未建立這些物件，後續使用時會造成 null pointer dereference。建議搜尋所有 `createSharedObjects` 的呼叫點，確認沒有遺漏。

**判斷依據**：diff 中新增了 shared.hsetex 與 shared.fields 的建立，但未看到其他初始化路徑的修改。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> rewriteClientCommandVector 參數數量與格式需確認</summary>

`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj);` 的參數數量與格式需與函式定義一致。若函式預期以 NULL 結尾或參數數量計算錯誤，可能導致記憶體越界或命令格式錯誤。建議檢查 `rewriteClientCommandVector` 的實作，確認此處用法正確。

**判斷依據**：此呼叫傳入 6 個參數，但未確認函式是否要求以 NULL 結尾或使用 argc 計算。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1980</code> 測試中 TTL 斷言使用固定範圍可能導致 flaky</summary>

`assert_range [r httl h1 FIELDS 1 f1] 90 100` 假設 TTL 在 90 到 100 秒之間，但若測試執行緩慢或系統時間有偏差，可能超出範圍。建議改用更寬鬆的範圍或先取得初始 TTL 再比較差值。

**判斷依據**：測試中兩次使用 assert_range 檢查 TTL，範圍固定為 90-100，可能受時間影響。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4614 (cache hit 3584) ｜ completion tokens 839 ｜ PR #9</sub>