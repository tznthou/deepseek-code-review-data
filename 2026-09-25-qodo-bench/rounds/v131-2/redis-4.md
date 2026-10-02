<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 cluster 初始化與 slot 統計相關程式碼重構，將部分邏輯從 cluster_legacy.c 移至 cluster.c，並調整 asmCron/asmBeforeSleep 的呼叫位置。主要風險在於初始化順序變更可能導致未初始化記憶體存取，以及 clusterCommonInit 中 malloc 未檢查失敗。整體方向合理，但需先確認初始化順序與錯誤處理。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/server.c:7740` | clusterCommonInit 呼叫順序可能導致未初始化記憶體存取 | 0.80 |
| 🔸 | Minor | `src/cluster.c:2138` | malloc 未檢查失敗 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:7740</code> clusterCommonInit 呼叫順序可能導致未初始化記憶體存取</summary>

原本在 clusterInit() 內呼叫 resetClusterStats() 與 asmInit()，現在改為在 clusterInit() 之前呼叫 clusterCommonInit()。clusterCommonInit() 會呼叫 resetClusterStats() 與 asmInit()，但 clusterInit() 中仍會執行 clusterUpdateMyselfIp() 等操作，這些操作可能依賴 slot stats 或 ASM 結構已初始化。若 clusterInit() 內部有使用到這些結構，且 clusterCommonInit() 未完整初始化，可能導致未定義行為。建議確認 clusterInit() 中所有依賴 slot stats 或 ASM 的程式碼路徑，確保初始化順序正確。

**判斷依據**：diff 顯示原本在 clusterInit() 內的 resetClusterStats() 與 asmInit() 被移除，改由 clusterCommonInit() 呼叫，且 clusterCommonInit() 在 clusterInit() 之前執行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/cluster.c:2138</code> malloc 未檢查失敗</summary>

clusterCommonInit() 中使用 malloc 分配 server.cluster_slot_stats，但未檢查返回值。若記憶體不足，後續 resetClusterStats() 存取該指標可能導致 segmentation fault。建議使用 zmalloc 或檢查返回值並處理錯誤。

**判斷依據**：diff 新增的 clusterCommonInit() 中直接使用 malloc 而未檢查返回值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5193 (cache hit 5120) ｜ completion tokens 572 ｜ PR #4</sub>