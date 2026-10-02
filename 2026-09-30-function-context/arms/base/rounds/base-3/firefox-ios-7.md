<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多處標註為 @MainActor 的閉包移除 @Sendable，以符合 Swift 6 的隔離規則。整體變更一致且風險低，但有一處邏輯變更（MainThreadThrottler.throttle）可能改變行為，需確認其意圖。另有一處直接呼叫 completionHandler 取代 ensureMainThread，需確認執行緒安全性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Utils/MainThreadThrottler.swift:26` | throttle 方法中 lastExecutionTime 更新時機變更可能導致節流失效 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1343` | 直接呼叫 completionHandler 可能違反執行緒隔離 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:26</code> throttle 方法中 lastExecutionTime 更新時機變更可能導致節流失效</summary>

原本的實作在檢查時間間隔後才更新 `lastExecutionTime`，現在則在檢查前就更新。這會使得連續呼叫時，第二次呼叫的 `timeIntervalSinceNow` 會是負的且絕對值很小，導致 `guard` 條件不成立而直接 return，造成節流永遠無法觸發。

**失敗情境**：假設 `threshold = 1` 秒，連續呼叫 `throttle` 兩次（間隔小於 1 秒），第一次呼叫後 `lastExecutionTime` 被設為現在，第二次呼叫時 `timeIntervalSinceNow` 約為 -0.1 秒，`-0.1 < -1` 為 false，guard 失敗直接 return，completion 永遠不會被執行。

**建議**：將 `lastExecutionTime = Date()` 移回 guard 之後，或改為在 guard 通過後才更新。

**判斷依據**：diff 中顯示原本的順序是 guard 在前，更新在後；現在被調換了。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1343</code> 直接呼叫 completionHandler 可能違反執行緒隔離</summary>

原本使用 `ensureMainThread` 確保 completionHandler 在主執行緒執行，現在直接呼叫。若此函式可能在非主執行緒被呼叫，則 completionHandler（標註 @MainActor）會在錯誤的執行緒執行，可能導致 UI 更新問題或 runtime crash。

**失敗情境**：`handleServerTrust` 在 `dispatchQueue.async` 閉包內執行（背景執行緒），若進入 else 分支，直接呼叫 completionHandler 會將 @MainActor 閉包在背景執行緒執行，違反 actor isolation。

**建議**：保留 `ensureMainThread` 包裝，或確認此分支一定在主執行緒。

**判斷依據**：diff 中移除了 ensureMainThread 包裝，直接呼叫 completionHandler。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15175 (cache hit 15104) ｜ completion tokens 746 ｜ PR #7</sub>