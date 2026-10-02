<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 slot range 的驗證流程改為先排序合併相鄰區間再驗證，並調整了 ASM 任務的記憶體管理與日誌輸出。主要風險在於 slotRangeArrayNormalizeAndValidate 會修改輸入陣列，可能導致呼叫端持有未合併的資料；asmCreateImportTask 的記憶體所有權轉移容易造成 double-free 或 use-after-free；parseSlotRangesOrReply 的錯誤處理可能洩漏 err 或未回覆錯誤。建議先修正記憶體管理與錯誤處理，再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster_asm.c:830` | asmCreateImportTask 直接接管 slots 所有權，但錯誤路徑可能造成 double-free 或 use-after-free | 0.95 |
| ⚠️ | Major | `src/cluster.c:1744` | slotRangeArrayNormalizeAndValidate 會修改輸入陣列，呼叫端可能持有未合併的資料 | 0.90 |
| ⚠️ | Major | `src/cluster.c:2015` | parseSlotRangesOrReply 錯誤處理可能洩漏 err 或未回覆錯誤 | 0.85 |
| 🔸 | Minor | `src/cluster_asm.c:1040` | asmCountKeysInSlots 在每次日誌事件時重新計算鍵數，可能造成效能負擔 | 0.70 |
| 🔸 | Minor | `src/cluster.c:1796` | slotRangeArrayToString 新增 NULL 檢查，但可能掩蓋呼叫端的邏輯錯誤 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster_asm.c:830</code> asmCreateImportTask 直接接管 slots 所有權，但錯誤路徑可能造成 double-free 或 use-after-free</summary>

原本 asmCreateImportTask 會複製 slots（slotRangeArrayDup），現在改為直接指派 task->slots = slots，並在錯誤路徑中 slotRangeArrayFree(slots)。這表示呼叫端（clusterMigrationCommandImport）不再需要釋放 slots，但若呼叫端仍持有指標並在之後使用或釋放，將導致 double-free 或 use-after-free。

檢查目前呼叫端：
- clusterMigrationCommandImport：已移除 slotRangeArrayFree(slots)，看似正確。
- clusterAsmProcess 的 ASM_EVENT_IMPORT_START：先複製 arg 到 slots，驗證後傳給 asmCreateImportTask，若 asmCreateImportTask 失敗會釋放 slots，但 clusterAsmProcess 沒有再釋放，可能造成記憶體洩漏（若 asmCreateImportTask 未釋放）或 double-free（若已釋放）。

建議：
- 明確所有權規則：asmCreateImportTask 應一律接管 slots（成功或失敗都負責釋放），或一律不接管（由呼叫端釋放）。
- 修正 clusterAsmProcess 中的錯誤處理，確保 slots 在所有路徑都被正確釋放。

**判斷依據**：diff 中 task->slots = slotRangeArrayDup(slots) 改為 task->slots = slots，且錯誤路徑新增 slotRangeArrayFree(slots)。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1744</code> slotRangeArrayNormalizeAndValidate 會修改輸入陣列，呼叫端可能持有未合併的資料</summary>

此函式現在會呼叫 slotRangeArraySortAndMerge，直接修改傳入的 slotRangeArray。若呼叫端在呼叫後仍使用原始陣列（例如 slotRangeArrayFromString 在驗證後回傳給使用者），則使用者拿到的將是合併後的陣列，可能與預期不符。此外，若驗證失敗，陣列已被修改，呼叫端難以復原。

建議：
1. 在函式內複製一份陣列進行排序合併，驗證通過後再將結果寫回原陣列（或回傳新陣列）。
2. 或明確在文件與函式名稱中標示此函式會修改輸入，並確保所有呼叫端都預期此行為。

**判斷依據**：diff 中新增的 slotRangeArraySortAndMerge(slots) 呼叫，以及函式名稱從 validateSlotRanges 改為 slotRangeArrayNormalizeAndValidate，暗示會修改輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2015</code> parseSlotRangesOrReply 錯誤處理可能洩漏 err 或未回覆錯誤</summary>

在 slotRangeArrayNormalizeAndValidate 失敗時，程式碼執行 sdsfree(err) 後直接回傳 NULL，但沒有呼叫 addReplyErrorSds 或 addReplyError 來回覆客戶端。這會導致客戶端等待回應直到逾時。

此外，若 slotRangeArrayNormalizeAndValidate 在設定 err 之前就失敗（例如 slots->num_ranges 檢查），err 可能為 NULL，sdsfree(NULL) 是安全的，但之後沒有回覆錯誤。

建議：
- 在釋放 err 之前，先呼叫 addReplyErrorSds(c, err) 或 addReplyError(c, err)，然後再釋放。
- 或確保 slotRangeArrayNormalizeAndValidate 總是在失敗時設定 err，並在此處直接使用 addReplyErrorSds(c, err)（該函式會接管 err 的記憶體）。

**判斷依據**：diff 中原本的 addReplyErrorSds(c, err) 被移除，改為 sdsfree(err)，但沒有回覆錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster_asm.c:1040</code> asmCountKeysInSlots 在每次日誌事件時重新計算鍵數，可能造成效能負擔</summary>

asmCountKeysInSlots 會走訪所有 slot 並呼叫 kvstoreDictSize，這在大型資料集上可能很耗時。此函式在 ASM_EVENT_IMPORT_COMPLETED、ASM_EVENT_MIGRATE_STARTED、ASM_EVENT_MIGRATE_COMPLETED 等事件中被呼叫，若這些事件頻繁發生，可能影響效能。

建議：
- 考慮在任務建立時計算一次鍵數並儲存在 asmTask 中，日誌時直接使用。
- 或僅在需要時（如 completed 事件）才計算。

**判斷依據**：diff 中新增的 asmCountKeysInSlots 呼叫，且函式內有雙重迴圈走訪所有 slot。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1796</code> slotRangeArrayToString 新增 NULL 檢查，但可能掩蓋呼叫端的邏輯錯誤</summary>

新增的 if (slots == NULL || slots->num_ranges == 0) return s; 可以避免 NULL 指標崩潰，但也可能讓呼叫端在傳入 NULL 時繼續執行，導致後續邏輯錯誤。建議在呼叫端確保 slots 不為 NULL，或在此處記錄警告。

**判斷依據**：diff 中新增的 NULL 檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6685 (cache hit 6656) ｜ completion tokens 1756 ｜ PR #2</sub>