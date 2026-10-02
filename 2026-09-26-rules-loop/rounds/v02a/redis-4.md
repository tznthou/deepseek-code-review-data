<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將部分 cluster 初始化與 slot-stats 相關函式從 cluster_legacy.c 移至 cluster.c，並調整呼叫時機。主要風險在於 clusterCommonInit() 使用 malloc 而非 zmalloc（違反 R02），且 asmCron/asmBeforeSleep 的呼叫順序可能影響行為。此外，clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 的拆分可能改變既有邏輯。建議優先修正記憶體配置函式，並確認呼叫順序與測試覆蓋。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:2138` | [R02] 使用 malloc 而非 zmalloc 配置記憶體 | 0.95 |
| ⚠️ | Major | `src/server.c:1658` | asmCron() 呼叫順序可能影響 clusterCron() 行為 | 0.80 |
| ⚠️ | Major | `src/server.c:1842` | asmBeforeSleep() 呼叫順序可能影響 clusterBeforeSleep() 行為 | 0.80 |
| ⚠️ | Major | `src/cluster.c:2210` | clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 拆分可能改變行為 | 0.75 |
| 🔸 | Minor | `src/cluster.c:2146` | clusterDeleteKeysInUnownedSlots 未檢查 cluster_module_flags | 0.60 |
| 🔸 | Minor | `src/cluster.c:2146` | clusterDeleteKeysInUnownedSlots 未檢查 DB 是否為 0 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:2138</code> [R02] 使用 malloc 而非 zmalloc 配置記憶體</summary>

clusterCommonInit() 中使用 `malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat))` 配置記憶體，違反專案規範 R02（必須使用 zmalloc 系列函式）。這會導致記憶體使用量無法被 Redis 的記憶體追蹤機制監控，且可能造成記憶體洩漏。

建議改為 `zmalloc(CLUSTER_SLOTS*sizeof(clusterSlotStat))`。

**判斷依據**：diff 中新增的 clusterCommonInit() 函式內使用 malloc，而原本在 server.c 中對應的配置是使用 zmalloc（見 diff 中刪除的 `server.cluster_slot_stats = zmalloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:1658</code> asmCron() 呼叫順序可能影響 clusterCron() 行為</summary>

在 serverCron() 中，原本 clusterCron() 內部會呼叫 asmCron()（見 cluster_legacy.c 刪除的 `asmCron();`），現在改為在 clusterCron() 之前呼叫 asmCron()。若 asmCron() 會修改 cluster 狀態（例如 slot 遷移狀態），可能導致 clusterCron() 讀取到不同的狀態，進而影響其邏輯。

建議確認 asmCron() 與 clusterCron() 的相依性，必要時調整順序或保留原本的呼叫位置。

**判斷依據**：diff 中 server.c 的 serverCron() 新增 `asmCron();` 並置於 `clusterCron();` 之前，而 cluster_legacy.c 中原本的 `asmCron();` 被移除。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:1842</code> asmBeforeSleep() 呼叫順序可能影響 clusterBeforeSleep() 行為</summary>

在 beforeSleep() 中，原本 clusterBeforeSleep() 內部會呼叫 asmBeforeSleep()（見 cluster_legacy.c 刪除的 `asmBeforeSleep();`），現在改為在 clusterBeforeSleep() 之後呼叫 asmBeforeSleep()。若 asmBeforeSleep() 依賴 clusterBeforeSleep() 設定的狀態，或反之，可能導致非預期行為。

建議確認兩者的相依性，必要時調整順序或保留原本的呼叫位置。

**判斷依據**：diff 中 server.c 的 beforeSleep() 新增 `asmBeforeSleep();` 並置於 `clusterBeforeSleep();` 之後，而 cluster_legacy.c 中原本的 `asmBeforeSleep();` 被移除。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2210</code> clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 拆分可能改變行為</summary>

原本 verifyClusterConfigWithData() 在一個迴圈中同時處理「刪除不屬於自己的 slot 的 keys」與「認領未分配的 slot」。現在拆分為兩個函式，並在 verifyClusterConfigWithData() 中先呼叫 clusterDeleteKeysInUnownedSlots() 再呼叫 clusterClaimUnassignedSlots()。

但原本的邏輯是：若 slot 有 keys 且未分配給任何人，則認領該 slot；若已分配給其他節點，則刪除 keys。拆分後，clusterDeleteKeysInUnownedSlots() 會刪除所有不屬於自己的 slot 的 keys（包括未分配的 slot），然後 clusterClaimUnassignedSlots() 才認領未分配的 slot。這可能導致原本應認領的 slot 的 keys 被刪除。

建議檢查此行為變更是否符合預期，並補充測試。

**判斷依據**：diff 中 verifyClusterConfigWithData() 的實作改為呼叫兩個新函式，而原本的單一迴圈邏輯被移除。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2146</code> clusterDeleteKeysInUnownedSlots 未檢查 cluster_module_flags</summary>

clusterDeleteKeysInUnownedSlots() 中未檢查 `server.cluster_module_flags & CLUSTER_MODULE_FLAG_NO_REDIRECTION`，但原本的 verifyClusterConfigWithData() 會先檢查此旗標並直接返回。若模組停用重導向，此函式仍可能刪除 keys。

建議在 clusterDeleteKeysInUnownedSlots() 開頭加入相同的旗標檢查，或確保呼叫者已處理。

**判斷依據**：diff 中新增的 clusterDeleteKeysInUnownedSlots() 沒有檢查 CLUSTER_MODULE_FLAG_NO_REDIRECTION，而原本的 verifyClusterConfigWithData() 有檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2146</code> clusterDeleteKeysInUnownedSlots 未檢查 DB 是否為 0</summary>

clusterDeleteKeysInUnownedSlots() 中未檢查目前是否在 DB0，但原本的 verifyClusterConfigWithData() 會先確認所有非 DB0 的資料庫皆為空。若在非 DB0 有 keys，此函式仍可能刪除 slot 中的 keys，可能造成非預期的資料遺失。

建議在呼叫 clusterDeleteKeysInUnownedSlots() 前先確認 DB0 以外的資料庫為空，或在此函式中加入檢查。

**判斷依據**：diff 中新增的 clusterDeleteKeysInUnownedSlots() 沒有檢查 DB 編號，而原本的 verifyClusterConfigWithData() 有檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6230 (cache hit 1536) ｜ completion tokens 1834 ｜ PR #4</sub>