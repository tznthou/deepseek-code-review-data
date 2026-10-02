<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個標註為 @MainActor 的 closure 移除 @Sendable，以符合 Swift 6 的嚴格並發檢查。主要風險在於移除 @Sendable 可能導致這些 closure 在非主執行緒被呼叫時產生資料競爭，尤其是透過 DispatchQueue.async 或非同步 API 傳遞的 closure。此外，ensureMainThread 泛型版本的簽名變更（回傳 T?）可能影響呼叫端，且 WebServer 類別移除 final 修飾詞可能違反專案規範。建議優先確認所有受影響的 closure 是否真的只在主執行緒執行，並補回必要的 @Sendable 或調整呼叫方式。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22` | 移除 @Sendable 可能導致非主執行緒呼叫時的資料競爭 | 0.80 |
| ⚠️ | Major | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:31` | ensureMainThread 泛型版本回傳值變更可能破壞呼叫端 | 0.70 |
| 🔸 | Minor | `firefox-ios/Client/Application/WebServer.swift:18` | [R12] WebServer 類別移除 final 修飾詞 | 0.60 |
| 🔸 | Minor | `firefox-ios/Client/Utils/MainThreadThrottler.swift:26` | throttle 方法中 guard 順序變更可能影響行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22</code> 移除 @Sendable 可能導致非主執行緒呼叫時的資料競爭</summary>

`ensureMainThread` 的泛型版本移除了 `@Sendable`，但此函式可能在非主執行緒被呼叫，並透過 `DispatchQueue.main.async` 將 closure 傳遞到主執行緒。若 closure 捕獲了非 Sendable 的狀態，可能導致資料競爭。建議保留 `@Sendable` 或確保所有呼叫端都在主執行緒。

**判斷依據**：diff 中將 `@escaping @MainActor @Sendable () -> T` 改為 `@escaping @MainActor () -> T`，但函式內仍使用 `DispatchQueue.main.async`，可能跨執行緒傳遞 closure。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:31</code> ensureMainThread 泛型版本回傳值變更可能破壞呼叫端</summary>

原本的 `ensureMainThread<T>` 不回傳值，現在改為回傳 `T?`。這可能導致現有呼叫端出現編譯錯誤或行為改變，尤其是那些依賴非同步執行且不預期回傳值的程式碼。建議確認所有呼叫端並更新。

**判斷依據**：diff 中新增了 `return nil`，且函式簽名改為 `-> T?`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Application/WebServer.swift:18</code> [R12] WebServer 類別移除 final 修飾詞</summary>

`WebServer` 類別原本是 `final`，現在移除了 `final`。根據專案規範 R12，不應被子類別化的類別應標記為 `final`。除非有明確的繼承需求，否則建議保留 `final`。

**判斷依據**：diff 中將 `final class WebServer` 改為 `class WebServer`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:26</code> throttle 方法中 guard 順序變更可能影響行為</summary>

原本的 `guard` 在設定 `lastExecutionTime` 之前，現在移到之後。這可能導致在 `threshold <= 0` 或時間未超過 threshold 時，`lastExecutionTime` 仍被更新，影響後續 throttle 判斷。建議確認此變更是否為預期行為。

**判斷依據**：diff 中將 `lastExecutionTime = Date()` 移到 `guard` 之前。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17234 (cache hit 17152) ｜ completion tokens 1011 ｜ PR #7</sub>