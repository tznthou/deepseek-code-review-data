<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將專案與多個 target 的 Swift 版本從 5.0 升級至 6.0，並為多個閉包與方法加上 @MainActor 與 @Sendable 標註以符合 Swift 6 的嚴格並發檢查。主要風險在於 LaunchCoordinator 中將原本同步的 onActionTap 閉包改為包在 Task 內執行，可能改變執行順序與時序；此外，部分閉包標註的變更可能導致 API 相容性問題。建議優先確認 Task 包裝的必要性與潛在的競態，並補齊相關測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271` | onActionTap 閉包改為 Task 包裝可能改變執行時序 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192` | [R13] 魔法數字 40 取代 UX.buttonSize | 0.70 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:79` | spamCallback 參數新增 @Sendable 可能限制閉包捕獲 | 0.60 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/BrowserViewController/WebEngineIntegration/BrowserWebUIDelegate.swift:42` | 移除 @Sendable 可能導致並發警告 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271</code> onActionTap 閉包改為 Task 包裝可能改變執行時序</summary>

原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。這會使 handleAction 的執行延後到下一次 run loop，且不再阻塞當前呼叫者。若呼叫者依賴同步完成（例如在閉包返回後立即讀取狀態），可能導致行為不一致。此外，Task 預設繼承當前 actor 的隔離，但此處閉包已標註 @MainActor，因此 Task 應在主執行緒執行，但時序仍可能改變。建議確認此變更是否為 Swift 6 編譯所必需，若非必要，考慮保留同步呼叫；若必要，請評估對呼叫端的影響並補充測試。

**判斷依據**：diff 中 onActionTap 閉包內容從直接呼叫改為 Task 包裝，且閉包簽名從 @MainActor 改為非隔離，可能導致執行緒與時序變化。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192</code> [R13] 魔法數字 40 取代 UX.buttonSize</summary>

原本使用 UX.buttonSize 常數，現在直接使用魔法數字 40。這違反了專案規範 R13（UI 常數應定義在巢狀 UX struct 中）。建議保留 UX struct 並使用常數，或將 40 定義為具名常數。

**判斷依據**：diff 中刪除了 UX struct 中的 buttonSize 定義，並在約束中直接使用 40。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:79</code> spamCallback 參數新增 @Sendable 可能限制閉包捕獲</summary>

handleJavaScriptAlert 的 spamCallback 參數從 @escaping () -> Void 改為 @escaping @MainActor @Sendable () -> Void。新增 @Sendable 要求閉包必須是 Sendable，這可能導致呼叫端若捕獲非 Sendable 的狀態時產生編譯錯誤。請確認所有呼叫此方法的地方都能滿足 Sendable 要求，或考慮是否真的需要 @Sendable。

**判斷依據**：diff 中該行新增了 @Sendable 標註。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/WebEngineIntegration/BrowserWebUIDelegate.swift:42</code> 移除 @Sendable 可能導致並發警告</summary>

completionHandler 參數從 @escaping @MainActor @Sendable () -> Void 改為 @escaping @MainActor () -> Void，移除了 @Sendable。若此方法實作 WKUIDelegate 協定，而協定要求 @Sendable，則可能導致編譯警告或錯誤。請確認協定定義是否要求 @Sendable。

**判斷依據**：diff 中該行移除了 @Sendable。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10703 (cache hit 8576) ｜ completion tokens 1149 ｜ PR #3</sub>