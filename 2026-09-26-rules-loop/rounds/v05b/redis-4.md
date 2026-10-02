<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將部分 cluster 初始化與 slot 統計相關程式碼從 cluster_legacy.c 移至 cluster.c，並調整 asmCron/asmBeforeSleep 的呼叫位置。主要風險在於 clusterCommonInit 使用 malloc 而非 zmalloc（違反 R02），且 clusterCommonInit 與 clusterClaimUnassignedSlots 未宣告為 static（違反 R07）。此外，clusterDeleteKeysInUnownedSlots 中 countKeysInSlot 可能回傳負值，導致條件判斷錯誤。整體重構方向合理，但需修正上述問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:2138` | [R02] 使用 malloc 而非 zmalloc | 0.95 |
| ⚠️ | Major | `src/cluster.c:2137` | [R07] clusterCommonInit 未宣告為 static | 0.90 |
| ⚠️ | Major | `src/cluster_legacy.c:5262` | [R07] clusterClaimUnassignedSlots 未宣告為 static | 0.90 |
| ⚠️ | Major | `src/cluster.c:2153` | countKeysInSlot 可能回傳負值，導致條件判斷錯誤 | 0.80 |
| 🔸 | Minor | `src/cluster.c:2153` | clusterDeleteKeysInUnownedSlots 未檢查 clusterIsMySlot 的例外情況 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:2138</code> [R02] 使用 malloc 而非 zmalloc</summary>

在 clusterCommonInit 中使用 `malloc` 分配記憶體，違反專案規範 R02（應使用 zmalloc 系列函式）。這會導致記憶體使用量未被追蹤，且可能造成記憶體洩漏。請改用 `zmalloc`。

**判斷依據**：diff 中新增的 clusterCommonInit 函式內使用 malloc，而專案規範 R02 要求使用 zmalloc。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2137</code> [R07] clusterCommonInit 未宣告為 static</summary>

clusterCommonInit 函式僅在 cluster.c 內部使用，但未宣告為 static，違反專案規範 R07。請加上 static 修飾詞。

**判斷依據**：函式定義於 cluster.c，且未在其他檔案中引用，應為 static。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster_legacy.c:5262</code> [R07] clusterClaimUnassignedSlots 未宣告為 static</summary>

clusterClaimUnassignedSlots 函式僅在 cluster_legacy.c 內部使用，但未宣告為 static，違反專案規範 R07。請加上 static 修飾詞。

**判斷依據**：函式定義於 cluster_legacy.c，且未在其他檔案中引用，應為 static。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2153</code> countKeysInSlot 可能回傳負值，導致條件判斷錯誤</summary>

在 clusterDeleteKeysInUnownedSlots 中，`countKeysInSlot(i)` 可能回傳負值（例如 -1 表示錯誤），但條件 `!countKeysInSlot(i)` 只會對 0 為真，負值會被視為 true，導致後續邏輯錯誤。建議明確檢查回傳值是否大於 0。

**判斷依據**：diff 中新增的 clusterDeleteKeysInUnownedSlots 函式使用 `!countKeysInSlot(i)`，但未處理負值情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2153</code> clusterDeleteKeysInUnownedSlots 未檢查 clusterIsMySlot 的例外情況</summary>

在 clusterDeleteKeysInUnownedSlots 中，條件 `clusterIsMySlot(i)` 可能無法涵蓋所有應跳過的情況，例如當 slot 正在遷移中時。建議參考原有 verifyClusterConfigWithData 的邏輯，確認是否需要額外檢查。

**判斷依據**：原有 verifyClusterConfigWithData 中有更完整的檢查，此處可能遺漏某些情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6206 (cache hit 6144) ｜ completion tokens 1053 ｜ PR #4</sub>