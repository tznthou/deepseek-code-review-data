<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將大量閉包型別中的 @Sendable 移除，並調整 ensureMainThread 泛型版本的回傳型別為 T?。整體而言，移除 @Sendable 在多數情境下是安全的，因為這些閉包通常已在主執行緒上執行，且 @MainActor 已提供執行緒隔離。然而，有兩個關鍵風險：1) ensureMainThread 泛型版本在非主執行緒時回傳 nil，可能導致呼叫端未處理 nil 而崩潰；2) MainThreadThrottler 的 throttle 方法中，lastExecutionTime 的更新順序被調換，可能造成節流邏輯失效。此外，WebServer 類別從 final 改為非 final，違反專案規範 R12。建議修正上述問題後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22` | ensureMainThread 泛型版本在非主執行緒時回傳 nil，可能導致呼叫端未處理 nil 而崩潰 | 0.95 |
| ⚠️ | Major | `firefox-ios/Client/Utils/MainThreadThrottler.swift:25` | throttle 方法中 lastExecutionTime 更新順序調換可能導致節流邏輯失效 | 0.85 |
| 🔸 | Minor | `firefox-ios/Client/Application/WebServer.swift:18` | [R12] WebServer 類別從 final 改為非 final，違反專案規範 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22</code> ensureMainThread 泛型版本在非主執行緒時回傳 nil，可能導致呼叫端未處理 nil 而崩潰</summary>

此函式原本回傳 Void，現在改為回傳 T?。在非主執行緒分支中，函式直接回傳 nil，但呼叫端可能預期取得實際結果。若呼叫端未檢查 nil 並強制解包，將導致執行時期崩潰。建議改為使用 async/await 或提供明確的錯誤處理機制，而非回傳 nil。

**判斷依據**：diff 中顯示函式簽章從 `public func ensureMainThread<T>(execute work: @escaping @MainActor @Sendable () -> T)` 改為 `public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T?`，且在 else 分支新增 `return nil`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:25</code> throttle 方法中 lastExecutionTime 更新順序調換可能導致節流邏輯失效</summary>

原本先檢查時間間隔，若未超過 threshold 則直接 return，不更新 lastExecutionTime。修改後，先更新 lastExecutionTime 再檢查，這會導致即使未超過 threshold，lastExecutionTime 也被更新，使得後續呼叫可能被錯誤地允許執行。建議恢復原本的順序：先檢查，若通過再更新。

**判斷依據**：diff 顯示原本的 `guard threshold <= 0 || lastExecutionTime.timeIntervalSinceNow < -threshold else { return }` 在 `lastExecutionTime = Date()` 之前，修改後順序對調。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Application/WebServer.swift:18</code> [R12] WebServer 類別從 final 改為非 final，違反專案規範</summary>

專案規範 R12 要求不應被子類別化的類別必須標記為 final。此處將 `final class WebServer` 改為 `class WebServer`，可能允許意外的繼承。除非有明確的繼承需求，否則應保留 final。

**判斷依據**：diff 中 `-final class WebServer: WebServerProtocol, @unchecked Sendable {` 改為 `+class WebServer: WebServerProtocol, @unchecked Sendable {`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17234 (cache hit 15104) ｜ completion tokens 1048 ｜ PR #7</sub>