<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 slot range 的驗證流程改為先排序並合併相鄰範圍，再進行驗證，並將此邏輯套用至 ASM 操作與相關函式。主要風險在於記憶體管理與錯誤處理路徑的變更，可能導致記憶體洩漏或重複釋放；此外，合併邏輯未處理重疊範圍，可能掩蓋使用者輸入錯誤。建議優先修正 `asmCreateImportTask` 的記憶體所有權問題，並確認 `parseSlotRangesOrReply` 的錯誤回覆行為。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster_asm.c:830` | 記憶體所有權轉移可能導致重複釋放或洩漏 | 0.95 |
| ⚠️ | Major | `src/cluster.c:2015` | 錯誤回覆被移除，可能導致客戶端無回應 | 0.85 |
| ⚠️ | Major | `src/cluster.c:1867` | 合併邏輯未處理重疊範圍，可能掩蓋輸入錯誤 | 0.80 |
| 🔸 | Minor | `src/cluster.c:1796` | 空指標檢查可能不必要，但可接受 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster_asm.c:830</code> 記憶體所有權轉移可能導致重複釋放或洩漏</summary>

在 `asmCreateImportTask` 中，原本使用 `slotRangeArrayDup(slots)` 複製一份 slot range 陣列，現在改為直接指派 `task->slots = slots`，將呼叫端傳入的記憶體所有權轉移給 task。然而，呼叫端 `clusterMigrationCommandImport` 已移除 `slotRangeArrayFree(slots)`，但其他呼叫端（如 `clusterAsmProcess`）可能仍持有該指標並在錯誤路徑中釋放，造成重複釋放（double free）或記憶體洩漏。

具體失敗情境：
1. `clusterAsmProcess` 在 `ASM_EVENT_IMPORT_START` 事件中，先複製一份 `slots` 並驗證，驗證成功後呼叫 `asmCreateImportTask(task_id, slots, &errsds)`。若 `asmCreateImportTask` 內部因其他原因失敗（例如 `source == getMyClusterNode()`），會執行 `goto err` 並呼叫 `slotRangeArrayFree(slots)`，但此時 `slots` 的所有權已轉移給 task（若 task 建立成功），導致 task 持有的指標被釋放，後續使用 task->slots 時會存取已釋放記憶體。
2. 若 `asmCreateImportTask` 成功，`clusterAsmProcess` 不會再釋放 `slots`，但 `clusterMigrationCommandImport` 已不再釋放，因此所有權轉移是完整的。然而，若未來有其他呼叫端未遵循此所有權轉移規則，可能造成洩漏或重複釋放。

建議：明確所有權轉移規則，例如在函式註解中說明「成功時取得所有權，失敗時釋放」，並確保所有呼叫端一致。或者，保留複製方式，避免所有權轉移的複雜性。

**判斷依據**：diff 中 `task->slots = slotRangeArrayDup(slots);` 改為 `task->slots = slots;`，且 `clusterMigrationCommandImport` 移除了 `slotRangeArrayFree(slots);`，但 `clusterAsmProcess` 中仍可能持有原始指標。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2015</code> 錯誤回覆被移除，可能導致客戶端無回應</summary>

在 `parseSlotRangesOrReply` 中，原本在驗證失敗時會呼叫 `addReplyErrorSds(c, err)` 將錯誤訊息回覆給客戶端，現在改為僅 `sdsfree(err)` 並回傳 NULL，沒有發送任何回覆。這會導致客戶端在提供無效 slot range 時收到空回應或連線逾時，而非明確的錯誤訊息。

具體失敗情境：
1. 使用者執行 `CLUSTER MIGRATION IMPORT 7000 7001 7002`（參數數量錯誤），函式會回傳 NULL，但客戶端不會收到任何錯誤回覆，可能導致客戶端等待逾時。
2. 使用者提供重疊或超出範圍的 slot range，驗證失敗後同樣沒有錯誤回覆。

建議：保留 `addReplyErrorSds(c, err)` 或改用 `addReplyError(c, err)` 發送錯誤訊息，並在回覆後釋放 `err`。

**判斷依據**：diff 中 `addReplyErrorSds(c, err);` 被移除，僅留下 `sdsfree(err);`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1867</code> 合併邏輯未處理重疊範圍，可能掩蓋輸入錯誤</summary>

`slotRangeArraySortAndMerge` 僅合併相鄰範圍（`prev.end + 1 == next.start`），但未處理重疊範圍。若使用者輸入重疊的 slot range（例如 `7000-7100 7050-7150`），合併後仍會保留兩個重疊的範圍，後續驗證會因重疊而失敗。然而，若重疊範圍在排序後相鄰且恰好符合合併條件（例如 `7000-7100 7101-7200`），則會被合併成一個範圍，這可能掩蓋使用者原本的輸入錯誤，因為使用者可能無意中提供了重疊或相鄰的範圍，但系統自動合併後通過驗證。

具體失敗情境：
1. 使用者輸入 `7000-7100 7100-7200`（重疊於 7100），排序後為 `7000-7100 7100-7200`，由於 `7100 + 1 != 7100`，不會合併，驗證時會因重疊而失敗，這是正確的。
2. 使用者輸入 `7000-7100 7101-7200`（相鄰），排序後合併為 `7000-7200`，驗證通過。這可能不是使用者預期的行為，因為使用者可能希望保留兩個獨立的範圍。

建議：在合併前先檢查重疊，若存在重疊則回傳錯誤，或僅在明確要求合併時才合併相鄰範圍。

**判斷依據**：diff 中新增的合併邏輯僅處理相鄰，未處理重疊。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1796</code> 空指標檢查可能不必要，但可接受</summary>

在 `slotRangeArrayToString` 中新增了 `if (slots == NULL || slots->num_ranges == 0) return s;`，這是一個防禦性檢查。然而，呼叫端通常不會傳入 NULL 或空陣列，因此這個檢查可能不是必要的。但這不會造成問題，反而提高了健壯性。

**判斷依據**：diff 中新增的檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6156 (cache hit 6144) ｜ completion tokens 1774 ｜ PR #2</sub>