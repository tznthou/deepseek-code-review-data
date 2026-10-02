<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 cluster 初始化與 slot 統計相關程式碼重構，將部分邏輯從 cluster_legacy.c 移至 cluster.c，並調整 asmCron/asmBeforeSleep 的呼叫位置。主要風險在於 clusterCommonInit 使用 malloc 而非 zmalloc（違反 R02），且 clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 的拆分可能改變原有行為：原本在 verifyClusterConfigWithData 中，若 slot 有 key 且無主，會先嘗試 claim，否則刪除；現在 claim 與 delete 分開，且 delete 在 claim 之前執行，可能導致原本可被 claim 的 slot 被刪除 key。此外，clusterCommonInit 的呼叫時機與原本初始化順序不同，需確認不會造成未初始化指標的使用。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:2138` | [R02] 使用 malloc 而非 zmalloc 分配記憶體 | 0.95 |
| ⚠️ | Major | `src/cluster.c:2210` | clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 的順序可能導致資料遺失 | 0.85 |
| ⚠️ | Major | `src/cluster.c:2153` | clusterDeleteKeysInUnownedSlots 未處理 importing 狀態的 slot | 0.80 |
| ⚠️ | Major | `src/cluster.c:2138` | clusterCommonInit 呼叫時機可能導致未初始化指標使用 | 0.75 |
| 🔸 | Minor | `src/cluster.c:2147` | clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 重複檢查 slave 狀態 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:2138</code> [R02] 使用 malloc 而非 zmalloc 分配記憶體</summary>

在 clusterCommonInit 中使用 `malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat))` 分配記憶體，違反專案規範 R02（必須使用 zmalloc 系列函式）。這會導致記憶體使用量無法被 Redis 的記憶體追蹤機制記錄，可能造成記憶體統計不準確或洩漏。請改用 `zmalloc`。

**判斷依據**：diff 中新增的 `clusterCommonInit` 函式內使用 `malloc`，而原本在 server.c 中使用 `zmalloc`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2210</code> clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 的順序可能導致資料遺失</summary>

原本的 verifyClusterConfigWithData 在發現 slot 有 key 且無主時，會先執行 clusterAddSlot 將 slot 指派給自己（claim），否則才刪除 key。現在拆分後，verifyClusterConfigWithData 先呼叫 clusterDeleteKeysInUnownedSlots（刪除不屬於自己的 slot 的 key），再呼叫 clusterClaimUnassignedSlots（claim 無主 slot）。這會導致原本無主但可被 claim 的 slot 中的 key 被刪除，造成資料遺失。建議調整順序：先 claim 無主 slot，再刪除仍不屬於自己的 slot 的 key。

**判斷依據**：diff 中 verifyClusterConfigWithData 的實作先呼叫 clusterDeleteKeysInUnownedSlots，再呼叫 clusterClaimUnassignedSlots。而 clusterDeleteKeysInUnownedSlots 會刪除所有不屬於自己的 slot 的 key，包括那些無主的 slot。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2153</code> clusterDeleteKeysInUnownedSlots 未處理 importing 狀態的 slot</summary>

clusterDeleteKeysInUnownedSlots 在判斷是否刪除 key 時，只檢查了 `clusterIsMySlot(i)` 和 `getImportingSlotSource(i)`，但未檢查 `server.cluster->importing_slots_from[i]`（即本節點是否正在從其他節點匯入該 slot）。若本節點正在匯入某 slot，且該 slot 尚未指派給自己，則此函式會刪除該 slot 的 key，可能導致匯入過程中的資料遺失。建議加入對 `server.cluster->importing_slots_from[i]` 的檢查。

**判斷依據**：diff 中 clusterDeleteKeysInUnownedSlots 的條件判斷缺少對 `server.cluster->importing_slots_from[i]` 的檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2138</code> clusterCommonInit 呼叫時機可能導致未初始化指標使用</summary>

clusterCommonInit 在 server.c 的 main 函式中被呼叫，取代原本的 `server.cluster_slot_stats = zmalloc(...)`。但原本的初始化是在 `clusterInit()` 之前，而 `clusterInit()` 中會呼叫 `resetClusterStats()` 和 `asmInit()`。現在 `clusterCommonInit()` 內部呼叫了 `resetClusterStats()` 和 `asmInit()`，但 `clusterInit()` 中仍保留了 `resetClusterStats()` 和 `asmInit()` 的呼叫（從 diff 中可見 cluster_legacy.c 的 clusterInit 移除了這兩個呼叫，但 cluster.c 的 clusterCommonInit 又呼叫了它們）。這可能導致重複初始化或初始化順序問題。需確認 `clusterCommonInit` 是否應完全取代原本的初始化，並移除 clusterInit 中的重複呼叫。

**判斷依據**：diff 中 clusterCommonInit 呼叫 resetClusterStats 和 asmInit，而 cluster_legacy.c 的 clusterInit 中移除了這兩個呼叫，但 cluster.c 的 clusterCommonInit 又呼叫了它們。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2147</code> clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 重複檢查 slave 狀態</summary>

clusterDeleteKeysInUnownedSlots 和 clusterClaimUnassignedSlots 都各自檢查了 `clusterNodeIsSlave(getMyClusterNode())` 或 `nodeIsSlave(myself)`，而呼叫它們的 verifyClusterConfigWithData 也已經檢查過 slave 狀態。這造成重複檢查，雖然不影響正確性，但可考慮移除內部檢查以簡化程式碼。

**判斷依據**：diff 中 clusterDeleteKeysInUnownedSlots 和 clusterClaimUnassignedSlots 都有 slave 檢查，而 verifyClusterConfigWithData 也有。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6230 (cache hit 6144) ｜ completion tokens 1651 ｜ PR #4</sub>