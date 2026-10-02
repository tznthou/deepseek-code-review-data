<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 slot range 的驗證函式改名並加入排序與合併相鄰範圍的功能，同時調整了 ASM 匯入任務的錯誤處理與日誌。主要風險在於 slotRangeArraySortAndMerge 的合併邏輯可能錯誤處理重疊範圍、asmCreateImportTask 的記憶體所有權轉移可能造成 double-free 或 use-after-free，以及 parseSlotRangesOrReply 的錯誤回覆不一致。建議先修正這些問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1867` | slotRangeArraySortAndMerge 合併邏輯錯誤處理重疊範圍 | 0.95 |
| 🛑 | Blocker | `src/cluster_asm.c:830` | asmCreateImportTask 記憶體所有權轉移可能導致 double-free 或 use-after-free | 0.90 |
| ⚠️ | Major | `src/cluster.c:2015` | parseSlotRangesOrReply 錯誤回覆不一致 | 0.85 |
| 🔸 | Minor | `src/cluster.c:1796` | slotRangeArrayToString 對 NULL 指標的處理可能掩蓋錯誤 | 0.70 |
| 🔸 | Minor | `src/cluster_asm.c:1013` | asmCountKeysInSlots 未檢查 slots 指標有效性 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1867</code> slotRangeArraySortAndMerge 合併邏輯錯誤處理重疊範圍</summary>

在合併時，程式碼僅檢查 `prev.end + 1 == next.start`，但若範圍重疊（例如 `0-100` 與 `50-150`），則會直接跳過合併，導致後續驗證時因重疊而失敗。然而，函式名稱與註解暗示其應能處理重疊範圍，且呼叫端 `slotRangeArrayNormalizeAndValidate` 在合併後才進行重疊檢查，因此重疊範圍將無法通過驗證，但錯誤訊息可能不直觀。建議在合併前先檢查重疊並回報明確錯誤，或修改合併邏輯以正確處理重疊（例如合併重疊範圍）。

**判斷依據**：diff 中新增的 slotRangeArraySortAndMerge 函式，其合併條件僅處理相鄰（end+1 == start），未處理重疊（end >= start）。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster_asm.c:830</code> asmCreateImportTask 記憶體所有權轉移可能導致 double-free 或 use-after-free</summary>

原本 `task->slots = slotRangeArrayDup(slots);` 會複製一份，但現在改為 `task->slots = slots;` 直接取得所有權。呼叫端 `clusterMigrationCommandImport` 已移除 `slotRangeArrayFree(slots)`，但其他呼叫端（如 `clusterAsmProcess` 中的 `ASM_EVENT_IMPORT_START`）在呼叫前會先 `slotRangeArrayDup(arg)` 並在錯誤時釋放，成功時則將所有權交給 task，這部分看似正確。然而，若 `asmCreateImportTask` 在取得所有權後、回傳前發生錯誤（例如 `asmTaskCreate` 失敗），則會執行 `goto err` 並 `slotRangeArrayFree(slots)`，但此時 `task->slots` 已指向同一記憶體，可能導致 task 後續使用已釋放的記憶體。建議在錯誤路徑中避免釋放已轉移所有權的 slots，或改為在成功建立 task 後才轉移所有權。

**判斷依據**：diff 中將 `slotRangeArrayDup(slots)` 改為直接指派，且錯誤處理路徑 `err:` 會 `slotRangeArrayFree(slots)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2015</code> parseSlotRangesOrReply 錯誤回覆不一致</summary>

原本使用 `serverAssert` 檢查參數，現在改為 `addReplyErrorArity(c)` 回覆錯誤，但後續在驗證失敗時，程式碼僅 `sdsfree(err)` 並釋放 slots，卻未呼叫 `addReplyErrorSds(c, err)` 回覆錯誤訊息，導致客戶端收到空回覆或錯誤格式。建議在驗證失敗時也回覆錯誤訊息，例如 `addReplyErrorSds(c, err)` 後再釋放。

**判斷依據**：diff 中移除了原本的 `addReplyErrorSds(c, err)`，僅保留 `sdsfree(err)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1796</code> slotRangeArrayToString 對 NULL 指標的處理可能掩蓋錯誤</summary>

新增的 `if (slots == NULL || slots->num_ranges == 0) return s;` 會在 slots 為 NULL 時回傳空字串，但呼叫端可能預期 NULL 表示錯誤，這可能掩蓋潛在的 bug。建議明確區分 NULL 和空陣列，或使用 assert 確保 slots 不為 NULL。

**判斷依據**：diff 中新增的 NULL 檢查，但未區分 NULL 與空陣列。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster_asm.c:1013</code> asmCountKeysInSlots 未檢查 slots 指標有效性</summary>

函式僅檢查 `if (!slots) return 0;`，但未檢查 `slots->ranges` 是否為 NULL 或 `num_ranges` 是否合理。若呼叫端傳入未初始化的 slotRangeArray，可能導致記憶體存取錯誤。建議增加對 `slots->ranges` 的檢查。

**判斷依據**：diff 中新增的函式，僅檢查 slots 指標。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7203 (cache hit 6144) ｜ completion tokens 1492 ｜ PR #2</sub>