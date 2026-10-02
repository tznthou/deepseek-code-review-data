<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將 slot 相關的常數從 GETSLOT_NOKEYS/GETSLOT_CROSSSLOT 改為 INVALID_CLUSTER_SLOT/CLUSTER_CROSSSLOT，並重構 extractSlotFromKeysResult 以處理 cluster 停用與 cross-slot 情況。主要風險在於 extractSlotFromKeysResult 中新增的 malloc 與迴圈邊界錯誤，可能導致 heap buffer overflow 與記憶體洩漏；此外，preprocessCommand 的條件變更可能影響無鍵命令的處理。建議先修正 extractSlotFromKeysResult 的迴圈與記憶體管理，再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1112` | 迴圈條件錯誤導致 heap buffer overflow | 0.95 |
| ⚠️ | Major | `src/cluster.c:1110` | malloc 失敗未處理，可能導致 null pointer dereference | 0.90 |
| ⚠️ | Major | `src/cluster.c:1122` | 記憶體洩漏：cross-slot 時未釋放 slot_buffer | 0.85 |
| ⚠️ | Major | `src/server.c:4141` | 條件變更可能導致無鍵命令的 slot 未被正確處理 | 0.80 |
| 🔸 | Minor | `src/db.c:3201` | extractKeysAndSlot 中 slot 可能未初始化 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1112</code> 迴圈條件錯誤導致 heap buffer overflow</summary>

在 `extractSlotFromKeysResult` 中，迴圈條件為 `j <= keys_result->numkeys`，但 `slot_buffer` 只配置了 `keys_result->numkeys` 個元素。當 `j == keys_result->numkeys` 時，`slot_buffer[j] = this_slot;` 會寫入超出配置的記憶體，造成 heap buffer overflow。此外，`argv[keys_result->keys[j].pos]` 在 `j == numkeys` 時也會讀取 `keys` 陣列之外的元素，可能導致越界讀取。

失敗情境：當命令包含至少一個 key 時，迴圈會多執行一次，寫入 `slot_buffer[numkeys]`，可能破壞 heap 中相鄰的資料，甚至導致程式崩潰或被利用。

建議修正：將迴圈條件改為 `j < keys_result->numkeys`。

**判斷依據**：diff 中新增的迴圈條件為 `j <= keys_result->numkeys`，而 `slot_buffer` 的大小為 `keys_result->numkeys`，因此當 `j == numkeys` 時會越界。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1110</code> malloc 失敗未處理，可能導致 null pointer dereference</summary>

`slot_buffer = malloc(sizeof(int) * keys_result->numkeys);` 沒有檢查回傳值。若記憶體配置失敗，`slot_buffer` 為 NULL，後續 `slot_buffer[j] = this_slot;` 會寫入 NULL 位址，造成程式崩潰。

失敗情境：在記憶體不足或 `numkeys` 極大時，malloc 可能失敗，導致伺服器 crash。

建議修正：檢查 malloc 回傳值，若為 NULL 則回傳錯誤或改用 stack allocation（若 numkeys 有上限）。

**判斷依據**：diff 中新增的 malloc 沒有對應的 NULL 檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1122</code> 記憶體洩漏：cross-slot 時未釋放 slot_buffer</summary>

在偵測到 cross-slot 時，程式碼執行 `free(slot_buffer); return CLUSTER_CROSSSLOT;`，但若 `slot_buffer` 配置成功且迴圈正常結束，最後也有 `free(slot_buffer)`。然而，若在迴圈中發生其他錯誤（例如 `keyHashSlot` 拋出例外？C 語言無例外，但可能有 longjmp），或未來修改程式碼時在迴圈中提前 return，都可能遺漏釋放。目前程式碼看似有釋放，但若 `malloc` 失敗，`slot_buffer` 為 NULL，`free(NULL)` 是安全的，但後續寫入會 crash。

建議：使用 goto 統一清理，或確保所有路徑都釋放記憶體。

**判斷依據**：diff 中 cross-slot 分支有 free，但若 malloc 失敗則 slot_buffer 為 NULL，後續寫入會 crash；且若未來在迴圈中新增其他 return 路徑，可能遺漏 free。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:4141</code> 條件變更可能導致無鍵命令的 slot 未被正確處理</summary>

原本的條件是 `else if (num_keys > 0)`，現在改為 `else if (num_keys >= 0)`。這表示當 `num_keys == 0`（無鍵命令）時，也會進入此區塊。若 `pcmd->slot` 為 `CLUSTER_CROSSSLOT`（但無鍵命令不應有此值），則會設定 `read_error` 並將 slot 重設為 `INVALID_CLUSTER_SLOT`。然而，若 `num_keys == 0` 且 `pcmd->slot` 為其他值（例如 `INVALID_CLUSTER_SLOT`），則不會有任何動作，但原本的程式碼也不會進入此區塊。這可能改變了無鍵命令的處理流程，需要確認是否會影響後續邏輯。

失敗情境：若某個無鍵命令的 `pcmd->slot` 被錯誤設定為 `CLUSTER_CROSSSLOT`，現在會被標記為 cross-slot 錯誤，但實際上不應如此。

建議：確認 `num_keys == 0` 時 `pcmd->slot` 的可能值，並考慮是否應維持 `num_keys > 0` 的條件。

**判斷依據**：diff 中將條件從 `num_keys > 0` 改為 `num_keys >= 0`，擴大了進入此區塊的範圍。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/db.c:3201</code> extractKeysAndSlot 中 slot 可能未初始化</summary>

在 `extractKeysAndSlot` 中，原本有 `*slot = INVALID_CLUSTER_SLOT;` 的初始化，現在改為僅在 `num_keys > 0` 時才設定 slot。若 `num_keys == 0` 或 `num_keys < 0`，`*slot` 將不會被設定，可能保留呼叫者傳入的舊值。這可能導致呼叫者誤用未初始化的 slot。

失敗情境：若呼叫者未先初始化 `*slot`，且 `num_keys == 0`，則 `*slot` 的值未定義，可能造成錯誤判斷。

建議：保留 `*slot = INVALID_CLUSTER_SLOT;` 的初始化，或確保所有呼叫者都先初始化。

**判斷依據**：diff 中移除了 `*slot = INVALID_CLUSTER_SLOT;` 的初始化，且僅在 `num_keys > 0` 時設定 slot。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4739 (cache hit 4736) ｜ completion tokens 1799 ｜ PR #3</sub>