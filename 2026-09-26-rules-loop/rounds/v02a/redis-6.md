<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Redis 版本從 8.2.0 更新至 8.2.1，並包含三個主要變更：修正複製期間資料庫清空時可能觸發 active defrag 的問題、修正 stream 在沒有 consumer group 時 XADD ACKED 選項可能導致 crash 的問題，以及新增對應的測試。整體變更範圍小且聚焦，但 replication.c 中的修正存在一個明確的邏輯錯誤：恢復 active defrag 設定時硬編碼為 1，而非使用先前儲存的值，這可能導致原本停用 defrag 的伺服器在複製後被意外啟用。此外，stream 修正的邏輯值得商榷：在沒有 cgroups_ref 時直接回傳 1（視為已引用）可能掩蓋其他潛在問題，且與函式語意不完全一致。建議修正 replication.c 的恢復邏輯，並重新評估 stream 修正的完整性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/replication.c:1961` | Active defrag 設定恢復錯誤：硬編碼為 1 而非原始值 | 0.95 |
| ⚠️ | Major | `src/t_stream.c:2707` | streamEntryIsReferenced 在無 cgroups_ref 時回傳 1 可能掩蓋問題 | 0.70 |
| 🔸 | Minor | `tests/unit/memefficiency.tcl:70` | 測試輔助函式 discard_replies_every 的邏輯可能不正確 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/replication.c:1961</code> Active defrag 設定恢復錯誤：硬編碼為 1 而非原始值</summary>

在 `rdbLoadEmptyDbFunc` 中，程式碼先將 `server.active_defrag_enabled` 儲存於 `orig_active_defrag`，然後在 `emptyData` 呼叫後直接設定為 1，而非恢復為 `orig_active_defrag`。這會導致原本停用 active defrag 的伺服器在複製同步後被意外啟用，可能造成不必要的效能影響或行為改變。

**失敗情境**：若使用者設定 `activedefrag no`，在複製同步觸發資料庫清空後，active defrag 會被強制啟用，直到下次設定變更。

**建議修法**：將 `server.active_defrag_enabled = 1;` 改為 `server.active_defrag_enabled = orig_active_defrag;`

**判斷依據**：diff 中新增的程式碼片段：
```
+    int orig_active_defrag = server.active_defrag_enabled;
+    server.active_defrag_enabled = 0;
+
     emptyData(-1, empty_db_flags, replicationEmptyDbCallback);
+
+    /* Restore the original active defragmentation setting. */
+    server.active_defrag_enabled = 1;
```
儲存了原始值但未使用，直接設定為 1，明顯違反意圖。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2707</code> streamEntryIsReferenced 在無 cgroups_ref 時回傳 1 可能掩蓋問題</summary>

新增的檢查 `if (!s->cgroups_ref) return 1;` 在沒有 consumer group 參考時直接回傳 1（表示已引用）。這使得呼叫者認為該 entry 被引用，因此不會刪除它。然而，此函式的語意是檢查 entry 是否被任何 consumer group 的 PEL 引用，若無 cgroups_ref，理論上應回傳 0（未引用）。回傳 1 可能導致記憶體洩漏或錯誤的保留行為，特別是在其他呼叫情境中。

**失敗情境**：若未來有其他程式碼路徑呼叫此函式，且預期在無 cgroups_ref 時回傳 0，則此變更會造成錯誤。

**建議修法**：應回傳 0 而非 1，或確認所有呼叫者都能接受此行為。

**判斷依據**：diff 中新增的程式碼：
```
+    if (!s->cgroups_ref) return 1;
```
此回傳值與函式名稱及註解不符，且可能影響其他呼叫者。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/memefficiency.tcl:70</code> 測試輔助函式 discard_replies_every 的邏輯可能不正確</summary>

新增的 `discard_replies_every` 函式在 `count % frequency != 0` 時執行丟棄，這表示只有當 count 不是 frequency 的倍數時才丟棄。但原本的程式碼是在 `count % 10000 == 0` 時丟棄，兩者邏輯相反。這可能導致測試行為改變，甚至無法正確丟棄回覆，造成記憶體累積或測試失敗。

**失敗情境**：若測試依賴定期丟棄回覆以避免記憶體耗盡，此變更可能導致測試不穩定或失敗。

**建議修法**：確認條件是否應為 `if {$count % $frequency == 0}`，或調整函式名稱與實作。

**判斷依據**：diff 中新增的函式，條件與原本的 `if {$count % 10000 == 0}` 相反。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5819 (cache hit 1536) ｜ completion tokens 1364 ｜ PR #6</sub>