<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將多個閉包型別中的 @Sendable 移除，並調整 ensureMainThread 泛型版本的回傳型別為 T?。整體而言，移除 @Sendable 在多數情境下是安全的，因為這些閉包通常已在主要執行緒上執行，且 @MainActor 已提供執行緒安全的保證。然而，有兩個地方需要特別注意：MainThreadThrottler.throttle 中 lastExecutionTime 的更新順序被調換，可能導致節流邏輯失效；另外，BrowserViewController+WebViewDelegates.swift 中直接呼叫 completionHandler 取代 ensureMainThread，可能造成執行緒安全問題。建議修正這兩個問題後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Utils/MainThreadThrottler.swift:26` | throttle 方法中 lastExecutionTime 更新順序錯誤 | 0.90 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1343` | 直接呼叫 completionHandler 可能違反執行緒安全 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:26</code> throttle 方法中 lastExecutionTime 更新順序錯誤</summary>

在 throttle 方法中，原本先檢查時間間隔再更新 lastExecutionTime，現在改成先更新 lastExecutionTime 再檢查。這會導致每次呼叫都更新時間戳，使得節流條件永遠無法滿足（除非 threshold <= 0），節流功能失效。

失敗情境：假設 threshold = 1 秒，連續快速呼叫 throttle 兩次，第一次呼叫後 lastExecutionTime 設為現在，第二次呼叫時，因為 lastExecutionTime 剛被更新，時間間隔小於 threshold，所以不會執行 completion，但 lastExecutionTime 又被更新，導致後續呼叫永遠被節流。

建議：將 lastExecutionTime = Date() 移回 guard 檢查之後。

**判斷依據**：diff 中顯示原本的順序是 guard 在前，lastExecutionTime 更新在後，現在被調換了。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1343</code> 直接呼叫 completionHandler 可能違反執行緒安全</summary>

在 handleServerTrust 中，原本使用 ensureMainThread 來確保 completionHandler 在主執行緒上執行，現在改成直接呼叫 completionHandler。但 handleServerTrust 是在 dispatchQueue.async 中執行的，該佇列可能是背景佇列，因此 completionHandler 可能在背景執行緒被呼叫，而 completionHandler 被標記為 @MainActor，這可能導致執行緒安全問題或 runtime crash。

失敗情境：當憑證不在信任清單中時，completionHandler 會在背景執行緒被呼叫，若 completionHandler 內部存取 UI 或 main actor 隔離的狀態，可能導致資料競爭或 crash。

建議：保留 ensureMainThread 包裝，或確保 dispatchQueue 是 main queue。

**判斷依據**：diff 中移除了 ensureMainThread 包裝，直接呼叫 completionHandler。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15175 (cache hit 15104) ｜ completion tokens 778 ｜ PR #7</sub>