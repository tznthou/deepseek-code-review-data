<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要移除閉包上的 @Sendable 標記，並調整 ensureMainThread 泛型版本的回傳型別為 T?。整體而言，移除 @Sendable 在多數情境下是合理的，因為 @MainActor 已隱含執行緒安全。但需特別注意：1) ensureMainThread 的變更可能導致呼叫端在非主執行緒時取得 nil 而未處理，造成行為改變或資料遺失；2) 移除 @Sendable 可能導致某些 API 不再符合 Sendable 協定，進而影響型別安全；3) 部分變更（如 WebServer 移除 final、MainThreadThrottler 調整順序）與 PR 主旨無關，可能引入非預期風險。建議優先修正 ensureMainThread 的 API 設計，並確認所有呼叫端皆能正確處理 nil 回傳值。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22` | ensureMainThread 泛型版本回傳 T? 可能導致呼叫端未處理 nil 而遺失結果 | 0.90 |
| 🔸 | Minor | `firefox-ios/Client/Application/WebServer.swift:18` | 移除 final 可能允許非預期的子類別化 | 0.70 |
| 🔸 | Minor | `firefox-ios/Client/Utils/MainThreadThrottler.swift:25` | throttle 方法中 lastExecutionTime 更新順序變更可能影響節流邏輯 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22</code> ensureMainThread 泛型版本回傳 T? 可能導致呼叫端未處理 nil 而遺失結果</summary>

此函式原本在非主執行緒時會將工作排入主佇列並忽略回傳值，現在改為回傳 nil。這使得呼叫端必須處理 nil 的情況，否則可能遺失重要結果。例如，若原本呼叫端假設函式會同步執行並取得結果，現在在非主執行緒時會得到 nil，可能導致後續邏輯錯誤。建議提供明確的 API 設計，例如使用 async/await 或 completion handler，避免回傳可選值造成混淆。

**判斷依據**：diff 中顯示函式簽章從原本的無回傳改為 T?，且在非主執行緒分支回傳 nil。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Application/WebServer.swift:18</code> 移除 final 可能允許非預期的子類別化</summary>

WebServer 類別原本為 final，現在移除 final 修飾詞。若此類別不應被繼承，移除 final 可能導致非預期的繼承，且喪失編譯器最佳化。建議確認是否有必要移除 final，若無則保留。

**判斷依據**：diff 中顯示 'final class WebServer' 改為 'class WebServer'。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:25</code> throttle 方法中 lastExecutionTime 更新順序變更可能影響節流邏輯</summary>

原本在 guard 條件檢查前更新 lastExecutionTime，現在移到 guard 之後。這可能導致在 threshold 條件不滿足時，lastExecutionTime 未被更新，使得下一次呼叫仍可能被節流，與預期行為不符。建議確認此變更是否為刻意調整，並確保節流邏輯正確。

**判斷依據**：diff 中顯示 lastExecutionTime = Date() 從 guard 之前移至 guard 之後。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17244 (cache hit 15104) ｜ completion tokens 977 ｜ PR #7</sub>