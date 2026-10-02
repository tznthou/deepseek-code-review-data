<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 cluster 初始化與 slot 統計相關程式碼重構，將部分邏輯從 cluster_legacy.c 移至 cluster.c，並調整 asmCron/asmBeforeSleep 的呼叫位置。主要風險在於初始化順序變更可能導致記憶體洩漏或未初始化使用，以及 clusterDeleteKeysInUnownedSlots 與 clusterClaimUnassignedSlots 的拆分可能改變行為。建議優先確認 clusterCommonInit 的記憶體配置與後續釋放，以及 asm 相關函式在 cluster 啟用時的正確呼叫時機。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/cluster.c:2138` | clusterCommonInit 使用 malloc 可能導致記憶體洩漏 | 0.80 |
| ⚠️ | Major | `src/cluster.c:2139` | clusterCommonInit 呼叫 resetClusterStats 可能使用未初始化的記憶體 | 0.75 |
| ⚠️ | Major | `src/cluster.c:2153` | clusterDeleteKeysInUnownedSlots 可能誤刪正在遷移的 slot 資料 | 0.70 |
| 🔸 | Minor | `src/cluster_legacy.c:5263` | clusterClaimUnassignedSlots 未檢查是否為 slave | 0.65 |
| 🔸 | Minor | `src/cluster.c:2160` | clusterDeleteKeysInUnownedSlots 的日誌訊息可能誤導 | 0.60 |
| 🔸 | Minor | `src/server.c:1658` | asmCron 與 clusterCron 的呼叫順序可能影響行為 | 0.60 |
| 🔸 | Minor | `src/server.c:1842` | asmBeforeSleep 與 clusterBeforeSleep 的呼叫順序可能影響行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2138</code> clusterCommonInit 使用 malloc 可能導致記憶體洩漏</summary>

clusterCommonInit 使用 `malloc` 配置 `server.cluster_slot_stats`，但原本在 server.c 中使用 `zmalloc`。若後續有對應的釋放邏輯使用 `zfree`，則混用配置器可能導致記憶體洩漏或未定義行為。建議改用 `zmalloc` 以保持一致。

**判斷依據**：diff 中新增的 clusterCommonInit 使用 malloc，而原本 server.c 中使用 zmalloc。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2139</code> clusterCommonInit 呼叫 resetClusterStats 可能使用未初始化的記憶體</summary>

clusterCommonInit 在配置 `server.cluster_slot_stats` 後立即呼叫 `resetClusterStats()`，但若 `resetClusterStats` 會讀取該記憶體內容（例如先讀取再寫入），則可能讀到未初始化的值。建議確認 `resetClusterStats` 的實作是否只寫入而不讀取，或改用 `zcalloc` 配置。

**判斷依據**：diff 中新增的 clusterCommonInit 呼叫 resetClusterStats，但未確認其是否安全。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/cluster.c:2153</code> clusterDeleteKeysInUnownedSlots 可能誤刪正在遷移的 slot 資料</summary>

clusterDeleteKeysInUnownedSlots 在判斷是否刪除時，僅檢查 `clusterIsMySlot(i)` 和 `getImportingSlotSource(i)`，但未檢查是否正在匯出（migrating）該 slot。若節點正在匯出 slot，且該 slot 仍有本地資料，則可能被誤刪。建議加入 `getMigratingSlotDest(i)` 的檢查。

**判斷依據**：diff 中新增的 clusterDeleteKeysInUnownedSlots 條件判斷缺少 migrating 狀態檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster_legacy.c:5263</code> clusterClaimUnassignedSlots 未檢查是否為 slave</summary>

clusterClaimUnassignedSlots 開頭有 `if (nodeIsSlave(myself)) return;`，但呼叫它的 `verifyClusterConfigWithData` 已經先檢查過 slave，因此此處的檢查是多餘的。不過若未來有其他呼叫者，保留此檢查是安全的。建議確認是否為冗餘程式碼。

**判斷依據**：diff 中新增的 clusterClaimUnassignedSlots 包含 slave 檢查，但呼叫者已檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2160</code> clusterDeleteKeysInUnownedSlots 的日誌訊息可能誤導</summary>

日誌訊息寫「Deleting keys in the slot.」但未說明原因，且可能與 clusterClaimUnassignedSlots 的日誌混淆。建議增加更具體的上下文，例如 slot 的擁有者資訊。

**判斷依據**：diff 中新增的日誌訊息較為簡略。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:1658</code> asmCron 與 clusterCron 的呼叫順序可能影響行為</summary>

原本 asmCron 在 clusterCron 內部呼叫，現在移至 serverCron 中並在 clusterCron 之前呼叫。若 asmCron 依賴 clusterCron 更新後的狀態，則可能導致行為差異。建議確認 asmCron 的相依性。

**判斷依據**：diff 中 server.c 的變更將 asmCron 移至 clusterCron 之前。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:1842</code> asmBeforeSleep 與 clusterBeforeSleep 的呼叫順序可能影響行為</summary>

原本 asmBeforeSleep 在 clusterBeforeSleep 內部呼叫，現在移至 beforeSleep 中並在 clusterBeforeSleep 之後呼叫。若 asmBeforeSleep 依賴 clusterBeforeSleep 的結果，則可能導致行為差異。建議確認 asmBeforeSleep 的相依性。

**判斷依據**：diff 中 server.c 的變更將 asmBeforeSleep 移至 clusterBeforeSleep 之後。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5229 (cache hit 5120) ｜ completion tokens 1548 ｜ PR #4</sub>