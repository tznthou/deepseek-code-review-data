<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 cluster 初始化與 slot 統計相關程式碼重構，將部分邏輯從 cluster_legacy.c 移至 cluster.c，並調整 asmCron/asmBeforeSleep 的呼叫位置。主要風險在於記憶體配置函式從 zmalloc 改為 malloc、clusterCommonInit 的呼叫時機、以及 clusterDeleteKeysInUnownedSlots 中刪除 key 的邏輯可能造成資料遺失。建議優先確認記憶體配置與初始化順序，並補齊測試。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:2138` | 使用 malloc 取代 zmalloc 可能導致記憶體未初始化或未對齊 | 0.95 |
| ⚠️ | Major | `src/cluster.c:2137` | clusterCommonInit() 呼叫順序可能導致未初始化相依性 | 0.85 |
| ⚠️ | Major | `src/cluster.c:2167` | clusterDeleteKeysInUnownedSlots() 可能誤刪正在遷移中的 key | 0.80 |
| ⚠️ | Major | `src/cluster.c:2212` | verifyClusterConfigWithData() 中 clusterClaimUnassignedSlots() 可能覆蓋既有設定 | 0.75 |
| 🔸 | Minor | `src/server.c:1658` | asmCron() 呼叫位置變更可能影響效能 | 0.70 |
| 🔸 | Minor | `src/server.c:1842` | asmBeforeSleep() 呼叫順序可能影響叢集狀態 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:2138</code> 使用 malloc 取代 zmalloc 可能導致記憶體未初始化或未對齊</summary>

在 clusterCommonInit() 中，原本使用 zmalloc 配置 server.cluster_slot_stats，現在改為 malloc。zmalloc 會將記憶體初始化為零，而 malloc 不會。若後續程式碼假設 slot stats 已歸零（例如 resetClusterStats() 可能只重置部分欄位），可能導致未定義行為或錯誤的統計數據。建議改回 zmalloc 或使用 zcalloc。

**判斷依據**：diff 中新增的 clusterCommonInit() 使用 malloc，而原本在 server.c 中使用 zmalloc。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2137</code> clusterCommonInit() 呼叫順序可能導致未初始化相依性</summary>

clusterCommonInit() 呼叫 resetClusterStats() 和 asmInit()，但這兩個函式可能依賴其他尚未初始化的全域狀態（例如 server.cluster 或 asm 相關結構）。原本在 clusterInit() 中呼叫的順序是 resetClusterStats() 在 clusterUpdateMyselfIp() 等之後，asmInit() 在最後。現在提前到 clusterInit() 之前，可能造成相依性問題。建議確認這些函式的相依性，或調整呼叫順序。

**判斷依據**：diff 中新增 clusterCommonInit()，並在 server.c 中於 clusterInit() 之前呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2167</code> clusterDeleteKeysInUnownedSlots() 可能誤刪正在遷移中的 key</summary>

此函式會刪除所有不在自己 slot 中的 key，但未檢查 slot 是否正在進行 legacy 遷移（例如 MIGRATING 狀態）。雖然註解提到 atomic slot migration 安全，但 legacy 遷移中若節點是 migrating 狀態，刪除 key 可能導致資料遺失。建議增加對 migrating 狀態的檢查，或確認此函式僅在特定條件下呼叫。

**判斷依據**：diff 中新增的 clusterDeleteKeysInUnownedSlots() 直接呼叫 clusterDelKeysInSlot，未檢查 migrating 狀態。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2212</code> verifyClusterConfigWithData() 中 clusterClaimUnassignedSlots() 可能覆蓋既有設定</summary>

clusterClaimUnassignedSlots() 會將所有有 key 但無主的 slot 指派給自己，但未檢查是否已有其他節點正在進行遷移或設定。這可能導致叢集狀態不一致。建議在 claim 前檢查 slot 是否處於特殊狀態，或增加日誌記錄。

**判斷依據**：diff 中新增的 verifyClusterConfigWithData() 呼叫 clusterClaimUnassignedSlots()，而該函式在 cluster_legacy.c 中實作。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:1658</code> asmCron() 呼叫位置變更可能影響效能</summary>

原本 asmCron() 在 clusterCron() 內部呼叫，現在移至 serverCron() 中與 clusterCron() 並列。這可能改變執行頻率或順序，若 asmCron() 有相依於 clusterCron() 的狀態更新，可能造成問題。建議確認兩者之間的相依性。

**判斷依據**：diff 中 server.c 的 serverCron() 修改。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:1842</code> asmBeforeSleep() 呼叫順序可能影響叢集狀態</summary>

原本 asmBeforeSleep() 在 clusterBeforeSleep() 內部呼叫，現在移至 beforeSleep() 中於 clusterBeforeSleep() 之後呼叫。若 asmBeforeSleep() 需要 clusterBeforeSleep() 的結果，順序變更可能造成問題。建議確認相依性。

**判斷依據**：diff 中 server.c 的 beforeSleep() 修改。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5229 (cache hit 5120) ｜ completion tokens 1402 ｜ PR #4</sub>