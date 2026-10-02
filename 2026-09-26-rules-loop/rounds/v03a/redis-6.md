<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Redis 版本從 8.2.0 升級至 8.2.1，並包含三個主要變更：修正複製時資料庫清空期間可能觸發 active defrag 的競態、修正 stream 在無 consumer group 參考時 XADD ACKED 選項的潛在崩潰，以及重構測試程式碼。整體變更方向正確，但 src/replication.c 中恢復 active defrag 設定的方式存在邏輯錯誤，可能導致設定值被意外覆寫；此外，新增的 stream 修正缺乏對應的單元測試，且測試輔助函式 discard_replies_every 的參數設計容易誤用。建議修正上述問題後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/replication.c:1961` | 恢復 active defrag 設定時硬編碼為 1，忽略原始值 | 0.95 |
| ⚠️ | Major | `src/t_stream.c:2707` | streamEntryIsReferenced 在無 cgroups_ref 時回傳 1 可能導致記憶體洩漏或錯誤保留 | 0.80 |
| 🔸 | Minor | `tests/unit/memefficiency.tcl:70` | discard_replies_every 輔助函式參數設計易誤用 | 0.70 |
| 🔸 | Minor | `tests/unit/type/stream.tcl:266` | 新增的 stream 測試未涵蓋無 cgroups_ref 的 XADD ACKED 情境 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/replication.c:1961</code> 恢復 active defrag 設定時硬編碼為 1，忽略原始值</summary>

在 `rdbLoadEmptyDbFunc` 中，程式碼先將 `server.active_defrag_enabled` 存入 `orig_active_defrag`，然後設為 0，但在 `emptyData` 呼叫後卻直接將 `server.active_defrag_enabled` 設為 1，而非恢復為 `orig_active_defrag`。

**失敗情境**：若使用者在執行 replicaof 之前已將 `activedefrag` 設為 `no`（預設值），此函式執行後會將該設定強制改為 `yes`，導致非預期的記憶體重組行為，可能影響效能或造成其他問題。

**建議修法**：將 `server.active_defrag_enabled = 1;` 改為 `server.active_defrag_enabled = orig_active_defrag;`。

**判斷依據**：diff 中新增的程式碼：
```
+    int orig_active_defrag = server.active_defrag_enabled;
+    server.active_defrag_enabled = 0;
+
     emptyData(-1, empty_db_flags, replicationEmptyDbCallback);
+
+    /* Restore the original active defragmentation setting. */
+    server.active_defrag_enabled = 1;
```
變數 `orig_active_defrag` 被儲存但未使用，且恢復值硬編碼為 1，明顯違反意圖。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2707</code> streamEntryIsReferenced 在無 cgroups_ref 時回傳 1 可能導致記憶體洩漏或錯誤保留</summary>

新增的 `if (!s->cgroups_ref) return 1;` 使得當 stream 沒有 consumer groups 時，函式直接回傳 1（表示被引用）。這可能導致在沒有 consumer groups 的情況下，某些應該被刪除的 stream entry 被錯誤保留，造成記憶體洩漏或資料不一致。

**失敗情境**：當一個 stream 從未有過 consumer group，或所有 consumer groups 都被刪除後，`s->cgroups_ref` 為 NULL。此時呼叫 `streamEntryIsReferenced` 會回傳 1，使得呼叫者認為該 entry 仍被引用，進而跳過刪除。這可能發生在 `XTRIM`、`XADD` 的 MAXLEN 修剪，或 `DEL` 刪除整個 stream 時。

**建議修法**：應回傳 0 而非 1，因為沒有 cgroups_ref 表示沒有任何 consumer group 引用該 entry。或者，應檢查該 entry 是否可能被其他機制引用（例如 PEL），但根據函式邏輯，沒有 cgroups_ref 就代表沒有 PEL 引用。

**判斷依據**：diff 中新增的程式碼：
```
+    if (!s->cgroups_ref) return 1;
```
函式名稱 `streamEntryIsReferenced` 暗示回傳值代表是否被引用，而 `cgroups_ref` 為 NULL 時應代表沒有引用，回傳 1 與直覺相反。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/memefficiency.tcl:70</code> discard_replies_every 輔助函式參數設計易誤用</summary>

新增的 `discard_replies_every` 函式接受 `frequency` 和 `discard_num` 參數，但呼叫時傳入的 `discard_num` 是每次要丟棄的回覆總數，而函式內部迴圈會執行 `discard_num` 次 `$rd read`。這在目前的使用情境下是正確的，但若未來有呼叫者誤解參數意義（例如以為是每次丟棄的數量），可能導致錯誤。

**建議修法**：可考慮將參數命名得更明確，例如 `discard_total`，或改為傳入每次丟棄的數量並在函式內乘以某個倍數。

**判斷依據**：diff 中新增的函式定義，以及多處呼叫如 `discard_replies_every $rd $count 10000 10000` 和 `discard_replies_every $rd $count 10000 20000`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/stream.tcl:266</code> 新增的 stream 測試未涵蓋無 cgroups_ref 的 XADD ACKED 情境</summary>

測試名稱宣稱「XADD with ACKED option doesn't crash after DEBUG RELOAD」，但測試中在第二次 DEBUG RELOAD 後，consumer group 仍然存在（只是 PEL 為空），因此 `s->cgroups_ref` 可能不為 NULL。這無法驗證 `streamEntryIsReferenced` 中新增的 `if (!s->cgroups_ref) return 1;` 分支。

**建議修法**：增加一個測試案例，在完全沒有 consumer group 的情況下（例如從未建立或已刪除所有 groups），執行 XADD ACKED，以確保該分支被覆蓋。

**判斷依據**：diff 中新增的測試程式碼，但未包含刪除 consumer group 的步驟。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5829 (cache hit 4736) ｜ completion tokens 1772 ｜ PR #6</sub>