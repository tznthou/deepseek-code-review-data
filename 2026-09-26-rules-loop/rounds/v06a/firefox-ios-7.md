<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將大量閉包型別中的 @Sendable 移除，並調整 ensureMainThread 泛型版本的回傳型別為 T?，以及將 WebServer 類別從 final 改為非 final。整體而言，這些變更與 Swift 6 的 @MainActor 隔離規則調整有關，但存在幾個潛在問題：ensureMainThread 的泛型版本在非主執行緒時回傳 nil，可能導致呼叫端未處理 nil 而崩潰；WebServer 移除 final 可能違反專案規範 R12；MainThreadThrottler 中 lastExecutionTime 的更新位置變更可能影響節流行為。建議優先修正 ensureMainThread 的 nil 處理與 WebServer 的 final 修飾詞。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22` | ensureMainThread 泛型版本在非主執行緒時回傳 nil，可能導致呼叫端未處理而崩潰 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Application/WebServer.swift:18` | [R12] WebServer 類別移除 final 修飾詞，可能違反專案規範 | 0.70 |
| 🔸 | Minor | `firefox-ios/Client/Utils/MainThreadThrottler.swift:25` | MainThreadThrottler 中 lastExecutionTime 更新位置變更可能影響節流行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22</code> ensureMainThread 泛型版本在非主執行緒時回傳 nil，可能導致呼叫端未處理而崩潰</summary>

原本的 ensureMainThread<T> 在非主執行緒時會將 work 排入主佇列後直接返回（無回傳值），但修改後回傳 T?，且在非主執行緒時回傳 nil。這使得呼叫端必須處理 nil 的情況，否則可能發生 force unwrap 崩潰。建議提供明確的文件說明，或考慮使用不同的 API 設計（例如使用 async/await 或 completion handler）。

**判斷依據**：diff 中顯示函式簽名從原本的無回傳改為 T?，且在 else 分支回傳 nil。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Application/WebServer.swift:18</code> [R12] WebServer 類別移除 final 修飾詞，可能違反專案規範</summary>

根據專案規範 R12，不應被子類別化的類別應標記為 final。此處將 final class WebServer 改為 class WebServer，若無明確的子類別化需求，建議保留 final。

**判斷依據**：diff 中顯示 final 關鍵字被移除。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:25</code> MainThreadThrottler 中 lastExecutionTime 更新位置變更可能影響節流行為</summary>

原本在 guard 條件判斷前更新 lastExecutionTime，現在移到 guard 之後。這可能導致在 threshold 內呼叫時，lastExecutionTime 不會更新，使得節流窗口延長。請確認此變更是否符合預期。

**判斷依據**：diff 中顯示 lastExecutionTime = Date() 從 guard 之前移到 guard 之後。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17224 (cache hit 15104) ｜ completion tokens 908 ｜ PR #7</sub>