<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要移除多個閉包上的 @Sendable 標記，並調整 ensureMainThread 泛型版本的回傳型別為 T?。整體而言，移除 @Sendable 在多數情境下是安全的，因為這些閉包通常已在 MainActor 上執行，且 Swift 6 的並發檢查已能處理。然而，ensureMainThread 的變更引入了行為差異：非主執行緒時回傳 nil，可能導致呼叫端未處理 nil 而崩潰或邏輯錯誤。此外，MainThreadThrottler 中 lastExecutionTime 的更新順序改變可能影響節流邏輯。建議優先修正 ensureMainThread 的 nil 處理，並確認所有呼叫端已妥善處理。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22` | ensureMainThread 非主執行緒時回傳 nil，可能導致呼叫端未處理而崩潰 | 0.90 |
| ⚠️ | Major | `firefox-ios/Client/Utils/MainThreadThrottler.swift:25` | MainThreadThrottler 中 lastExecutionTime 更新順序改變可能導致節流失效 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22</code> ensureMainThread 非主執行緒時回傳 nil，可能導致呼叫端未處理而崩潰</summary>

泛型版本的 ensureMainThread 現在在非主執行緒時回傳 nil，而先前版本會在主執行緒上非同步執行並忽略結果。這可能導致呼叫端在未檢查 nil 的情況下強制解包或直接使用回傳值，造成崩潰或邏輯錯誤。例如，若呼叫端原本預期函式會同步回傳結果，現在可能收到 nil 而無法完成工作。建議：1) 檢查所有呼叫端是否已處理 nil；2) 考慮改為非同步版本或提供明確的錯誤處理；3) 若無法保證所有呼叫端都處理 nil，應保留原有行為或提供替代方案。

**判斷依據**：diff 中顯示函式簽名從原本的無回傳改為回傳 T?，且在 else 分支回傳 nil。原本的實作在非主執行緒時僅非同步執行 work 並忽略結果，現在則回傳 nil，這改變了 API 契約。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:25</code> MainThreadThrottler 中 lastExecutionTime 更新順序改變可能導致節流失效</summary>

原本的程式碼在檢查 threshold 後才更新 lastExecutionTime，現在則先更新再檢查。這可能導致節流邏輯錯誤：如果 threshold 條件不滿足，原本會直接 return 而不更新時間，現在卻會更新時間，使得下一次呼叫可能被錯誤地允許或阻止。例如，若 threshold 為 1 秒，第一次呼叫後 lastExecutionTime 被更新，第二次呼叫在 0.5 秒後到來，原本應被阻止，但現在因為先更新了時間，檢查時 timeIntervalSinceNow 可能小於 -threshold，導致被允許執行。建議恢復原本的順序，或確認此變更為有意為之。

**判斷依據**：diff 顯示原本的 guard 在更新 lastExecutionTime 之前，現在被移到更新之後。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15139 (cache hit 15104) ｜ completion tokens 900 ｜ PR #7</sub>