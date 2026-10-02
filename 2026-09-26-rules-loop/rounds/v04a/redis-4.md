<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 cluster 初始化與 slot 統計相關程式碼從 cluster_legacy.c 重構至 cluster.c，並將 ASM 相關 cron 呼叫移至 server.c。主要風險在於 clusterCommonInit 使用 malloc 而非 zmalloc（違反 R02），以及 clusterDeleteKeysInUnownedSlots 在刪除 key 後未保存配置，可能導致重啟後配置不一致。整體重構方向合理，但需修正記憶體分配與配置持久化問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:2138` | [R02] 使用 malloc 而非 zmalloc 分配 cluster_slot_stats | 0.95 |
| ⚠️ | Major | `src/cluster.c:2167` | clusterDeleteKeysInUnownedSlots 刪除 key 後未保存配置 | 0.80 |
| 🔸 | Minor | `src/cluster.c:2147` | clusterDeleteKeysInUnownedSlots 中 slave 檢查重複 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:2138</code> [R02] 使用 malloc 而非 zmalloc 分配 cluster_slot_stats</summary>

在 clusterCommonInit 中使用 `malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat))` 分配記憶體，違反專案規範 R02（必須使用 zmalloc 系列函數）。這會導致記憶體使用量無法被 Redis 的記憶體追蹤機制統計，且可能造成記憶體洩漏偵測失效。

建議改為 `zmalloc(CLUSTER_SLOTS*sizeof(clusterSlotStat))`。

**判斷依據**：diff 中新增的 clusterCommonInit 函式內使用 malloc，而原程式碼在 server.c 中使用 zmalloc。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2167</code> clusterDeleteKeysInUnownedSlots 刪除 key 後未保存配置</summary>

在 clusterDeleteKeysInUnownedSlots 中，當發現不屬於自己的 slot 中有 key 時，會呼叫 `clusterDelKeysInSlot(i, 0)` 刪除 key，但之後沒有呼叫 `clusterSaveConfigOrDie(1)` 保存配置。這可能導致節點重啟後，這些 key 仍然存在（因為配置未更新），再次觸發刪除流程，造成不必要的延遲或資料不一致。

建議在刪除 key 後保存配置，或至少記錄需要保存的標誌。

**判斷依據**：原 verifyClusterConfigWithData 中在處理完所有 slot 後會呼叫 clusterSaveConfigOrDie(1)，但新函式 clusterDeleteKeysInUnownedSlots 沒有此步驟。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2147</code> clusterDeleteKeysInUnownedSlots 中 slave 檢查重複</summary>

clusterDeleteKeysInUnownedSlots 開頭檢查 `clusterNodeIsSlave(getMyClusterNode())`，但呼叫它的 verifyClusterConfigWithData 已經做過相同檢查。雖然不影響正確性，但重複檢查可能造成混淆。

建議移除其中一個檢查，或保留但加上註解說明為何需要重複。

**判斷依據**：verifyClusterConfigWithData 中已有 `if (clusterNodeIsSlave(getMyClusterNode())) return C_OK;`，而 clusterDeleteKeysInUnownedSlots 又重複檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5722 (cache hit 5120) ｜ completion tokens 843 ｜ PR #4</sub>