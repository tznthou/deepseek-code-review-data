<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 cluster 相關的初始化、cron 與 beforeSleep 呼叫從 cluster_legacy.c 移至 cluster.c 與 server.c，並重構 verifyClusterConfigWithData 為 clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots。主要風險在於 clusterCommonInit 使用 malloc 而非 zmalloc（違反 R02），且 clusterCommonInit 與 clusterClaimUnassignedSlots 未宣告為 static（違反 R07）。此外，clusterDeleteKeysInUnownedSlots 的條件判斷可能因未檢查 clusterIsMySlot 而誤刪屬於自己的 slot 的 keys。建議先修正記憶體配置函式與函式可見性，並確認 slot 所有權判斷邏輯。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:2138` | [R02] 使用 malloc 而非 zmalloc | 0.95 |
| ⚠️ | Major | `src/cluster.c:2137` | [R07] clusterCommonInit 未宣告為 static | 0.90 |
| ⚠️ | Major | `src/cluster_legacy.c:5262` | [R07] clusterClaimUnassignedSlots 未宣告為 static | 0.90 |
| ⚠️ | Major | `src/cluster.c:2153` | clusterDeleteKeysInUnownedSlots 可能誤刪屬於自己的 slot 的 keys | 0.80 |
| 🔸 | Minor | `src/cluster.c:2210` | clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 的順序可能導致問題 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:2138</code> [R02] 使用 malloc 而非 zmalloc</summary>

在 clusterCommonInit 中使用 `malloc` 配置 `server.cluster_slot_stats`，違反專案規範 R02（必須使用 zmalloc/zfree 系列）。這會導致記憶體使用量無法被 Redis 的記憶體追蹤機制記錄，且可能造成記憶體洩漏。請改用 `zmalloc`。

**判斷依據**：diff 中新增的這一行直接呼叫 malloc，而專案規範 R02 明確禁止直接使用 malloc。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2137</code> [R07] clusterCommonInit 未宣告為 static</summary>

函式 `clusterCommonInit` 僅在 cluster.c 內部使用（由 server.c 呼叫），但未宣告為 `static`，違反專案規範 R07（內部輔助函式必須宣告為 static）。這會造成符號污染，並可能導致連結時的名稱衝突。請加上 `static` 修飾詞。

**判斷依據**：diff 中新增的函式定義沒有 static 關鍵字，且該函式僅在 cluster.c 中被呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster_legacy.c:5262</code> [R07] clusterClaimUnassignedSlots 未宣告為 static</summary>

函式 `clusterClaimUnassignedSlots` 僅在 cluster_legacy.c 內部使用（由 verifyClusterConfigWithData 呼叫），但未宣告為 `static`，違反專案規範 R07。請加上 `static` 修飾詞。

**判斷依據**：diff 中新增的函式定義沒有 static 關鍵字，且該函式僅在 cluster_legacy.c 中被呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2153</code> clusterDeleteKeysInUnownedSlots 可能誤刪屬於自己的 slot 的 keys</summary>

在 `clusterDeleteKeysInUnownedSlots` 中，條件判斷為 `!countKeysInSlot(i) || clusterIsMySlot(i) || getImportingSlotSource(i)`，但 `clusterIsMySlot(i)` 可能無法正確判斷 slot 是否屬於自己（例如在 cluster 尚未完全初始化時）。若判斷錯誤，可能導致刪除屬於自己的 slot 的 keys，造成資料遺失。建議確認 `clusterIsMySlot` 的實作是否可靠，或改用 `server.cluster->slots[i] == myself` 進行判斷。

**判斷依據**：diff 中新增的條件判斷使用 clusterIsMySlot，但該函式可能依賴於 cluster state，若 state 尚未完全建立可能回傳錯誤結果。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2210</code> clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 的順序可能導致問題</summary>

在 `verifyClusterConfigWithData` 中，先呼叫 `clusterDeleteKeysInUnownedSlots` 再呼叫 `clusterClaimUnassignedSlots`。若某 slot 同時有 keys 且未指派給任何節點，`clusterDeleteKeysInUnownedSlots` 會因為 `clusterIsMySlot(i)` 為 false 而刪除 keys，但隨後 `clusterClaimUnassignedSlots` 會將該 slot 指派給自己，造成資料遺失。建議調整順序或合併邏輯，先處理未指派的 slot。

**判斷依據**：diff 中顯示這兩個函式依序呼叫，且 clusterDeleteKeysInUnownedSlots 的條件未排除未指派的 slot。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6240 (cache hit 5120) ｜ completion tokens 1331 ｜ PR #4</sub>