<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 Redis 版本從 8.2.0 升級至 8.2.1，包含三個主要變更：修正複製期間資料庫清空時主動碎片整理可能造成的問題、修正 stream 中 consumer group 參考為空時可能導致的崩潰，以及新增對應的測試。整體風險中等，主要疑慮在於 replication.c 中恢復 active_defrag_enabled 時硬編碼為 1，可能覆蓋原本的設定值；此外，stream.c 的修正可能改變既有行為，需確認其正確性。建議合併前先處理此問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/replication.c:1962` | 硬編碼恢復 active_defrag_enabled 可能覆蓋原始設定 | 0.80 |
| ⚠️ | Major | `src/t_stream.c:2708` | streamEntryIsReferenced 在 cgroups_ref 為空時回傳 1 可能導致錯誤保留 | 0.70 |
| 🔸 | Minor | `tests/unit/memefficiency.tcl:70` | 測試輔助函式 discard_replies_every 的參數名稱可能造成混淆 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/replication.c:1962</code> 硬編碼恢復 active_defrag_enabled 可能覆蓋原始設定</summary>

在 `rdbLoadEmptyDbFunc` 中，暫時停用 active defrag 後，恢復時直接設定 `server.active_defrag_enabled = 1;`，而非使用先前儲存的 `orig_active_defrag`。這可能導致如果原始設定為 0（例如使用者明確停用），在複製同步後被意外啟用。建議改為 `server.active_defrag_enabled = orig_active_defrag;`。

**判斷依據**：diff 中新增的程式碼：
```c
+    int orig_active_defrag = server.active_defrag_enabled;
+    server.active_defrag_enabled = 0;
...
+    server.active_defrag_enabled = 1;
```
變數 `orig_active_defrag` 被儲存但未使用，且恢復值硬編碼為 1。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2708</code> streamEntryIsReferenced 在 cgroups_ref 為空時回傳 1 可能導致錯誤保留</summary>

新增的 `if (!s->cgroups_ref) return 1;` 會在沒有 consumer group 參考時直接回傳 1，表示該 entry 被引用。這可能導致在沒有 consumer group 的情況下，stream 的 entry 永遠不會被刪除，即使已達 MAXLEN 限制。需確認此行為是否符合預期，特別是在沒有 consumer group 的 stream 上使用 `XADD ... MAXLEN` 時。

**判斷依據**：diff 中新增的程式碼：
```c
+    if (!s->cgroups_ref) return 1;
```
此函式用於判斷 entry 是否被引用，若無 cgroups_ref 則回傳 1 可能造成記憶體無法釋放。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/memefficiency.tcl:70</code> 測試輔助函式 discard_replies_every 的參數名稱可能造成混淆</summary>

函式 `discard_replies_every` 的參數 `frequency` 和 `discard_num` 語意不明確，且呼叫時傳入的數值（如 10000 和 10000）可能讓讀者難以理解其用途。建議重新命名參數或加入註解說明。

**判斷依據**：diff 中新增的函式定義，參數名稱未清楚表達其用途。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5311 (cache hit 4736) ｜ completion tokens 896 ｜ PR #6</sub>