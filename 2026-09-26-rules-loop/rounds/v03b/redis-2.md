<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 將 slot range 的驗證流程改為先正規化（排序與合併相鄰區間）再驗證，並調整了 ASM 任務建立時的記憶體管理與錯誤處理，同時新增了計算 slot 內鍵數的輔助函式。主要風險在於 slotRangeArraySortAndMerge 的合併邏輯可能造成資料遺失（例如重疊區間或非相鄰區間被錯誤合併），以及 asmCreateImportTask 的記憶體所有權轉移可能導致 double-free 或 use-after-free。此外，parseSlotRangesOrReply 的錯誤處理路徑可能造成記憶體洩漏。建議先修正這些記憶體管理與合併邏輯問題，再進行合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1867` | slotRangeArraySortAndMerge 合併邏輯可能造成資料遺失 | 0.90 |
| 🛑 | Blocker | `src/cluster_asm.c:830` | asmCreateImportTask 記憶體所有權轉移可能導致 double-free 或 use-after-free | 0.85 |
| ⚠️ | Major | `src/cluster.c:2015` | parseSlotRangesOrReply 錯誤路徑可能造成記憶體洩漏 | 0.80 |
| ⚠️ | Major | `src/cluster.c:1796` | slotRangeArrayToString 未檢查 slots 指標是否為 NULL | 0.75 |
| 🔸 | Minor | `src/cluster_asm.c:1013` | asmCountKeysInSlots 未檢查 slots 指標是否為 NULL | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1867</code> slotRangeArraySortAndMerge 合併邏輯可能造成資料遺失</summary>

在 slotRangeArraySortAndMerge 中，合併條件僅檢查 `slots->ranges[idx].end + 1 == slots->ranges[i].start`，但未檢查重疊區間。若輸入包含重疊區間（例如 `0-10 5-15`），排序後會將第二個區間直接覆蓋到第一個區間上，導致第一個區間的部分資料遺失。此外，若區間非相鄰但重疊（例如 `0-10 5-6`），也會錯誤合併。建議在合併前先檢查重疊，若重疊則回傳錯誤或保留原始區間。

**判斷依據**：diff 中新增的 slotRangeArraySortAndMerge 函式，合併條件僅考慮相鄰，未處理重疊。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster_asm.c:830</code> asmCreateImportTask 記憶體所有權轉移可能導致 double-free 或 use-after-free</summary>

在 asmCreateImportTask 中，原本使用 `slotRangeArrayDup(slots)` 複製一份 slots，現在改為直接指派 `task->slots = slots`，將所有權轉移給 task。但呼叫端 clusterMigrationCommandImport 在呼叫後不再釋放 slots，而 clusterAsmProcess 中則會先複製一份再傳入，因此可能造成記憶體洩漏或 double-free。建議明確所有權轉移規則，並在錯誤路徑中正確釋放。

**判斷依據**：diff 中將 `slotRangeArrayDup(slots)` 改為 `task->slots = slots`，且呼叫端釋放邏輯不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2015</code> parseSlotRangesOrReply 錯誤路徑可能造成記憶體洩漏</summary>

在 parseSlotRangesOrReply 中，當 slotRangeArrayNormalizeAndValidate 回傳錯誤時，程式碼執行 `sdsfree(err)` 後直接 `slotRangeArrayFree(slots)` 並回傳 NULL，但未將 err 設為 NULL，可能造成後續使用已釋放的 err。此外，若 slotRangeArrayNormalizeAndValidate 內部已釋放 err，則此處 double-free。建議確認 err 的所有權，並在釋放後設為 NULL。

**判斷依據**：diff 中錯誤處理路徑，sdsfree(err) 後未將 err 設為 NULL，且可能與內部釋放衝突。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1796</code> slotRangeArrayToString 未檢查 slots 指標是否為 NULL</summary>

slotRangeArrayToString 新增了 `if (slots == NULL || slots->num_ranges == 0) return s;`，但若 slots 為 NULL，則 `slots->num_ranges` 會造成 NULL pointer dereference。建議改為 `if (slots == NULL) return s;` 或使用 `if (!slots || slots->num_ranges == 0)`。

**判斷依據**：diff 中新增的檢查，slots 為 NULL 時仍會存取 slots->num_ranges。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster_asm.c:1013</code> asmCountKeysInSlots 未檢查 slots 指標是否為 NULL</summary>

asmCountKeysInSlots 函式開頭有 `if (!slots) return 0;`，但後續直接使用 `slots->num_ranges`，若 slots 為 NULL 則會 crash。建議改為 `if (!slots || slots->num_ranges == 0) return 0;`。

**判斷依據**：diff 中新增的函式，未檢查 slots->num_ranges 是否為 0。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7203 (cache hit 7168) ｜ completion tokens 1450 ｜ PR #2</sub>