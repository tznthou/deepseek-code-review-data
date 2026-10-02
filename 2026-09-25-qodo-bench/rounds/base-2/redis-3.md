<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將 slot 相關的常數從 GETSLOT_NOKEYS/GETSLOT_CROSSSLOT 改為 INVALID_CLUSTER_SLOT/CLUSTER_CROSSSLOT，並重構 extractSlotFromKeysResult 以使用動態記憶體配置。主要風險在於 extractSlotFromKeysResult 中的迴圈邊界錯誤（j <= numkeys 應為 j < numkeys），可能導致堆積緩衝區溢位；此外，extractKeysAndSlot 中 slot 的初始化邏輯變更可能在某些路徑下留下未初始化的 slot 值。建議修正這些問題後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1112` | 迴圈邊界錯誤導致堆積緩衝區溢位 | 0.95 |
| ⚠️ | Major | `src/cluster.c:1110` | 記憶體配置失敗未檢查 | 0.80 |
| ⚠️ | Major | `src/db.c:3201` | slot 可能未初始化 | 0.70 |
| 🔸 | Minor | `src/server.c:4141` | 條件判斷變更可能影響無 key 命令的處理 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1112</code> 迴圈邊界錯誤導致堆積緩衝區溢位</summary>

在 `extractSlotFromKeysResult` 中，迴圈條件為 `j <= keys_result->numkeys`，但 `slot_buffer` 僅配置了 `keys_result->numkeys` 個元素。當 `j == keys_result->numkeys` 時，`slot_buffer[j] = this_slot;` 會寫入超出配置的記憶體，造成堆積緩衝區溢位。此外，`argv[keys_result->keys[j].pos]` 在 `j == numkeys` 時也會讀取 `keys` 陣列之後的記憶體，可能導致未定義行為。

**失敗情境**：當命令包含至少一個 key 時，每次呼叫此函式都會觸發溢位，可能導致程式崩潰或安全漏洞。

**建議修法**：將迴圈條件改為 `j < keys_result->numkeys`。

**判斷依據**：diff 中新增的迴圈條件 `j <= keys_result->numkeys` 與配置大小 `malloc(sizeof(int) * keys_result->numkeys)` 不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1110</code> 記憶體配置失敗未檢查</summary>

`malloc` 的返回值未檢查，若配置失敗（回傳 NULL），後續寫入 `slot_buffer[j]` 會導致空指標解參考，造成程式崩潰。

**失敗情境**：在記憶體不足的環境下，`malloc` 回傳 NULL，程式將在寫入時崩潰。

**建議修法**：檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或採取其他處理。

**判斷依據**：diff 中新增的 `malloc` 呼叫沒有對應的 NULL 檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/db.c:3201</code> slot 可能未初始化</summary>

在 `extractKeysAndSlot` 中，原本的程式碼在 `num_keys >= 0` 時會將 `*slot` 設為 `INVALID_CLUSTER_SLOT`，但修改後僅在 `num_keys > 0` 時呼叫 `extractSlotFromKeysResult` 來設定 `*slot`。若 `num_keys == 0`，`*slot` 將不會被設定，可能保留呼叫者傳入的未初始化值，導致後續使用時出現未定義行為。

**失敗情境**：當命令沒有 key 時，`*slot` 可能包含垃圾值，若後續程式碼依賴此值判斷 slot，可能造成錯誤。

**建議修法**：在 `num_keys == 0` 時明確將 `*slot` 設為 `INVALID_CLUSTER_SLOT`，或確保呼叫者已初始化。

**判斷依據**：diff 中移除了 `*slot = INVALID_CLUSTER_SLOT;` 的初始化，且條件改為 `num_keys > 0`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:4141</code> 條件判斷變更可能影響無 key 命令的處理</summary>

原本的條件 `num_keys > 0` 改為 `num_keys >= 0`，這使得 `num_keys == 0` 的命令也會進入此分支。雖然目前僅在 `pcmd->slot == CLUSTER_CROSSSLOT` 時執行操作，但若未來在此分支新增其他邏輯，可能會影響無 key 命令。此外，`num_keys == 0` 時 `pcmd->slot` 可能為 `INVALID_CLUSTER_SLOT`，不會觸發 cross-slot 處理，但條件變更本身可能隱含意圖改變。

**建議**：確認此變更是否必要，若僅為處理 cross-slot，可保留 `num_keys > 0` 並在內部檢查 `pcmd->slot == CLUSTER_CROSSSLOT`。

**判斷依據**：diff 中條件從 `num_keys > 0` 改為 `num_keys >= 0`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4739 (cache hit 4736) ｜ completion tokens 1356 ｜ PR #3</sub>