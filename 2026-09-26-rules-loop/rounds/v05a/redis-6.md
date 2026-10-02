<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 Redis 版本從 8.2.0 更新至 8.2.1，並包含三個主要變更：在複製資料庫清空期間暫時停用主動碎片整理、修正 stream 中 cgroups_ref 為 NULL 時的參考檢查、以及新增/重構測試。主要風險在於 replication.c 中恢復 active_defrag_enabled 時硬編碼為 1，可能覆蓋原始設定；stream 修正的邏輯正確性需進一步確認；測試程式碼的輔助函式 discard_replies_every 在特定條件下可能未讀取足夠的回覆，導致測試不穩定。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/replication.c:1961` | 恢復 active_defrag_enabled 時硬編碼為 1，可能覆蓋原始設定 | 0.90 |
| ⚠️ | Major | `src/t_stream.c:2707` | streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1 可能不正確 | 0.70 |
| 🔸 | Minor | `tests/unit/memefficiency.tcl:70` | discard_replies_every 在 count 為 frequency 倍數時未讀取任何回覆 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/replication.c:1961</code> 恢復 active_defrag_enabled 時硬編碼為 1，可能覆蓋原始設定</summary>

在 rdbLoadEmptyDbFunc 中，程式碼先將 server.active_defrag_enabled 儲存於 orig_active_defrag，但在 emptyData 呼叫後卻直接設定為 1，而非還原為 orig_active_defrag。若原始設定為 0（例如使用者停用主動碎片整理），此函式會意外啟用該功能，可能導致非預期的效能影響或行為變更。

建議修改為：
```c
server.active_defrag_enabled = orig_active_defrag;
```

**判斷依據**：diff 中新增的程式碼片段：
```c
+    int orig_active_defrag = server.active_defrag_enabled;
+    server.active_defrag_enabled = 0;
+
     emptyData(-1, empty_db_flags, replicationEmptyDbCallback);
+
+    /* Restore the original active defragmentation setting. */
+    server.active_defrag_enabled = 1;
```
變數 orig_active_defrag 被儲存但未使用，且恢復值固定為 1，與註解「Restore the original」矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2707</code> streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1 可能不正確</summary>

新增的檢查 `if (!s->cgroups_ref) return 1;` 表示當 stream 沒有 consumer groups 時，直接回傳 1（視為被引用）。這可能導致某些刪除或修剪操作無法正確進行，因為函式名稱暗示應回傳是否被引用，而 NULL cgroups_ref 通常代表沒有 group，理論上應回傳 0。需要確認此處的邏輯是否符合預期，並檢查所有呼叫此函式的地方是否依賴此行為。

**判斷依據**：diff 中新增的程式碼片段：
```c
+    if (!s->cgroups_ref) return 1;
```
此函式原本會直接呼叫 raxFind(s->cgroups_ref, ...)，若 s->cgroups_ref 為 NULL 可能導致 crash。但回傳 1 可能掩蓋了真正的引用狀態，需進一步分析。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/memefficiency.tcl:70</code> discard_replies_every 在 count 為 frequency 倍數時未讀取任何回覆</summary>

輔助函式 discard_replies_every 的條件為 `if {$count % $frequency != 0}`，表示當 count 剛好是 frequency 的倍數時，不會讀取任何回覆。這可能導致測試中累積未讀取的回覆，最終造成記憶體耗盡或測試逾時。建議改為 `if {$count % $frequency == 0}` 或調整邏輯以確保在正確時機讀取。

**判斷依據**：diff 中新增的輔助函式，其條件判斷與原本內嵌的邏輯相反。原本的程式碼是 `if {$count % 10000 == 0}` 才讀取，而新函式在不等於 0 時讀取，可能造成行為不一致。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5795 (cache hit 4736) ｜ completion tokens 1166 ｜ PR #6</sub>