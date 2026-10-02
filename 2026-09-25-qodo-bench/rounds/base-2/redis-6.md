<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Redis 版本從 8.2.0 升級至 8.2.1，並包含多項錯誤修正與測試變更。主要風險在於 replication.c 中對 active defrag 的暫時停用與恢復邏輯，可能因未使用原始值恢復而導致設定不一致；t_stream.c 的 null 檢查可能改變既有行為；測試程式碼的輔助函式 discard_replies_every 存在邏輯錯誤，可能導致測試不穩定。建議優先修正 replication.c 的恢復邏輯與測試輔助函式。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/replication.c:1961` | active_defrag_enabled 恢復為硬編碼 1，未使用原始值 | 0.95 |
| ⚠️ | Major | `tests/unit/memefficiency.tcl:70` | discard_replies_every 輔助函式邏輯錯誤：只在 count 為 frequency 的倍數時丟棄回覆 | 0.85 |
| ⚠️ | Major | `src/t_stream.c:2707` | streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1，可能導致記憶體洩漏或錯誤保留 | 0.80 |
| 🔸 | Minor | `tests/unit/memefficiency.tcl:982` | 測試中 config set activedefrag yes 可能失敗，但未正確處理 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/replication.c:1961</code> active_defrag_enabled 恢復為硬編碼 1，未使用原始值</summary>

在 rdbLoadEmptyDbFunc 中，程式碼先將 server.active_defrag_enabled 儲存於 orig_active_defrag，但在 emptyData 呼叫後卻直接設定為 1，而非恢復為 orig_active_defrag。若原始值為 0（例如使用者明確停用 active defrag），此函式會意外啟用 active defrag，導致行為不一致。

失敗情境：當使用者在設定檔中設定 activedefrag no，且 replica 進行同步時，此函式會將 active_defrag_enabled 設為 1，之後 active defrag 可能被觸發，造成不必要的效能影響或潛在錯誤。

建議修改：
```c
server.active_defrag_enabled = orig_active_defrag;
```

**判斷依據**：diff 中新增的程式碼：
```c
+    int orig_active_defrag = server.active_defrag_enabled;
+    server.active_defrag_enabled = 0;
 
     emptyData(-1, empty_db_flags, replicationEmptyDbCallback);
+
+    /* Restore the original active defragmentation setting. */
+    server.active_defrag_enabled = 1;
```
變數 orig_active_defrag 被儲存但未使用，恢復時直接寫入 1。

</details>

<details><summary>⚠️ <b>Major</b> — <code>tests/unit/memefficiency.tcl:70</code> discard_replies_every 輔助函式邏輯錯誤：只在 count 為 frequency 的倍數時丟棄回覆</summary>

函式 `discard_replies_every` 的條件 `if {$count % $frequency != 0}` 表示當 count 不是 frequency 的倍數時才執行丟棄，這與函式名稱和原本的意圖相反。原本的程式碼是在 count 為 10000 的倍數時丟棄 10000 個回覆，但新函式卻在 count 不是倍數時丟棄，導致回覆未被正確丟棄，可能造成測試客戶端緩衝區累積過多資料，影響測試穩定性。

失敗情境：在測試迴圈中，當 count 達到 10000 的倍數時，不會丟棄任何回覆，而其他時候卻丟棄 10000 個回覆，導致客戶端讀取錯誤的回覆或記憶體耗盡。

建議修改：
```tcl
proc discard_replies_every {rd count frequency discard_num} {
    if {$count % $frequency == 0} {
        for {set k 0} {$k < $discard_num} {incr k} {
            $rd read ; # Discard replies
        }
    }
}
```

**判斷依據**：diff 中新增的函式，條件為 `!= 0`，但原本的程式碼使用 `== 0`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2707</code> streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1，可能導致記憶體洩漏或錯誤保留</summary>

新增的 null 檢查 `if (!s->cgroups_ref) return 1;` 表示當 stream 沒有 consumer groups 時，函式直接回傳 1（視為被引用）。這可能導致呼叫者認為 entry 被引用而無法刪除，造成記憶體洩漏或資料保留過久。

失敗情境：當一個 stream 沒有 consumer groups，且執行 XTRIM 或 MAXLEN 刪除舊 entry 時，此函式回傳 1，導致 entry 被保留，無法正確修剪。

建議：確認此行為是否符合預期。若無 cgroups 時 entry 不應被視為引用，應回傳 0；若此為刻意設計（例如保守處理），應加入註解說明。

**判斷依據**：diff 中新增的一行：
```c
+    if (!s->cgroups_ref) return 1;
```
此檢查在原本的 raxFind 之前，直接回傳 1。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/memefficiency.tcl:982</code> 測試中 config set activedefrag yes 可能失敗，但未正確處理</summary>

在新增的測試中，使用 `catch {$replica config set activedefrag yes} e` 來嘗試啟用 active defrag，但若設定失敗（例如不支援），後續的 `if {[$replica config get activedefrag] eq "activedefrag yes"}` 會進行比較，但若 config get 回傳格式不同，可能導致條件判斷錯誤。此外，若設定失敗，測試會直接跳過後續驗證，可能掩蓋問題。

建議：明確檢查設定是否成功，並在失敗時輸出錯誤訊息或標記測試為 skipped。

**判斷依據**：diff 中新增的測試程式碼片段。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4818 (cache hit 4736) ｜ completion tokens 1633 ｜ PR #6</sub>