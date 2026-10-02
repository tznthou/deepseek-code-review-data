<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將 slot range 的驗證流程改為先正規化（排序與合併相鄰範圍）再驗證，並調整相關函式名稱與記憶體管理。整體方向合理，但存在幾個需要修正的問題：`parseSlotRangesOrReply` 在驗證失敗時未回覆錯誤給客戶端，可能導致客戶端收到空回覆；`asmCreateImportTask` 的錯誤處理路徑中可能重複釋放記憶體；`asmCountKeysInSlots` 使用 `server.db[0]` 可能不正確；以及測試中未驗證錯誤情境。建議修正後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:2015` | 驗證失敗時未回覆錯誤給客戶端 | 0.95 |
| 🛑 | Blocker | `src/cluster_asm.c:830` | 錯誤路徑可能導致重複釋放記憶體 | 0.90 |
| ⚠️ | Major | `src/cluster_asm.c:1012` | 使用 server.db[0] 可能不正確 | 0.80 |
| 🔸 | Minor | `tests/unit/cluster/atomic-slot-migration.tcl:514` | 測試未涵蓋錯誤情境 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:2015</code> 驗證失敗時未回覆錯誤給客戶端</summary>

在 `parseSlotRangesOrReply` 中，當 `slotRangeArrayNormalizeAndValidate` 回傳錯誤時，程式碼釋放了 `err` 和 `slots` 並回傳 `NULL`，但沒有呼叫 `addReplyErrorSds` 或類似函式將錯誤訊息回傳給客戶端。這會導致客戶端在輸入無效的 slot range 時收到空回覆（nil），而非明確的錯誤訊息，違反 Redis 命令的錯誤處理慣例。

**失敗情境**：執行 `CLUSTER MIGRATION IMPORT 7000 7001 7000 7001`（重疊範圍），客戶端會收到空回覆，無法得知錯誤原因。

**建議修法**：在釋放 `err` 之前，先呼叫 `addReplyErrorSds(c, err)` 將錯誤訊息回傳給客戶端，再釋放 `slots`。

**判斷依據**：diff 中 `parseSlotRangesOrReply` 的修改片段顯示，原本的 `addReplyErrorSds(c, err)` 被移除，改為直接 `sdsfree(err)`，且沒有其他回覆錯誤的程式碼。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster_asm.c:830</code> 錯誤路徑可能導致重複釋放記憶體</summary>

在 `asmCreateImportTask` 中，函式現在直接使用傳入的 `slots` 指標（`task->slots = slots;`），並在錯誤路徑中呼叫 `slotRangeArrayFree(slots)`。然而，呼叫端 `clusterMigrationCommandImport` 在呼叫 `asmCreateImportTask` 後已不再釋放 `slots`（原本的 `slotRangeArrayFree(slots)` 被移除），因此所有權已轉移。但若 `asmCreateImportTask` 在錯誤路徑中釋放了 `slots`，而呼叫端在某些情況下仍持有該指標（例如 `clusterAsmProcess` 中先複製了一份再傳入），可能導致重複釋放或使用已釋放的記憶體。

**失敗情境**：在 `clusterAsmProcess` 中，`slots` 是透過 `slotRangeArrayDup(arg)` 複製的，若 `asmCreateImportTask` 失敗並釋放了 `slots`，呼叫端後續若再使用 `arg` 或 `slots` 可能造成問題。

**建議修法**：明確所有權轉移規則，例如在 `asmCreateImportTask` 成功時才接管 `slots`，失敗時由呼叫端負責釋放；或統一由 `asmCreateImportTask` 釋放，但確保呼叫端不再使用。

**判斷依據**：diff 中 `asmCreateImportTask` 的修改顯示 `task->slots = slots;` 取代了原本的 `slotRangeArrayDup(slots)`，且錯誤路徑新增了 `slotRangeArrayFree(slots)`。同時 `clusterMigrationCommandImport` 移除了呼叫後的 `slotRangeArrayFree(slots)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster_asm.c:1012</code> 使用 server.db[0] 可能不正確</summary>

`asmCountKeysInSlots` 函式使用 `server.db[0].keys` 來計算 key 數量，但 Redis 支援多個資料庫（預設 16 個），且 slot 與資料庫無關。若 key 存在於非 0 號資料庫，此函式將無法正確計算。

**失敗情境**：在非預設資料庫（例如 `SELECT 1`）中執行 slot migration，日誌中記錄的 key 數量會不正確。

**建議修法**：確認 slot migration 是否僅考慮 db0，或應遍歷所有資料庫。若僅考慮 db0，應在程式碼中明確註明原因。

**判斷依據**：diff 中新增的 `asmCountKeysInSlots` 函式直接使用 `server.db[0].keys`，未考慮其他資料庫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/cluster/atomic-slot-migration.tcl:514</code> 測試未涵蓋錯誤情境</summary>

新增的測試僅驗證了成功案例（相鄰和未排序的範圍），但未測試無效輸入（如重疊範圍、超出範圍）的錯誤處理。這使得 `parseSlotRangesOrReply` 中的錯誤回覆缺失問題無法被測試發現。

**建議修法**：增加測試案例，驗證無效輸入時客戶端能收到明確的錯誤訊息。

**判斷依據**：diff 中新增的測試僅包含成功案例，未包含錯誤案例。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6156 (cache hit 1408) ｜ completion tokens 1792 ｜ PR #2</sub>