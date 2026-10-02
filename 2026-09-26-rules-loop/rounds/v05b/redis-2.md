<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 slot range 的驗證流程改為先正規化（排序與合併相鄰範圍）再驗證，並調整了 ASM 任務建立流程的記憶體管理與錯誤處理。主要風險在於 asmCreateImportTask 的所有權轉移可能導致 double-free 或 use-after-free，以及 slotRangeArrayNormalizeAndValidate 在錯誤時未釋放 err 字串。此外，新增的 asmCountKeysInSlots 在大型 slot 範圍下可能有效能問題。建議優先修正記憶體管理問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster_asm.c:830` | asmCreateImportTask 中 slots 所有權轉移導致 double-free 或 use-after-free | 0.90 |
| ⚠️ | Major | `src/cluster.c:2015` | slotRangeArrayNormalizeAndValidate 錯誤時未釋放 err 字串 | 0.80 |
| ⚠️ | Major | `src/cluster_asm.c:1012` | asmCountKeysInSlots 可能導致效能問題 | 0.70 |
| ⚠️ | Major | `src/cluster_asm.c:2871` | clusterAsmProcess 中 slotRangeArrayDup 後未在錯誤路徑釋放 | 0.70 |
| 🔸 | Minor | `src/cluster.c:1744` | slotRangeArrayNormalizeAndValidate 中排序與合併可能改變原始陣列 | 0.60 |
| 🔸 | Minor | `src/cluster.c:1855` | slotRangeArraySortAndMerge 未處理重疊範圍 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster_asm.c:830</code> asmCreateImportTask 中 slots 所有權轉移導致 double-free 或 use-after-free</summary>

在 asmCreateImportTask 中，原本使用 slotRangeArrayDup(slots) 複製一份，現在改為直接指派 task->slots = slots，將傳入的 slots 所有權轉移給 task。然而，呼叫端 clusterMigrationCommandImport 在呼叫後不再釋放 slots（已移除 slotRangeArrayFree(slots)），但其他呼叫端（如 clusterAsmProcess）仍可能預期函式不會取得所有權，導致後續釋放時發生 double-free 或 use-after-free。

具體失敗情境：
1. clusterAsmProcess 在 ASM_EVENT_IMPORT_START 分支中，先 slotRangeArrayDup(arg) 複製一份，再呼叫 asmCreateImportTask(task_id, slots, &errsds)。若 asmCreateImportTask 成功，slots 所有權轉移給 task，但 clusterAsmProcess 之後沒有釋放 slots（原本就沒有），所以不會 double-free。但若 asmCreateImportTask 失敗，它會釋放 slots（goto err），而 clusterAsmProcess 在失敗後也沒有釋放 slots，所以不會 double-free。然而，若未來有其他呼叫端在呼叫後仍釋放 slots，就會 double-free。
2. 更嚴重的問題是：在 asmCreateImportTask 中，若 task 建立後但在回傳前發生錯誤（例如 sdsnew 失敗），會 goto err 並釋放 slots，但此時 task 已持有 slots 指標，之後 task 若被釋放，會再次釋放 slots，造成 double-free。

建議：明確所有權轉移的契約，並在所有呼叫端一致遵守。或者，保留 slotRangeArrayDup 複製，避免所有權轉移。

**判斷依據**：diff 中將原本的 task->slots = slotRangeArrayDup(slots); 改為 task->slots = slots;，且移除了 clusterMigrationCommandImport 中的 slotRangeArrayFree(slots);。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2015</code> slotRangeArrayNormalizeAndValidate 錯誤時未釋放 err 字串</summary>

在 parseSlotRangesOrReply 中，原本呼叫 validateSlotRanges 失敗時會 addReplyErrorSds(c, err) 將 err 傳給客戶端並由 addReplyErrorSds 負責釋放。現在改為 slotRangeArrayNormalizeAndValidate，失敗時直接 sdsfree(err) 後 slotRangeArrayFree(slots) 並回傳 NULL，但沒有將錯誤訊息回覆給客戶端。這會導致客戶端收到空回覆或不明錯誤，且 err 字串被釋放後無法使用。

具體失敗情境：當使用者輸入無效的 slot range（例如重疊或超出範圍）時，parseSlotRangesOrReply 會回傳 NULL，但呼叫端可能沒有處理錯誤回覆，導致客戶端收到空回覆或連線中斷。

建議：在釋放 err 之前，先呼叫 addReplyErrorSds(c, err) 將錯誤訊息傳給客戶端，或修改函式介面以傳回錯誤訊息。

**判斷依據**：diff 中將原本的 addReplyErrorSds(c, err); 改為 sdsfree(err);，且沒有其他錯誤回覆。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster_asm.c:1012</code> asmCountKeysInSlots 可能導致效能問題</summary>

新增的 asmCountKeysInSlots 函式會對每個 slot 呼叫 kvstoreDictSize，若 slot 範圍很大（例如整個 16384 個 slot），會執行大量函式呼叫，可能造成效能瓶頸。此外，此函式在 asmLogTaskEvent 中被呼叫，而 asmLogTaskEvent 可能在任務生命週期的多個事件中被呼叫，進一步放大效能影響。

具體失敗情境：當 slot 範圍涵蓋大量 slot 時，每次記錄事件都會遍歷所有 slot 並呼叫 kvstoreDictSize，可能導致明顯延遲。

建議：考慮使用更有效率的方式計算 key 數量，例如直接從資料庫統計資訊取得，或快取結果。

**判斷依據**：diff 中新增的函式，在迴圈中呼叫 kvstoreDictSize。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster_asm.c:2871</code> clusterAsmProcess 中 slotRangeArrayDup 後未在錯誤路徑釋放</summary>

在 clusterAsmProcess 的 ASM_EVENT_IMPORT_START 分支中，先 slotRangeArrayDup(arg) 複製一份 slots，然後呼叫 slotRangeArrayNormalizeAndValidate。若驗證失敗，會 slotRangeArrayFree(slots) 並 break，但此時 ret 設為 C_ERR，errsds 可能已設定。然而，若驗證成功但 asmCreateImportTask 失敗，asmCreateImportTask 會釋放 slots（因為所有權轉移），但 clusterAsmProcess 沒有再釋放 slots，所以不會 double-free。但若 asmCreateImportTask 成功，slots 所有權轉移給 task，clusterAsmProcess 也沒有釋放 slots，所以不會 double-free。然而，若未來 asmCreateImportTask 的實作變更，可能導致 double-free。

具體失敗情境：若 asmCreateImportTask 在成功建立 task 後但在回傳前發生錯誤，會釋放 slots，而 clusterAsmProcess 之後可能仍持有 slots 指標並嘗試釋放，造成 double-free。

建議：明確所有權轉移的契約，並在所有呼叫端一致遵守。

**判斷依據**：diff 中新增的程式碼，slotRangeArrayDup 後在驗證失敗時釋放，但成功後所有權轉移給 asmCreateImportTask，若 asmCreateImportTask 失敗會釋放 slots，但 clusterAsmProcess 沒有處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1744</code> slotRangeArrayNormalizeAndValidate 中排序與合併可能改變原始陣列</summary>

slotRangeArrayNormalizeAndValidate 現在會呼叫 slotRangeArraySortAndMerge 來排序與合併相鄰範圍，這會修改傳入的 slotRangeArray 結構。若呼叫端預期驗證不會修改資料，可能會導致非預期的行為。

具體失敗情境：若某個呼叫端在驗證後仍使用原始的 slotRangeArray，且依賴其原始順序或範圍，則會得到錯誤的結果。

建議：在文件或函式名稱中明確指出此函式會修改輸入，或提供一個不會修改的驗證版本。

**判斷依據**：diff 中新增的呼叫，會修改 slots 的內容。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1855</code> slotRangeArraySortAndMerge 未處理重疊範圍</summary>

slotRangeArraySortAndMerge 只合併相鄰範圍（prev.end + 1 == next.start），但未處理重疊範圍。若輸入包含重疊範圍（例如 1000-2000 和 1500-2500），合併後仍會保留重疊，後續驗證會失敗。這可能不是問題，但函式名稱和註解可能讓人誤以為會處理重疊。

具體失敗情境：若使用者輸入重疊範圍，驗證會失敗，但錯誤訊息可能不明確。

建議：在註解中明確說明重疊範圍不會被合併，或考慮在合併時處理重疊。

**判斷依據**：diff 中新增的註解，但未處理重疊。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7169 (cache hit 7168) ｜ completion tokens 2534 ｜ PR #2</sub>