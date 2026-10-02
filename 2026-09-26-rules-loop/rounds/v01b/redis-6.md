<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 Redis 版本從 8.2.0 升級至 8.2.1，並包含多項錯誤修正與測試改進。主要變更包括：在複製資料庫清空期間暫時停用主動碎片整理以避免潛在問題、修正 stream 在無消費者群組參考時可能發生的崩潰、以及新增相關測試。整體風險中等，需特別注意 replication.c 中恢復 active_defrag_enabled 的邏輯可能未正確處理原始設定，以及 stream.c 中新增的提前返回可能改變既有行為。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/replication.c:1961` | 恢復 active_defrag_enabled 時未使用原始值 | 0.80 |
| ⚠️ | Major | `src/t_stream.c:2708` | streamEntryIsReferenced 在無 cgroups_ref 時提前返回 1 可能導致錯誤 | 0.75 |
| 🔸 | Minor | `tests/unit/memefficiency.tcl:70` | 測試輔助函式 discard_replies_every 的參數名稱可能造成混淆 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/replication.c:1961</code> 恢復 active_defrag_enabled 時未使用原始值</summary>

在 `rdbLoadEmptyDbFunc` 中，程式碼先將 `server.active_defrag_enabled` 設為 0，但在清空資料庫後直接將其設為 1，而非恢復為先前的值（`orig_active_defrag`）。這可能導致如果原始設定為停用（0），函式結束後主動碎片整理會被意外啟用。

**失敗情境**：若使用者在設定檔中停用主動碎片整理（`activedefrag no`），當複製同步觸發資料庫清空時，此函式會將該設定強制改為啟用，之後可能導致不必要的效能影響或非預期行為。

**建議修法**：將最後一行改為 `server.active_defrag_enabled = orig_active_defrag;`

**判斷依據**：diff 中新增的程式碼片段顯示 `int orig_active_defrag = server.active_defrag_enabled;` 被儲存但未使用，且最後直接指派為 1。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2708</code> streamEntryIsReferenced 在無 cgroups_ref 時提前返回 1 可能導致錯誤</summary>

新增的 `if (!s->cgroups_ref) return 1;` 會在 stream 沒有消費者群組參考時直接返回 1（表示被參考）。這可能導致某些依賴此函式的邏輯（例如刪除或修剪）誤判訊息仍被參考，進而無法正確釋放記憶體或執行操作。

**失敗情境**：當一個 stream 從未有消費者群組時，呼叫 `streamEntryIsReferenced` 會錯誤地回報為已參考，可能阻止合法的刪除或修剪操作。

**建議修法**：確認此行為是否為預期。若無消費者群組時應視為未參考，應返回 0；若確實需要返回 1，應在程式碼中加上註解說明原因。

**判斷依據**：diff 中新增的這一行在檢查 `s->cgroups_ref` 為 NULL 時直接返回 1，與函式名稱「IsReferenced」的語意可能衝突。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/memefficiency.tcl:70</code> 測試輔助函式 discard_replies_every 的參數名稱可能造成混淆</summary>

新增的 `discard_replies_every` 函式參數 `frequency` 與 `discard_num` 的用途不夠直觀。從呼叫方式 `discard_replies_every $rd $count 10000 10000` 來看，`frequency` 是檢查的間隔，`discard_num` 是要丟棄的回覆數量。但函式內部的條件 `if {$count % $frequency != 0}` 表示只有在 `count` 不是 `frequency` 的倍數時才丟棄，這與函式名稱「every」的語意可能相反。

**建議**：考慮重新命名參數或調整邏輯，使其更清晰。

**判斷依據**：diff 中新增的函式定義，其條件判斷與常見的「每 N 次」邏輯相反。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5819 (cache hit 5760) ｜ completion tokens 1124 ｜ PR #6</sub>