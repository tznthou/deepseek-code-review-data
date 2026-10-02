<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 slot range 的驗證流程改為先正規化（排序並合併相鄰範圍）再驗證，並調整了 ASM 任務建立時的記憶體管理與錯誤處理。主要風險在於 `asmCreateImportTask` 的記憶體所有權轉移、`slotRangeArraySortAndMerge` 的合併邏輯可能未涵蓋重疊範圍，以及 `parseSlotRangesOrReply` 的錯誤回覆方式變更可能影響用戶端。建議優先確認記憶體管理與合併邏輯的正確性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/cluster_asm.c:830` | 記憶體所有權轉移可能導致 double-free 或 memory leak | 0.80 |
| ⚠️ | Major | `src/cluster.c:1867` | 合併邏輯未處理重疊範圍，可能導致驗證失敗或資料錯誤 | 0.70 |
| 🔸 | Minor | `src/cluster.c:2015` | 錯誤回覆方式變更可能影響用戶端相容性 | 0.60 |
| 🔸 | Minor | `src/cluster_asm.c:2871` | 重複驗證 slot ranges 可能造成效能浪費 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/cluster_asm.c:830</code> 記憶體所有權轉移可能導致 double-free 或 memory leak</summary>

在 `asmCreateImportTask` 中，原本使用 `slotRangeArrayDup(slots)` 複製一份 slot ranges，現在改為直接指派 `task->slots = slots`，將傳入的 `slots` 指標所有權轉移給 task。然而，呼叫端 `clusterMigrationCommandImport` 已移除 `slotRangeArrayFree(slots)`，但其他呼叫路徑（如 `clusterAsmProcess` 中的 `ASM_EVENT_IMPORT_START`）仍可能預期函式會複製資料，導致後續釋放時發生 double-free 或 memory leak。

建議明確所有權規則：若函式取得所有權，應在文件註解中說明，並確保所有呼叫端不再釋放該指標；或者保留複製行為，避免所有權轉移。

**判斷依據**：diff 中 `task->slots = slotRangeArrayDup(slots);` 改為 `task->slots = slots;`，且 `clusterMigrationCommandImport` 移除了 `slotRangeArrayFree(slots)`，但 `clusterAsmProcess` 中仍可能傳入需要釋放的 slots。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1867</code> 合併邏輯未處理重疊範圍，可能導致驗證失敗或資料錯誤</summary>

`slotRangeArraySortAndMerge` 僅合併相鄰範圍（`prev.end + 1 == next.start`），但未處理重疊範圍（例如 `0-100` 和 `50-150`）。若輸入包含重疊範圍，合併後仍會保留重疊，後續 `slotRangeArrayNormalizeAndValidate` 會偵測到重疊並回傳錯誤，但錯誤訊息可能不夠明確。此外，若重疊範圍未合併，可能影響後續使用 slot ranges 的邏輯（如 key 計數）。

建議在合併時一併處理重疊範圍，或至少在驗證階段提供更明確的錯誤訊息。

**判斷依據**：diff 中新增的 `slotRangeArraySortAndMerge` 函式僅檢查 `end + 1 == start`，未處理重疊。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2015</code> 錯誤回覆方式變更可能影響用戶端相容性</summary>

在 `parseSlotRangesOrReply` 中，原本使用 `addReplyErrorSds(c, err)` 回傳錯誤訊息，現在改為 `sdsfree(err)` 後直接回傳 NULL，由呼叫端處理錯誤回覆。這可能導致錯誤訊息遺失或格式不一致，影響用戶端對錯誤的解析。

建議確認所有呼叫端都能正確處理 NULL 回傳並提供適當的錯誤回覆，或保留原本的錯誤回覆方式。

**判斷依據**：diff 中 `addReplyErrorSds(c, err);` 被移除，改為 `sdsfree(err);`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster_asm.c:2871</code> 重複驗證 slot ranges 可能造成效能浪費</summary>

在 `clusterAsmProcess` 的 `ASM_EVENT_IMPORT_START` 分支中，先呼叫 `slotRangeArrayNormalizeAndValidate` 驗證並正規化 slots，然後再傳給 `asmCreateImportTask`，而 `asmCreateImportTask` 內部又會呼叫 `validateImportSlotRanges` 進行驗證。這導致重複驗證，可能影響效能。

建議考慮將驗證邏輯整合，避免重複工作。

**判斷依據**：diff 中新增了驗證步驟，但 `asmCreateImportTask` 內部仍會呼叫 `validateImportSlotRanges`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7193 (cache hit 6144) ｜ completion tokens 1392 ｜ PR #2</sub>