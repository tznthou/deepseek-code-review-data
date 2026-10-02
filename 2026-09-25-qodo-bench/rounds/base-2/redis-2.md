<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 slot range 的驗證流程改為先正規化（排序並合併相鄰範圍）再驗證，並調整了 ASM 任務建立時的記憶體管理與錯誤處理。主要風險在於 slotRangeArraySortAndMerge 的合併邏輯可能未正確處理重疊範圍，且 asmCreateImportTask 的記憶體所有權轉移在多個錯誤路徑下可能造成 double-free 或 use-after-free。此外，parseSlotRangesOrReply 的錯誤回覆路徑可能遺漏錯誤訊息。建議優先修正記憶體管理與合併邏輯，並補充重疊範圍的測試案例。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1867` | slotRangeArraySortAndMerge 合併邏輯可能錯誤處理重疊範圍 | 0.90 |
| 🛑 | Blocker | `src/cluster_asm.c:830` | asmCreateImportTask 記憶體所有權轉移可能導致 double-free 或 use-after-free | 0.85 |
| ⚠️ | Major | `src/cluster.c:2015` | parseSlotRangesOrReply 錯誤路徑可能遺漏錯誤訊息 | 0.80 |
| ⚠️ | Major | `src/cluster.c:1739` | slotRangeArrayNormalizeAndValidate 在排序合併後未重新驗證範圍數量上限 | 0.75 |
| 🔸 | Minor | `src/cluster_asm.c:2871` | clusterAsmProcess 中 slotRangeArrayDup 後未檢查 NULL | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1867</code> slotRangeArraySortAndMerge 合併邏輯可能錯誤處理重疊範圍</summary>

在 `slotRangeArraySortAndMerge` 中，合併條件僅檢查 `slots->ranges[idx].end + 1 == slots->ranges[i].start`，但未處理重疊範圍（例如 `0-10` 與 `5-15`）。若輸入包含重疊範圍，排序後 `idx` 指向的範圍可能與後續範圍重疊，但因為條件不成立，重疊範圍不會被合併，導致後續驗證可能誤判為合法（或產生未定義行為）。

**失敗情境**：呼叫 `slotRangeArrayNormalizeAndValidate` 時傳入包含重疊範圍的陣列（例如 `0-10 5-15`），排序後 `idx=0` 指向 `0-10`，`i=1` 指向 `5-15`，條件 `10+1 == 5` 不成立，因此兩個範圍都保留。後續驗證迴圈會檢查每個範圍的 start/end 是否在合法範圍內，但不會檢查重疊，因此可能通過驗證，導致後續邏輯假設範圍不重疊而產生錯誤。

**建議修法**：在合併時同時處理重疊與相鄰情況，例如將條件改為 `slots->ranges[idx].end + 1 >= slots->ranges[i].start`，並更新 end 為兩者最大值。同時在註解中明確說明重疊範圍的處理方式。

**判斷依據**：diff 中新增的 `slotRangeArraySortAndMerge` 函式，合併條件僅處理相鄰（end+1 == start），未處理重疊。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster_asm.c:830</code> asmCreateImportTask 記憶體所有權轉移可能導致 double-free 或 use-after-free</summary>

在 `asmCreateImportTask` 中，原本使用 `slotRangeArrayDup(slots)` 複製一份 slots，現在改為直接指派 `task->slots = slots`，將所有權轉移給 task。然而，函式內有多個錯誤路徑會 `goto err`，在 `err` 標籤處執行 `slotRangeArrayFree(slots)`。若呼叫端在錯誤發生後也嘗試釋放 slots（例如 `clusterMigrationCommandImport` 中原本在呼叫後有 `slotRangeArrayFree(slots)`，但此 PR 已移除），則可能造成 double-free。此外，若 `asmCreateImportTask` 成功，呼叫端不再持有 slots 的所有權，但若呼叫端在其他地方仍使用該指標，可能造成 use-after-free。

**失敗情境**：
1. 呼叫 `asmCreateImportTask` 時，若 `validateImportSlotRanges` 回傳 NULL，函式會 `goto err` 並釋放 slots，但呼叫端（例如 `clusterAsmProcess`）可能也嘗試釋放同一指標，導致 double-free。
2. 若 `asmCreateImportTask` 成功，呼叫端若仍持有原始 slots 指標並在後續使用，可能存取已釋放記憶體。

**建議修法**：明確所有權規則。若函式取得所有權，則在所有錯誤路徑上由函式負責釋放，且呼叫端不得再釋放；若函式不取得所有權，則應保留 `slotRangeArrayDup` 並在錯誤時不釋放傳入的 slots。同時檢查所有呼叫端，確保沒有重複釋放或使用已釋放指標。

**判斷依據**：diff 中將 `task->slots = slotRangeArrayDup(slots);` 改為 `task->slots = slots;`，且新增 `err` 標籤執行 `slotRangeArrayFree(slots)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2015</code> parseSlotRangesOrReply 錯誤路徑可能遺漏錯誤訊息</summary>

