<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 ASM 與 slot-stats 相關初始化/週期性呼叫從 cluster_legacy.c 移至 cluster.c 與 server.c，並重構 verifyClusterConfigWithData 的邏輯。主要風險在於 clusterCommonInit 使用 malloc 而非 zmalloc，可能導致記憶體統計不一致；clusterDeleteKeysInUnownedSlots 在刪除前未檢查 slot 是否正在匯入，可能誤刪資料；以及 asmCron 與 asmBeforeSleep 的呼叫順序變更可能影響 ASM 狀態機。建議先修正這些問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/cluster.c:2138` | clusterCommonInit 使用 malloc 而非 zmalloc，可能導致記憶體統計不一致 | 0.85 |
| ⚠️ | Major | `src/cluster.c:2153` | clusterDeleteKeysInUnownedSlots 未檢查 slot 是否正在匯入，可能誤刪資料 | 0.80 |
| ⚠️ | Major | `src/server.c:1450` | asmCron 與 clusterCron 的呼叫順序變更可能影響 ASM 狀態機 | 0.75 |
| ⚠️ | Major | `src/server.c:1795` | asmBeforeSleep 與 clusterBeforeSleep 的呼叫順序變更可能影響 ASM 狀態機 | 0.75 |
| 🔸 | Minor | `src/cluster.c:2138` | clusterCommonInit 未檢查 malloc 回傳值 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2138</code> clusterCommonInit 使用 malloc 而非 zmalloc，可能導致記憶體統計不一致</summary>

在 clusterCommonInit 中，`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));` 使用了標準 malloc，而 Redis 內部通常使用 zmalloc 來追蹤記憶體使用量。若使用 malloc，`zmalloc_used_memory()` 將不會包含這塊記憶體，導致記憶體統計偏低，可能影響 maxmemory 政策或監控。建議改用 `zmalloc`。

**判斷依據**：diff 中新增的 clusterCommonInit 函式內，該行使用 malloc 而非 zmalloc。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2153</code> clusterDeleteKeysInUnownedSlots 未檢查 slot 是否正在匯入，可能誤刪資料</summary>

在 clusterDeleteKeysInUnownedSlots 中，條件 `if (!countKeysInSlot(i) || clusterIsMySlot(i) || getImportingSlotSource(i))` 會跳過有匯入來源的 slot，但若 slot 同時有匯入來源且不屬於自己，則會跳過刪除。然而，若 slot 正在匯入但尚未完成，且該 slot 不屬於自己，則可能誤刪正在匯入的資料。建議確認此邏輯是否符合預期，或增加更明確的條件。

**判斷依據**：diff 中新增的 clusterDeleteKeysInUnownedSlots 函式，條件判斷可能遺漏匯入狀態。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:1450</code> asmCron 與 clusterCron 的呼叫順序變更可能影響 ASM 狀態機</summary>

在 serverCron 中，原本 clusterCron 內部會呼叫 asmCron，現在改為在 clusterCron 之前呼叫 asmCron。若 asmCron 依賴 clusterCron 所更新的某些狀態，則可能導致行為不一致。建議確認 asmCron 與 clusterCron 的相依性，或保持原有順序。

**判斷依據**：diff 中 server.c 的變更，將 asmCron 呼叫移至 clusterCron 之前。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:1795</code> asmBeforeSleep 與 clusterBeforeSleep 的呼叫順序變更可能影響 ASM 狀態機</summary>

在 beforeSleep 中，原本 clusterBeforeSleep 內部會呼叫 asmBeforeSleep，現在改為在 clusterBeforeSleep 之後呼叫 asmBeforeSleep。若 asmBeforeSleep 依賴 clusterBeforeSleep 所更新的某些狀態，則可能導致行為不一致。建議確認 asmBeforeSleep 與 clusterBeforeSleep 的相依性，或保持原有順序。

**判斷依據**：diff 中 server.c 的變更，將 asmBeforeSleep 呼叫移至 clusterBeforeSleep 之後。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2138</code> clusterCommonInit 未檢查 malloc 回傳值</summary>

在 clusterCommonInit 中，`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));` 未檢查 malloc 是否成功。若記憶體不足，可能導致後續使用 NULL 指標而崩潰。建議檢查回傳值並處理錯誤。

**判斷依據**：diff 中新增的 clusterCommonInit 函式內，該行未檢查 malloc 回傳值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 25048 (cache hit 24960) ｜ completion tokens 1302 ｜ PR #4</sub>