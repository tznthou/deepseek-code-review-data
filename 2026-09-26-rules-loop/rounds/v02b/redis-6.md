<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Redis 版本從 8.2.0 更新至 8.2.1，包含三個主要變更：修正複製期間資料庫 flush 時可能觸發 active defrag 的問題、修正 stream 在沒有 consumer group 參考時 XADD ACKED 選項可能導致的崩潰，以及新增對應的測試。整體變更範圍小且目標明確，但 replication.c 中的修正存在一個明確的邏輯錯誤：在 emptyData 之後無條件將 active_defrag_enabled 設為 1，而非還原為原始值，這可能導致原本停用 defrag 的伺服器在複製後意外啟用 defrag。此外，stream.c 的修正雖然解決了 null 指標問題，但回傳值 1 的語意可能與函式名稱不符，需進一步確認。建議先修正 replication.c 的還原邏輯再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/replication.c:1961` | active_defrag_enabled 未正確還原為原始值 | 0.95 |
| ⚠️ | Major | `src/t_stream.c:2708` | streamEntryIsReferenced 在無 cgroups_ref 時回傳 1 可能誤導呼叫者 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/replication.c:1961</code> active_defrag_enabled 未正確還原為原始值</summary>

在 `rdbLoadEmptyDbFunc` 中，程式碼先將 `server.active_defrag_enabled` 儲存至 `orig_active_defrag`，然後設為 0，但在 `emptyData` 呼叫後，卻直接設為 1，而非還原為 `orig_active_defrag`。這會導致原本停用 active defrag 的伺服器在執行複製同步後，意外啟用 active defrag，可能造成非預期的記憶體整理行為與效能影響。

建議修正：
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
註解聲稱要還原原始設定，但實際卻寫死為 1。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2708</code> streamEntryIsReferenced 在無 cgroups_ref 時回傳 1 可能誤導呼叫者</summary>

新增的 `if (!s->cgroups_ref) return 1;` 避免了 null 指標解參考，但回傳 1 表示該 entry 被引用，這可能導致呼叫者認為該 entry 仍被 consumer group 參考，而無法刪除。然而，若 `cgroups_ref` 為 null，表示沒有任何 consumer group 參考此 stream，因此該 entry 實際上並未被任何 group 參考，回傳 0 可能更為正確。需要確認此函式的呼叫者如何處理回傳值，以判斷此行為是否會造成問題。

**判斷依據**：diff 中新增的一行：
```c
+    if (!s->cgroups_ref) return 1;
```
此函式名稱暗示回傳值代表 entry 是否被引用，但回傳 1 可能與實際狀態不符。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5819 (cache hit 5760) ｜ completion tokens 873 ｜ PR #6</sub>