<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 Redis 版本從 8.2.0 更新至 8.2.1，並包含三個主要變更：修正複製時資料庫清空期間可能觸發主動碎片整理的競態、修正 stream 在沒有消費者群組參考時 XADD ACKED 選項可能導致的崩潰，以及重構測試程式碼以減少重複。整體風險中等，主要問題在於 replication.c 中恢復 active_defrag_enabled 時硬編碼為 1，可能覆蓋原始設定；此外，t_stream.c 的修正可能改變既有行為，需要進一步驗證。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/replication.c:1961` | 硬編碼恢復 active_defrag_enabled 可能覆蓋原始設定 | 0.90 |
| ⚠️ | Major | `src/t_stream.c:2708` | streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1 可能導致記憶體洩漏或錯誤保留 | 0.80 |
| 🔸 | Minor | `tests/unit/memefficiency.tcl:70` | 測試輔助函式 discard_replies_every 的參數名稱與用途不符 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/replication.c:1961</code> 硬編碼恢復 active_defrag_enabled 可能覆蓋原始設定</summary>

在 rdbLoadEmptyDbFunc 中，暫時停用主動碎片整理後，恢復時直接設定 `server.active_defrag_enabled = 1;`，但原始值可能為 0（例如使用者明確停用）。這會導致複製同步後主動碎片整理被意外啟用，可能影響效能或造成非預期行為。建議改為 `server.active_defrag_enabled = orig_active_defrag;`。

**判斷依據**：diff 中新增的兩行程式碼：`int orig_active_defrag = server.active_defrag_enabled;` 與 `server.active_defrag_enabled = 1;`。變數 orig_active_defrag 被儲存但未使用，且恢復值硬編碼為 1。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2708</code> streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1 可能導致記憶體洩漏或錯誤保留</summary>

新增的 `if (!s->cgroups_ref) return 1;` 會在沒有消費者群組參考時直接回傳 1（表示被參考），這可能導致某些清理邏輯（如 XADD MAXLEN 修剪）無法刪除實際上未被參考的條目，造成記憶體使用增加。需要確認此行為是否符合預期，並考慮是否應回傳 0。

**判斷依據**：diff 中新增的一行，位於 streamEntryIsReferenced 函式內，在原本的 raxFind 之前。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/memefficiency.tcl:70</code> 測試輔助函式 discard_replies_every 的參數名稱與用途不符</summary>

函式參數 `discard_num` 在呼叫時傳入的值（如 10000、20000）代表要丟棄的回覆總數，但函式內部的迴圈是 `for {set k 0} {$k < $discard_num} {incr k}`，這會丟棄 `discard_num` 次回覆，而不是每 `frequency` 次丟棄 `discard_num` 個。這可能導致測試行為與預期不同，特別是在 `discard_num` 大於 `frequency` 時。建議重新命名參數或調整邏輯。

**判斷依據**：diff 中新增的函式定義，以及後續呼叫如 `discard_replies_every $rd $count 10000 10000`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5809 (cache hit 4736) ｜ completion tokens 978 ｜ PR #6</sub>