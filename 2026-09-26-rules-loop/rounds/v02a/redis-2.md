<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將 slot range 的驗證流程改為先正規化（排序與合併相鄰範圍）再驗證，並新增 asmCountKeysInSlots 函式以統計 key 數量，同時調整了錯誤處理與記憶體管理。整體方向合理，但存在幾個需要修正的問題：parseSlotRangesOrReply 在驗證失敗時未回覆錯誤給客戶端，可能導致客戶端收到空回覆；asmCreateImportTask 的記憶體所有權轉移不明確，可能造成 double-free 或 use-after-free；asmCountKeysInSlots 未檢查 slots 指標是否為 NULL，且僅統計 db[0] 的 key 數量，可能與實際情況不符。建議優先修正這些問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/cluster.c:2015` | 驗證失敗時未回覆錯誤給客戶端 | 0.90 |
| ⚠️ | Major | `src/cluster_asm.c:830` | 記憶體所有權轉移不明確，可能導致 double-free 或 use-after-free | 0.85 |
| ⚠️ | Major | `src/cluster_asm.c:1012` | asmCountKeysInSlots 未檢查 slots 指標是否為 NULL | 0.80 |
| 🔸 | Minor | `src/cluster_asm.c:1019` | asmCountKeysInSlots 僅統計 db[0] 的 key 數量 | 0.70 |
| 🔸 | Minor | `src/cluster.c:1994` | 參數驗證條件可能過於嚴格 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2015</code> 驗證失敗時未回覆錯誤給客戶端</summary>

在 `parseSlotRangesOrReply` 中，當 `slotRangeArrayNormalizeAndValidate` 回傳錯誤時，程式碼僅釋放 `err` 和 `slots` 並回傳 `NULL`，但沒有呼叫 `addReplyErrorSds` 或類似函式將錯誤訊息回覆給客戶端。這會導致客戶端在輸入無效的 slot range 時收到空回覆，而不是明確的錯誤訊息。

建議在釋放 `err` 之前，先呼叫 `addReplyErrorSds(c, err)` 將錯誤訊息回覆給客戶端，然後再釋放 `err`。

**判斷依據**：diff 中顯示原本的程式碼是 `addReplyErrorSds(c, err);`，但修改後被移除，僅留下 `sdsfree(err);`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster_asm.c:830</code> 記憶體所有權轉移不明確，可能導致 double-free 或 use-after-free</summary>

在 `asmCreateImportTask` 中，原本使用 `slotRangeArrayDup(slots)` 複製一份 slot range 陣列，但修改後直接將傳入的 `slots` 指標指派給 `task->slots`。這表示呼叫端傳入的 `slots` 記憶體所有權被轉移給 task，但呼叫端可能不知道這件事，導致後續釋放時發生 double-free 或 use-after-free。

例如，在 `clusterMigrationCommandImport` 中，原本在呼叫 `asmCreateImportTask` 後會呼叫 `slotRangeArrayFree(slots)`，但修改後移除了這個呼叫，這表示 `slots` 的所有權已轉移給 task。然而，在 `clusterAsmProcess` 中，傳入的 `arg` 是從外部傳入的指標，若該指標在呼叫後仍被使用，就可能發生問題。

建議明確所有權轉移的規則，並在文件或註解中說明。或者，保留原本的複製行為，避免所有權轉移。

**判斷依據**：diff 中顯示原本是 `task->slots = slotRangeArrayDup(slots);`，修改後改為 `task->slots = slots;`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster_asm.c:1012</code> asmCountKeysInSlots 未檢查 slots 指標是否為 NULL</summary>

`asmCountKeysInSlots` 函式在開頭檢查 `if (!slots) return 0;`，但後續的迴圈中直接使用 `slots->num_ranges` 和 `slots->ranges`，若 `slots` 為 NULL，則會導致 segmentation fault。雖然函式開頭有檢查，但若呼叫端傳入 NULL，仍會進入函式並在迴圈中崩潰。

建議在函式開頭明確檢查 `slots` 是否為 NULL，並回傳 0。

**判斷依據**：函式開頭有 `if (!slots) return 0;`，但後續仍直接使用 `slots->num_ranges` 和 `slots->ranges`，若 `slots` 為 NULL，則會崩潰。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster_asm.c:1019</code> asmCountKeysInSlots 僅統計 db[0] 的 key 數量</summary>

`asmCountKeysInSlots` 函式僅統計 `server.db[0]` 的 key 數量，但 Redis 支援多個資料庫（預設 16 個），且 slot 可能分佈在不同的資料庫中。若 slot 中的 key 存在於其他資料庫，則統計結果會不準確。

建議確認此函式的使用情境，若需要統計所有資料庫的 key 數量，應迭代所有資料庫。

**判斷依據**：程式碼中明確使用 `server.db[0]`，僅統計第一個資料庫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:1994</code> 參數驗證條件可能過於嚴格</summary>

在 `parseSlotRangesOrReply` 中，新增的參數驗證條件為 `if (argc < 0 || pos < 0 || pos >= argc || (argc - pos) < 2 || ((argc - pos) % 2) != 0)`。其中 `argc < 0` 和 `pos < 0` 的檢查可能永遠不會成立，因為 `argc` 和 `pos` 通常是從命令解析而來，不會是負數。但這不會造成問題，只是多餘的檢查。

建議確認這些檢查是否必要，若無必要可移除。

**判斷依據**：diff 中新增的條件包含 `argc < 0` 和 `pos < 0`，但這兩個變數通常不會是負數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7193 (cache hit 1536) ｜ completion tokens 1796 ｜ PR #2</sub>