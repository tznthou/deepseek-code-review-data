<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將多個閉包型別中的 @Sendable 移除，並調整 ensureMainThread 泛型版本的回傳型別為 T?。整體而言，這些變更與 Swift 6 的 @MainActor 隔離規則相關，但移除 @Sendable 可能導致併發安全性問題，特別是在跨執行緒傳遞閉包時。最關鍵的風險在於 ensureMainThread 的泛型版本現在會回傳 nil，若呼叫端未處理可能導致非預期的 nil 回傳。此外，MainThreadThrottler 的邏輯變更可能改變節流行為。建議優先修正 ensureMainThread 的 API 設計，並確認所有移除 @Sendable 的閉包不會被傳遞到非主執行緒的環境。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22` | ensureMainThread 泛型版本回傳 nil 可能導致呼叫端未處理的 nil 值 | 0.90 |
| ⚠️ | Major | `firefox-ios/Client/Utils/MainThreadThrottler.swift:25` | MainThreadThrottler 節流邏輯變更可能導致行為不一致 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Application/WebServer.swift:18` | [R12] WebServer 類別移除 final 可能允許非預期的繼承 | 0.70 |
| 🔸 | Minor | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:10` | 移除 @Sendable 可能降低併發安全性 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22</code> ensureMainThread 泛型版本回傳 nil 可能導致呼叫端未處理的 nil 值</summary>

此函式原本回傳 Void，現在改為回傳 T?。當不在主執行緒時，會將工作排入主佇列並回傳 nil。這可能導致呼叫端在非主執行緒呼叫時得到 nil，若未檢查可能造成非預期的行為或崩潰。建議考慮使用 async 版本或提供明確的 completion handler，避免回傳 nil。

**判斷依據**：diff 中顯示函式簽章從 `public func ensureMainThread<T>(execute work: @escaping @MainActor @Sendable () -> T)` 改為 `public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T?`，且在 else 分支回傳 nil。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:25</code> MainThreadThrottler 節流邏輯變更可能導致行為不一致</summary>

原本的 guard 在更新 lastExecutionTime 之前執行，現在移到更新之後。這可能導致在邊界條件下（例如 threshold 剛好等於 0 或時間差等於 threshold）行為不同。請確認此變更是否為預期，並考慮加入測試。

**判斷依據**：diff 中顯示 `lastExecutionTime = Date()` 被移到 guard 之前，且 guard 條件未變。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Application/WebServer.swift:18</code> [R12] WebServer 類別移除 final 可能允許非預期的繼承</summary>

此類別原本為 final，現在移除 final。若無意讓其他類別繼承，建議保留 final 以利編譯器最佳化並明確設計意圖。

**判斷依據**：diff 中顯示 `final class WebServer` 改為 `class WebServer`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:10</code> 移除 @Sendable 可能降低併發安全性</summary>

多個閉包型別移除了 @Sendable，這可能導致在 Swift 6 嚴格併發檢查下出現編譯錯誤或執行期問題。請確認這些閉包不會被傳遞到非主執行緒的環境，或考慮保留 @Sendable 以確保安全。

**判斷依據**：diff 中多處將 `@MainActor @Sendable` 改為 `@MainActor`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17186 (cache hit 17152) ｜ completion tokens 1145 ｜ PR #7</sub>