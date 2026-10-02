<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 slot range 的驗證流程改為先正規化（排序與合併相鄰區間）再驗證，並將函式更名為 slotRangeArrayNormalizeAndValidate。主要風險在於 asmCreateImportTask 的記憶體所有權轉移：原本複製 slots，現在直接接管呼叫者傳入的指標，但 clusterMigrationCommandImport 已移除釋放，而 clusterAsmProcess 的呼叫路徑則重複釋放，可能造成 double-free 或 use-after-free。此外，slotRangeArraySortAndMerge 在合併時未檢查重疊區間，若輸入包含重疊（如 1000-2000 與 1500-2500），會產生錯誤的合併結果，且後續驗證可能無法偵測。建議先修正記憶體管理與重疊處理，再考慮合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster_asm.c:830` | asmCreateImportTask 直接接管 slots 指標，導致呼叫者釋放後 use-after-free | 0.95 |
| 🛑 | Blocker | `src/cluster_asm.c:2871` | clusterAsmProcess 中 slotRangeArrayDup 的記憶體洩漏與重複釋放風險 | 0.90 |
| ⚠️ | Major | `src/cluster.c:1867` | slotRangeArraySortAndMerge 未處理重疊區間，可能產生錯誤合併 | 0.85 |
| ⚠️ | Major | `src/cluster.c:2015` | parseSlotRangesOrReply 錯誤處理不當：釋放 err 後未回傳錯誤訊息 | 0.80 |
| 🔸 | Minor | `src/cluster.c:1796` | slotRangeArrayToString 對 NULL 指標的處理不一致 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster_asm.c:830</code> asmCreateImportTask 直接接管 slots 指標，導致呼叫者釋放後 use-after-free</summary>

在 asmCreateImportTask 中，原本使用 `task->slots = slotRangeArrayDup(slots);` 複製一份，現在改為 `task->slots = slots;` 直接接管呼叫者傳入的指標。然而，呼叫者 clusterMigrationCommandImport 在呼叫後已移除 `slotRangeArrayFree(slots)`，但另一個呼叫者 clusterAsmProcess 在呼叫前會先 `slotRangeArrayDup(arg)` 並在錯誤時釋放，但成功時並未釋放該複本，導致記憶體洩漏。更嚴重的是，若 asmCreateImportTask 內部在後續步驟失敗並執行 `goto err`，會呼叫 `slotRangeArrayFree(slots)`，此時 slots 已指派給 task->slots，造成 task 持有懸空指標，後續使用 task->slots 會導致 use-after-free。

建議：保留原本的複製語意（`task->slots = slotRangeArrayDup(slots);`），並在錯誤路徑釋放傳入的 slots（或由呼叫者負責）。

**判斷依據**：diff 中 `-    task->slots = slotRangeArrayDup(slots);` 改為 `+    task->slots = slots;`，且 `err:` 標籤下新增 `slotRangeArrayFree(slots);`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster_asm.c:2871</code> clusterAsmProcess 中 slotRangeArrayDup 的記憶體洩漏與重複釋放風險</summary>

在 clusterAsmProcess 的 ASM_EVENT_IMPORT_START 分支中，新增了 `slotRangeArray *slots = slotRangeArrayDup(arg);`，然後呼叫 `slotRangeArrayNormalizeAndValidate(slots, &errsds)`。若驗證失敗，會釋放 slots 並回傳錯誤；但若驗證成功，則將 slots 傳給 asmCreateImportTask。由於 asmCreateImportTask 現在直接接管 slots（不複製），因此 slots 的所有權轉移給 task，但 clusterAsmProcess 並未釋放原本的 arg（由呼叫者傳入），這可能導致記憶體洩漏。更糟的是，若 asmCreateImportTask 內部失敗並釋放 slots，則 task->slots 成為懸空指標，後續使用會造成 use-after-free。

建議：統一記憶體管理策略，例如讓 asmCreateImportTask 始終複製，或明確所有權轉移並在文件註明。

**判斷依據**：diff 中新增的程式碼片段，以及 asmCreateImportTask 的變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1867</code> slotRangeArraySortAndMerge 未處理重疊區間，可能產生錯誤合併</summary>

函式 slotRangeArraySortAndMerge 在合併時僅檢查 `prev.end + 1 == next.start`（相鄰），但未檢查重疊（例如 1000-2000 與 1500-2500）。若輸入包含重疊區間，排序後會將它們視為相鄰而合併成 1000-2500，但實際上重疊部分不應被合併，且後續的 validateSlotRanges 可能無法偵測到原始的重疊錯誤。這可能導致 slot 範圍驗證失效，允許不合法的重疊範圍進入系統。

建議：在合併前先檢查重疊，若發現重疊則回傳錯誤或保留原狀，並在 validateSlotRanges 中明確處理。

**判斷依據**：diff 中新增的 slotRangeArraySortAndMerge 函式，註解提到 'Overlapping ranges are not merged.' 但程式碼未檢查重疊。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2015</code> parseSlotRangesOrReply 錯誤處理不當：釋放 err 後未回傳錯誤訊息</summary>

在 parseSlotRangesOrReply 中，原本的錯誤處理是 `addReplyErrorSds(c, err);` 將錯誤訊息傳送給客戶端，但現在改為 `sdsfree(err);` 直接釋放，且未呼叫 addReplyError。這會導致當 slot 範圍驗證失敗時，客戶端收到空回覆或無錯誤訊息，造成使用者無法得知錯誤原因。

建議：保留 addReplyErrorSds 或改用 addReplyError 並傳入 err 內容。

**判斷依據**：diff 中 `-        addReplyErrorSds(c, err);` 被移除，改為 `+        sdsfree(err);`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1796</code> slotRangeArrayToString 對 NULL 指標的處理不一致</summary>

新增了 `if (slots == NULL || slots->num_ranges == 0) return s;` 來處理 NULL 或空陣列，但其他函式（如 slotRangeArrayIsEqual）並未對 NULL 做防護。這可能導致呼叫者預期 slotRangeArrayToString 永遠不會回傳 NULL，但實際上可能回傳空字串，造成行為不一致。

建議：統一 API 對 NULL 的處理方式，或在文件註明。

**判斷依據**：diff 中新增的防護程式碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7193 (cache hit 7168) ｜ completion tokens 1878 ｜ PR #2</sub>