<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將多個閉包型別中的 `@Sendable` 標記移除，並調整 `ensureMainThread` 泛型版本的回傳型別為 `T?`。整體而言，這些變更與 Swift 6 的 `@MainActor` 隔離規則調整有關，但移除 `@Sendable` 可能導致併發安全問題，特別是在跨執行緒傳遞閉包時。最關鍵的風險在於 `ensureMainThread` 的泛型版本現在在非主執行緒時會回傳 `nil`，這可能導致呼叫端未處理 `nil` 而發生錯誤。建議先確認所有呼叫端都正確處理了新的可選回傳值，並評估移除 `@Sendable` 對併發安全的影響。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22` | ensureMainThread 泛型版本在非主執行緒時回傳 nil，可能導致呼叫端未處理 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Utils/MainThreadThrottler.swift:25` | throttle 方法中 lastExecutionTime 更新順序改變可能影響節流邏輯 | 0.60 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1343` | 移除 ensureMainThread 包裝可能導致 completionHandler 在非主執行緒被呼叫 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22</code> ensureMainThread 泛型版本在非主執行緒時回傳 nil，可能導致呼叫端未處理</summary>

`ensureMainThread<T>` 現在在非主執行緒時會回傳 `nil`，但呼叫端可能預期它會同步等待或總是有值。這可能導致呼叫端在未檢查 `nil` 的情況下強制解包，造成執行時期錯誤。建議確認所有呼叫端都正確處理了 `nil`，或考慮提供非同步版本。

**判斷依據**：diff 中顯示函式回傳型別從 `Void` 改為 `T?`，且在非主執行緒分支回傳 `nil`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:25</code> throttle 方法中 lastExecutionTime 更新順序改變可能影響節流邏輯</summary>

原本 `lastExecutionTime` 在 guard 之後才更新，現在移到 guard 之前。這可能導致在 threshold 條件不滿足時也更新了時間，影響後續呼叫的節流判斷。請確認此變更是否為預期行為。

**判斷依據**：diff 中顯示 `lastExecutionTime = Date()` 被移到 guard 之前。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1343</code> 移除 ensureMainThread 包裝可能導致 completionHandler 在非主執行緒被呼叫</summary>

原本使用 `ensureMainThread` 確保 `completionHandler` 在主執行緒執行，現在直接呼叫。若此處原本可能在背景執行緒，則可能違反 `@MainActor` 隔離。請確認此函式是否總是在主執行緒被呼叫。

**判斷依據**：diff 中顯示原本的 `ensureMainThread { completionHandler(...) }` 被替換為直接呼叫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15175 (cache hit 1536) ｜ completion tokens 937 ｜ PR #7</sub>