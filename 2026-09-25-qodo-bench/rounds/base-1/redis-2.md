<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 slot range 的驗證流程改為先排序並合併相鄰區間，再進行驗證，並將此邏輯套用至 ASM 匯入任務。主要風險在於 `asmCreateImportTask` 的記憶體所有權轉移、`slotRangeArrayNormalizeAndValidate` 的錯誤處理，以及 `asmCountKeysInSlots` 的效能問題。建議優先修正記憶體管理與錯誤回覆路徑，並評估大量 slot 時的效能影響。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster_asm.c:830` | 記憶體所有權轉移後，錯誤路徑可能造成 double free 或記憶體洩漏 | 0.95 |
| ⚠️ | Major | `src/cluster.c:2015` | 驗證失敗時未回覆錯誤給客戶端 | 0.85 |
| ⚠️ | Major | `src/cluster_asm.c:1012` | `asmCountKeysInSlots` 可能造成大量迴圈與效能問題 | 0.80 |
| 🔸 | Minor | `src/cluster.c:1744` | `slotRangeArrayNormalizeAndValidate` 在排序合併後未重新檢查範圍數量上限 | 0.70 |
| 🔸 | Minor | `src/cluster.c:1855` | `slotRangeArraySortAndMerge` 未處理重疊範圍 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster_asm.c:830</code> 記憶體所有權轉移後，錯誤路徑可能造成 double free 或記憶體洩漏</summary>

在 `asmCreateImportTask` 中，原本使用 `slotRangeArrayDup(slots)` 複製一份 slot range，現在改為直接指派 `task->slots = slots;`，將所有權轉移給 task。然而，函式內有多個 `goto err` 路徑，這些路徑會執行 `slotRangeArrayFree(slots)`。若在 `task->slots = slots;` 之後發生錯誤（例如後續的 `asmTaskAdd` 失敗），則會釋放 `slots`，但 `task` 仍持有指向已釋放記憶體的指標，導致後續使用時發生 use-after-free。此外，呼叫端 `clusterMigrationCommandImport` 已不再於失敗時釋放 `slots`，若 `asmCreateImportTask` 在指派前就失敗，則 `slots` 不會被釋放，造成記憶體洩漏。

建議：
- 在 `task->slots = slots;` 之後，將 `slots` 設為 NULL，並在錯誤路徑中檢查 `slots` 是否為 NULL 再決定是否釋放。
- 或者，在指派前先完成所有可能失敗的操作，確保所有權轉移後不會再有錯誤路徑。

**判斷依據**：diff 中 `task->slots = slots;` 取代了原本的 `task->slots = slotRangeArrayDup(slots);`，且函式內有多個 `goto err` 路徑會執行 `slotRangeArrayFree(slots)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2015</code> 驗證失敗時未回覆錯誤給客戶端</summary>

在 `parseSlotRangesOrReply` 中，原本驗證失敗時會呼叫 `addReplyErrorSds(c, err)` 將錯誤訊息回覆給客戶端，但修改後只呼叫 `sdsfree(err)` 釋放錯誤訊息，卻未回覆任何錯誤。這會導致客戶端在提供無效 slot range 時收到空回覆或逾時，而非明確的錯誤訊息。

建議：
- 在釋放 `err` 之前，先呼叫 `addReplyErrorSds(c, err)` 回覆錯誤。
- 或者，若 `err` 為 NULL，則回覆一個通用的錯誤訊息。

**判斷依據**：diff 中移除了 `addReplyErrorSds(c, err);`，只留下 `sdsfree(err);`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster_asm.c:1012</code> `asmCountKeysInSlots` 可能造成大量迴圈與效能問題</summary>

`asmCountKeysInSlots` 會針對每個 slot range 中的每個 slot 呼叫 `kvstoreDictSize`，若 slot range 涵蓋大量 slot（例如整個 hash slot 空間 0-16383），則會執行 16384 次函式呼叫。雖然 `kvstoreDictSize` 本身可能只是 O(1) 的查詢，但大量的函式呼叫仍可能造成不必要的效能負擔，特別是在日誌記錄或任務啟動時頻繁呼叫。

建議：
- 評估是否有更有效率的方式取得 key 數量，例如直接從 `kvstore` 取得總數，或使用批次 API。
- 若無法避免，考慮加入快取或限制呼叫頻率。

**判斷依據**：新增的函式包含巢狀迴圈，內層迴圈範圍由 slot range 決定，可能高達 16384 次迭代。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1744</code> `slotRangeArrayNormalizeAndValidate` 在排序合併後未重新檢查範圍數量上限</summary>

函式在排序合併前檢查 `slots->num_ranges >= CLUSTER_SLOTS`，但合併後範圍數量可能減少，因此不會違反上限。然而，若合併後範圍數量仍大於等於 `CLUSTER_SLOTS`，則後續的驗證迴圈仍會執行，但這可能不是預期行為。建議在合併後再次檢查範圍數量，或確認此情況是否可能發生。

**判斷依據**：合併後未重新驗證 `num_ranges` 是否仍小於 `CLUSTER_SLOTS`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1855</code> `slotRangeArraySortAndMerge` 未處理重疊範圍</summary>

註解明確指出「Overlapping ranges are not merged.」，但若輸入包含重疊範圍（例如 100-200 和 150-250），合併後仍會保留兩個範圍，且後續的驗證會偵測到重疊並回報錯誤。這可能是預期行為，但建議在函式中明確處理或至少記錄此情況，以避免未來誤用。

**判斷依據**：註解說明重疊範圍不會被合併，但未說明後續如何處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6192 (cache hit 1536) ｜ completion tokens 1781 ｜ PR #2</sub>