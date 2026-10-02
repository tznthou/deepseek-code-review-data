<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將原本在 cluster_legacy.c 中的部分函式（verifyClusterConfigWithData 的邏輯、clusterClaimUnassignedSlots、clusterDeleteKeysInUnownedSlots）移至 cluster.c，並將 asmCron/asmBeforeSleep 的呼叫從 cluster_legacy.c 移到 server.c 的 serverCron/beforeSleep 中。主要風險在於記憶體配置方式從 zmalloc 改為 malloc（可能造成記憶體未初始化或洩漏），以及 asmCron/asmBeforeSleep 的呼叫時機與順序改變可能影響原子槽遷移的正確性。建議先確認記憶體配置與初始化方式，並驗證 asm 相關函式在新呼叫位置下的行為。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/cluster.c:2138` | 使用 malloc 取代 zmalloc 可能導致記憶體未初始化或洩漏 | 0.80 |
| ⚠️ | Major | `src/server.c:1658` | asmCron() 呼叫順序可能影響原子槽遷移 | 0.70 |
| ⚠️ | Major | `src/server.c:1842` | asmBeforeSleep() 呼叫順序可能影響原子槽遷移 | 0.70 |
| 🔸 | Minor | `src/cluster.c:2153` | clusterDeleteKeysInUnownedSlots 中未檢查 clusterIsMySlot 的例外情況 | 0.60 |
| 🔸 | Minor | `src/cluster.c:2167` | clusterDeleteKeysInUnownedSlots 中未保存配置變更 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2138</code> 使用 malloc 取代 zmalloc 可能導致記憶體未初始化或洩漏</summary>

在 clusterCommonInit() 中，原本使用 zmalloc 配置 server.cluster_slot_stats，現在改為 malloc。zmalloc 通常會追蹤記憶體使用量並在 OOM 時終止程式，而 malloc 不會。此外，若後續程式碼假設記憶體已初始化為零，則可能讀取到未定義內容。建議改回 zmalloc，或確認後續有完整初始化。

**判斷依據**：diff 中新增的 clusterCommonInit() 使用 malloc，而原本在 server.c 中使用 zmalloc。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:1658</code> asmCron() 呼叫順序可能影響原子槽遷移</summary>

原本 asmCron() 在 clusterCron() 內部最後呼叫，現在移到 serverCron 中 clusterCron() 之前。若 asmCron 依賴 clusterCron 更新後的叢集狀態，順序變更可能導致行為錯誤。建議確認 asmCron 的相依性，或維持原本順序。

**判斷依據**：diff 顯示在 serverCron 中先呼叫 asmCron() 再呼叫 clusterCron()，而原本在 cluster_legacy.c 的 clusterCron() 中 asmCron() 是在最後呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:1842</code> asmBeforeSleep() 呼叫順序可能影響原子槽遷移</summary>

原本 asmBeforeSleep() 在 clusterBeforeSleep() 內部最後呼叫，現在移到 beforeSleep 中 clusterBeforeSleep() 之後。若 asmBeforeSleep 依賴 clusterBeforeSleep 的某些副作用，順序變更可能導致問題。建議確認相依性。

**判斷依據**：diff 顯示在 beforeSleep 中先呼叫 clusterBeforeSleep() 再呼叫 asmBeforeSleep()，而原本在 cluster_legacy.c 的 clusterBeforeSleep() 中 asmBeforeSleep() 是在最後呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2153</code> clusterDeleteKeysInUnownedSlots 中未檢查 clusterIsMySlot 的例外情況</summary>

在 clusterDeleteKeysInUnownedSlots 中，條件 `!clusterIsMySlot(i)` 會跳過屬於自己的槽，但若槽正在遷出（migrating）且仍有本地 keys，是否應刪除？原邏輯中若槽屬於自己則保留，但遷出狀態下可能仍需處理。建議確認遷出狀態下的行為。

**判斷依據**：diff 中新增的 clusterDeleteKeysInUnownedSlots 函式，條件與原 verifyClusterConfigWithData 中的邏輯略有不同（原邏輯檢查 server.cluster->slots[j] == myself 或 importing_slots_from[j] != NULL）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2167</code> clusterDeleteKeysInUnownedSlots 中未保存配置變更</summary>

原 verifyClusterConfigWithData 在刪除 keys 後會呼叫 clusterSaveConfigOrDie(1) 保存配置，但新的 clusterDeleteKeysInUnownedSlots 沒有保存。若刪除 keys 後配置未變更，可能不需要保存，但若刪除動作影響了 slot 狀態，可能需要保存。建議確認。

**判斷依據**：diff 中 clusterDeleteKeysInUnownedSlots 呼叫 clusterDelKeysInSlot 後未呼叫 clusterSaveConfigOrDie，而原函式在迴圈後有呼叫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5229 (cache hit 1536) ｜ completion tokens 1297 ｜ PR #4</sub>