<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將 slot range 的驗證函式改名並加入排序與合併相鄰範圍的功能，同時調整 import task 的記憶體管理與錯誤處理，並新增測試。主要風險在於 slotRangeArraySortAndMerge 的合併邏輯可能未正確處理重疊範圍，以及 asmCreateImportTask 的記憶體所有權轉移可能導致 double-free 或 use-after-free。此外，parseSlotRangesOrReply 的錯誤處理路徑可能造成記憶體洩漏。建議優先修正這些問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1867` | slotRangeArraySortAndMerge 合併邏輯未處理重疊範圍，可能導致資料錯誤 | 0.90 |
| 🛑 | Blocker | `src/cluster_asm.c:830` | asmCreateImportTask 記憶體所有權轉移可能導致 double-free 或 use-after-free | 0.85 |
| ⚠️ | Major | `src/cluster.c:2015` | parseSlotRangesOrReply 錯誤路徑可能造成記憶體洩漏 | 0.80 |
| 🔸 | Minor | `src/cluster.c:1796` | slotRangeArrayToString 對 NULL 指標的處理可能掩蓋錯誤 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1867</code> slotRangeArraySortAndMerge 合併邏輯未處理重疊範圍，可能導致資料錯誤</summary>

在 `slotRangeArraySortAndMerge` 中，合併條件僅檢查 `slots->ranges[idx].end + 1 == slots->ranges[i].start`，但未處理重疊（overlap）的情況。若輸入包含重疊範圍（例如 `0-100 50-150`），排序後會將第二個範圍直接覆蓋到 `idx+1` 位置，但 `idx` 並未前進，導致後續合併判斷錯誤，最終可能產生不正確的範圍合併結果。

**失敗情境**：
1. 輸入 `0-100 50-150`，排序後順序不變。
2. 迴圈中 `i=1`，`slots->ranges[0].end + 1 = 101 != 50`，所以執行 `slots->ranges[++idx] = slots->ranges[i]`，此時 `idx=1`，`slots->ranges[1]` 被覆蓋為 `50-150`。
3. 迴圈結束，`num_ranges = 2`，結果為 `0-100 50-150`，但這兩個範圍重疊，後續驗證函式會偵測到重疊並回傳錯誤，但此函式本身並未回報錯誤，且可能破壞原始資料。

**建議**：
- 在合併前先檢查重疊，若發現重疊應回傳錯誤或保留原始範圍，交由驗證函式處理。
- 或者，在合併時若發現重疊，直接將 `end` 設為較大值，但需確保後續驗證能正確偵測。

**判斷依據**：diff 中新增的 `slotRangeArraySortAndMerge` 函式，合併條件僅考慮相鄰，未處理重疊。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster_asm.c:830</code> asmCreateImportTask 記憶體所有權轉移可能導致 double-free 或 use-after-free</summary>

在 `asmCreateImportTask` 中，原本使用 `slotRangeArrayDup(slots)` 複製一份 slots，但現在改為直接 `task->slots = slots;`，將傳入的 slots 指標直接指派給 task，並在錯誤路徑中新增 `slotRangeArrayFree(slots)`。這導致記憶體所有權轉移，但呼叫端 `clusterMigrationCommandImport` 已移除 `slotRangeArrayFree(slots)`，因此正常路徑下 task 會持有 slots，並在 task 釋放時一併釋放。然而，錯誤路徑中若 `asmCreateImportTask` 內部在指派 `task->slots = slots` 之後發生錯誤（例如後續的 `asmTaskAddToManager` 失敗），則會執行 `slotRangeArrayFree(slots)`，但此時 `task->slots` 仍指向同一塊記憶體，若 task 之後被釋放，可能導致 double-free。

**失敗情境**：
1. `asmCreateImportTask` 成功建立 task 並指派 `task->slots = slots`。
2. 後續某個步驟失敗（例如 `asmTaskAddToManager` 回傳錯誤），進入 `err` 標籤。
3. `err` 標籤執行 `slotRangeArrayFree(slots)`，釋放記憶體。
4. 但 `task` 可能已被加入 manager 或仍持有指標，後續釋放 task 時會再次 free 同一塊記憶體，造成 double-free。

**建議**：
- 在錯誤路徑中，若已指派 `task->slots = slots`，則不應再 free slots，或先將 `task->slots` 設為 NULL。
- 或者，在指派前先完成所有可能失敗的步驟，確保指派後不會再有錯誤。

**判斷依據**：diff 中 `task->slots = slots;` 取代了原本的 `slotRangeArrayDup(slots)`，且錯誤路徑新增 `slotRangeArrayFree(slots)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2015</code> parseSlotRangesOrReply 錯誤路徑可能造成記憶體洩漏</summary>

在 `parseSlotRangesOrReply` 中，當 `slotRangeArrayNormalizeAndValidate` 回傳錯誤時，原本會將 `err` 透過 `addReplyErrorSds` 傳送給客戶端，但現在改為 `sdsfree(err)` 後直接回傳 NULL，未將錯誤訊息回覆給客戶端。這可能導致客戶端收到空回覆或不明錯誤，且 `err` 被釋放後，呼叫端可能無法取得錯誤細節。

**失敗情境**：
1. 使用者輸入無效的 slot range，例如 `CLUSTER MIGRATION IMPORT 7000 7000 7000 7000`（重疊）。
2. `slotRangeArrayNormalizeAndValidate` 回傳 C_ERR 並設定 `err`。
3. 函式執行 `sdsfree(err)` 後回傳 NULL，但未呼叫 `addReplyError`，客戶端可能收到空回覆或連線中斷。

**建議**：
- 保留原本的 `addReplyErrorSds(c, err)` 或改為 `addReplyError(c, err)` 後再釋放。
- 或者，將錯誤訊息複製到其他變數，在釋放後仍能回覆。

**判斷依據**：diff 中將原本的 `addReplyErrorSds(c, err)` 改為 `sdsfree(err)`，移除了錯誤回覆。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1796</code> slotRangeArrayToString 對 NULL 指標的處理可能掩蓋錯誤</summary>

新增的 `if (slots == NULL || slots->num_ranges == 0) return s;` 會在 slots 為 NULL 或空陣列時回傳空字串，但這可能掩蓋了呼叫端的邏輯錯誤。若 slots 為 NULL，通常表示程式有 bug，應使用 assert 或記錄錯誤，而非靜默回傳空字串。

**失敗情境**：
1. 某個函式意外傳入 NULL 的 slotRangeArray 給 `slotRangeArrayToString`。
2. 函式回傳空字串，後續程式可能將空字串視為有效資料，導致錯誤擴散。

**建議**：
- 考慮使用 `serverAssert(slots != NULL)` 或記錄警告。
- 若空陣列是合法狀態，則保留對 `num_ranges == 0` 的處理，但對 NULL 應有更嚴格的檢查。

**判斷依據**：diff 中新增的 NULL 檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7183 (cache hit 7168) ｜ completion tokens 2045 ｜ PR #2</sub>