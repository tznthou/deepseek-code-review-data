<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多個標記為 @MainActor 的 closure 移除 @Sendable，以符合 Swift 6 的嚴格並發檢查。整體變更範圍廣，但多數為機械式移除。主要風險在於 DispatchQueueHelper.swift 中 ensureMainThread 泛型版本的 API 變更：從 Void 改為回傳 T?，且非主執行緒時直接回傳 nil，可能導致呼叫端未處理 nil 而產生非預期行為。另外，MainThreadThrottler.swift 中 throttle 方法的 guard 順序調整可能造成邏輯錯誤。建議修正上述問題後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22` | ensureMainThread 泛型版本在非主執行緒時回傳 nil，可能導致呼叫端未處理而當機 | 0.95 |
| ⚠️ | Major | `firefox-ios/Client/Utils/MainThreadThrottler.swift:25` | throttle 方法中 guard 順序調整可能導致邏輯錯誤 | 0.85 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22</code> ensureMainThread 泛型版本在非主執行緒時回傳 nil，可能導致呼叫端未處理而當機</summary>

原本的 `ensureMainThread<T>` 函式沒有回傳值，現在改成回傳 `T?`。在非主執行緒時，函式會將工作排入 main queue 後直接回傳 `nil`。這對呼叫端是破壞性變更：如果呼叫端預期會得到一個值（例如 `let result = ensureMainThread { ... }`），在非主執行緒時會拿到 `nil`，可能導致後續 force unwrap 或未預期的行為。

建議：
1. 保留原本的 Void 回傳，或提供一個明確的 async 版本。
2. 如果必須回傳 `T?`，請在文件與所有呼叫端明確處理 nil 的情況。

**判斷依據**：diff 中顯示函式簽章從 `-> Void` 改為 `-> T?`，且在 else 分支直接 `return nil`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:25</code> throttle 方法中 guard 順序調整可能導致邏輯錯誤</summary>

原本的程式碼先檢查 `guard threshold <= 0 || lastExecutionTime.timeIntervalSinceNow < -threshold else { return }`，然後才更新 `lastExecutionTime`。修改後，先更新 `lastExecutionTime`，再執行 guard 檢查。這會導致即使 guard 條件不成立（即不應該執行），`lastExecutionTime` 仍被更新，影響後續 throttle 判斷。

例如：threshold = 1 秒，連續呼叫兩次，第一次呼叫後 lastExecutionTime 更新為現在，第二次呼叫時，因為先更新了 lastExecutionTime，guard 條件 `lastExecutionTime.timeIntervalSinceNow < -threshold` 會是 false（因為剛更新），所以直接 return，但 lastExecutionTime 已經被更新，導致後續的 throttle 判斷錯誤。

建議：將 `lastExecutionTime = Date()` 移回 guard 之後。

**判斷依據**：diff 中顯示 `lastExecutionTime = Date()` 被移到 guard 之前。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 68267 (cache hit 68224) ｜ completion tokens 919 ｜ PR #7</sub>