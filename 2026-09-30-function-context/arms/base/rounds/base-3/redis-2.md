<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 slot range 的驗證流程改為先正規化（排序並合併相鄰範圍）再驗證，並調整了 ASM 任務建立時的記憶體管理與錯誤處理。主要風險在於 slotRangeArraySortAndMerge 未處理重疊範圍，可能導致後續驗證漏判；asmCreateImportTask 的所有權轉移容易造成 double-free 或 use-after-free；parseSlotRangesOrReply 的錯誤回覆不一致；以及 asmCountKeysInSlots 的效能與正確性疑慮。建議優先修正記憶體管理與重疊範圍處理。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1867` | slotRangeArraySortAndMerge 未處理重疊範圍，可能導致驗證失效 | 0.90 |
| 🛑 | Blocker | `src/cluster_asm.c:830` | asmCreateImportTask 所有權轉移可能導致 double-free 或 use-after-free | 0.85 |
| ⚠️ | Major | `src/cluster.c:2015` | parseSlotRangesOrReply 錯誤路徑未回覆錯誤訊息 | 0.80 |
| ⚠️ | Major | `src/cluster_asm.c:1018` | asmCountKeysInSlots 可能造成效能問題或非預期行為 | 0.70 |
| ⚠️ | Major | `src/cluster_asm.c:2871` | clusterAsmProcess 中 slotRangeArrayDup 後未檢查 NULL | 0.70 |
| 🔸 | Minor | `src/cluster.c:1796` | slotRangeArrayToString 對 NULL 或空陣列的處理不一致 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1867</code> slotRangeArraySortAndMerge 未處理重疊範圍，可能導致驗證失效</summary>

函式僅合併相鄰範圍（prev.end + 1 == next.start），但未處理重疊範圍（例如 100-200 和 150-250）。若輸入包含重疊範圍，合併後仍保留重疊，後續 validateSlotRanges 會偵測到重疊並回傳錯誤，但若重疊範圍在合併後變成相鄰（例如 100-200 和 201-300 合併為 100-300），則可能掩蓋原始的重疊問題。此外，若重疊範圍未合併，validateSlotRanges 仍會偵測到，但錯誤訊息可能不如預期。建議在合併前先檢查重疊，或明確規定重疊範圍為非法輸入。

**判斷依據**：diff 中新增的 slotRangeArraySortAndMerge 函式，僅處理相鄰合併，未處理重疊。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster_asm.c:830</code> asmCreateImportTask 所有權轉移可能導致 double-free 或 use-after-free</summary>

原本 asmCreateImportTask 會複製 slots（slotRangeArrayDup），現在改為直接指派 task->slots = slots，並在錯誤路徑釋放 slots。這表示呼叫端（clusterMigrationCommandImport 和 clusterAsmProcess）不再擁有 slots 的所有權，但 clusterMigrationCommandImport 已移除 slotRangeArrayFree(slots)，而 clusterAsmProcess 在呼叫前會先複製一份再傳入，因此不會 double-free。然而，若未來有其他呼叫端未遵循此所有權轉移，可能導致 double-free 或 use-after-free。建議明確文件化所有權轉移，或改為在成功時轉移、失敗時由呼叫端釋放。

**判斷依據**：diff 中將 slotRangeArrayDup(slots) 改為 slots，並在錯誤路徑新增 slotRangeArrayFree(slots)。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2015</code> parseSlotRangesOrReply 錯誤路徑未回覆錯誤訊息</summary>

原本在 validateSlotRanges 失敗時會呼叫 addReplyErrorSds(c, err) 回覆錯誤，現在改為 sdsfree(err) 後直接回傳 NULL，未回覆任何錯誤給客戶端。這可能導致客戶端收到空回覆或連線中斷，而非明確的錯誤訊息。建議保留 addReplyErrorSds 或改為 addReplyError(c, err)。

**判斷依據**：diff 中移除了 addReplyErrorSds(c, err)，改為 sdsfree(err)。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster_asm.c:1018</code> asmCountKeysInSlots 可能造成效能問題或非預期行為</summary>

asmCountKeysInSlots 會對每個 slot 呼叫 kvstoreDictSize，若 slot 範圍很大（例如 0-16383），可能導致大量的函式呼叫，影響效能。此外，此函式在 asmLogTaskEvent 中被呼叫，而 asmLogTaskEvent 可能在任務生命週期的多個事件中被呼叫，若 slot 範圍大且 key 數量多，可能造成明顯延遲。建議考慮快取或使用更有效率的方式計算 key 數量。

**判斷依據**：diff 中新增的 asmCountKeysInSlots 函式，在迴圈中逐一呼叫 kvstoreDictSize。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster_asm.c:2871</code> clusterAsmProcess 中 slotRangeArrayDup 後未檢查 NULL</summary>

clusterAsmProcess 在 ASM_EVENT_IMPORT_START 分支中呼叫 slotRangeArrayDup(arg)，但未檢查回傳值是否為 NULL。若記憶體不足，slotRangeArrayDup 可能回傳 NULL，後續 slotRangeArrayNormalizeAndValidate 會對 NULL 指標進行操作，導致 crash。建議檢查回傳值並處理錯誤。

**判斷依據**：diff 中新增的程式碼，未檢查 slotRangeArrayDup 的回傳值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1796</code> slotRangeArrayToString 對 NULL 或空陣列的處理不一致</summary>

slotRangeArrayToString 新增了對 NULL 或 num_ranges == 0 的檢查，回傳空 sds。但其他函式（如 slotRangeArrayIsEqual）可能未預期 NULL 或空陣列，可能導致不一致行為。建議確認所有呼叫端都能正確處理空字串。

**判斷依據**：diff 中新增的檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6192 (cache hit 6144) ｜ completion tokens 1695 ｜ PR #2</sub>