<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 cluster 初始化與 slot 統計相關程式碼從 cluster_legacy.c 重構至 cluster.c，並將 asmCron/asmBeforeSleep 呼叫移至 server.c。主要風險在於 clusterCommonInit 使用 malloc 而非 zmalloc（違反 R02），且 clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 的拆分可能改變既有行為（例如不再處理 importing 狀態下的 slot）。此外，cluster.c 中新增的 migration/syncslots 命令處理可能與 cluster_legacy.c 中的既有處理重複，需確認是否會造成雙重回應。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:2138` | [R02] 使用 malloc 而非 zmalloc | 0.95 |
| ⚠️ | Major | `src/cluster.c:2153` | clusterDeleteKeysInUnownedSlots 可能誤刪 importing 狀態的 slot | 0.80 |
| ⚠️ | Major | `src/cluster.c:2153` | clusterClaimUnassignedSlots 可能重複處理 importing 狀態 | 0.75 |
| ⚠️ | Major | `src/cluster.c:1092` | cluster.c 中新增的 migration/syncslots 命令處理可能與 cluster_legacy.c 重複 | 0.70 |
| 🔸 | Minor | `src/server.c:1657` | asmCron 呼叫順序可能影響 clusterCron 行為 | 0.60 |
| 🔸 | Minor | `src/server.c:1841` | asmBeforeSleep 呼叫順序可能影響 clusterBeforeSleep 行為 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:2138</code> [R02] 使用 malloc 而非 zmalloc</summary>

clusterCommonInit 中使用 `malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat))` 分配記憶體，違反專案規範 R02（必須使用 zmalloc 系列）。這會導致記憶體使用量無法被 Redis 的記憶體追蹤機制記錄，可能造成記憶體洩漏或統計錯誤。

建議改為 `zmalloc(CLUSTER_SLOTS*sizeof(clusterSlotStat))`。

**判斷依據**：diff 中新增的 clusterCommonInit 函式內使用 malloc，而原本在 server.c 的初始化使用 zmalloc（見 diff 中被移除的 `server.cluster_slot_stats = zmalloc(...)`）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2153</code> clusterDeleteKeysInUnownedSlots 可能誤刪 importing 狀態的 slot</summary>

在 clusterDeleteKeysInUnownedSlots 中，條件 `!getImportingSlotSource(i)` 會跳過正在 importing 的 slot，但原本的 verifyClusterConfigWithData 邏輯中，若 slot 有 keys 且非 importing 且非 assigned，會刪除 keys；若 slot 有 keys 且非 importing 且 assigned 給其他節點，也會刪除 keys。新的拆分將「刪除 unowned slots 的 keys」與「claim unassigned slots」分開，但 clusterDeleteKeysInUnownedSlots 只處理「assigned to another node」的情況，而 clusterClaimUnassignedSlots 只處理「unassigned」的情況。然而，原本的邏輯在遇到「assigned to another node」時會直接刪除 keys，但新的 clusterDeleteKeysInUnownedSlots 在遇到「assigned to another node」時也會刪除 keys，這部分行為一致。但需注意：原本的邏輯在刪除 keys 後會呼叫 clusterSaveConfigOrDie(1) 來保存配置，而新的 clusterDeleteKeysInUnownedSlots 沒有保存配置，這可能導致配置不一致。

建議確認是否需要在刪除 keys 後保存配置，或將保存配置的邏輯移至呼叫端。

**判斷依據**：diff 中新增的 clusterDeleteKeysInUnownedSlots 函式，與被移除的 verifyClusterConfigWithData 中的對應邏輯比較，缺少 clusterSaveConfigOrDie 呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2153</code> clusterClaimUnassignedSlots 可能重複處理 importing 狀態</summary>

clusterClaimUnassignedSlots 中，條件 `server.cluster->importing_slots_from[i] != NULL` 會跳過 importing 的 slot，但原本的 verifyClusterConfigWithData 在處理 unassigned slot 時，若該 slot 有 keys 且非 importing，則會 claim。新的邏輯一致。但需注意：原本的邏輯在 claim 後會呼叫 clusterSaveConfigOrDie(1)，而新的 clusterClaimUnassignedSlots 有呼叫 clusterSaveConfigOrDie(1)，這部分一致。

然而，原本的 verifyClusterConfigWithData 在處理完所有 slot 後才呼叫一次 clusterSaveConfigOrDie，而新的 clusterClaimUnassignedSlots 在每次 claim 後都會呼叫 clusterSaveConfigOrDie，這可能導致多次寫入配置檔，影響效能。

建議考慮將 clusterSaveConfigOrDie 移到 clusterClaimUnassignedSlots 的呼叫端，或累積變更後一次保存。

**判斷依據**：diff 中新增的 clusterClaimUnassignedSlots 函式，與被移除的 verifyClusterConfigWithData 中的對應邏輯比較，clusterSaveConfigOrDie 的呼叫時機不同。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1092</code> cluster.c 中新增的 migration/syncslots 命令處理可能與 cluster_legacy.c 重複</summary>

在 clusterCommand 中新增了對 "migration" 和 "syncslots" 的處理，但原本這些處理位於 cluster_legacy.c 的 clusterCommandSpecial 中。現在 cluster_legacy.c 中已移除這些處理，但需確認 cluster.c 中的 clusterCommand 是否會被 cluster_legacy.c 的 clusterCommandSpecial 呼叫，或者兩者是否會同時執行。如果 clusterCommand 在 cluster_legacy.c 中也有定義，可能會造成重複處理或錯誤。

建議確認 clusterCommand 的呼叫鏈，確保不會重複處理。

**判斷依據**：diff 中 cluster.c 新增的程式碼，與 cluster_legacy.c 中被移除的程式碼對應。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:1657</code> asmCron 呼叫順序可能影響 clusterCron 行為</summary>

在 serverCron 中，原本只有 clusterCron 被呼叫，現在改為先呼叫 asmCron 再呼叫 clusterCron。如果 asmCron 會修改 cluster 狀態，可能會影響 clusterCron 的執行結果。需確認 asmCron 與 clusterCron 的相依性。

**判斷依據**：diff 中 server.c 的修改。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:1841</code> asmBeforeSleep 呼叫順序可能影響 clusterBeforeSleep 行為</summary>

在 beforeSleep 中，原本只有 clusterBeforeSleep 被呼叫，現在改為先呼叫 clusterBeforeSleep 再呼叫 asmBeforeSleep。如果 asmBeforeSleep 依賴 clusterBeforeSleep 的結果，或反之，可能會造成問題。需確認兩者的相依性。

**判斷依據**：diff 中 server.c 的修改。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6230 (cache hit 6144) ｜ completion tokens 1953 ｜ PR #4</sub>