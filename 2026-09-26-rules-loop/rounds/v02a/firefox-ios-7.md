<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個標記為 @MainActor 的 closure 移除 @Sendable 屬性，以符合 Swift 6 的嚴格並發檢查。整體改動範圍廣泛，涉及 UI、網路、儲存等模組。主要風險在於移除 @Sendable 後，這些 closure 可能被傳遞到非隔離的 context，導致資料競爭或編譯器警告。另外，ensureMainThread 泛型版本的簽名變更（回傳 T?）可能造成呼叫端行為改變，需確認所有使用處都已更新。WebServer 類別移除 final 修飾詞，若無繼承需求應保留 final 以利最佳化。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22` | ensureMainThread 泛型版本回傳型別改為 T? 可能造成呼叫端未處理 nil | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Application/WebServer.swift:18` | [R12] WebServer 類別移除 final 修飾詞 | 0.70 |
| 🔸 | Minor | `firefox-ios/Client/Utils/MainThreadThrottler.swift:26` | throttle 方法中 lastExecutionTime 更新順序可能影響節流邏輯 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22</code> ensureMainThread 泛型版本回傳型別改為 T? 可能造成呼叫端未處理 nil</summary>

原本的 `ensureMainThread<T>` 沒有回傳值，現在改成回傳 `T?`。在非主執行緒時會回傳 `nil`，但呼叫端若未檢查 nil 而直接使用，可能導致 force unwrap 崩潰或邏輯錯誤。請確認所有呼叫點都已正確處理可選值，或考慮提供非同步版本以避免回傳 nil。

**判斷依據**：diff 中將回傳型別從 Void 改為 T?，並在非主執行緒分支回傳 nil。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Application/WebServer.swift:18</code> [R12] WebServer 類別移除 final 修飾詞</summary>

WebServer 原本是 final class，現在改成 class。若此類別不預期被繼承，應保留 final 以利編譯器最佳化並防止意外繼承。請確認是否有繼承需求，否則建議加回 final。

**判斷依據**：diff 中將 `final class WebServer` 改為 `class WebServer`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:26</code> throttle 方法中 lastExecutionTime 更新順序可能影響節流邏輯</summary>

原本先檢查 threshold 再更新 lastExecutionTime，現在改成先更新 lastExecutionTime 再檢查。這會導致第一次呼叫時 lastExecutionTime 被設為現在，但 threshold 檢查可能因此永遠通過（因為時間差為 0，小於 threshold）。請確認此行為變更是否符合預期。

**判斷依據**：diff 中將 `lastExecutionTime = Date()` 移到 guard 之前。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17234 (cache hit 1536) ｜ completion tokens 798 ｜ PR #7</sub>