<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Redis 版本從 8.2.0 升級至 8.2.1，並包含三個主要修正：在複製同步清空資料庫時暫時停用主動碎片整理、修正 stream 在無消費者群組參考時可能發生的崩潰，以及新增對應的測試。整體變更範圍小且目標明確，但 replication.c 中恢復 active_defrag_enabled 的方式存在邏輯缺陷，可能導致設定值被錯誤覆寫，建議修正後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/replication.c:1961` | 恢復 active_defrag_enabled 時未使用原始值，可能覆寫使用者設定 | 0.95 |
| ⚠️ | Major | `src/t_stream.c:2708` | streamEntryIsReferenced 在無 cgroups_ref 時直接回傳 1，可能導致記憶體洩漏或錯誤保留 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>src/replication.c:1961</code> 恢復 active_defrag_enabled 時未使用原始值，可能覆寫使用者設定</summary>

在 `rdbLoadEmptyDbFunc` 中，程式碼先將 `server.active_defrag_enabled` 儲存於 `orig_active_defrag`，然後設為 0，但在清空資料庫後卻直接設回 1，而非使用 `orig_active_defrag`。

**失敗情境**：若使用者在執行 `REPLICAOF` 前已將 `activedefrag` 設為 `no`，此函式執行後會將該設定強制改為 `yes`，導致非預期的行為變更。

**建議修法**：將 `server.active_defrag_enabled = 1;` 改為 `server.active_defrag_enabled = orig_active_defrag;`。

**判斷依據**：diff 中新增的程式碼：
```c
+    int orig_active_defrag = server.active_defrag_enabled;
+    server.active_defrag_enabled = 0;
...
+    server.active_defrag_enabled = 1;
```
變數 `orig_active_defrag` 被儲存但從未被使用，且恢復時使用常數 1，明顯與註解「Restore the original」矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2708</code> streamEntryIsReferenced 在無 cgroups_ref 時直接回傳 1，可能導致記憶體洩漏或錯誤保留</summary>

新增的 `if (!s->cgroups_ref) return 1;` 使得當 stream 沒有消費者群組參考時，函式直接回傳 1（表示被參考）。這可能導致呼叫者認為該 entry 仍被參考而無法刪除，造成記憶體無法釋放。

**失敗情境**：若某個 stream 從未有消費者群組，且呼叫 `streamEntryIsReferenced` 來判斷是否可刪除 entry，此函式會錯誤地回傳 1，使 entry 永遠無法被刪除。

**建議修法**：確認此處的意圖。若無 cgroups_ref 即代表沒有 PEL 參考，應回傳 0；若此函式僅用於特定情境（如 ACKED 選項），請補充註解說明為何回傳 1 是安全的。

**判斷依據**：diff 中新增的這一行直接回傳 1，但函式名稱與上下文暗示應回傳是否被參考。若無參考，邏輯上應回傳 0。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5819 (cache hit 4736) ｜ completion tokens 858 ｜ PR #6</sub>