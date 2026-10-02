<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將 slot 相關的常數從 GETSLOT_NOKEYS/GETSLOT_CROSSSLOT 改為 INVALID_CLUSTER_SLOT/CLUSTER_CROSSSLOT，並重構 extractSlotFromKeysResult 函式。主要風險在於 extractSlotFromKeysResult 中的迴圈邊界錯誤（j <= numkeys）導致堆積緩衝區溢位，以及 extractKeysAndSlot 中 slot 未初始化可能造成未定義行為。建議先修正這兩個問題再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1112` | 迴圈條件錯誤導致堆積緩衝區溢位 | 0.99 |
| ⚠️ | Major | `src/db.c:3201` | slot 可能未初始化即被使用 | 0.90 |
| 🔸 | Minor | `src/cluster.c:1110` | 記憶體配置失敗未處理 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1112</code> 迴圈條件錯誤導致堆積緩衝區溢位</summary>

在 `extractSlotFromKeysResult` 中，迴圈條件 `j <= keys_result->numkeys` 會多執行一次，而 `slot_buffer` 只配置了 `keys_result->numkeys` 個元素，因此最後一次迭代會寫入 `slot_buffer[numkeys]`，造成堆積緩衝區溢位。此外，該次迭代還會讀取 `argv[keys_result->keys[numkeys].pos]`，可能讀取到未初始化的記憶體。

建議將迴圈條件改為 `j < keys_result->numkeys`。

**判斷依據**：diff 中新增的迴圈條件為 `j <= keys_result->numkeys`，而 `slot_buffer` 的大小為 `keys_result->numkeys`，因此當 `j == numkeys` 時會越界寫入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/db.c:3201</code> slot 可能未初始化即被使用</summary>

在 `extractKeysAndSlot` 中，原本的程式碼會先將 `*slot` 設為 `INVALID_CLUSTER_SLOT`，再根據 `num_keys` 決定是否呼叫 `extractSlotFromKeysResult`。修改後，只有當 `num_keys > 0` 時才會設定 `*slot`，若 `num_keys == 0` 或 `num_keys < 0`，`*slot` 將保持未初始化狀態。呼叫端若未檢查 `num_keys` 就直接使用 `*slot`，可能導致未定義行為。

建議在函式開頭明確初始化 `*slot = INVALID_CLUSTER_SLOT;`。

**判斷依據**：diff 中移除了原本的 `*slot = INVALID_CLUSTER_SLOT;` 初始化，且未在條件分支外設定預設值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1110</code> 記憶體配置失敗未處理</summary>

`malloc` 可能回傳 NULL，但程式碼未檢查就直接使用 `slot_buffer`，可能導致 NULL 指標解參考。雖然在 Redis 中記憶體配置失敗通常會觸發 OOM 處理，但此處直接使用仍不夠安全。建議檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或觸發 OOM。

**判斷依據**：diff 中新增的 `malloc` 呼叫沒有後續的 NULL 檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4703 (cache hit 1408) ｜ completion tokens 910 ｜ PR #3</sub>