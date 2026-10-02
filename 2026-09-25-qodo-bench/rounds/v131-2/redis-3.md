<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將 slot 相關的常數從 GETSLOT_NOKEYS/GETSLOT_CROSSSLOT 統一為 INVALID_CLUSTER_SLOT/CLUSTER_CROSSSLOT，並重構 extractSlotFromKeysResult 以使用動態分配的 buffer 來追蹤 slot。整體方向合理，但 extractSlotFromKeysResult 中引入的 buffer 存在越界寫入與記憶體洩漏風險，且 extractKeysAndSlot 的修改可能導致 slot 未初始化。建議修正後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1112` | slot_buffer 越界寫入 | 0.95 |
| ⚠️ | Major | `src/cluster.c:1110` | 記憶體洩漏：slot_buffer 未在所有路徑釋放 | 0.90 |
| ⚠️ | Major | `src/db.c:3201` | extractKeysAndSlot 可能未初始化 *slot | 0.85 |
| 🔸 | Minor | `src/server.c:4141` | 條件判斷可能包含 num_keys == 0 的情況 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1112</code> slot_buffer 越界寫入</summary>

迴圈條件 `j <= keys_result->numkeys` 會導致寫入 `slot_buffer[keys_result->numkeys]`，超出分配的大小（`malloc(sizeof(int) * keys_result->numkeys)`），造成堆疊緩衝區溢位。應改為 `j < keys_result->numkeys`。

**判斷依據**：diff 中新增的迴圈條件為 `j <= keys_result->numkeys`，而 buffer 大小為 `keys_result->numkeys`，因此當 j 等於 numkeys 時會越界。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1110</code> 記憶體洩漏：slot_buffer 未在所有路徑釋放</summary>

在迴圈中若發現 cross-slot，會 `free(slot_buffer)` 後回傳，但若 `keyHashSlot` 或 `sdslen` 拋出例外（在 C 中通常不會），或未來程式碼修改導致提前回傳，可能遺漏釋放。此外，若 `malloc` 失敗（回傳 NULL），後續寫入會導致 segmentation fault。建議使用 stack 陣列或確保所有路徑釋放，並檢查 malloc 回傳值。

**判斷依據**：diff 中新增了 malloc，但未檢查回傳值，且釋放邏輯分散在多個回傳點。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/db.c:3201</code> extractKeysAndSlot 可能未初始化 *slot</summary>

原本在 `num_keys >= 0` 時會設定 `*slot = INVALID_CLUSTER_SLOT`，現在改為只有 `num_keys > 0` 才呼叫 `extractSlotFromKeysResult`。若 `num_keys == 0`，`*slot` 將保持呼叫者傳入的值，可能導致未定義行為。應在 `num_keys == 0` 時明確設定 `*slot = INVALID_CLUSTER_SLOT`。

**判斷依據**：diff 中移除了原本的 `*slot = INVALID_CLUSTER_SLOT;`，且條件改為 `num_keys > 0`，未涵蓋 `num_keys == 0` 的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:4141</code> 條件判斷可能包含 num_keys == 0 的情況</summary>

原本 `else if (num_keys > 0)` 改為 `else if (num_keys >= 0)`，使得 `num_keys == 0` 時也會進入此分支。若 `pcmd->slot` 為 `CLUSTER_CROSSSLOT`（不太可能，因為沒有 keys），會錯誤設定 read_error。建議確認此變更是否必要，或改回 `num_keys > 0`。

**判斷依據**：diff 中條件從 `num_keys > 0` 改為 `num_keys >= 0`，擴大了執行範圍。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4703 (cache hit 4608) ｜ completion tokens 1065 ｜ PR #3</sub>