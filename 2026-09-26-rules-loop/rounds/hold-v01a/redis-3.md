<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將原本的 GETSLOT_NOKEYS/GETSLOT_CROSSSLOT 常數統一為 INVALID_CLUSTER_SLOT/CLUSTER_CROSSSLOT，並重構 extractSlotFromKeysResult 以回傳 CLUSTER_CROSSSLOT。主要風險在於 extractSlotFromKeysResult 中新增的 malloc 與迴圈邊界錯誤，可能導致 heap buffer overflow 與記憶體洩漏；此外，preprocessCommand 的條件變更可能造成 slot 未初始化。建議先修正這些問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1112` | extractSlotFromKeysResult 迴圈邊界錯誤導致 heap buffer overflow | 0.95 |
| 🛑 | Blocker | `src/cluster.c:1110` | [R02] 使用 malloc/free 而非 zmalloc/zfree | 0.90 |
| ⚠️ | Major | `src/cluster.c:1110` | extractSlotFromKeysResult 在 cross-slot 時可能洩漏記憶體 | 0.85 |
| ⚠️ | Major | `src/server.c:4141` | preprocessCommand 條件變更可能導致 slot 未初始化 | 0.80 |
| 🔸 | Minor | `src/cluster.c:1110` | extractSlotFromKeysResult 中 slot_buffer 可能非必要 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1112</code> extractSlotFromKeysResult 迴圈邊界錯誤導致 heap buffer overflow</summary>

迴圈條件 `j <= keys_result->numkeys` 會多執行一次，當 `j == numkeys` 時，`slot_buffer[j] = this_slot;` 會寫入超出配置的記憶體（配置大小為 `numkeys` 個 int）。此外，`argv[keys_result->keys[j].pos]` 也會讀取超出 `keys_result->keys` 陣列範圍的記憶體。

**失敗情境**：當 `numkeys > 0` 時，最後一次迭代會造成 heap buffer overflow，可能導致程式崩潰或任意程式碼執行。

**建議修法**：將迴圈條件改為 `j < keys_result->numkeys`。

**判斷依據**：diff 中新增的迴圈條件為 `j <= keys_result->numkeys`，而 `slot_buffer` 配置大小為 `sizeof(int) * keys_result->numkeys`，因此當 `j == numkeys` 時會越界寫入。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1110</code> [R02] 使用 malloc/free 而非 zmalloc/zfree</summary>

新增的 `malloc` 與 `free` 呼叫違反專案規範 R02，應使用 `zmalloc` 與 `zfree` 以利記憶體追蹤。

**建議修法**：將 `malloc` 改為 `zmalloc`，`free` 改為 `zfree`。

**判斷依據**：diff 中新增 `malloc` 呼叫，且後續使用 `free` 釋放，違反 R02。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1110</code> extractSlotFromKeysResult 在 cross-slot 時可能洩漏記憶體</summary>

在偵測到 cross-slot 時，函式會 `free(slot_buffer)` 後回傳 `CLUSTER_CROSSSLOT`，但若 `malloc` 失敗（回傳 NULL），則 `slot_buffer` 為 NULL，`free(NULL)` 是安全的，但後續的 `slot_buffer[j] = this_slot` 會對 NULL 指標寫入，造成 segmentation fault。

**失敗情境**：當記憶體不足導致 `malloc` 回傳 NULL 時，程式會崩潰。

**建議修法**：檢查 `malloc` 回傳值，若為 NULL 則回傳錯誤或改用 `zmalloc`（其會終止程式）。

**判斷依據**：diff 中未檢查 `malloc` 回傳值，且後續直接使用 `slot_buffer`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:4141</code> preprocessCommand 條件變更可能導致 slot 未初始化</summary>

原本條件為 `num_keys > 0`，現在改為 `num_keys >= 0`。當 `num_keys == 0` 時，`extractSlotFromKeysResult` 會回傳 `INVALID_CLUSTER_SLOT`，但 `pcmd->slot` 可能未被初始化（若 `extractKeysAndSlot` 未設定）。

**失敗情境**：若 `num_keys == 0` 且 `pcmd->slot` 未初始化，則 `pcmd->slot == CLUSTER_CROSSSLOT` 的判斷可能讀取未初始化的記憶體，導致非預期行為。

**建議修法**：確認 `extractKeysAndSlot` 在 `num_keys == 0` 時會設定 `*slot`，或將條件改回 `num_keys > 0`。

**判斷依據**：diff 中將條件從 `num_keys > 0` 改為 `num_keys >= 0`，但未確認 `pcmd->slot` 在 `num_keys == 0` 時是否已初始化。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1110</code> extractSlotFromKeysResult 中 slot_buffer 可能非必要</summary>

新增的 `slot_buffer` 僅用於暫存每個 key 的 slot，但實際上可以直接在迴圈中比較，無需配置額外記憶體。這增加了記憶體使用與失敗點。

**建議修法**：移除 `slot_buffer`，直接在迴圈中計算並比較 slot。

**判斷依據**：diff 中新增 `slot_buffer` 並在迴圈中寫入，但未見其他用途。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5740 (cache hit 4736) ｜ completion tokens 1479 ｜ PR #3</sub>