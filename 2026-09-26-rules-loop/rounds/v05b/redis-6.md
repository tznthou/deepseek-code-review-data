<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Redis 版本從 8.2.0 升級至 8.2.1，並包含三個主要變更：修正複製期間資料庫清空時可能觸發 active defrag 的問題、修正 stream 在沒有 consumer group 參考時可能誤判為已參考的邏輯錯誤，以及新增對應的測試。整體風險中等，主要問題在於 replication.c 中恢復 active defrag 設定時硬編碼為 1，可能破壞使用者原本的設定；此外 t_stream.c 的修正可能改變既有行為，需確認是否為預期。建議修正後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/replication.c:1962` | 恢復 active defrag 設定時硬編碼為 1，可能覆蓋使用者設定 | 0.90 |
| ⚠️ | Major | `src/t_stream.c:2708` | streamEntryIsReferenced 在無 cgroups_ref 時回傳 1，可能導致資料無法刪除 | 0.80 |
| 🔸 | Minor | `src/replication.c:1953` | 註解與程式碼行為不一致 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/replication.c:1962</code> 恢復 active defrag 設定時硬編碼為 1，可能覆蓋使用者設定</summary>

在 `rdbLoadEmptyDbFunc` 中，暫時停用 active defrag 後，恢復時直接設定 `server.active_defrag_enabled = 1`，但原始值可能為 0（使用者停用）。這會導致複製同步後 active defrag 被意外啟用，違反使用者設定。

**失敗情境**：使用者設定 `activedefrag no`，當複製觸發資料庫清空時，此函式會將 `active_defrag_enabled` 設為 1，之後 active defrag 便會開始運作，可能造成不必要的效能影響。

**建議**：使用先前儲存的 `orig_active_defrag` 變數來恢復設定：
```c
server.active_defrag_enabled = orig_active_defrag;
```

**判斷依據**：diff 中新增的程式碼：
```c
+    int orig_active_defrag = server.active_defrag_enabled;
+    server.active_defrag_enabled = 0;
...
+    server.active_defrag_enabled = 1;
```
變數 `orig_active_defrag` 已儲存原始值，但恢復時未使用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2708</code> streamEntryIsReferenced 在無 cgroups_ref 時回傳 1，可能導致資料無法刪除</summary>

新增的 `if (!s->cgroups_ref) return 1;` 會在 stream 沒有 consumer group 參考時直接回傳 1（表示已參考），這會阻止某些刪除操作（例如 XDEL 或 MAXLEN 修剪）。然而，若沒有 consumer group，該 entry 應被視為未參考，回傳 0 才合理。

**失敗情境**：在沒有 consumer group 的 stream 上執行 XDEL 或 XADD with MAXLEN，可能無法刪除 entry，導致記憶體無法釋放。

**建議**：確認此處邏輯是否應回傳 0。若此修正的目的是處理 DEBUG RELOAD 後 cgroups_ref 為 NULL 的情況，則應回傳 0 表示未參考，而非 1。

**判斷依據**：diff 新增行：`+    if (!s->cgroups_ref) return 1;`
函式名稱 `streamEntryIsReferenced` 語意上應回傳是否被參考，若無 cgroups_ref 則不可能被參考。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/replication.c:1953</code> 註解與程式碼行為不一致</summary>

註解寫「Temporarily disable active defragmentation during database flush」，但實際上是將 `server.active_defrag_enabled` 設為 0，這確實停用 defrag。然而，恢復時使用硬編碼 1，與「restore the original setting」的註解不符。建議修正恢復邏輯後，此問題自然解決。

**判斷依據**：diff 中新增的註解與後續恢復程式碼不一致。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5795 (cache hit 5760) ｜ completion tokens 1076 ｜ PR #6</sub>