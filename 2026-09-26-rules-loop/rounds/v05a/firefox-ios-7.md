<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將多個閉包型別中的 @Sendable 移除，並調整 ensureMainThread 泛型版本的回傳型別為 T?。整體而言，移除 @Sendable 在多數情境下是合理的，因為 @MainActor 已隱含執行緒安全。但需特別注意 ensureMainThread 的變更：非主執行緒時回傳 nil 可能導致呼叫端未處理 nil 而崩潰，且 DispatchQueue.main.async 中的 work 執行結果被忽略，可能造成資料遺失。另外，MainThreadThrottler 中 lastExecutionTime 的更新順序變更可能影響節流邏輯。建議優先修正 ensureMainThread 的設計，並確認所有呼叫端都正確處理可選回傳值。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22` | ensureMainThread 非主執行緒時回傳 nil 可能導致呼叫端未處理而崩潰 | 0.90 |
| ⚠️ | Major | `firefox-ios/Client/Utils/MainThreadThrottler.swift:25` | MainThreadThrottler 中 lastExecutionTime 更新順序變更可能影響節流邏輯 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1343` | 移除 ensureMainThread 包裝可能導致 completionHandler 在非主執行緒執行 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22</code> ensureMainThread 非主執行緒時回傳 nil 可能導致呼叫端未處理而崩潰</summary>

此函式現在回傳 T?，但在非主執行緒時直接回傳 nil，且非同步執行的 work 結果被忽略。若呼叫端預期取得非 nil 值（例如強制解包），可能導致執行時期錯誤。建議改為非同步版本或提供明確的錯誤處理機制。

**判斷依據**：diff 中顯示新增了回傳型別 T?，並在 else 分支回傳 nil，同時 work 的結果被忽略。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Utils/MainThreadThrottler.swift:25</code> MainThreadThrottler 中 lastExecutionTime 更新順序變更可能影響節流邏輯</summary>

原本先檢查 threshold 再更新 lastExecutionTime，現在改為先更新再檢查。這可能導致在 threshold 內連續呼叫時，最後一次呼叫的時間被記錄，但實際上並未執行，造成後續節流判斷錯誤。建議維持原本順序。

**判斷依據**：diff 中顯示 lastExecutionTime = Date() 被移到 guard 之前。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1343</code> 移除 ensureMainThread 包裝可能導致 completionHandler 在非主執行緒執行</summary>

原本使用 ensureMainThread 確保 completionHandler 在主執行緒執行，現在直接呼叫。若此函式可能在背景執行緒被呼叫，則可能違反 @MainActor 隔離。需確認呼叫端是否總是在主執行緒。

**判斷依據**：diff 中移除了 ensureMainThread 包裝，直接呼叫 completionHandler。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17186 (cache hit 15104) ｜ completion tokens 902 ｜ PR #7</sub>