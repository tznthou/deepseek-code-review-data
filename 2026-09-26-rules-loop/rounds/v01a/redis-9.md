<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在複製到 replica 時會移除欄位過期時間的問題，方法是將複製命令從 HSET 改為 HSETEX 並加上 KEEPTTL 旗標。主要風險在於新增的 rewriteClientCommandVector 呼叫參數是否正確、共享物件初始化是否完整，以及測試是否涵蓋所有情境。整體而言，變更範圍小且目標明確，但需確認命令重寫的正確性與測試的穩定性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2571` | rewriteClientCommandVector 參數數量可能不正確 | 0.80 |
| 🔸 | Minor | `src/server.c:2130` | 共享物件 hsetex 和 fields 未在 server.h 中宣告 | 0.60 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1970` | 測試中缺少對 HINCRBYFLOAT 複製命令的明確驗證 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> rewriteClientCommandVector 參數數量可能不正確</summary>

呼叫 `rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj);` 時，第二個參數為 6，但實際傳入的參數有 7 個（hsetex, key, keepttl, fields, 1, field, value）。這可能導致命令向量長度設定錯誤，造成複製或 AOF 寫入異常。請確認 rewriteClientCommandVector 的參數定義，並修正為正確的數量。

**判斷依據**：diff 中新增的 rewriteClientCommandVector 呼叫，第二個參數為 6，但後續參數數量明顯超過 6 個。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:2130</code> 共享物件 hsetex 和 fields 未在 server.h 中宣告</summary>

在 server.c 中新增了 `shared.hsetex` 和 `shared.fields` 的初始化，但 server.h 中的 sharedObjectsStruct 是否已包含這兩個成員？從 diff 中看到 server.h 有新增 `*hsetex` 和 `*fields`，但需確認是否已正確加入結構體中，否則可能導致編譯錯誤。

**判斷依據**：diff 中 server.c 新增了 shared.hsetex 和 shared.fields 的初始化，但 server.h 的修改僅在部分行顯示，需確認結構體定義是否完整。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1970</code> 測試中缺少對 HINCRBYFLOAT 複製命令的明確驗證</summary>

測試中使用了 `assert_replication_stream` 來驗證複製流，但對於 HINCRBYFLOAT 產生的 HSETEX 命令，僅檢查了命令格式，未驗證實際的 TTL 值是否正確保留。建議增加對 TTL 的明確斷言，以確保 KEEPTTL 旗標生效。

**判斷依據**：測試中僅檢查命令格式，未驗證 TTL 值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4604 (cache hit 3584) ｜ completion tokens 953 ｜ PR #9</sub>