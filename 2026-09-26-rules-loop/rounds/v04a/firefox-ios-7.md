<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要移除大量閉包上的 @Sendable 標註，並調整 ensureMainThread 泛型版本的回傳型別為 T?。整體而言，移除 @Sendable 在多數情境下是合理的，因為 @MainActor 已隱含執行緒安全。但需特別注意 ensureMainThread 的變更：非主執行緒時現在會回傳 nil，這可能導致呼叫端在未預期的情況下收到 nil 而崩潰或產生錯誤行為。此外，WebServer 類別從 final 改為非 final，違反專案規範 R12，且可能影響效能與設計意圖。建議優先修正 ensureMainThread 的 nil 回傳問題，並確認 WebServer 是否真的需要被繼承。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22` | ensureMainThread 非主執行緒時回傳 nil 可能導致呼叫端意外崩潰 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Application/WebServer.swift:18` | [R12] WebServer 類別不應移除 final | 0.90 |
| 🔸 | Minor | `firefox-ios/Client/Utils/MainThreadThrottler.swift:26` | throttle 方法中 lastExecutionTime 更新時機可能造成行為改變 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22</code> ensureMainThread 非主執行緒時回傳 nil 可能導致呼叫端意外崩潰</summary>

泛型版本 `ensureMainThread<T>` 現在在非主執行緒時回傳 `nil`，而原本是直接忽略結果。這會讓所有依賴此函式回傳值的呼叫端在背景執行緒呼叫時收到 `nil`，若未處理可能導致 force unwrap 崩潰或邏輯錯誤。

**失敗情境**：假設某個函式在背景執行緒呼叫 `ensureMainThread { return someValue }`，並預期取得 `someValue`，但現在會得到 `nil`，若後續使用 `!` 解包就會崩潰。

**建議**：考慮提供兩個版本：一個回傳 `T?`（目前行為），另一個維持原本的 `Void` 版本；或者改用 `async` 版本讓呼叫端明確處理非同步。

**判斷依據**：diff 中顯示函式簽章從 `-> T` 改為 `-> T?`，且在 else 分支新增 `return nil`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Application/WebServer.swift:18</code> [R12] WebServer 類別不應移除 final</summary>

此類別原本標記為 `final`，但此次變更移除了 `final`。根據專案規範 R12，不應被子類別化的類別應標記為 `final`。此變更可能允許意外的繼承，且失去編譯器最佳化。

**建議**：除非有明確的繼承需求，否則應保留 `final`。

**判斷依據**：diff 中 `final class WebServer` 改為 `class WebServer`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:26</code> throttle 方法中 lastExecutionTime 更新時機可能造成行為改變</summary>

原本 `lastExecutionTime` 只在通過 guard 後才更新，現在則在 guard 之前更新。這會影響節流邏輯：即使因為時間間隔不足而 return，`lastExecutionTime` 也會被更新，導致後續呼叫可能被錯誤地允許或拒絕。

**失敗情境**：假設 threshold 為 1 秒，連續兩次呼叫間隔 0.5 秒。原本第二次呼叫會因為未達 threshold 而被忽略，但現在第二次呼叫會更新 `lastExecutionTime`，使得第三次呼叫（距離第二次 0.5 秒）可能被允許，違反節流意圖。

**建議**：將 `lastExecutionTime = Date()` 移回 guard 之後，或確認此行為變更是有意的。

**判斷依據**：diff 中顯示 `lastExecutionTime = Date()` 被移到 guard 之前。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16022 (cache hit 15104) ｜ completion tokens 1044 ｜ PR #7</sub>