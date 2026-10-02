<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多個 @MainActor 閉包中的 @Sendable 標記移除，以符合 Swift 6 的嚴格並發檢查。整體而言，這是一個機械性的重構，但其中 `ensureMainThread<T>` 的變更引入了行為差異：原本在非主執行緒時會非同步執行並忽略結果，現在改為回傳 nil，可能導致呼叫端誤判。此外，`MainThreadThrottler.throttle` 的邏輯順序調整可能造成節流失效。建議優先修正這兩個問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22` | ensureMainThread<T> 在非主執行緒時回傳 nil 可能造成呼叫端誤判 | 0.90 |
| ⚠️ | Major | `firefox-ios/Client/Utils/MainThreadThrottler.swift:25` | MainThreadThrottler.throttle 的節流邏輯可能失效 | 0.85 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1339` | handleServerTrust 中移除 ensureMainThread 可能導致 completionHandler 在背景執行緒呼叫 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22</code> ensureMainThread<T> 在非主執行緒時回傳 nil 可能造成呼叫端誤判</summary>

原本的 `ensureMainThread<T>` 在非主執行緒時會透過 `DispatchQueue.main.async` 非同步執行工作並忽略結果，但現在改為回傳 `nil`。這會讓呼叫端無法區分「工作尚未執行」與「工作執行後回傳 nil」，可能導致邏輯錯誤。例如，若呼叫端預期取得一個非 nil 的值，但在背景執行緒呼叫時會立即收到 nil，而實際工作稍後才在主執行緒完成。建議改為使用 `DispatchQueue.main.sync` 同步等待結果，或保留非同步行為但提供 completion handler。

**判斷依據**：diff 中顯示 `ensureMainThread<T>` 的實作從原本的 `MainActor.assumeIsolated { _ = work() }` 改為 `return MainActor.assumeIsolated { return work() }`，且在 else 分支新增 `return nil`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:25</code> MainThreadThrottler.throttle 的節流邏輯可能失效</summary>

原本的 `throttle` 方法先檢查時間間隔，若未超過閾值則直接 return，否則更新 `lastExecutionTime` 並執行 completion。修改後，`lastExecutionTime` 在檢查前就被更新，導致每次呼叫都會更新時間戳，使得節流條件永遠不成立（因為 `lastExecutionTime.timeIntervalSinceNow` 會是極小的負數，永遠小於 `-threshold`）。這會讓節流功能失效，可能造成過多的執行。建議將 `lastExecutionTime = Date()` 移回 guard 之後。

**判斷依據**：diff 顯示 `lastExecutionTime = Date()` 被移到 guard 之前，而原本的順序是先 guard 再更新時間。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1339</code> handleServerTrust 中移除 ensureMainThread 可能導致 completionHandler 在背景執行緒呼叫</summary>

在 `handleServerTrust` 的 else 分支中，原本使用 `ensureMainThread` 來確保 `completionHandler` 在主執行緒執行，但修改後直接呼叫 `completionHandler(.performDefaultHandling, nil)`。由於此方法可能在背景執行緒（dispatchQueue.async）中執行，直接呼叫可能導致 UI 更新或狀態變更不在主執行緒，違反 @MainActor 隔離。建議保留 `ensureMainThread` 或改用 `DispatchQueue.main.async`。

**判斷依據**：diff 中原本的 `ensureMainThread { completionHandler(.performDefaultHandling, nil) }` 被改為直接呼叫 `completionHandler(.performDefaultHandling, nil)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 68267 (cache hit 1536) ｜ completion tokens 1173 ｜ PR #7</sub>