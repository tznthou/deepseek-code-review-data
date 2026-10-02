<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 cluster 初始化與 slot 統計相關程式碼從 cluster_legacy.c 重構至 cluster.c，並將 ASM 相關 cron 呼叫移至 server.c。主要風險在於 clusterCommonInit 使用 malloc 而非 zmalloc（違反 R02），且 clusterCommonInit 與 clusterClaimUnassignedSlots 未宣告為 static（違反 R07）。此外，clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 的邏輯拆分可能改變行為，需確認與原 verifyClusterConfigWithData 的語意一致。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/cluster.c:2138` | [R02] 使用 malloc 而非 zmalloc | 0.95 |
| ⚠️ | Major | `src/cluster.c:2167` | clusterDeleteKeysInUnownedSlots 可能遺漏 clusterSaveConfigOrDie 呼叫 | 0.80 |
| 🔸 | Minor | `src/cluster.c:2137` | [R07] clusterCommonInit 未宣告為 static | 0.90 |
| 🔸 | Minor | `src/cluster_legacy.c:5262` | [R07] clusterClaimUnassignedSlots 未宣告為 static | 0.90 |
| 🔸 | Minor | `src/server.c:1658` | asmCron 呼叫順序可能影響行為 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2138</code> [R02] 使用 malloc 而非 zmalloc</summary>

在 clusterCommonInit 中使用 `malloc` 分配 `server.cluster_slot_stats`，違反專案規範 R02（應使用 zmalloc 系列函式以追蹤記憶體使用）。建議改用 `zmalloc`。

**判斷依據**：diff 中新增的 clusterCommonInit 函式內使用 malloc，而原程式碼在 server.c 中使用 zmalloc。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2167</code> clusterDeleteKeysInUnownedSlots 可能遺漏 clusterSaveConfigOrDie 呼叫</summary>

原 verifyClusterConfigWithData 在刪除不屬於自己的 slot 的 keys 後，會呼叫 clusterSaveConfigOrDie(1) 保存配置。重構後，clusterDeleteKeysInUnownedSlots 僅刪除 keys，未保存配置；clusterClaimUnassignedSlots 則在 claim 後保存。若刪除 keys 後配置未變更，可能不需保存，但需確認原邏輯中 update_config 計數是否包含刪除 keys 的情況。原程式碼中，當 slot 有 keys 且不屬於自己時，會執行 clusterDelKeysInSlot 並增加 update_config，最後保存配置。重構後，刪除 keys 的動作未觸發保存，可能導致配置不一致。

**判斷依據**：原 verifyClusterConfigWithData 中，在 clusterDelKeysInSlot 後會 update_config++，最後 clusterSaveConfigOrDie(1)。新函式 clusterDeleteKeysInUnownedSlots 未保存配置。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2137</code> [R07] clusterCommonInit 未宣告為 static</summary>

clusterCommonInit 僅在 server.c 中被呼叫，應宣告為 static 以符合內部函式封裝慣例。

**判斷依據**：函式定義於 cluster.c，但未加 static，且僅在 server.c 的 main 中呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster_legacy.c:5262</code> [R07] clusterClaimUnassignedSlots 未宣告為 static</summary>

clusterClaimUnassignedSlots 僅在 cluster.c 中被呼叫，應宣告為 static。

**判斷依據**：函式定義於 cluster_legacy.c，但未加 static，且僅在 cluster.c 的 verifyClusterConfigWithData 中呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:1658</code> asmCron 呼叫順序可能影響行為</summary>

原 clusterCron 中，asmCron 在 clusterUpdateState 之後呼叫；現在 asmCron 在 clusterCron 之前呼叫。若 asmCron 依賴 clusterCron 的某些狀態更新，可能導致行為差異。建議確認順序變更的影響。

**判斷依據**：原程式碼在 clusterCron 內呼叫 asmCron，現在移至 serverCron 中並置於 clusterCron 之前。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6240 (cache hit 6144) ｜ completion tokens 1116 ｜ PR #4</sub>