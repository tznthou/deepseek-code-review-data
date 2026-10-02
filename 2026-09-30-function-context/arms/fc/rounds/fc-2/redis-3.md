<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 主要重構了 cluster slot 相關的常數與函式，將原本的 GETSLOT_NOKEYS/GETSLOT_CROSSSLOT 改為 INVALID_CLUSTER_SLOT/CLUSTER_CROSSSLOT，並調整 extractSlotFromKeysResult 的實作。整體方向合理，但 extractSlotFromKeysResult 中新增的 slot_buffer 存在越界寫入與記憶體洩漏風險，且 extractKeysAndSlot 的行為變更可能影響呼叫端。建議先修正這些問題再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1112` | slot_buffer 越界寫入 | 0.95 |
| ⚠️ | Major | `src/cluster.c:1110` | 記憶體洩漏：slot_buffer 未在所有路徑釋放 | 0.90 |
| ⚠️ | Major | `src/db.c:3201` | extractKeysAndSlot 行為變更可能影響呼叫端 | 0.85 |
| 🔸 | Minor | `src/server.c:4143` | preprocessCommand 中 cross-slot 處理邏輯可能不完整 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1112</code> slot_buffer 越界寫入</summary>

在 extractSlotFromKeysResult 中，迴圈條件 `j <= keys_result->numkeys` 會導致 slot_buffer 寫入越界。slot_buffer 的大小是 `keys_result->numkeys`，但迴圈會執行 `numkeys + 1` 次，最後一次寫入 slot_buffer[numkeys] 時超出分配範圍。這可能造成記憶體損壞或未定義行為。

建議將迴圈條件改為 `j < keys_result->numkeys`。

**判斷依據**：diff 中新增的迴圈條件為 `j <= keys_result->numkeys`，而 slot_buffer 分配大小為 `sizeof(int) * keys_result->numkeys`，因此當 j 等於 numkeys 時會越界。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1110</code> 記憶體洩漏：slot_buffer 未在所有路徑釋放</summary>

在 extractSlotFromKeysResult 中，如果迴圈內因為 cross-slot 而提前返回，slot_buffer 會被釋放；但如果迴圈正常結束，slot_buffer 也會被釋放。然而，如果 `keys_result->numkeys` 為 0，函式會在分配 slot_buffer 之前返回，這沒有問題。但若 `keys_result->numkeys` 大於 0，且迴圈中沒有 cross-slot，slot_buffer 會在函式結尾釋放。目前看起來所有路徑都有釋放，但若未來修改程式碼時在迴圈中新增其他提前返回路徑，可能會遺漏釋放。建議使用更安全的管理方式，例如在函式開頭分配並使用 goto 清理，或改用可變長度陣列（VLA）或動態陣列搭配 defer 機制。

**判斷依據**：slot_buffer 使用 malloc 分配，但釋放邏輯分散在多個 return 路徑，容易在未來維護時遺漏。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/db.c:3201</code> extractKeysAndSlot 行為變更可能影響呼叫端</summary>

原本 extractKeysAndSlot 在 num_keys >= 0 時都會呼叫 extractSlotFromKeysResult 並設定 *slot，現在改為只有 num_keys > 0 時才設定。這意味著當 num_keys == 0 時，*slot 將保持呼叫前的值，而不是被設定為 INVALID_CLUSTER_SLOT。如果呼叫端依賴 *slot 在無 key 時被設為 INVALID_CLUSTER_SLOT，可能會出現錯誤。建議檢查所有呼叫端，確認它們在 num_keys == 0 時的行為是否正確，或考慮在 num_keys == 0 時明確設定 *slot = INVALID_CLUSTER_SLOT。

**判斷依據**：diff 中將原本的 `if (num_keys >= 0)` 改為 `if (num_keys > 0)`，且移除了 `*slot = INVALID_CLUSTER_SLOT;` 的初始化。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:4143</code> preprocessCommand 中 cross-slot 處理邏輯可能不完整</summary>

在 preprocessCommand 中，原本當 num_keys > 0 且 slot 為 INVALID_CLUSTER_SLOT 時設定 cross-slot 錯誤，現在改為檢查 slot == CLUSTER_CROSSSLOT。但 extractSlotFromKeysResult 在 cluster 停用時會回傳 INVALID_CLUSTER_SLOT，而此時 num_keys 可能大於 0，但 slot 不會是 CLUSTER_CROSSSLOT，因此不會設定錯誤。這可能導致在 cluster 停用時，帶有 key 的命令不會被正確處理。需要確認 cluster 停用時是否應該允許命令執行，以及此處的邏輯是否正確。

**判斷依據**：diff 中將條件從 `pcmd->slot == INVALID_CLUSTER_SLOT` 改為 `pcmd->slot == CLUSTER_CROSSSLOT`，但未考慮 cluster 停用時的情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9540 (cache hit 9472) ｜ completion tokens 1364 ｜ PR #3</sub>