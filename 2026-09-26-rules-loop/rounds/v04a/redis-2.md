<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 slot range 的驗證流程改為先正規化（排序與合併相鄰範圍）再驗證，並調整了 ASM 任務建立時的記憶體管理與錯誤處理。主要風險在於 asmCreateImportTask 的記憶體所有權轉移、slotRangeArrayNormalizeAndValidate 的錯誤處理不一致，以及 asmCountKeysInSlots 的效能問題。建議優先修正記憶體管理與錯誤處理路徑。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster_asm.c:830` | asmCreateImportTask 記憶體所有權轉移不一致導致 double-free 或 memory leak | 0.95 |
| ⚠️ | Major | `src/cluster.c:2015` | slotRangeArrayNormalizeAndValidate 錯誤時未回傳錯誤訊息給客戶端 | 0.85 |
| ⚠️ | Major | `src/cluster_asm.c:1012` | asmCountKeysInSlots 可能造成大量迴圈與效能問題 | 0.80 |
| 🔸 | Minor | `src/cluster.c:1855` | slotRangeArraySortAndMerge 未處理重疊範圍 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster_asm.c:830</code> asmCreateImportTask 記憶體所有權轉移不一致導致 double-free 或 memory leak</summary>

在 `asmCreateImportTask` 中，原本 `task->slots = slotRangeArrayDup(slots);` 改為 `task->slots = slots;`，直接取得傳入指標的所有權。但呼叫端 `clusterMigrationCommandImport` 移除了 `slotRangeArrayFree(slots);`，而 `clusterAsmProcess` 在呼叫前會先 `slotRangeArrayDup(arg)` 再傳入，因此該 dup 的記憶體會由 task 持有，但若後續錯誤路徑（如 `source == getMyClusterNode()` 或已有其他任務）會 `goto err` 並 `slotRangeArrayFree(slots)`，此時 task 尚未建立，不會 double-free。然而，若 `asmTaskCreate` 失敗（回傳 NULL），則 `task->slots = slots;` 不會執行，但 `err` 標籤仍會 `slotRangeArrayFree(slots)`，導致傳入的 slots 被釋放，但呼叫端可能仍持有指標（例如 `clusterAsmProcess` 中的 `slots` 變數），造成 double-free。此外，`clusterMigrationCommandImport` 在 `asmCreateImportTask` 回傳 NULL 時不會釋放 slots（因為已移除 free），但 `asmCreateImportTask` 內部會釋放，因此該路徑正確。但若 `asmCreateImportTask` 成功，slots 所有權轉移給 task，後續 task 釋放時會 free，但 `clusterMigrationCommandImport` 不再 free，正確。然而，`clusterAsmProcess` 中，若 `slotRangeArrayNormalizeAndValidate` 失敗，會 free 掉 dup 的 slots，但 `asmCreateImportTask` 未被呼叫，因此不會 double-free。但若 `asmCreateImportTask` 內部在 `asmTaskCreate` 失敗時 free 了傳入的 slots，而 `clusterAsmProcess` 並不知道，後續也不會再 free，因此不會 double-free。但問題在於 `asmCreateImportTask` 的錯誤處理不一致：有些錯誤路徑會 free slots，有些不會，導致呼叫端難以管理記憶體。建議明確所有權：要嘛總是由 `asmCreateImportTask` 取得所有權並在錯誤時 free，要嘛總是由呼叫端保留所有權並在錯誤時 free，不要混用。

**判斷依據**：diff 中 `task->slots = slotRangeArrayDup(slots);` 改為 `task->slots = slots;`，且 `clusterMigrationCommandImport` 移除了 `slotRangeArrayFree(slots);`，但 `clusterAsmProcess` 仍保留 `slotRangeArrayDup(arg)` 並在驗證失敗時 free。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2015</code> slotRangeArrayNormalizeAndValidate 錯誤時未回傳錯誤訊息給客戶端</summary>

在 `parseSlotRangesOrReply` 中，原本 `validateSlotRanges` 失敗時會 `addReplyErrorSds(c, err);` 將錯誤訊息回傳給客戶端，但改為 `slotRangeArrayNormalizeAndValidate` 後，錯誤處理變成 `sdsfree(err); slotRangeArrayFree(slots); return NULL;`，沒有回傳任何錯誤訊息。這會導致客戶端收到空回覆或連線中斷，無法得知具體錯誤原因。應保留 `addReplyErrorSds(c, err);` 或改用其他方式回傳錯誤。

**判斷依據**：diff 中原本的 `addReplyErrorSds(c, err);` 被移除，改為 `sdsfree(err);`，導致錯誤訊息遺失。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster_asm.c:1012</code> asmCountKeysInSlots 可能造成大量迴圈與效能問題</summary>

`asmCountKeysInSlots` 會對每個 slot range 中的每個 slot 呼叫 `kvstoreDictSize`，若 slot range 涵蓋大量 slots（例如整個 cluster 有 16384 個 slots），且被頻繁呼叫（例如在日誌事件中），可能造成顯著的效能影響。建議考慮使用更有效率的方式計算 key 數量，或限制使用情境。

**判斷依據**：新增的函式，在日誌事件中被呼叫，可能對每個 slot 進行查詢。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1855</code> slotRangeArraySortAndMerge 未處理重疊範圍</summary>

註解提到「Overlapping ranges are not merged.」，但若輸入包含重疊範圍（例如 100-200 和 150-250），排序後合併邏輯只會合併相鄰（end+1 == start）的範圍，重疊的範圍會保留為兩個獨立的範圍，但後續驗證會檢查重疊並回傳錯誤。這可能導致使用者輸入重疊範圍時，正規化後仍無法通過驗證，但錯誤訊息可能不夠明確。建議在正規化階段一併處理重疊，或提供更清楚的錯誤訊息。

**判斷依據**：註解明確指出不處理重疊，但驗證函式會拒絕重疊，可能造成混淆。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6685 (cache hit 6144) ｜ completion tokens 1762 ｜ PR #2</sub>