<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 旨在清理 cluster 相關的 slot 常數與函式，將原本的 GETSLOT_NOKEYS/GETSLOT_CROSSSLOT 改為 INVALID_CLUSTER_SLOT/CLUSTER_CROSSSLOT，並重構 extractSlotFromKeysResult 與 getSlotFromCommand。主要風險在於 extractSlotFromKeysResult 中的迴圈邊界錯誤（j <= numkeys）導致越界讀取，以及 slot_buffer 的分配與釋放邏輯可能造成記憶體洩漏或未定義行為。此外，extractKeysAndSlot 的 slot 初始化邏輯變更可能在某些路徑下留下未初始化的 *slot。建議優先修正迴圈邊界與 slot 初始化問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1112` | extractSlotFromKeysResult 迴圈邊界錯誤導致越界讀取 | 0.95 |
| ⚠️ | Major | `src/cluster.c:1110` | slot_buffer 分配後未檢查 malloc 失敗 | 0.85 |
| ⚠️ | Major | `src/cluster.c:1057` | slot_buffer 在 cross-slot 時釋放後仍可能被使用 | 0.80 |
| ⚠️ | Major | `src/db.c:3201` | extractKeysAndSlot 可能留下未初始化的 *slot | 0.75 |
| 🔸 | Minor | `src/server.c:4143` | preprocessCommand 中 cross-slot 處理後未設定 slot 為 INVALID_CLUSTER_SLOT | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1112</code> extractSlotFromKeysResult 迴圈邊界錯誤導致越界讀取</summary>

在 `extractSlotFromKeysResult` 中，迴圈條件 `j <= keys_result->numkeys` 應為 `j < keys_result->numkeys`。當 `j == numkeys` 時，`keys_result->keys[j]` 會讀取到陣列之外，造成未定義行為，可能導致程式崩潰或洩漏記憶體內容。

建議修正為：
```c
for (int j = 0; j < keys_result->numkeys; j++) {
```

**判斷依據**：diff 中新增的迴圈條件為 `j <= keys_result->numkeys`，而 `keys_result->keys` 陣列大小為 `numkeys`，因此最後一次迭代會越界。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1110</code> slot_buffer 分配後未檢查 malloc 失敗</summary>

`slot_buffer = malloc(sizeof(int) * keys_result->numkeys);` 未檢查回傳值是否為 NULL。若記憶體不足，後續寫入 `slot_buffer[j]` 會導致 NULL pointer dereference。

建議加入檢查：
```c
int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);
if (!slot_buffer) return INVALID_CLUSTER_SLOT;
```

**判斷依據**：diff 中新增的 malloc 呼叫沒有 NULL 檢查，且後續直接使用 slot_buffer。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1057</code> slot_buffer 在 cross-slot 時釋放後仍可能被使用</summary>

在偵測到 cross-slot 時，程式碼執行 `free(slot_buffer); return CLUSTER_CROSSSLOT;`，但若後續程式碼（例如在迴圈外）仍嘗試使用 slot_buffer，會造成 use-after-free。目前程式碼在 cross-slot 時直接 return，因此暫時安全，但未來修改時容易出錯。建議將 slot_buffer 的生命週期限制在迴圈內，或使用更安全的管理方式。

**判斷依據**：diff 中在 cross-slot 分支釋放 slot_buffer 後立即 return，但若未來在 return 前加入其他使用 slot_buffer 的程式碼，將導致 use-after-free。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/db.c:3201</code> extractKeysAndSlot 可能留下未初始化的 *slot</summary>

在 `extractKeysAndSlot` 中，原本 `*slot = INVALID_CLUSTER_SLOT;` 被移除，改為僅在 `num_keys > 0` 時設定 `*slot`。若 `num_keys == 0` 或 `num_keys < 0`，`*slot` 將保持呼叫者傳入的未初始化值，可能導致後續使用未定義行為。

建議在函式開頭初始化 `*slot = INVALID_CLUSTER_SLOT;`，或確保所有呼叫者在呼叫前已初始化。

**判斷依據**：diff 中移除了 `*slot = INVALID_CLUSTER_SLOT;` 的初始化，且僅在 `num_keys > 0` 時賦值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:4143</code> preprocessCommand 中 cross-slot 處理後未設定 slot 為 INVALID_CLUSTER_SLOT</summary>

在 `preprocessCommand` 中，當 `pcmd->slot == CLUSTER_CROSSSLOT` 時，程式碼設定 `pcmd->read_error = CLIENT_READ_CROSS_SLOT;` 並將 `pcmd->slot = INVALID_CLUSTER_SLOT;`。但若後續程式碼依賴 `pcmd->slot` 為有效值，可能會誤用。建議確認此處重設 slot 的必要性，或考慮在錯誤時直接 return。

**判斷依據**：diff 中新增了 cross-slot 的處理，但未明確說明為何需要重設 slot。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9540 (cache hit 1536) ｜ completion tokens 1474 ｜ PR #3</sub>