<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 slot range 的驗證流程改為先排序並合併相鄰區間，再進行重疊與範圍檢查，並新增了對應的測試。主要風險在於 `asmCreateImportTask` 的記憶體所有權轉移，以及 `slotRangeArraySortAndMerge` 對重疊區間未合併的處理可能與驗證邏輯不一致。此外，`parseSlotRangesOrReply` 中錯誤訊息的釋放方式有變更，需確認不會造成記憶體洩漏。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/cluster_asm.c:830` | asmCreateImportTask 的記憶體所有權轉移可能造成 double-free 或 use-after-free | 0.80 |
| ⚠️ | Major | `src/cluster.c:1855` | slotRangeArraySortAndMerge 未合併重疊區間，可能導致驗證失敗或錯誤合併 | 0.70 |
| 🔸 | Minor | `src/cluster.c:2015` | parseSlotRangesOrReply 中錯誤訊息釋放方式變更可能造成記憶體洩漏 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/cluster_asm.c:830</code> asmCreateImportTask 的記憶體所有權轉移可能造成 double-free 或 use-after-free</summary>

在 `asmCreateImportTask` 中，原本使用 `slotRangeArrayDup(slots)` 複製一份 slots，現在改為直接指派 `task->slots = slots`，並在錯誤路徑中釋放 `slots`。這表示呼叫端（如 `clusterMigrationCommandImport`）不再需要釋放 slots，但其他呼叫端（如 `clusterAsmProcess`）可能仍持有原始指標，導致 double-free 或 use-after-free。

具體情境：
1. `clusterMigrationCommandImport` 呼叫 `parseSlotRangesOrReply` 取得 slots，然後傳給 `asmCreateImportTask`。若 `asmCreateImportTask` 成功，slots 的所有權轉移給 task，之後 task 釋放時會 free slots。但 `clusterMigrationCommandImport` 在成功後沒有釋放 slots，這是正確的。
2. 然而，`clusterAsmProcess` 在 `ASM_EVENT_IMPORT_START` 事件中，先 `slotRangeArrayDup(arg)` 複製一份 slots，然後呼叫 `asmCreateImportTask`。若 `asmCreateImportTask` 失敗，它會釋放傳入的 slots（即複製的那份），但 `clusterAsmProcess` 在失敗後沒有釋放原始 `arg`，這可能導致記憶體洩漏。若 `asmCreateImportTask` 成功，則 task 擁有複製的 slots，但 `clusterAsmProcess` 也沒有釋放原始 `arg`，同樣可能洩漏。

建議：明確所有權規則，例如讓 `asmCreateImportTask` 總是複製 slots，或讓呼叫端在成功後不再持有所有權，並在文件或註解中說明。

**判斷依據**：diff 中 `task->slots = slotRangeArrayDup(slots);` 改為 `task->slots = slots;`，且錯誤路徑新增 `slotRangeArrayFree(slots);`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1855</code> slotRangeArraySortAndMerge 未合併重疊區間，可能導致驗證失敗或錯誤合併</summary>

`slotRangeArraySortAndMerge` 的註解明確指出「Overlapping ranges are not merged.」，但函式名稱和用途暗示會合併相鄰區間。若輸入包含重疊區間（例如 `0-100 50-150`），排序後相鄰檢查 `prev.end + 1 == next.start` 不成立，因此不會合併，但後續的 `slotRangeArrayNormalizeAndValidate` 會偵測到重疊並回傳錯誤。這可能不是預期行為，因為呼叫端可能期望重疊區間被合併或至少被視為有效。

具體情境：
- 使用者輸入 `CLUSTER MIGRATION IMPORT 0 100 50 150`，預期可能被視為 `0-150`，但實際上會因為重疊而回傳錯誤。
- 若未來有其他程式碼依賴此函式來正規化重疊區間，可能會產生非預期結果。

建議：明確函式的行為，若只合併相鄰區間，應在函式名稱或註解中強調，並確保所有呼叫端都了解重疊區間不會被合併。或者考慮合併重疊區間，以符合直覺。

**判斷依據**：diff 中新增的函式註解明確指出重疊區間不會被合併，但函式名稱 `slotRangeArraySortAndMerge` 可能造成誤解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2015</code> parseSlotRangesOrReply 中錯誤訊息釋放方式變更可能造成記憶體洩漏</summary>

在 `parseSlotRangesOrReply` 中，原本在驗證失敗時使用 `addReplyErrorSds(c, err)` 將錯誤訊息傳給客戶端，該函式會負責釋放 `err`。現在改為 `sdsfree(err)` 後直接回傳 NULL，但沒有將錯誤訊息回覆給客戶端。這可能導致客戶端收到不明確的錯誤（例如只有 generic error），且若 `err` 為 NULL 時呼叫 `sdsfree` 可能不安全。

具體情境：
- 當 `slotRangeArrayNormalizeAndValidate` 回傳錯誤並設定 `err`，程式會釋放 `err` 但沒有回覆客戶端，客戶端可能只看到 generic error，難以除錯。
- 若 `err` 為 NULL（例如某些錯誤路徑未設定），`sdsfree(NULL)` 可能導致 crash（取決於實作）。

建議：保留 `addReplyErrorSds` 或明確回覆錯誤訊息，並確保 `err` 不為 NULL 再釋放。

**判斷依據**：diff 中原本的 `addReplyErrorSds(c, err);` 被移除，改為 `sdsfree(err);`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 22310 (cache hit 1536) ｜ completion tokens 1564 ｜ PR #2</sub>