在 `parseSlotRangesOrReply` 中，原本在 `validateSlotRanges` 失敗時會呼叫 `addReplyErrorSds(c, err)` 將錯誤訊息回覆給客戶端，但修改後僅執行 `sdsfree(err)` 並釋放 slots，未回覆任何錯誤。這可能導致客戶端在輸入無效的 slot range 時收到空回覆或連線中斷，而非明確的錯誤訊息。

**失敗情境**：客戶端執行 `CLUSTER MIGRATION IMPORT` 指令並提供無效的 slot range（例如 start > end），`slotRangeArrayNormalizeAndValidate` 回傳 C_ERR 並設定 err，但函式未將 err 回覆給客戶端，客戶端可能無法得知錯誤原因。

**建議修法**：在錯誤路徑中保留 `addReplyErrorSds(c, err)`，或改為 `addReplyError(c, err)` 後再釋放 err。

**判斷依據**：diff 中移除了 `addReplyErrorSds(c, err)`，僅保留 `sdsfree(err)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1739</code> slotRangeArrayNormalizeAndValidate 在排序合併後未重新驗證範圍數量上限</summary>

函式開頭檢查 `slots->num_ranges >= CLUSTER_SLOTS`，但排序合併後範圍數量可能減少，因此此檢查可能過早拒絕合法輸入。例如，輸入包含 16384 個單獨 slot 的範圍（每個範圍一個 slot），合併後可能變成一個範圍，但因為原始數量已達上限而被拒絕。雖然此情況極端，但可能影響正確性。

**失敗情境**：客戶端提供大量相鄰的單一 slot 範圍（例如 `0 0 1 1 2 2 ...`），原始數量可能超過 CLUSTER_SLOTS，但合併後數量遠小於上限，卻被錯誤拒絕。

**建議修法**：將數量上限檢查移至排序合併之後，或改為檢查合併後的數量。

**判斷依據**：diff 中在排序合併前檢查 `slots->num_ranges >= CLUSTER_SLOTS`，但合併後數量可能減少。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster_asm.c:2871</code> clusterAsmProcess 中 slotRangeArrayDup 後未檢查 NULL</summary>

在 `clusterAsmProcess` 的 `ASM_EVENT_IMPORT_START` 分支中，呼叫 `slotRangeArrayDup(arg)` 後未檢查回傳值是否為 NULL。若記憶體分配失敗，後續 `slotRangeArrayNormalizeAndValidate` 可能對 NULL 指標解參考，導致 crash。

**失敗情境**：系統記憶體不足時，`slotRangeArrayDup` 回傳 NULL，接著呼叫 `slotRangeArrayNormalizeAndValidate(slots, &errsds)` 會嘗試存取 `slots->num_ranges`，造成 segmentation fault。

**建議修法**：檢查 `slots` 是否為 NULL，若為 NULL 則設定錯誤並跳至錯誤處理。

**判斷依據**：diff 中新增的程式碼未檢查 `slotRangeArrayDup` 的回傳值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6192 (cache hit 6144) ｜ completion tokens 2229 ｜ PR #2</sub>