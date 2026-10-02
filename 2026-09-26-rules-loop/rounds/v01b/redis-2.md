<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 slot range 的驗證函式改名並加入排序與合併相鄰範圍的功能，同時調整 import task 的記憶體管理與日誌輸出。主要風險在於 slotRangeArraySortAndMerge 的合併邏輯可能造成資料損毀（未處理重疊範圍、未更新 num_ranges 前的越界讀取），以及 asmCreateImportTask 的記憶體所有權轉移可能導致 use-after-free 或 double-free。此外，parseSlotRangesOrReply 的錯誤處理路徑可能洩漏記憶體。建議先修正合併邏輯與記憶體管理問題，再考慮合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1867` | slotRangeArraySortAndMerge 未處理重疊範圍，可能導致資料損毀 | 0.95 |
| 🛑 | Blocker | `src/cluster.c:1866` | slotRangeArraySortAndMerge 在更新 num_ranges 前可能越界讀取 | 0.90 |
| 🛑 | Blocker | `src/cluster_asm.c:830` | asmCreateImportTask 轉移 slots 所有權可能導致 use-after-free 或 double-free | 0.85 |
| ⚠️ | Major | `src/cluster.c:2015` | parseSlotRangesOrReply 錯誤路徑可能洩漏記憶體 | 0.80 |
| 🔸 | Minor | `src/cluster.c:1796` | slotRangeArrayToString 對 NULL 指標的處理不一致 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1867</code> slotRangeArraySortAndMerge 未處理重疊範圍，可能導致資料損毀</summary>

函式僅合併相鄰範圍（prev.end + 1 == next.start），但未檢查重疊範圍（例如 100-200 與 150-300）。若輸入包含重疊範圍，合併後會產生錯誤的範圍，且後續驗證可能無法偵測到重疊，導致 slot 被重複分配或遷移錯誤。

建議在合併前先檢查重疊，或保留重疊範圍並在驗證階段回報錯誤。

**判斷依據**：diff 中新增的 slotRangeArraySortAndMerge 函式，其合併條件僅為 end + 1 == start，未考慮重疊情況。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1866</code> slotRangeArraySortAndMerge 在更新 num_ranges 前可能越界讀取</summary>

在合併迴圈中，當 i 遞增時，slots->ranges[i] 可能指向已合併的範圍，但 num_ranges 尚未更新，導致讀取到未初始化的記憶體或重複處理。

建議先計算新的範圍數量，再進行合併，或使用獨立的輸出陣列。

**判斷依據**：diff 中新增的 slotRangeArraySortAndMerge 函式，其迴圈條件使用 slots->num_ranges，但該值在迴圈結束後才更新。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster_asm.c:830</code> asmCreateImportTask 轉移 slots 所有權可能導致 use-after-free 或 double-free</summary>

原本 asmCreateImportTask 會複製 slots（slotRangeArrayDup），現在改為直接指派 task->slots = slots。這表示呼叫端（clusterMigrationCommandImport 或 clusterAsmProcess）不再擁有 slots 的所有權，但錯誤路徑中仍會釋放 slots（slotRangeArrayFree），可能造成 double-free。此外，若 task 建立後 slots 被修改或釋放，task 內部的指標可能失效。

建議保留複製，或明確所有權轉移並移除呼叫端的釋放。

**判斷依據**：diff 中將 slotRangeArrayDup(slots) 改為 slots，且錯誤路徑新增 slotRangeArrayFree(slots)。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2015</code> parseSlotRangesOrReply 錯誤路徑可能洩漏記憶體</summary>

在 slotRangeArrayNormalizeAndValidate 失敗時，程式碼執行 sdsfree(err) 後直接 slotRangeArrayFree(slots) 並回傳 NULL，但未釋放 err 指向的 sds（若 err 非 NULL）。這可能導致記憶體洩漏。

建議在釋放 slots 前先處理 err，或使用 goto 統一清理。

**判斷依據**：diff 中 parseSlotRangesOrReply 的錯誤處理區塊。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1796</code> slotRangeArrayToString 對 NULL 指標的處理不一致</summary>

新增的 NULL 檢查僅在 slots == NULL 或 num_ranges == 0 時回傳空字串，但未處理 slots->ranges 為 NULL 的情況。若呼叫端傳入未初始化的 slotRangeArray，可能導致崩潰。

建議增加對 slots->ranges 的檢查，或確保所有呼叫端都正確初始化。

**判斷依據**：diff 中 slotRangeArrayToString 新增的 NULL 檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7193 (cache hit 7168) ｜ completion tokens 1428 ｜ PR #2</sub>