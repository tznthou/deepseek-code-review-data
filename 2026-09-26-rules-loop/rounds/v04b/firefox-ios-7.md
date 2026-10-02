<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要移除多個閉包型別上的 @Sendable 標註，並調整 ensureMainThread 泛型版本的回傳型別為 T?。整體而言，這些變更與 Swift 6 的 @MainActor 隔離規則相符，但其中 MainThreadThrottler.throttle 的邏輯變更可能導致節流行為失效，且 WebServer 類別移除 final 修飾詞違反專案規範 R12。建議優先修正 throttle 的邏輯與 WebServer 的 final 修飾詞。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Utils/MainThreadThrottler.swift:26` | throttle 方法中 lastExecutionTime 更新時機錯誤，導致節流失效 | 0.95 |
| ⚠️ | Major | `firefox-ios/Client/Application/WebServer.swift:18` | [R12] WebServer 類別不應移除 final 修飾詞 | 0.90 |
| ⚠️ | Major | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22` | ensureMainThread 泛型版本在非主執行緒時回傳 nil，可能造成呼叫端未處理 nil 而崩潰 | 0.80 |
| 🔸 | Minor | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:31` | ensureMainThread 泛型版本在非主執行緒時未執行 work，可能造成行為不一致 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:26</code> throttle 方法中 lastExecutionTime 更新時機錯誤，導致節流失效</summary>

在 `throttle(completion:)` 中，原本先檢查時間間隔再更新 `lastExecutionTime`，現在改為先更新 `lastExecutionTime` 再檢查。這會導致每次呼叫都更新時間戳，使得 `guard` 條件永遠為 false（因為 `lastExecutionTime.timeIntervalSinceNow` 會是極小的負值），節流機制完全失效。

**失敗情境**：連續快速呼叫 `throttle` 時，原本應只執行最後一次，但現在每次都會執行。

**建議**：將 `lastExecutionTime = Date()` 移回 `guard` 之後，或改為在 `guard` 通過後才更新。

**判斷依據**：diff 中顯示原本的 `guard` 在 `lastExecutionTime = Date()` 之前，現在順序對調。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Application/WebServer.swift:18</code> [R12] WebServer 類別不應移除 final 修飾詞</summary>

`WebServer` 原本宣告為 `final class`，此 PR 移除了 `final`。根據專案規範 R12，不應被子類別化的類別應標記為 `final`。此類別為單例且無子類別需求，移除 `final` 可能導致意外的繼承與效能損失。

**建議**：恢復 `final` 修飾詞。

**判斷依據**：diff 中 `final class WebServer` 改為 `class WebServer`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22</code> ensureMainThread 泛型版本在非主執行緒時回傳 nil，可能造成呼叫端未處理 nil 而崩潰</summary>

`ensureMainThread<T>` 現在回傳 `T?`，在非主執行緒時直接回傳 `nil`。這改變了 API 行為，原本呼叫端可能假設會同步取得結果，現在可能收到 nil 而導致後續邏輯錯誤或崩潰。

**失敗情境**：呼叫端在非主執行緒呼叫 `ensureMainThread` 並直接使用回傳值（例如強制解包），會得到 nil 而崩潰。

**建議**：確認所有呼叫端都正確處理 nil，或考慮提供非同步版本。

**判斷依據**：diff 中新增了 `-> T?` 並在 else 分支回傳 nil。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:31</code> ensureMainThread 泛型版本在非主執行緒時未執行 work，可能造成行為不一致</summary>

在非主執行緒時，原本會將 work 排入 main queue 執行，現在直接回傳 nil 而不執行 work。這可能導致某些依賴 work 執行的邏輯被跳過。

**建議**：確認此變更符合預期，或考慮保留非同步執行。

**判斷依據**：diff 中 else 分支從 `DispatchQueue.main.async { _ = work() }` 改為 `return nil`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16022 (cache hit 16000) ｜ completion tokens 1148 ｜ PR #7</sub>