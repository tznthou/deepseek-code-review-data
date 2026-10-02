<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Redis 版本從 8.2.0 更新至 8.2.1，並包含多項錯誤修正與測試變更。主要風險在於 `src/replication.c` 中對 `active_defrag_enabled` 的處理：程式碼在 `emptyData` 後無條件將該全域變數設為 1，若原本為 0（例如使用者停用 defrag），會意外啟用 defrag，可能造成效能影響或非預期行為。此外，`src/t_stream.c` 中新增的 `if (!s->cgroups_ref) return 1;` 可能改變既有語意，需確認是否會導致記憶體洩漏或錯誤的刪除行為。測試程式碼的變更主要為重構，風險較低。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/replication.c:1961` | 無條件將 active_defrag_enabled 設為 1，可能意外啟用 defrag | 0.95 |
| ⚠️ | Major | `src/t_stream.c:2708` | streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1，可能導致記憶體洩漏 | 0.70 |
| 🔸 | Minor | `tests/unit/memefficiency.tcl:70` | 測試輔助函式 discard_replies_every 的參數名稱可能造成混淆 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/replication.c:1961</code> 無條件將 active_defrag_enabled 設為 1，可能意外啟用 defrag</summary>

在 `rdbLoadEmptyDbFunc` 中，程式碼先將 `server.active_defrag_enabled` 設為 0，呼叫 `emptyData` 後再無條件設為 1。如果原本 `active_defrag_enabled` 為 0（例如使用者透過設定停用 defrag），此函式會錯誤地啟用 defrag，可能導致非預期的記憶體重整行為，甚至影響效能或穩定性。

建議改為儲存原始值並在最後恢復：
```c
int orig_active_defrag = server.active_defrag_enabled;
server.active_defrag_enabled = 0;
emptyData(-1, empty_db_flags, replicationEmptyDbCallback);
server.active_defrag_enabled = orig_active_defrag;
```

**判斷依據**：diff 中新增的程式碼：
```c
+    int orig_active_defrag = server.active_defrag_enabled;
+    server.active_defrag_enabled = 0;
+
     emptyData(-1, empty_db_flags, replicationEmptyDbCallback);
+
+    /* Restore the original active defragmentation setting. */
+    server.active_defrag_enabled = 1;
```
變數 `orig_active_defrag` 被儲存但未使用，且最後直接指派為 1，而非恢復原值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2708</code> streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1，可能導致記憶體洩漏</summary>

新增的 `if (!s->cgroups_ref) return 1;` 會在沒有 consumer groups 時直接回傳 1（表示被引用）。這可能導致某些清理邏輯（例如 `XADD ... ACKED` 或 `XTRIM`）誤以為 entry 仍被引用而無法刪除，造成記憶體洩漏或資料殘留。需要確認此變更的意圖：若沒有 cgroups，entry 應視為未被引用（回傳 0）才合理。建議檢查相關呼叫點，並考慮回傳 0 或調整邏輯。

**判斷依據**：diff 中新增的一行：
```c
+    if (!s->cgroups_ref) return 1;
```
此函式原本會執行 `raxFind(s->cgroups_ref, ...)`，若 `s->cgroups_ref` 為 NULL 會導致 crash。但回傳 1 可能掩蓋了真正的語意。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/memefficiency.tcl:70</code> 測試輔助函式 discard_replies_every 的參數名稱可能造成混淆</summary>

新函式 `discard_replies_every` 的參數 `frequency` 和 `discard_num` 在呼叫時傳入的值相同（例如 10000），但語意不同：`frequency` 是觸發間隔，`discard_num` 是每次丟棄的回覆數。雖然目前呼叫都一致，但未來可能誤用。建議在函式內加入註解或改用更明確的參數名稱。

**判斷依據**：diff 中新增的函式定義。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4818 (cache hit 4736) ｜ completion tokens 1147 ｜ PR #6</sub>