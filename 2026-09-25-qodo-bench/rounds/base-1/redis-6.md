<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 Redis 版本從 8.2.0 更新至 8.2.1，並包含多項 bug 修正與測試變更。主要風險在於 replication.c 中 active defrag 的暫時停用與恢復邏輯，以及 t_stream.c 中 streamEntryIsReferenced 的 null 檢查可能改變既有行為。整體而言，變更範圍明確，但需注意 defrag 恢復邏輯的潛在問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/replication.c:1962` | active defrag 恢復邏輯可能錯誤地啟用 defrag | 0.80 |
| ⚠️ | Major | `src/t_stream.c:2708` | streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1 可能導致記憶體洩漏或錯誤保留 | 0.70 |
| 🔸 | Minor | `tests/unit/memefficiency.tcl:70` | discard_replies_every 函式參數名稱可能造成混淆 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/replication.c:1962</code> active defrag 恢復邏輯可能錯誤地啟用 defrag</summary>

在 rdbLoadEmptyDbFunc 中，程式碼先儲存 `orig_active_defrag = server.active_defrag_enabled`，然後將其設為 0，最後在 emptyData 後直接設為 1，而非恢復為 orig_active_defrag。這可能導致原本停用 defrag 的伺服器在同步後意外啟用 defrag。

失敗情境：若使用者在設定檔中將 active-defrag 設為 no，則 server.active_defrag_enabled 初始為 0。當 replica 進行同步時，此函式會將其暫時設為 0，但最後會設為 1，導致 defrag 被意外啟用，可能影響效能或造成非預期行為。

建議：將最後一行改為 `server.active_defrag_enabled = orig_active_defrag;`

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
註解說要恢復原始設定，但實際上是設為 1，而非 orig_active_defrag。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2708</code> streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1 可能導致記憶體洩漏或錯誤保留</summary>

新增的 `if (!s->cgroups_ref) return 1;` 會在沒有 consumer groups 時直接回傳 1，表示該 entry 被引用。這可能導致 stream 的 entry 無法被刪除，即使沒有 consumer group 引用它。

失敗情境：當 stream 沒有 consumer groups 時，呼叫 streamEntryIsReferenced 會回傳 1，使得呼叫者認為 entry 仍被引用，因此不會刪除它，可能造成記憶體洩漏或資料不一致。

建議：確認此處的意圖。若 cgroups_ref 為 NULL，應回傳 0（未被引用）而非 1。或者，應檢查呼叫者是否正確處理此情況。

**判斷依據**：diff 中新增的一行：
```
+    if (!s->cgroups_ref) return 1;
```
此函式原本會直接使用 s->cgroups_ref 進行 raxFind，若為 NULL 可能導致 crash。但回傳 1 可能造成錯誤的引用判斷。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/memefficiency.tcl:70</code> discard_replies_every 函式參數名稱可能造成混淆</summary>

函式 `discard_replies_every` 的參數 `frequency` 和 `discard_num` 的語意不夠清晰。`frequency` 代表每多少次觸發一次丟棄，`discard_num` 代表每次丟棄的數量。但呼叫時傳入的數值可能與預期不符，例如在 lpush 的測試中，原本每次丟棄 20000 個 replies，但函式呼叫為 `discard_replies_every $rd $count 10000 20000`，這表示每 10000 次丟棄 20000 個 replies，與原本邏輯相同，但可讀性較差。

建議：考慮重新命名參數或加入註解，以提升可讀性。

**判斷依據**：diff 中新增的函式定義。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4818 (cache hit 1536) ｜ completion tokens 1137 ｜ PR #6</sub>