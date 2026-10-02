<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 Redis 版本從 8.2.0 升級至 8.2.1，並包含多項錯誤修正與測試變更。主要變更包括：在複製資料庫清空期間暫時停用主動碎片整理、修正 stream 中 consumer group 參考為 NULL 時的潛在崩潰、更新版本號、重構測試程式碼並新增測試案例。整體風險中等，需特別注意 replication.c 中 active_defrag_enabled 的恢復邏輯可能未正確處理原始狀態，以及 t_stream.c 中新增的 NULL 檢查可能改變既有行為。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/replication.c:1962` | active_defrag_enabled 恢復邏輯可能錯誤 | 0.80 |
| ⚠️ | Major | `src/t_stream.c:2708` | streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1 可能不正確 | 0.75 |
| 🔸 | Minor | `tests/unit/memefficiency.tcl:70` | discard_replies_every 函式參數名稱可能造成混淆 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/replication.c:1962</code> active_defrag_enabled 恢復邏輯可能錯誤</summary>

在 `rdbLoadEmptyDbFunc` 中，程式碼先將 `server.active_defrag_enabled` 儲存至 `orig_active_defrag`，然後設為 0，但在 `emptyData` 呼叫後卻直接設為 1，而非恢復為 `orig_active_defrag`。這可能導致如果原始設定為 0（停用），在清空資料庫後主動碎片整理會被意外啟用。

**失敗情境**：若使用者在設定中停用主動碎片整理（`activedefrag no`），且複製同步觸發資料庫清空，則清空後主動碎片整理會被強制啟用，可能造成非預期的效能影響或行為變更。

**建議修法**：將 `server.active_defrag_enabled = 1;` 改為 `server.active_defrag_enabled = orig_active_defrag;`

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
註解聲稱要恢復原始設定，但實際卻硬編碼為 1。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2708</code> streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1 可能不正確</summary>

新增的檢查 `if (!s->cgroups_ref) return 1;` 表示當 stream 沒有 consumer groups 參考時，直接回傳 1（已參考）。這可能導致呼叫者認為該 entry 被參考而無法刪除，即使實際上沒有 consumer group 參考它。

**失敗情境**：若某個 stream entry 僅存在於 stream 本身，且沒有 consumer group 參考，此函式會錯誤回傳 1，使得呼叫者（例如 `streamTrim` 或 `XADD` 的 MAXLEN 修剪）無法刪除該 entry，造成記憶體無法釋放或修剪行為不正確。

**建議修法**：應回傳 0 表示未參考，或檢查呼叫者邏輯是否依賴此行為。需確認原始意圖：若無 cgroups_ref，則 entry 不可能被 PEL 參考，因此應回傳 0。

**判斷依據**：diff 中新增的程式碼：
```
+    if (!s->cgroups_ref) return 1;
     unsigned char buf[sizeof(streamID)];
     streamEncodeID(buf, id);
     return raxFind(s->cgroups_ref, buf, sizeof(streamID), NULL);
```
此檢查在原本的 `raxFind` 之前，若 `cgroups_ref` 為 NULL，原本的 `raxFind` 可能導致 crash，但回傳 1 可能造成邏輯錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/memefficiency.tcl:70</code> discard_replies_every 函式參數名稱可能造成混淆</summary>

函式 `discard_replies_every` 的參數 `frequency` 和 `discard_num` 在呼叫時傳入相同的值（例如 10000），但函式內部的邏輯是當 `count % frequency == 0` 時，丟棄 `discard_num` 個回覆。這可能造成閱讀上的混淆，因為 `frequency` 和 `discard_num` 通常不會相同。

**建議**：可考慮重新命名參數或加入註解說明，但此為測試程式碼，影響有限。

**判斷依據**：diff 中新增的函式定義，以及後續呼叫如 `discard_replies_every $rd $count 10000 10000`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5311 (cache hit 5248) ｜ completion tokens 1246 ｜ PR #6</sub>