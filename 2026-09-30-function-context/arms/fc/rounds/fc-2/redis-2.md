<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 slot range 的驗證流程改為先排序並合併相鄰區間，再進行驗證，並新增了 asmCountKeysInSlots 函式來統計 key 數量。主要風險在於 slotRangeArraySortAndMerge 的合併邏輯可能造成記憶體洩漏或資料損毀，以及 asmCreateImportTask 的錯誤處理路徑可能導致 double free。此外，parseSlotRangesOrReply 的錯誤處理變更可能造成記憶體洩漏。建議優先修正這些問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1867` | slotRangeArraySortAndMerge 合併時未釋放被合併的 slotRange，可能造成記憶體洩漏 | 0.90 |
| 🛑 | Blocker | `src/cluster_asm.c:830` | asmCreateImportTask 錯誤路徑可能造成 double free | 0.85 |
| ⚠️ | Major | `src/cluster.c:2015` | parseSlotRangesOrReply 錯誤路徑可能造成記憶體洩漏 | 0.80 |
| ⚠️ | Major | `src/cluster.c:1867` | slotRangeArraySortAndMerge 未處理重疊區間，可能導致驗證失敗或錯誤合併 | 0.75 |
| 🔸 | Minor | `src/cluster_asm.c:1012` | asmCountKeysInSlots 未檢查 slots 是否為 NULL，可能造成空指標存取 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1867</code> slotRangeArraySortAndMerge 合併時未釋放被合併的 slotRange，可能造成記憶體洩漏</summary>

在 slotRangeArraySortAndMerge 中，當合併相鄰區間時，直接將前一個區間的 end 更新為下一個區間的 end，但沒有釋放被合併的 slotRange 結構。如果 slotRange 結構中包含動態分配的記憶體（例如指向其他資料的指標），則會造成記憶體洩漏。此外，如果 slotRange 結構中有其他需要清理的資源，也會造成資源洩漏。建議在合併時，若 slotRange 結構擁有動態資源，應先釋放被合併的 slotRange 的資源，再更新 end。

**判斷依據**：diff 中新增的 slotRangeArraySortAndMerge 函式，在合併相鄰區間時僅更新 end 欄位，未見任何釋放資源的程式碼。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster_asm.c:830</code> asmCreateImportTask 錯誤路徑可能造成 double free</summary>

在 asmCreateImportTask 中，錯誤處理路徑新增了 `slotRangeArrayFree(slots)`，但呼叫端 clusterMigrationCommandImport 在呼叫 asmCreateImportTask 後已不再釋放 slots（原本的 `slotRangeArrayFree(slots)` 被移除）。然而，若 asmCreateImportTask 在成功建立 task 後，task->slots 直接指向傳入的 slots，則當 task 被取消或釋放時，可能會再次釋放 slots，造成 double free。建議明確所有權：在成功路徑中，task 應擁有 slots 的所有權，呼叫端不應再釋放；在失敗路徑中，asmCreateImportTask 應負責釋放 slots。目前程式碼在成功路徑中將 slots 直接賦值給 task->slots，但未將傳入的 slots 指標設為 NULL，可能導致呼叫端誤用。

**判斷依據**：diff 中 asmCreateImportTask 的修改：成功路徑 `task->slots = slots;`，錯誤路徑 `slotRangeArrayFree(slots);`，且呼叫端移除了 `slotRangeArrayFree(slots)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2015</code> parseSlotRangesOrReply 錯誤路徑可能造成記憶體洩漏</summary>

在 parseSlotRangesOrReply 中，原本在 validateSlotRanges 失敗時會呼叫 `addReplyErrorSds(c, err)` 將錯誤訊息回覆給客戶端，但修改後改為 `sdsfree(err)` 直接釋放錯誤訊息，而沒有回覆給客戶端。這可能導致客戶端收到空回覆或連線中斷，且錯誤訊息未被記錄。建議保留原本的 `addReplyErrorSds(c, err)` 行為，或改為 `addReplyError(c, err)` 後再釋放。

**判斷依據**：diff 中 parseSlotRangesOrReply 的修改：原本的 `addReplyErrorSds(c, err)` 被移除，改為 `sdsfree(err)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1867</code> slotRangeArraySortAndMerge 未處理重疊區間，可能導致驗證失敗或錯誤合併</summary>

註解中提到「Overlapping ranges are not merged.」，但函式僅合併相鄰區間（prev.end + 1 == next.start），未處理重疊區間。如果輸入包含重疊區間（例如 100-200 和 150-250），排序後合併邏輯不會將它們合併，但後續的驗證會因為 used_slots 陣列偵測到重複 slot 而回傳錯誤。這可能不是預期的行為，因為函式名稱為 NormalizeAndValidate，暗示應該正規化所有區間。建議明確處理重疊區間：要麼合併重疊區間，要麼在驗證前偵測並回報錯誤。

**判斷依據**：diff 中 slotRangeArraySortAndMerge 的註解與實作。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster_asm.c:1012</code> asmCountKeysInSlots 未檢查 slots 是否為 NULL，可能造成空指標存取</summary>

asmCountKeysInSlots 函式開頭有 `if (!slots) return 0;`，但後續使用 `slots->num_ranges` 和 `slots->ranges` 時未再檢查 slots 是否為 NULL。雖然開頭已檢查，但若 slots 在函式執行期間被其他執行緒釋放，可能造成 use-after-free。不過，此函式似乎只在單執行緒環境中呼叫，風險較低。建議在函式內再次確認 slots 不為 NULL，或確保呼叫端持有 slots 的參考。

**判斷依據**：diff 中新增的 asmCountKeysInSlots 函式。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 22310 (cache hit 22272) ｜ completion tokens 1682 ｜ PR #2</sub>