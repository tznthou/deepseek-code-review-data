<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要清理 cluster slot 相關程式碼：以 INVALID_CLUSTER_SLOT 取代 GETSLOT_NOKEYS、以 CLUSTER_CROSSSLOT 取代 GETSLOT_CROSSSLOT，並重構 extractSlotFromKeysResult 以回傳 CLUSTER_CROSSSLOT。主要風險在於 extractSlotFromKeysResult 的迴圈邊界錯誤（j <= numkeys 造成越界寫入），以及 extractKeysAndSlot 中 slot 初始化邏輯變更可能導致未初始化變數被使用。建議先修正這兩個 blocker 再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1112` | 迴圈邊界錯誤導致 heap buffer overflow | 0.95 |
| 🛑 | Blocker | `src/db.c:3201` | slot 可能未初始化即被使用 | 0.90 |
| ⚠️ | Major | `src/cluster.c:1110` | malloc 未檢查失敗 | 0.80 |
| ⚠️ | Major | `src/server.c:4141` | 條件判斷變更可能影響無 key 命令的處理 | 0.75 |
| 🔸 | Minor | `src/cluster.c:1110` | slot_buffer 可能造成不必要的記憶體分配 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1112</code> 迴圈邊界錯誤導致 heap buffer overflow</summary>

迴圈條件 `j <= keys_result->numkeys` 會讓 `j` 等於 `numkeys` 時仍進入迴圈，此時 `slot_buffer[j]` 寫入超出配置的記憶體（配置大小為 `numkeys`）。這會造成 heap buffer overflow，可能導致程式崩潰或安全漏洞。

建議改為 `j < keys_result->numkeys`。

**判斷依據**：diff 中新增的迴圈條件為 `j <= keys_result->numkeys`，而 `slot_buffer` 配置大小為 `sizeof(int) * keys_result->numkeys`，因此當 `j == numkeys` 時寫入越界。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/db.c:3201</code> slot 可能未初始化即被使用</summary>

在 `extractKeysAndSlot` 中，原本 `*slot` 會先被設為 `INVALID_CLUSTER_SLOT`，但修改後只有當 `num_keys > 0` 時才呼叫 `extractSlotFromKeysResult` 設定 `*slot`。若 `num_keys == 0`，`*slot` 將保持呼叫者傳入的值，可能導致未初始化變數被使用。

建議在函式開頭明確初始化 `*slot = INVALID_CLUSTER_SLOT`，或確保所有呼叫者都已初始化。

**判斷依據**：diff 中移除了 `*slot = INVALID_CLUSTER_SLOT;` 這一行，且新增的條件只在 `num_keys > 0` 時設定 `*slot`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1110</code> malloc 未檢查失敗</summary>

`malloc` 可能回傳 NULL，但程式碼未檢查，後續寫入 `slot_buffer[j]` 會導致 NULL pointer dereference。

建議檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或採取其他處理。

**判斷依據**：diff 中新增的 `malloc` 呼叫沒有對回傳值做 NULL 檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:4141</code> 條件判斷變更可能影響無 key 命令的處理</summary>

原本 `else if (num_keys > 0)` 只在有 key 時檢查 cross-slot，現在改為 `else if (num_keys >= 0)`，這會讓 `num_keys == 0` 的命令也進入檢查。若 `pcmd->slot` 為 `CLUSTER_CROSSSLOT`（不太可能，因為無 key 命令不會有 cross-slot），則會設定錯誤。但更可能的是，原本 `num_keys == 0` 時會跳過此區塊，現在會執行，可能影響後續邏輯。

建議確認此變更是否必要，或改回 `num_keys > 0`。

**判斷依據**：diff 中將條件從 `num_keys > 0` 改為 `num_keys >= 0`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1110</code> slot_buffer 可能造成不必要的記憶體分配</summary>

原本的實作不需要額外記憶體，現在為了追蹤 slot 而分配 `slot_buffer`。雖然在 cross-slot 時可以釋放，但若所有 key 都在同一 slot，仍會分配並釋放記憶體。若此函式被頻繁呼叫，可能影響效能。

建議考慮是否真的需要此 buffer，或改用其他方式。

**判斷依據**：diff 中新增了 `slot_buffer` 的分配與釋放。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4739 (cache hit 1536) ｜ completion tokens 1380 ｜ PR #3</sub>