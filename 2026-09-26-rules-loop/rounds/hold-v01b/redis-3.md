<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 旨在清理與 slot 相關的程式碼，將原本的 GETSLOT_NOKEYS/GETSLOT_CROSSSLOT 常數替換為 INVALID_CLUSTER_SLOT/CLUSTER_CROSSSLOT，並重構 extractSlotFromKeysResult 函式。主要風險在於 extractSlotFromKeysResult 中的記憶體管理錯誤（malloc 未檢查、越界寫入、free 位置不當）以及 extractKeysAndSlot 中 slot 未初始化可能導致的未定義行為。此外，preprocessCommand 的條件變更可能改變行為。建議先修正這些問題再合併。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1110` | extractSlotFromKeysResult 中 malloc 未檢查且迴圈越界寫入 | 0.95 |
| 🛑 | Blocker | `src/cluster.c:1115` | extractSlotFromKeysResult 中 free 位置不當導致記憶體洩漏 | 0.90 |
| ⚠️ | Major | `src/cluster.c:1110` | [R02] 使用 malloc/free 而非 zmalloc/zfree | 0.90 |
| ⚠️ | Major | `src/cluster.c:1115` | [R02] 使用 free 而非 zfree | 0.90 |
| ⚠️ | Major | `src/cluster.c:1117` | [R02] 使用 free 而非 zfree | 0.90 |
| ⚠️ | Major | `src/db.c:3201` | extractKeysAndSlot 中 slot 未初始化可能導致未定義行為 | 0.85 |
| ⚠️ | Major | `src/server.c:4141` | preprocessCommand 條件變更可能導致行為改變 | 0.80 |
| 🔸 | Minor | `src/cluster.c:1110` | extractSlotFromKeysResult 中 slot_buffer 可能未完全初始化 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1110</code> extractSlotFromKeysResult 中 malloc 未檢查且迴圈越界寫入</summary>

在 `extractSlotFromKeysResult` 中，`malloc` 的回傳值未檢查，若記憶體配置失敗會導致對 NULL 指標寫入。此外，迴圈條件 `j <= keys_result->numkeys` 會寫入 `slot_buffer[numkeys]`，造成堆積緩衝區溢位。建議改為 `j < keys_result->numkeys`，並檢查 `malloc` 回傳值，失敗時回傳 `INVALID_CLUSTER_SLOT`。

**判斷依據**：diff 中新增的 malloc 未檢查回傳值，且迴圈條件使用 `<=` 導致越界。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1115</code> extractSlotFromKeysResult 中 free 位置不當導致記憶體洩漏</summary>

在 cross-slot 偵測到時，函式會 `free(slot_buffer)` 並回傳 `CLUSTER_CROSSSLOT`，但若迴圈正常結束，`free(slot_buffer)` 在迴圈外執行，這部分正確。然而，若在迴圈中發生 cross-slot，`free` 後直接回傳，但 `slot_buffer` 可能包含未初始化的值（若 `malloc` 成功但迴圈未完全填滿），但這不影響 free。真正的問題是：若 `malloc` 失敗（未檢查），則 `slot_buffer` 為 NULL，後續寫入會 crash。建議在 malloc 失敗時直接回傳 `INVALID_CLUSTER_SLOT`，並確保所有路徑都釋放記憶體。

**判斷依據**：diff 中 cross-slot 分支的 free 與回傳，但未處理 malloc 失敗。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1110</code> [R02] 使用 malloc/free 而非 zmalloc/zfree</summary>

根據規範 R02，應使用 zmalloc/zfree 而非標準 malloc/free。此處新增的 `malloc` 和 `free` 違反規範，且無法追蹤記憶體使用。建議改用 `zmalloc` 和 `zfree`。

**判斷依據**：diff 中新增的 malloc 呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1115</code> [R02] 使用 free 而非 zfree</summary>

根據規範 R02，應使用 zfree 而非 free。此處的 `free(slot_buffer)` 違反規範。建議改用 `zfree`。

**判斷依據**：diff 中新增的 free 呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1117</code> [R02] 使用 free 而非 zfree</summary>

根據規範 R02，應使用 zfree 而非 free。此處的 `free(slot_buffer)` 違反規範。建議改用 `zfree`。

**判斷依據**：diff 中新增的 free 呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/db.c:3201</code> extractKeysAndSlot 中 slot 未初始化可能導致未定義行為</summary>

在 `extractKeysAndSlot` 中，原本 `*slot = INVALID_CLUSTER_SLOT;` 被移除，改為僅在 `num_keys > 0` 時才呼叫 `extractSlotFromKeysResult` 設定 slot。若 `num_keys == 0`，`*slot` 將保持呼叫者傳入的值，可能未初始化，導致未定義行為。建議保留 `*slot = INVALID_CLUSTER_SLOT;` 的初始化，或確保所有呼叫者都先初始化 slot。

**判斷依據**：diff 中移除了 `*slot = INVALID_CLUSTER_SLOT;` 的初始化。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:4141</code> preprocessCommand 條件變更可能導致行為改變</summary>

原本條件為 `num_keys > 0`，現在改為 `num_keys >= 0`。這表示當 `num_keys == 0` 時，也會進入此區塊，但此時 `pcmd->slot` 可能為 `INVALID_CLUSTER_SLOT`（因為沒有 keys），不會觸發 cross-slot 錯誤。然而，若 `num_keys == 0` 且 `pcmd->slot` 意外為 `CLUSTER_CROSSSLOT`（不應發生），則會錯誤地設定 read_error。建議確認此變更是否必要，或改回 `num_keys > 0`。

**判斷依據**：diff 中條件從 `num_keys > 0` 改為 `num_keys >= 0`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1110</code> extractSlotFromKeysResult 中 slot_buffer 可能未完全初始化</summary>

若 `malloc` 成功但迴圈因 cross-slot 提前結束，`slot_buffer` 中剩餘元素未初始化，但這不影響 free。然而，若未來程式碼讀取這些未初始化值，可能導致問題。建議在 malloc 後使用 `memset` 初始化，或避免分配不必要的記憶體。

**判斷依據**：diff 中新增的 malloc 未初始化記憶體。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5740 (cache hit 5632) ｜ completion tokens 1893 ｜ PR #3</sub>