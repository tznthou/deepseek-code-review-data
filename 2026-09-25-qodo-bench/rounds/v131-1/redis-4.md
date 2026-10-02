<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 cluster 初始化與 slot 統計相關程式碼重構，將 slot-stats 初始化移至 clusterCommonInit()，並將 ASM 相關 cron 呼叫移至 server.c 的通用路徑。主要風險在於初始化順序與記憶體配置函式的變更（malloc vs zmalloc），以及 ASM cron 呼叫位置的調整可能影響行為。整體結構合理，但需確認記憶體配置一致性與初始化順序。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/cluster.c:2138` | 使用 malloc 而非 zmalloc 配置 cluster_slot_stats | 0.80 |
| ⚠️ | Major | `src/server.c:1658` | asmCron() 呼叫順序變更可能影響行為 | 0.70 |
| ⚠️ | Major | `src/server.c:1842` | asmBeforeSleep() 呼叫順序變更可能影響行為 | 0.70 |
| 🔸 | Minor | `src/cluster.c:2139` | clusterCommonInit() 中 resetClusterStats() 可能重複初始化 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2138</code> 使用 malloc 而非 zmalloc 配置 cluster_slot_stats</summary>

在 clusterCommonInit() 中，`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));` 使用標準 malloc，而原本在 server.c 中使用 zmalloc。zmalloc 是 Redis 的記憶體配置封裝，提供記憶體統計與 OOM 處理。若改用 malloc，可能導致記憶體統計不正確，且在記憶體不足時行為不一致。建議改回 zmalloc。

**判斷依據**：diff 中新增的 clusterCommonInit() 使用 malloc，而刪除的 server.c 程式碼原本使用 zmalloc。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:1658</code> asmCron() 呼叫順序變更可能影響行為</summary>

原本 asmCron() 在 clusterCron() 內部呼叫，現在移至 serverCron() 中 clusterCron() 之前。若 asmCron() 依賴 clusterCron() 的某些狀態更新，順序變更可能導致問題。需確認 asmCron() 的相依性。

**判斷依據**：diff 顯示 asmCron() 從 clusterCron() 中移除，並在 serverCron() 中新增於 clusterCron() 之前。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:1842</code> asmBeforeSleep() 呼叫順序變更可能影響行為</summary>

原本 asmBeforeSleep() 在 clusterBeforeSleep() 內部呼叫，現在移至 server.c 中 clusterBeforeSleep() 之後。若 asmBeforeSleep() 依賴 clusterBeforeSleep() 的某些狀態，順序變更可能導致問題。需確認相依性。

**判斷依據**：diff 顯示 asmBeforeSleep() 從 clusterBeforeSleep() 中移除，並在 server.c 中新增於 clusterBeforeSleep() 之後。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2139</code> clusterCommonInit() 中 resetClusterStats() 可能重複初始化</summary>

clusterCommonInit() 呼叫 resetClusterStats()，但原本 clusterInit() 中也呼叫 resetClusterStats()。現在 clusterInit() 中已移除該呼叫，但需確認沒有其他路徑重複初始化。

**判斷依據**：diff 顯示 clusterInit() 中移除 resetClusterStats()，並在 clusterCommonInit() 中新增。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5193 (cache hit 1408) ｜ completion tokens 895 ｜ PR #4</sub>