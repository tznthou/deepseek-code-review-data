<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 cluster 初始化與 slot 統計相關程式碼從 cluster_legacy.c 重構至 cluster.c，並將 asmCron/asmBeforeSleep 的呼叫移至 server.c 的週期性任務中。主要風險在於 clusterCommonInit 使用 malloc 而非 zmalloc（違反 R02），可能導致記憶體統計不正確；此外，clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 的邏輯拆分可能改變行為，需確認與原 verifyClusterConfigWithData 的語意一致。整體而言，重構方向合理，但需修正記憶體配置函式並確保測試覆蓋。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:2138` | [R02] 使用 malloc 而非 zmalloc 配置 cluster_slot_stats | 0.95 |
| ⚠️ | Major | `src/cluster.c:2167` | clusterDeleteKeysInUnownedSlots 未處理 clusterDelKeysInSlot 的失敗 | 0.80 |
| ⚠️ | Major | `src/cluster_legacy.c:5281` | clusterClaimUnassignedSlots 可能重複宣告 slot 所有權 | 0.75 |
| 🔸 | Minor | `src/server.c:1658` | asmCron 與 clusterCron 的執行順序可能影響行為 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:2138</code> [R02] 使用 malloc 而非 zmalloc 配置 cluster_slot_stats</summary>

在 clusterCommonInit 中使用 `malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat))` 配置記憶體，違反專案規範 R02（應使用 zmalloc 系列函式）。這會導致記憶體使用量未被 Redis 的記憶體追蹤機制記錄，可能造成 `INFO memory` 回報不正確，且無法透過記憶體監控發現洩漏。建議改用 `zmalloc`。

**判斷依據**：diff 中新增的 clusterCommonInit 函式內使用 malloc，而原本在 server.c 中是使用 zmalloc（見刪除行 `server.cluster_slot_stats = zmalloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2167</code> clusterDeleteKeysInUnownedSlots 未處理 clusterDelKeysInSlot 的失敗</summary>

在 clusterDeleteKeysInUnownedSlots 中呼叫 `clusterDelKeysInSlot(i, 0)` 後未檢查回傳值。若刪除失敗（例如內部錯誤），函式仍會繼續執行，可能導致後續邏輯基於不正確的狀態。建議檢查回傳值並記錄錯誤或採取適當措施。

**判斷依據**：diff 中新增的 clusterDeleteKeysInUnownedSlots 函式內直接呼叫 clusterDelKeysInSlot，未使用其回傳值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster_legacy.c:5281</code> clusterClaimUnassignedSlots 可能重複宣告 slot 所有權</summary>

clusterClaimUnassignedSlots 在迴圈中對每個未指派且有 key 的 slot 呼叫 `clusterAddSlot(myself, i)`，但未檢查該 slot 是否已在本次迴圈中被宣告。若多個 slot 連續未指派，clusterAddSlot 可能觸發多次 clusterSaveConfigOrDie，導致不必要的 I/O。建議累積變更後一次儲存，或確認 clusterAddSlot 內部已處理。

**判斷依據**：diff 中新增的 clusterClaimUnassignedSlots 函式內，在迴圈中直接呼叫 clusterAddSlot，且 update_config 僅用於計數，未用於延遲儲存。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:1658</code> asmCron 與 clusterCron 的執行順序可能影響行為</summary>

在 serverCron 中，原本 asmCron 是在 clusterCron 內部呼叫（見 cluster_legacy.c 刪除行），現在改為在 clusterCron 之前呼叫。若 asmCron 依賴 clusterCron 先更新某些狀態，順序變更可能導致非預期行為。建議確認兩者之間沒有隱含依賴，或調整順序。

**判斷依據**：diff 中 server.c 的修改將 asmCron 呼叫移至 clusterCron 之前，而原本在 cluster_legacy.c 中 asmCron 是在 clusterCron 函式內最後呼叫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6220 (cache hit 6144) ｜ completion tokens 1104 ｜ PR #4</sub>