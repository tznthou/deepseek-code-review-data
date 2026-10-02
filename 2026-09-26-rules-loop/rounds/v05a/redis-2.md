<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 slot range 的驗證流程改為先正規化（排序與合併相鄰區間）再驗證，並調整相關函式名稱與呼叫點。主要風險在於 asmCreateImportTask 的記憶體所有權轉移、parseSlotRangesOrReply 的錯誤處理路徑，以及 slotRangeArraySortAndMerge 對重疊區間未處理可能導致的資料遺失。建議優先修正記憶體管理與錯誤回覆邏輯。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster_asm.c:830` | asmCreateImportTask 直接持有傳入的 slots 指標，導致記憶體所有權混亂 | 0.95 |
| ⚠️ | Major | `src/cluster.c:2015` | parseSlotRangesOrReply 在驗證失敗時未回覆錯誤給客戶端 | 0.85 |
| ⚠️ | Major | `src/cluster.c:1867` | slotRangeArraySortAndMerge 未處理重疊區間，可能導致資料遺失 | 0.80 |
| 🔸 | Minor | `src/cluster.c:1796` | slotRangeArrayToString 對 NULL 指標的處理可能掩蓋錯誤 | 0.70 |
| 🔸 | Minor | `src/cluster_asm.c:1013` | asmCountKeysInSlots 未檢查 slots 指標是否為 NULL | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster_asm.c:830</code> asmCreateImportTask 直接持有傳入的 slots 指標，導致記憶體所有權混亂</summary>

在 `asmCreateImportTask` 中，原本使用 `slotRangeArrayDup(slots)` 複製一份，現在改為直接 `task->slots = slots;`。這使得呼叫端（如 `clusterMigrationCommandImport`）不再負責釋放 `slots`，但其他呼叫路徑（如 `clusterAsmProcess`）可能仍持有原始指標並在錯誤時釋放，造成 double-free 或 use-after-free。

例如：
- `clusterMigrationCommandImport` 呼叫 `asmCreateImportTask` 後不再 `slotRangeArrayFree(slots)`，若任務建立失敗，函式內部會釋放 `slots`，但呼叫端可能仍持有指標。
- `clusterAsmProcess` 中，先 `slotRangeArrayDup(arg)` 產生新指標，再傳給 `asmCreateImportTask`，若後續錯誤，`clusterAsmProcess` 可能再次釋放同一指標。

建議：明確所有權轉移規則，例如讓 `asmCreateImportTask` 一律複製傳入的 slots，或由呼叫端統一管理生命週期。

**判斷依據**：diff 中 `task->slots = slotRangeArrayDup(slots);` 改為 `task->slots = slots;`，且 `clusterMigrationCommandImport` 移除了 `slotRangeArrayFree(slots)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2015</code> parseSlotRangesOrReply 在驗證失敗時未回覆錯誤給客戶端</summary>

原本 `validateSlotRanges` 失敗時會呼叫 `addReplyErrorSds(c, err)` 將錯誤訊息回覆給客戶端，但改為 `slotRangeArrayNormalizeAndValidate` 後，錯誤路徑只釋放 `err` 和 `slots`，沒有回覆任何錯誤。這會導致客戶端收到空回覆或連線中斷，而非明確的錯誤訊息。

建議：在錯誤路徑中保留 `addReplyErrorSds(c, err)` 或改用其他方式回覆錯誤。

**判斷依據**：diff 中原本的 `addReplyErrorSds(c, err);` 被移除，改為 `sdsfree(err);`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1867</code> slotRangeArraySortAndMerge 未處理重疊區間，可能導致資料遺失</summary>

函式註解明確指出「Overlapping ranges are not merged.」，但合併邏輯僅處理相鄰（`prev.end + 1 == next.start`）的情況。若輸入包含重疊區間（例如 `0-10 5-15`），排序後會保留兩個區間，但後續驗證會因重疊而失敗。然而，若重疊區間在合併前未被偵測，可能導致某些 slot 被重複計算或遺漏。

建議：在合併前先檢查重疊，或明確拒絕重疊輸入。

**判斷依據**：diff 中新增的 `slotRangeArraySortAndMerge` 函式，註解提到不處理重疊，但未見重疊檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1796</code> slotRangeArrayToString 對 NULL 指標的處理可能掩蓋錯誤</summary>

新增的 `if (slots == NULL || slots->num_ranges == 0) return s;` 會在輸入為 NULL 時回傳空字串，但這可能讓呼叫端誤以為是合法空範圍，而忽略潛在的 NULL 指標錯誤。建議在 NULL 時回傳 NULL 或使用 assert。

**判斷依據**：diff 中新增的 NULL 檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster_asm.c:1013</code> asmCountKeysInSlots 未檢查 slots 指標是否為 NULL</summary>

函式開頭有 `if (!slots) return 0;`，但後續直接使用 `slots->num_ranges` 和 `slots->ranges`，若呼叫端傳入 NULL 會導致 crash。雖然目前呼叫點可能都有保證非 NULL，但建議增加防禦性檢查或 assert。

**判斷依據**：diff 中新增的 `asmCountKeysInSlots` 函式。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7169 (cache hit 6144) ｜ completion tokens 1523 ｜ PR #2</sub>