<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 slot range 的驗證函式改名並加入排序與合併相鄰範圍的功能，同時調整了 ASM import task 的記憶體管理與錯誤處理，並新增了測試。主要風險在於 slotRangeArrayNormalizeAndValidate 在驗證前會修改輸入陣列，可能造成呼叫端持有指標失效或資料意外變更；此外 asmCreateImportTask 的記憶體所有權轉移方式容易導致 double-free 或 use-after-free。建議先釐清所有呼叫端對 slotRangeArray 的所有權與可變性假設，再合併。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1744` | slotRangeArrayNormalizeAndValidate 在驗證前修改輸入陣列，可能造成呼叫端資料損毀或 use-after-free | 0.90 |
| 🛑 | Blocker | `src/cluster_asm.c:830` | asmCreateImportTask 直接取得 slots 所有權，但呼叫端可能仍持有指標，導致 double-free 或 use-after-free | 0.85 |
| ⚠️ | Major | `src/cluster_asm.c:804` | asmCreateImportTask 錯誤路徑可能未釋放 slots 或造成 double-free | 0.80 |
| ⚠️ | Major | `src/cluster.c:1796` | slotRangeArrayToString 對 NULL 指標的處理不一致 | 0.75 |
| ⚠️ | Major | `src/cluster.c:2015` | parseSlotRangesOrReply 錯誤處理不當：未回覆錯誤且可能洩漏記憶體 | 0.70 |
| 🔸 | Minor | `src/cluster_asm.c:1012` | asmCountKeysInSlots 未檢查 slots 指標是否為 NULL | 0.60 |
| 🔸 | Minor | `src/cluster_asm.c:2871` | clusterAsmProcess 中 slotRangeArrayDup 後未在成功路徑釋放原始指標 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1744</code> slotRangeArrayNormalizeAndValidate 在驗證前修改輸入陣列，可能造成呼叫端資料損毀或 use-after-free</summary>

此函式在進行任何驗證之前呼叫 `slotRangeArraySortAndMerge(slots)`，這會就地排序並合併相鄰範圍，改變 `slots` 的內容與 `num_ranges`。若呼叫端在呼叫後仍持有原始指標或假設範圍不變，可能導致資料不一致或記憶體問題。例如 `slotRangeArrayFromString` 在解析後呼叫此函式，若解析出的陣列後續被其他程式碼使用，其內容已被修改。建議改為先驗證原始範圍，再決定是否正規化，或提供一個明確的「正規化並驗證」的獨立函式，並在文件與呼叫端明確所有權與可變性。

**判斷依據**：diff 中新增的兩行：`/* Sort and merge adjacent slot ranges. */` 與 `slotRangeArraySortAndMerge(slots);` 位於 `slotRangeArrayNormalizeAndValidate` 函式內，且在驗證迴圈之前。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster_asm.c:830</code> asmCreateImportTask 直接取得 slots 所有權，但呼叫端可能仍持有指標，導致 double-free 或 use-after-free</summary>

原本 `task->slots = slotRangeArrayDup(slots);` 會複製一份，現在改為 `task->slots = slots;` 直接取得所有權。然而呼叫端 `clusterMigrationCommandImport` 在呼叫後不再 free，但其他呼叫端（如 `clusterAsmProcess`）在呼叫前會先 `slotRangeArrayDup` 並在錯誤時 free，但成功時卻未釋放原始指標，造成記憶體洩漏。此外，若 `asmCreateImportTask` 內部在取得所有權後發生錯誤並 `goto err`，會 free `slots`，但呼叫端可能仍持有指標，導致 double-free。建議明確所有權轉移規則：要嘛一律由呼叫端保留所有權並傳遞 const 指標，要嘛一律轉移所有權並在文件註明，且所有錯誤路徑都必須一致。

**判斷依據**：diff 中 `-    task->slots = slotRangeArrayDup(slots);` 改為 `+    task->slots = slots;`，且 `clusterMigrationCommandImport` 移除了 `slotRangeArrayFree(slots)`，但 `clusterAsmProcess` 中仍存在 `slotRangeArrayDup` 與條件式 free。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster_asm.c:804</code> asmCreateImportTask 錯誤路徑可能未釋放 slots 或造成 double-free</summary>

在 `asmCreateImportTask` 中，多個錯誤路徑改為 `goto err`，而 `err` 標籤會執行 `slotRangeArrayFree(slots)`。但若呼叫端在傳入前已複製（如 `clusterAsmProcess`），則原始指標仍由呼叫端持有，此處 free 會造成 double-free；若呼叫端未複製（如 `clusterMigrationCommandImport`），則 free 是正確的。所有權不一致導致記憶體管理混亂。建議統一所有權模型，並在每個呼叫端明確註釋。

**判斷依據**：diff 中將原本的 `return NULL;` 改為 `goto err;`，且 `err` 標籤包含 `slotRangeArrayFree(slots);`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1796</code> slotRangeArrayToString 對 NULL 指標的處理不一致</summary>

新增了 `if (slots == NULL || slots->num_ranges == 0) return s;`，但函式開頭已經建立 `sds s = sdsempty();`，若 `slots` 為 NULL，會先建立空 sds 再返回，呼叫端可能預期 NULL 或空字串，造成不一致。此外，若 `slots` 為 NULL，後續的 `slotRangeArrayToString` 呼叫（如 `asmLogTaskEvent`）可能未檢查返回值，導致空字串被記錄。建議明確函式對 NULL 的契約，並檢查所有呼叫端。

**判斷依據**：diff 中新增的這一行位於 `slotRangeArrayToString` 函式內，且在 `sds s = sdsempty();` 之後。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2015</code> parseSlotRangesOrReply 錯誤處理不當：未回覆錯誤且可能洩漏記憶體</summary>

原本在 `validateSlotRanges` 失敗時會 `addReplyErrorSds(c, err)` 將錯誤訊息回覆給客戶端，現在改為 `sdsfree(err)` 後直接返回 NULL，但未呼叫 `addReplyError`，導致客戶端收到空回覆或連線中斷。此外，`slotRangeArrayFree(slots)` 在錯誤時被呼叫，但 `slots` 可能為 NULL（若 `slotRangeArrayCreate` 失敗），需檢查。建議保留錯誤回覆，並確保所有錯誤路徑都釋放資源。

**判斷依據**：diff 中將 `addReplyErrorSds(c, err);` 移除，改為 `sdsfree(err);`，且未新增任何回覆。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster_asm.c:1012</code> asmCountKeysInSlots 未檢查 slots 指標是否為 NULL</summary>

函式開頭有 `if (!slots) return 0;`，但後續直接存取 `slots->num_ranges` 與 `slots->ranges`，若 `slots` 為 NULL 會 crash。雖然目前呼叫端可能保證非 NULL，但防禦性不足。建議保留 NULL 檢查，或明確函式契約。

**判斷依據**：diff 中新增的函式，開頭有 NULL 檢查，但後續未再檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster_asm.c:2871</code> clusterAsmProcess 中 slotRangeArrayDup 後未在成功路徑釋放原始指標</summary>

在 `ASM_EVENT_IMPORT_START` 分支中，先 `slotRangeArray *slots = slotRangeArrayDup(arg);`，然後驗證並傳給 `asmCreateImportTask`。若成功，`asmCreateImportTask` 取得 `slots` 的所有權，但 `arg` 指向的原始陣列未被釋放，造成記憶體洩漏。建議在成功後由呼叫端釋放 `arg`，或改為直接傳遞 `arg` 並由 `asmCreateImportTask` 負責複製。

**判斷依據**：diff 中新增的程式碼，未見對 `arg` 的釋放。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7183 (cache hit 6144) ｜ completion tokens 2299 ｜ PR #2</sub>