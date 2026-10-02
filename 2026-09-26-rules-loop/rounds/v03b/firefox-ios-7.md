<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要移除大量閉包上的 @Sendable 標註，並調整 ensureMainThread 泛型版本的回傳型別為 T?。整體變更範圍廣，但多數為機械式移除。主要風險在於 ensureMainThread 的語意變更（非主執行緒時回傳 nil）可能導致呼叫端未處理 nil 而產生非預期行為，以及移除 @Sendable 後可能引入資料競爭或違反 Swift 6 嚴格並發檢查。另有少數變更（如 WebServer 移除 final、MainThreadThrottler 調整 guard 順序）需進一步確認意圖。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22` | ensureMainThread 泛型版本在非主執行緒時回傳 nil，可能導致呼叫端未處理而崩潰 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Application/WebServer.swift:18` | [R12] WebServer 類別移除 final 修飾詞，可能違反專案規範 | 0.60 |
| 🔸 | Minor | `firefox-ios/Client/Utils/MainThreadThrottler.swift:25` | MainThreadThrottler 中 guard 順序調整可能改變行為 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22</code> ensureMainThread 泛型版本在非主執行緒時回傳 nil，可能導致呼叫端未處理而崩潰</summary>

原本的 ensureMainThread<T> 在非主執行緒時會將 work 排入 main queue 後直接返回（無回傳值）。現在改為回傳 T?，且在非主執行緒時回傳 nil。這表示呼叫端若假設一定能取得結果（例如強制解包），在非主執行緒呼叫時會得到 nil 而可能導致崩潰。

建議：
1. 檢查所有呼叫點，確認是否正確處理 nil。
2. 若此函式僅供主執行緒呼叫，應考慮加入 precondition(Thread.isMainThread) 或改用 async 版本。
3. 或者保留原行為，提供另一個明確的 async 版本。

**判斷依據**：diff 中顯示函式簽名從原本的無回傳改為 T?，且在 else 分支回傳 nil。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Application/WebServer.swift:18</code> [R12] WebServer 類別移除 final 修飾詞，可能違反專案規範</summary>

原本 `final class WebServer` 改為 `class WebServer`。若此類別不預期被繼承，應保留 final 以符合專案規範 R12（Classes That Should Not Be Subclassed Must Be Marked Final）。請確認是否有繼承需求，否則建議加回 final。

**判斷依據**：diff 中 `final class WebServer` 改為 `class WebServer`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:25</code> MainThreadThrottler 中 guard 順序調整可能改變行為</summary>

原本先檢查 threshold 條件，通過後才更新 lastExecutionTime。現在先更新 lastExecutionTime 再檢查條件。這可能導致在 threshold 條件不滿足時，lastExecutionTime 仍被更新，影響後續 throttle 判斷。請確認此變更是否為預期行為。

**判斷依據**：diff 中顯示 lastExecutionTime = Date() 被移到 guard 之前。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17244 (cache hit 17152) ｜ completion tokens 970 ｜ PR #7</sub>