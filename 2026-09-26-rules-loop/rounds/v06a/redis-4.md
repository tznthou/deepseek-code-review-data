<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將部分 cluster 功能（slot-stats 初始化、ASM cron、migration/syncslots 命令處理）從 cluster_legacy.c 重構至 cluster.c，並將 verifyClusterConfigWithData 拆分為 clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots。主要風險在於 clusterCommonInit 使用 malloc 而非 zmalloc（違反 R02），以及 asmCron/asmBeforeSleep 的呼叫順序變更可能影響行為。整體重構方向合理，但需修正記憶體分配函式並確認呼叫順序無副作用。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:2138` | [R02] 使用 malloc 而非 zmalloc 分配 cluster_slot_stats | 0.95 |
| ⚠️ | Major | `src/server.c:1658` | asmCron 呼叫順序變更可能影響行為 | 0.70 |
| ⚠️ | Major | `src/server.c:1842` | asmBeforeSleep 呼叫順序變更可能影響行為 | 0.70 |
| 🔸 | Minor | `src/cluster.c:2138` | clusterCommonInit 中未檢查 malloc 回傳值 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:2138</code> [R02] 使用 malloc 而非 zmalloc 分配 cluster_slot_stats</summary>

在 clusterCommonInit 中，使用 `malloc` 分配 `server.cluster_slot_stats`，違反專案規範 R02（應使用 zmalloc 系列函式）。這會導致記憶體使用量未被 Redis 的記憶體追蹤機制記錄，可能影響 `INFO memory` 的準確性，並在 OOM 時無法正確處理。建議改用 `zmalloc`。

**判斷依據**：diff 中新增的 clusterCommonInit 函式內，該行使用 malloc 而非 zmalloc。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:1658</code> asmCron 呼叫順序變更可能影響行為</summary>

原本 asmCron 在 clusterCron 內部呼叫（cluster_legacy.c 的 clusterCron 末尾），現在移至 serverCron 中，在 clusterCron 之前呼叫。若 asmCron 依賴 clusterCron 更新後的狀態（例如 slot 遷移狀態），此順序變更可能導致非預期行為。建議確認 asmCron 與 clusterCron 的相依性，或保持原有順序。

**判斷依據**：diff 顯示 server.c 中新增 asmCron() 呼叫，且位於 clusterCron() 之前；原 cluster_legacy.c 中 asmCron 在 clusterCron 末尾呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:1842</code> asmBeforeSleep 呼叫順序變更可能影響行為</summary>

原本 asmBeforeSleep 在 clusterBeforeSleep 內部呼叫（cluster_legacy.c 的 clusterBeforeSleep 末尾），現在移至 server.c 中，在 clusterBeforeSleep 之後呼叫。若 asmBeforeSleep 依賴 clusterBeforeSleep 的某些副作用（例如更新節點狀態），此順序變更可能導致問題。建議確認兩者相依性，或保持原有順序。

**判斷依據**：diff 顯示 server.c 中新增 asmBeforeSleep() 呼叫，且位於 clusterBeforeSleep() 之後；原 cluster_legacy.c 中 asmBeforeSleep 在 clusterBeforeSleep 末尾呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2138</code> clusterCommonInit 中未檢查 malloc 回傳值</summary>

malloc 可能失敗並回傳 NULL，但程式碼未檢查，後續 resetClusterStats 或 asmInit 可能對 NULL 指標進行操作，導致 crash。建議加入 NULL 檢查並在失敗時進行適當處理（如記錄錯誤並退出）。

**判斷依據**：diff 中新增的 clusterCommonInit 函式，malloc 後直接呼叫 resetClusterStats，未檢查回傳值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6220 (cache hit 5120) ｜ completion tokens 1036 ｜ PR #4</sub>