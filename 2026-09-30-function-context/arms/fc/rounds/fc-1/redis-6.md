<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Redis 版本從 8.2.0 更新至 8.2.1，並包含多項修正：停用複製資料庫清空期間的主動碎片整理、修正 stream 在 RDB 載入後因缺少 cgroups_ref 可能導致的當機、新增相關測試。主要風險在於 replication.c 中恢復 active_defrag_enabled 的方式可能不正確，以及 streamEntryIsReferenced 的修正可能改變既有行為。建議優先修正 replication.c 的設定恢復邏輯。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/replication.c:1962` | active_defrag_enabled 恢復為硬編碼 1，忽略原始設定 | 0.95 |
| ⚠️ | Major | `src/t_stream.c:2708` | streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1 可能過度保留資料 | 0.80 |
| 🔸 | Minor | `tests/unit/memefficiency.tcl:70` | discard_replies_every 函式參數名稱可能造成混淆 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/replication.c:1962</code> active_defrag_enabled 恢復為硬編碼 1，忽略原始設定</summary>

在 `rdbLoadEmptyDbFunc` 中，程式碼先將 `server.active_defrag_enabled` 存到 `orig_active_defrag`，然後設為 0，但在 `emptyData` 之後卻直接設為 1，而不是恢復為 `orig_active_defrag`。如果原始設定為 0（例如使用者停用主動碎片整理），此函式會意外地啟用它，可能導致非預期的碎片整理行為。

失敗情境：使用者設定 `activedefrag no`，然後執行會觸發 `rdbLoadEmptyDbFunc` 的操作（例如複製同步），之後主動碎片整理會被意外啟用。

建議修改：
```c
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
註解說要恢復原始設定，但實際卻設為 1。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2708</code> streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1 可能過度保留資料</summary>

新增的 `if (!s->cgroups_ref) return 1;` 在沒有 consumer group references 時回傳 1，表示該 entry 被引用。這可能導致在沒有 PEL 的情況下，stream 的 entry 永遠不會被刪除，造成記憶體洩漏或資料無法清理。

失敗情境：建立 stream 並建立 consumer group，但沒有任何 PEL 條目（例如所有訊息都已 ack），然後執行 XADD MAXLEN 或 XTRIM，預期會刪除舊 entry，但因為 `cgroups_ref` 為 NULL 而回傳 1，導致 entry 被保留。

建議：確認此修正是否為了解決特定 crash，並評估是否應回傳 0 或進行其他處理。

**判斷依據**：diff 中新增的這一行，位於 `streamEntryIsReferenced` 函式內，在檢查 PEL 之前。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/memefficiency.tcl:70</code> discard_replies_every 函式參數名稱可能造成混淆</summary>

新定義的 `discard_replies_every` 函式參數 `frequency` 和 `discard_num` 的命名可能不夠清晰。`frequency` 實際上是「每多少筆丟棄一次」，而 `discard_num` 是「每次丟棄的回覆數」。建議改名為 `discard_interval` 和 `replies_per_discard` 以提高可讀性。

**判斷依據**：diff 中新增的函式定義。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 23032 (cache hit 1536) ｜ completion tokens 1030 ｜ PR #6</sub>