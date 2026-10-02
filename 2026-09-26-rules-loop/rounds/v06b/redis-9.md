<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在複製到 replica 時會移除 field expiration 的問題，方法是將複製指令從 HSET 改為 HSETEX 並加上 KEEPTTL 旗標。主要風險在於新增的 shared 物件（hsetex、fields）是否正確初始化，以及 rewriteClientCommandVector 的參數順序是否正確。測試涵蓋了 replica 同步情境，但需確認測試中的 TTL 範圍斷言是否穩定。整體而言，變更集中且合理，但需驗證編譯與測試結果。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2571` | rewriteClientCommandVector 參數順序可能錯誤 | 0.80 |
| 🔸 | Minor | `src/server.c:2130` | 新增 shared 物件未確認是否在所有初始化路徑中建立 | 0.60 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1981` | 測試中 TTL 範圍斷言可能不穩定 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> rewriteClientCommandVector 參數順序可能錯誤</summary>

在 `rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj)` 中，參數順序可能與函式預期不符。根據 Redis 原始碼慣例，`rewriteClientCommandVector` 的參數為 `(client *c, int argc, ...)`，其中 `argc` 是新的參數數量，後續依序為新的 argv 元素。此處傳入 6 個參數，但實際提供的元素為 7 個（hsetex, key, keepttl, fields, 1, field, value），可能導致記憶體越界或錯誤的指令重寫。建議檢查 `rewriteClientCommandVector` 的實作，確認參數數量與傳入元素一致。

**判斷依據**：diff 中新增的這一行，argc 為 6，但後續有 7 個參數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:2130</code> 新增 shared 物件未確認是否在所有初始化路徑中建立</summary>

新增了 `shared.hsetex` 和 `shared.fields`，但需確認這些 shared 物件是否在所有必要的初始化流程中被建立（例如 `createSharedObjects` 是否總是被呼叫）。若某些啟動路徑未呼叫此函式，可能導致 null pointer dereference。

**判斷依據**：diff 中新增的 shared 物件建立，但未見其他初始化路徑的修改。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1981</code> 測試中 TTL 範圍斷言可能不穩定</summary>

測試使用 `assert_range [r httl h1 FIELDS 1 f1] 90 100` 來驗證 TTL 在 90 到 100 秒之間。由於測試執行時間可能超過 10 秒，TTL 可能低於 90，導致測試偶發失敗。建議放寬範圍或使用更精確的驗證方式。

**判斷依據**：diff 中新增的測試斷言，TTL 範圍固定為 90-100。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4594 (cache hit 4480) ｜ completion tokens 895 ｜ PR #9</sub>