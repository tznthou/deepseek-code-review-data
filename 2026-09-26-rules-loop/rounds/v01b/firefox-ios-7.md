<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要移除大量閉包上的 @Sendable 標註，並調整 ensureMainThread 泛型版本的回傳型別為 T?。整體而言，移除 @Sendable 在多數情境下是安全的，因為這些閉包已標註 @MainActor，且 Swift 6 對 @MainActor 閉包有隱含的 Sendable 推斷。然而，有兩個地方需要特別注意：MainThreadThrottler.throttle 中 lastExecutionTime 的更新順序被調換，可能導致節流邏輯失效；BrowserViewController+WebViewDelegates.swift 中 handleServerTrust 的 ensureMainThread 包裝被移除，可能造成 completionHandler 在背景執行緒被呼叫，違反 @MainActor 隔離。建議修正這兩個問題後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Utils/MainThreadThrottler.swift:26` | throttle 方法中 lastExecutionTime 更新順序錯誤導致節流失效 | 0.95 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1343` | 移除 ensureMainThread 包裝可能導致 completionHandler 在背景執行緒被呼叫 | 0.85 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:26</code> throttle 方法中 lastExecutionTime 更新順序錯誤導致節流失效</summary>

在 `throttle` 方法中，原本先檢查 `guard threshold <= 0 || lastExecutionTime.timeIntervalSinceNow < -threshold else { return }` 再更新 `lastExecutionTime = Date()`。但修改後將 `lastExecutionTime = Date()` 移到 guard 之前，這會導致每次呼叫都先更新時間戳，使得 guard 條件永遠為真（因為 `lastExecutionTime` 剛被設為現在，`timeIntervalSinceNow` 接近 0，若 threshold > 0 則條件 `0 < -threshold` 為 false，guard 會直接 return，永遠不會執行 completion）。這完全破壞了節流功能，可能導致 UI 操作被意外忽略或延遲。

**失敗情境**：假設 threshold = 1 秒，連續快速呼叫 `throttle` 兩次。第一次呼叫後 `lastExecutionTime` 被設為現在，第二次呼叫時 guard 檢查 `lastExecutionTime.timeIntervalSinceNow < -1`，由於時間差幾乎為 0，條件不成立，直接 return，completion 永遠不會被執行。

**建議修法**：將 `lastExecutionTime = Date()` 移回 guard 之後，保持原有邏輯。

**判斷依據**：diff 中顯示原本的順序是 guard 在前，更新在後；修改後順序顛倒。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1343</code> 移除 ensureMainThread 包裝可能導致 completionHandler 在背景執行緒被呼叫</summary>

在 `handleServerTrust` 方法中，原本使用 `ensureMainThread { completionHandler(.performDefaultHandling, nil) }` 來確保 completionHandler 在主執行緒被呼叫。修改後直接呼叫 `completionHandler(.performDefaultHandling, nil)`，但此方法可能從背景執行緒（`dispatchQueue.async` 內）被呼叫，而 completionHandler 的型別是 `@MainActor`，這違反了 actor 隔離，可能導致執行時錯誤或資料競爭。

**失敗情境**：當 `dispatchQueue` 不是主佇列時，`handleServerTrust` 內部的 `dispatchQueue.async` 區塊會在背景執行緒執行，此時直接呼叫 `completionHandler` 會觸發 Swift 執行時檢查，可能導致 crash 或未定義行為。

**建議修法**：恢復使用 `ensureMainThread` 或明確切換到主執行緒後再呼叫 completionHandler。

**判斷依據**：diff 中顯示原本有 `ensureMainThread { completionHandler(.performDefaultHandling, nil) }`，修改後直接呼叫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17234 (cache hit 17152) ｜ completion tokens 988 ｜ PR #7</sub>