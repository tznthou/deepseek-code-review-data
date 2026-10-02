<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將部分 cluster 初始化與 slot 統計相關程式碼從 cluster_legacy.c 移至 cluster.c，並調整 asmCron/asmBeforeSleep 的呼叫位置。主要風險在於 clusterCommonInit 使用 malloc 而非 zmalloc（違反 R02），且 clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 的邏輯拆分可能改變行為：原本在 verifyClusterConfigWithData 中若發現 slot 有 key 且未指派給任何人時會直接接管，現在則先刪除未擁有 slot 的 key，再接管未指派 slot，可能導致資料遺失。此外，clusterCommonInit 的呼叫時機與原本的初始化順序不同，需確認是否會影響後續 clusterInit 的執行。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:2138` | [R02] 使用 malloc 而非 zmalloc 分配 cluster_slot_stats | 0.95 |
| ⚠️ | Major | `src/cluster.c:2210` | clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 的順序可能導致資料遺失 | 0.80 |
| ⚠️ | Major | `src/server.c:7740` | clusterCommonInit 呼叫時機可能影響後續初始化 | 0.70 |
| 🔸 | Minor | `src/cluster.c:2138` | clusterCommonInit 中未檢查 malloc 回傳值 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:2138</code> [R02] 使用 malloc 而非 zmalloc 分配 cluster_slot_stats</summary>

在 clusterCommonInit 中使用 `malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat))` 分配記憶體，違反專案規範 R02（必須使用 zmalloc 系列函數）。這會導致記憶體使用量無法被 Redis 的記憶體追蹤機制記錄，且可能造成記憶體洩漏。

建議改為 `zmalloc(CLUSTER_SLOTS*sizeof(clusterSlotStat))`。

**判斷依據**：diff 中新增的 clusterCommonInit 函式內使用 malloc，而原本在 server.c 中使用 zmalloc。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2210</code> clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 的順序可能導致資料遺失</summary>

原本 verifyClusterConfigWithData 的邏輯是：若 slot 有 key 且未指派給任何人，則直接接管該 slot（clusterAddSlot）；若已指派給其他節點，則刪除該 slot 的 key。現在拆分為兩個函式，且先呼叫 clusterDeleteKeysInUnownedSlots（刪除所有未擁有 slot 的 key），再呼叫 clusterClaimUnassignedSlots（接管未指派 slot）。這會導致原本應被接管的 slot（未指派但我們有 key）在接管前就被刪除 key，造成資料遺失。

建議調整順序：先接管未指派 slot，再刪除仍不屬於我們的 slot 的 key，或合併成單一函式以保留原始邏輯。

**判斷依據**：diff 中 verifyClusterConfigWithData 的實作改為先呼叫 clusterDeleteKeysInUnownedSlots 再呼叫 clusterClaimUnassignedSlots，而原本的邏輯是在同一個迴圈中先判斷 slot 是否未指派，若是則接管，否則刪除。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:7740</code> clusterCommonInit 呼叫時機可能影響後續初始化</summary>

原本在 server.c 中，cluster_slot_stats 的分配是在 clusterInit 之前，且使用 zmalloc。現在改為在 clusterInit 之前呼叫 clusterCommonInit，其中包含 resetClusterStats 和 asmInit。但 clusterInit 中原本也有 resetClusterStats 和 asmInit 的呼叫，現在被移除了。需確認 clusterCommonInit 是否在所有需要這些初始化的路徑上都被呼叫，且不會造成重複初始化或遺漏。

建議檢查所有 cluster 初始化路徑，確保 clusterCommonInit 被正確呼叫，且不會與其他初始化步驟衝突。

**判斷依據**：diff 中 server.c 的 main 函式改為呼叫 clusterCommonInit 再呼叫 clusterInit，而 clusterInit 中移除了 resetClusterStats 和 asmInit。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2138</code> clusterCommonInit 中未檢查 malloc 回傳值</summary>

使用 malloc 分配記憶體後未檢查回傳值是否為 NULL，若記憶體不足可能導致後續 dereference NULL 指標。雖然 zmalloc 在 OOM 時會 abort，但若改用 zmalloc 則無此問題。

建議改用 zmalloc 並依賴其 OOM 處理，或在使用 malloc 時檢查回傳值。

**判斷依據**：diff 中新增的 clusterCommonInit 函式內使用 malloc 且未檢查回傳值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5722 (cache hit 5632) ｜ completion tokens 1262 ｜ PR #4</sub>