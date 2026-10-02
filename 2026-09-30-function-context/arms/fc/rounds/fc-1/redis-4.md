<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 ASM 與 slot-stats 相關初始化/週期性呼叫從 cluster_legacy.c 移至 cluster.c 與 server.c，並重構 verifyClusterConfigWithData 為 clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots。主要風險在於 clusterCommonInit 使用 malloc 而非 zmalloc，以及 clusterDeleteKeysInUnownedSlots 中 clusterDelKeysInSlot 的參數語意可能導致資料遺失。整體重構方向合理，但需修正上述問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:2138` | clusterCommonInit 使用 malloc 而非 zmalloc 分配 cluster_slot_stats | 0.90 |
| 🛑 | Blocker | `src/cluster.c:2167` | clusterDeleteKeysInUnownedSlots 中 clusterDelKeysInSlot 的參數可能導致資料遺失 | 0.85 |
| ⚠️ | Major | `src/cluster.c:2153` | clusterDeleteKeysInUnownedSlots 可能刪除正在匯入的 slot 中的 keys | 0.75 |
| ⚠️ | Major | `src/cluster_legacy.c:5281` | clusterClaimUnassignedSlots 中 clusterAddSlot 可能未正確更新節點狀態 | 0.70 |
| 🔸 | Minor | `src/server.c:1445` | serverCron 中 asmCron 與 clusterCron 的呼叫順序可能影響行為 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:2138</code> clusterCommonInit 使用 malloc 而非 zmalloc 分配 cluster_slot_stats</summary>

在 clusterCommonInit 中，`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));` 使用了標準 malloc，而非 Redis 慣用的 zmalloc。這會導致記憶體分配未納入 Redis 的記憶體統計，且無法在 OOM 時觸發 Redis 的錯誤處理。建議改用 `zmalloc`。

**判斷依據**：diff 中新增的 clusterCommonInit 函式內使用 malloc，而原本在 server.c 中使用 zmalloc。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:2167</code> clusterDeleteKeysInUnownedSlots 中 clusterDelKeysInSlot 的參數可能導致資料遺失</summary>

在 clusterDeleteKeysInUnownedSlots 中呼叫 `clusterDelKeysInSlot(i, 0)`。第二個參數的語意需要確認：若為 `save` 旗標，傳 0 可能表示不保存，但若為其他語意（例如是否為 async），可能導致錯誤。請檢查 clusterDelKeysInSlot 的定義，確保傳入正確的參數。

**判斷依據**：diff 中新增的 clusterDeleteKeysInUnownedSlots 函式內呼叫 clusterDelKeysInSlot(i, 0)，但未提供該函式的定義，無法確認參數意義。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2153</code> clusterDeleteKeysInUnownedSlots 可能刪除正在匯入的 slot 中的 keys</summary>

在 clusterDeleteKeysInUnownedSlots 中，條件 `!clusterIsMySlot(i) || getImportingSlotSource(i)` 會跳過匯入中的 slot，但若 `getImportingSlotSource(i)` 回傳非 NULL 但該 slot 實際上不屬於我們，仍可能刪除 keys。需確認匯入狀態的處理是否正確。

**判斷依據**：diff 中新增的 clusterDeleteKeysInUnownedSlots 函式內的條件判斷。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster_legacy.c:5281</code> clusterClaimUnassignedSlots 中 clusterAddSlot 可能未正確更新節點狀態</summary>

在 clusterClaimUnassignedSlots 中呼叫 `clusterAddSlot(myself, i)`，但未檢查回傳值。若 clusterAddSlot 失敗（例如 slot 已被指派），可能導致狀態不一致。建議檢查回傳值並處理錯誤。

**判斷依據**：diff 中新增的 clusterClaimUnassignedSlots 函式內呼叫 clusterAddSlot 但未檢查回傳值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:1445</code> serverCron 中 asmCron 與 clusterCron 的呼叫順序可能影響行為</summary>

在 serverCron 中，將 asmCron 移至 clusterCron 之前呼叫。若 asmCron 依賴 clusterCron 的某些狀態更新，可能導致行為差異。建議確認兩者之間的相依性。

**判斷依據**：diff 中 server.c 的修改，原本只有 clusterCron，現在加入 asmCron 且順序在前。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 25048 (cache hit 1536) ｜ completion tokens 1198 ｜ PR #4</sub>