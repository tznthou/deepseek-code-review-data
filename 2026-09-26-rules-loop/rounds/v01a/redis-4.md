<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 cluster 相關的初始化與 slot 統計邏輯從 cluster_legacy.c 移至 cluster.c，並將 asmCron/asmBeforeSleep 的呼叫移至 server.c 的 serverCron/beforeSleep。主要風險在於 clusterCommonInit 使用 malloc 而非 zmalloc（違反 R02），且 clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 的拆分可能改變原有行為（例如原本會儲存設定，現在可能不會）。此外，cluster.c 中新增的 clusterMigrationCommand 與 clusterSyncSlotsCommand 呼叫可能缺少對應的 JSON 定義（R06）。整體而言，重構方向合理，但需修正記憶體配置函式並確認行為一致性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:2138` | [R02] 使用 malloc 而非 zmalloc | 0.95 |
| ⚠️ | Major | `src/cluster.c:2167` | clusterDeleteKeysInUnownedSlots 可能遺漏 clusterSaveConfigOrDie | 0.80 |
| ⚠️ | Major | `src/cluster.c:2210` | clusterClaimUnassignedSlots 可能重複處理已刪除的 slot | 0.75 |
| ⚠️ | Major | `src/cluster.c:1092` | [R06] 新增 cluster migration 與 syncslots 命令可能缺少 JSON 定義 | 0.70 |
| 🔸 | Minor | `src/server.c:1657` | asmCron 與 clusterCron 的執行順序可能影響行為 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:2138</code> [R02] 使用 malloc 而非 zmalloc</summary>

在 clusterCommonInit 中，使用 `malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat))` 配置記憶體，違反專案規範 R02（必須使用 zmalloc 系列函式）。這會導致記憶體使用量無法被 Redis 的記憶體追蹤機制記錄，可能造成記憶體統計不正確或洩漏未被偵測。

建議改為 `zmalloc(CLUSTER_SLOTS*sizeof(clusterSlotStat))`。

**判斷依據**：diff 中新增的 clusterCommonInit 函式內使用 malloc，而專案規範 R02 明確要求使用 zmalloc。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2167</code> clusterDeleteKeysInUnownedSlots 可能遺漏 clusterSaveConfigOrDie</summary>

原本的 verifyClusterConfigWithData 在處理完 slot 後，若 update_config > 0 會呼叫 clusterSaveConfigOrDie(1) 儲存設定。新的 clusterDeleteKeysInUnownedSlots 只刪除 keys，沒有儲存設定，而 clusterClaimUnassignedSlots 則有儲存。這可能導致在某些情況下設定未持久化，重啟後又回到不一致狀態。

建議確認刪除 keys 後是否需要儲存設定，或將儲存邏輯統一在 verifyClusterConfigWithData 中處理。

**判斷依據**：diff 中 clusterDeleteKeysInUnownedSlots 函式內呼叫 clusterDelKeysInSlot 後沒有 clusterSaveConfigOrDie，而原本的 verifyClusterConfigWithData 在 update_config 時會儲存。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2210</code> clusterClaimUnassignedSlots 可能重複處理已刪除的 slot</summary>

在 verifyClusterConfigWithData 中，先呼叫 clusterDeleteKeysInUnownedSlots 刪除不屬於自己的 slot 的 keys，再呼叫 clusterClaimUnassignedSlots 取得未指派 slot 的所有權。但 clusterDeleteKeysInUnownedSlots 刪除 keys 後，該 slot 可能變成無 keys 且無 owner，clusterClaimUnassignedSlots 會跳過（因為 countKeysInSlot 為 0），因此不會取得所有權。這與原本的行為不同：原本在發現 keys 且 slot 未指派時會直接取得所有權，現在若 keys 被刪除，則不會取得所有權。

請確認這是否符合預期，或調整順序/條件。

**判斷依據**：diff 中 verifyClusterConfigWithData 的呼叫順序，以及 clusterClaimUnassignedSlots 的條件 `!countKeysInSlot(i)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:1092</code> [R06] 新增 cluster migration 與 syncslots 命令可能缺少 JSON 定義</summary>

在 clusterCommand 中新增了對 clusterMigrationCommand 和 clusterSyncSlotsCommand 的呼叫，但未看到對應的 JSON 定義檔案（src/commands/cluster-migration.json 等）。根據規範 R06，每個命令都必須有對應的 JSON 定義。

請確認是否已新增或更新 JSON 檔案，否則可能導致文件或命令註冊不一致。

**判斷依據**：diff 中新增的命令分派，但未見 JSON 檔案變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:1657</code> asmCron 與 clusterCron 的執行順序可能影響行為</summary>

原本 asmCron 是在 clusterCron 內部呼叫（在 cluster_legacy.c 的 clusterCron 中），現在移到 serverCron 中，在 clusterCron 之前呼叫。這可能改變執行順序，若 asmCron 依賴 clusterCron 的某些狀態更新，可能導致問題。

請確認 asmCron 與 clusterCron 的相依性，確保順序變更不會造成影響。

**判斷依據**：diff 中 server.c 的 serverCron 修改，以及原本 cluster_legacy.c 中 clusterCron 內的 asmCron 呼叫被移除。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6230 (cache hit 5120) ｜ completion tokens 1526 ｜ PR #4</sub>