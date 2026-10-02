<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將多個閉包型別中的 @Sendable 移除，並調整 ensureMainThread 泛型版本的回傳型別為 T?。整體而言，這些變更與 Swift 6 的 @MainActor 隔離規則相關，但移除 @Sendable 可能導致在非同步情境下的資料隔離問題。此外，ensureMainThread 的變更可能造成呼叫端未處理 nil 回傳值而導致邏輯錯誤。最需要優先確認的是 ensureMainThread 的變更是否會影響現有呼叫端，以及移除 @Sendable 是否會引入資料競爭。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22` | ensureMainThread 泛型版本回傳型別改為 T? 可能導致呼叫端未處理 nil 而崩潰 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Application/WebServer.swift:18` | [R12] WebServer 類別移除 final 修飾詞，可能違反設計意圖 | 0.70 |
| 🔸 | Minor | `firefox-ios/Client/Utils/MainThreadThrottler.swift:26` | throttle 方法中 lastExecutionTime 更新順序變更可能影響節流邏輯 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22</code> ensureMainThread 泛型版本回傳型別改為 T? 可能導致呼叫端未處理 nil 而崩潰</summary>

原本的 ensureMainThread<T> 回傳 Void，現在改為回傳 T?。在非主執行緒時，函式會回傳 nil，但呼叫端可能仍預期會得到 T 值，導致後續強制解包或直接使用時發生崩潰。建議檢查所有呼叫端是否已正確處理 nil 情況，或考慮提供非同步版本。

**判斷依據**：diff 中顯示回傳型別從原本的無回傳改為 T?，且在 else 分支回傳 nil。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Application/WebServer.swift:18</code> [R12] WebServer 類別移除 final 修飾詞，可能違反設計意圖</summary>

原本的 final class WebServer 被改為 class WebServer，移除了 final 修飾詞。這可能允許意外的子類別化，並失去編譯器最佳化。除非有明確的繼承需求，否則應保留 final。

**判斷依據**：diff 中顯示 final 關鍵字被移除。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:26</code> throttle 方法中 lastExecutionTime 更新順序變更可能影響節流邏輯</summary>

原本在 guard 檢查後才更新 lastExecutionTime，現在改為先更新再檢查。這可能導致在 threshold 條件不滿足時，lastExecutionTime 仍被更新，影響後續節流判斷。建議確認此變更是否為預期行為。

**判斷依據**：diff 中顯示 lastExecutionTime 的賦值被移到 guard 之前。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17224 (cache hit 17152) ｜ completion tokens 776 ｜ PR #7</sub>