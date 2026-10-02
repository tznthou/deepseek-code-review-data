<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Redis 版本從 8.2.0 升級至 8.2.1，並包含三個主要變更：修正複製期間資料庫清空時可能觸發 active defrag 的競態、修正 stream 在沒有 consumer group 參考時 XADD ACKED 選項的潛在崩潰，以及新增對應的測試。整體風險中等，主要問題在於 replication.c 中 active defrag 的恢復邏輯可能不正確，以及 t_stream.c 中 streamEntryIsReferenced 的回傳值語意可能造成錯誤的刪除行為。建議修正後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/replication.c:1961` | active defrag 恢復邏輯錯誤：無條件設為 1，忽略原始設定 | 0.95 |
| ⚠️ | Major | `src/t_stream.c:2708` | streamEntryIsReferenced 在無 cgroups_ref 時回傳 1 可能導致錯誤刪除 | 0.80 |
| 🔸 | Minor | `tests/unit/memefficiency.tcl:70` | 測試輔助函式 discard_replies_every 的參數名稱與用途不符 | 0.60 |
| 🔸 | Minor | `tests/unit/type/stream.tcl:247` | 測試名稱與實際測試內容不完全匹配 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>src/replication.c:1961</code> active defrag 恢復邏輯錯誤：無條件設為 1，忽略原始設定</summary>

在 `rdbLoadEmptyDbFunc` 中，程式碼先將 `server.active_defrag_enabled` 存入 `orig_active_defrag`，然後在 `emptyData` 後無條件地將 `server.active_defrag_enabled` 設為 1，而不是恢復為 `orig_active_defrag`。

**失敗情境**：如果使用者在執行 replicaof 之前將 `activedefrag` 設定為 `no`（預設值），則在同步完成後，`activedefrag` 會被意外啟用，可能導致不必要的 CPU 消耗或行為改變。

**建議修法**：將 `server.active_defrag_enabled = 1;` 改為 `server.active_defrag_enabled = orig_active_defrag;`。

**判斷依據**：diff 中新增的兩行：`int orig_active_defrag = server.active_defrag_enabled;` 和 `server.active_defrag_enabled = 1;`。變數 `orig_active_defrag` 被儲存但從未被使用，且恢復值硬編碼為 1。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2708</code> streamEntryIsReferenced 在無 cgroups_ref 時回傳 1 可能導致錯誤刪除</summary>

新增的 `if (!s->cgroups_ref) return 1;` 表示當 stream 沒有 consumer groups 時，函式直接回傳 1（代表 entry 被引用）。這可能導致呼叫者認為 entry 被引用而跳過刪除，但實際上沒有 PEL 參考，應該可以安全刪除。

**失敗情境**：在沒有 consumer group 的 stream 上執行 XADD with MAXLEN 或 XTRIM 時，舊的 entry 可能不會被刪除，導致記憶體無法釋放或長度超過預期。

**建議修法**：確認此函式的語意。若回傳 1 表示「被引用」，則在沒有 cgroups_ref 時應回傳 0（未被引用）。若回傳 1 表示「存在」（即 raxFind 的結果），則應回傳 0 表示不存在。請檢查所有呼叫點以確認正確行為。

**判斷依據**：diff 中新增的這一行。函式名稱 `streamEntryIsReferenced` 暗示回傳值為布林（是否被引用），而 `raxFind` 在找不到時回傳 0。因此，當沒有 cgroups_ref 時，entry 不可能被任何 group 引用，應回傳 0。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/memefficiency.tcl:70</code> 測試輔助函式 discard_replies_every 的參數名稱與用途不符</summary>

函式 `discard_replies_every` 的參數 `frequency` 和 `discard_num` 的命名可能造成混淆。`frequency` 實際上是模數（modulus），而 `discard_num` 是要丟棄的回覆數量。雖然不影響功能，但可讀性較差。

**建議修法**：將參數改名為 `modulus` 和 `discard_count`，或加入註解說明。

**判斷依據**：diff 中新增的 proc 定義。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/stream.tcl:247</code> 測試名稱與實際測試內容不完全匹配</summary>

測試名稱是「XADD with ACKED option doesn't crash after DEBUG RELOAD」，但測試中還包含了驗證 MAXLEN 修剪行為的斷言。名稱可能無法完全反映測試範圍。

**建議修法**：將測試名稱改為更全面的描述，例如「XADD with ACKED option and MAXLEN after DEBUG RELOAD」。

**判斷依據**：diff 中新增的測試名稱。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5809 (cache hit 5760) ｜ completion tokens 1312 ｜ PR #6</sub>