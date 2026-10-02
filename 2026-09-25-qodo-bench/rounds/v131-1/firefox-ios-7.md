<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將大量閉包型別中的 `@Sendable` 屬性移除，並調整 `ensureMainThread` 泛型版本的回傳型別為 `T?`。主要風險在於移除 `@Sendable` 可能導致資料競爭，特別是在 `WebServer` 類別中，其 handler 閉包可能在非主執行緒被呼叫，且該類別被標記為 `@unchecked Sendable`，若閉包捕獲非 Sendable 狀態，可能造成未定義行為。此外，`ensureMainThread` 的變更可能導致呼叫端忽略 nil 回傳值而產生邏輯錯誤。建議優先檢視 `WebServer` 的執行緒安全性，並確認所有呼叫端正確處理 `ensureMainThread` 的新回傳型別。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Application/WebServer.swift:59` | 移除 @Sendable 可能導致 handler 閉包在非主執行緒執行時產生資料競爭 | 0.80 |
| ⚠️ | Major | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22` | ensureMainThread 泛型版本回傳 T? 可能導致呼叫端忽略 nil 而產生邏輯錯誤 | 0.70 |
| 🔸 | Minor | `firefox-ios/Client/Utils/MainThreadThrottler.swift:25` | throttle 方法中 lastExecutionTime 更新順序變更可能影響節流邏輯 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Application/WebServer.swift:59</code> 移除 @Sendable 可能導致 handler 閉包在非主執行緒執行時產生資料競爭</summary>

`WebServer` 類別被標記為 `@unchecked Sendable`，但其 handler 閉包現在不再要求 `@Sendable`。若 handler 閉包捕獲非 Sendable 的狀態，且該閉包在非主執行緒被呼叫，可能導致資料競爭。建議確認 GCDWebServer 呼叫 handler 的執行緒，若可能非主執行緒，應保留 `@Sendable` 或確保閉包內只存取 Sendable 狀態。

**判斷依據**：diff 中移除 `@Sendable`，且 `WebServer` 類別標記為 `@unchecked Sendable`，但 handler 閉包可能被 GCDWebServer 在任意執行緒呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22</code> ensureMainThread 泛型版本回傳 T? 可能導致呼叫端忽略 nil 而產生邏輯錯誤</summary>

`ensureMainThread<T>` 現在在非主執行緒時回傳 `nil`，但呼叫端可能未處理 nil 而直接使用回傳值，導致非預期的 nil 或崩潰。建議檢查所有呼叫端，確認它們正確處理 nil 情況，或考慮提供非同步版本。

**判斷依據**：diff 中新增回傳 `nil` 的分支，且函式簽名改為 `T?`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:25</code> throttle 方法中 lastExecutionTime 更新順序變更可能影響節流邏輯</summary>

原本在 guard 檢查前更新 `lastExecutionTime`，現在移到 guard 之後。這可能導致在 threshold 條件不滿足時，`lastExecutionTime` 未被更新，使得後續呼叫的節流判斷不正確。建議確認此變更是否為預期行為。

**判斷依據**：diff 中 `lastExecutionTime = Date()` 從 guard 前移到 guard 後。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15139 (cache hit 1408) ｜ completion tokens 1015 ｜ PR #7</sub>