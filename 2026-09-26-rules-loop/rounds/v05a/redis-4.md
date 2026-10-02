<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 cluster 相關的初始化與 slot 統計邏輯從 cluster_legacy.c 移至 cluster.c，並將 ASM 相關呼叫移至 server.c 的週期性任務中。主要風險在於 clusterCommonInit() 使用 malloc 而非 zmalloc，違反記憶體追蹤規範；此外，clusterDeleteKeysInUnownedSlots() 與 clusterClaimUnassignedSlots() 的拆分可能改變行為，需確認與原邏輯一致。整體結構調整合理，但需修正記憶體配置方式並驗證行為等價性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/cluster.c:2138` | [R02] 使用 malloc 而非 zmalloc 配置 cluster_slot_stats | 0.95 |
| ⚠️ | Major | `src/cluster.c:2167` | clusterDeleteKeysInUnownedSlots() 可能遺漏 clusterSaveConfigOrDie 呼叫 | 0.85 |
| 🔸 | Minor | `src/cluster.c:2147` | clusterDeleteKeysInUnownedSlots() 未檢查 cluster_module_flags | 0.70 |
| 🔸 | Minor | `src/cluster_legacy.c:5263` | clusterClaimUnassignedSlots() 未檢查 cluster_module_flags | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2138</code> [R02] 使用 malloc 而非 zmalloc 配置 cluster_slot_stats</summary>

在 clusterCommonInit() 中，`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));` 使用了標準 malloc，違反 Redis 記憶體管理規範。應改用 zmalloc 以納入記憶體追蹤。

**判斷依據**：diff 中新增的 clusterCommonInit() 函式內，該行直接呼叫 malloc，而原程式碼在 server.c 中使用 zmalloc。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2167</code> clusterDeleteKeysInUnownedSlots() 可能遺漏 clusterSaveConfigOrDie 呼叫</summary>

原 verifyClusterConfigWithData() 在處理完 slot 後，若 update_config > 0 會呼叫 clusterSaveConfigOrDie(1) 保存配置。新拆分的 clusterDeleteKeysInUnownedSlots() 僅刪除金鑰，未保存配置；clusterClaimUnassignedSlots() 則有保存。若刪除金鑰後配置未變更，可能不需保存，但需確認原邏輯中刪除金鑰是否會觸發配置變更（例如移除 importing 狀態）。若會，則可能遺漏持久化。

**判斷依據**：原程式碼在 clusterDelKeysInSlot 後，若 update_config 遞增，最後會呼叫 clusterSaveConfigOrDie(1)。新函式 clusterDeleteKeysInUnownedSlots() 內無此呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2147</code> clusterDeleteKeysInUnownedSlots() 未檢查 cluster_module_flags</summary>

原 verifyClusterConfigWithData() 開頭會檢查 CLUSTER_MODULE_FLAG_NO_REDIRECTION，若設定則直接返回。新拆分的 clusterDeleteKeysInUnownedSlots() 未包含此檢查，但呼叫它的 verifyClusterConfigWithData() 仍會先檢查，因此目前行為不變。然而，若未來有其他呼叫者直接呼叫 clusterDeleteKeysInUnownedSlots()，可能跳過此保護。建議在函式內也加入檢查以確保獨立使用時的安全性。

**判斷依據**：原函式開頭有 `if (server.cluster_module_flags & CLUSTER_MODULE_FLAG_NO_REDIRECTION) return C_OK;`，新函式未包含。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster_legacy.c:5263</code> clusterClaimUnassignedSlots() 未檢查 cluster_module_flags</summary>

與 clusterDeleteKeysInUnownedSlots() 類似，原 verifyClusterConfigWithData() 的 CLUSTER_MODULE_FLAG_NO_REDIRECTION 檢查未包含在新函式中。目前呼叫鏈仍安全，但建議在函式內加入檢查以維持獨立性。

**判斷依據**：原函式開頭有 `if (server.cluster_module_flags & CLUSTER_MODULE_FLAG_NO_REDIRECTION) return C_OK;`，新函式未包含。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6206 (cache hit 5248) ｜ completion tokens 1077 ｜ PR #4</sub>