<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將專案 Swift 版本從 5.0 升級至 6.0，並在多個 UI 相關閉包與協定中加入 @MainActor 與 @Sendable 標註，以符合 Swift 6 的嚴格並行檢查。主要風險在於 LaunchCoordinator 中將原本同步的 onActionTap 閉包改為包在 Task 中執行，可能改變執行時序與錯誤處理；另外 DownloadToast 將常數 40 直接寫死，違反專案 UX 常數規範。整體而言，變更方向正確，但需確認並行標註的完整性與測試涵蓋。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271` | onActionTap 閉包改為非同步執行可能造成行為差異 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192` | [R13] 魔法數字 40 應定義於 UX 結構中 | 0.90 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/BrowserViewController/WebEngineIntegration/BrowserWebUIDelegate.swift:42` | completionHandler 缺少 @Sendable 標註可能導致 Swift 6 編譯警告 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271</code> onActionTap 閉包改為非同步執行可能造成行為差異</summary>

原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在包在 `Task { ... }` 中，使得 handleAction 變成非同步執行。若 handleAction 內部有依賴呼叫順序或需要立即完成的邏輯（例如 completion 必須在特定時序前被呼叫），可能導致行為改變。此外，Task 未指定優先權或取消處理，可能造成不必要的延遲或資源浪費。建議確認 handleAction 是否為非同步設計，或考慮使用 `Task { @MainActor in ... }` 明確標註執行緒，並評估是否需保留同步行為。

**判斷依據**：diff 中 onActionTap 閉包內容由直接呼叫改為包在 Task 中，且未見其他同步機制。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192</code> [R13] 魔法數字 40 應定義於 UX 結構中</summary>

原本使用 `UX.buttonSize` 常數，現改為直接寫死 `40`，違反專案規範 R13（UI 常數應定義於巢狀 UX struct）。建議保留 `UX.buttonSize` 常數，或將 40 定義於 DownloadToast 的 UX struct 中。

**判斷依據**：diff 中刪除了 `struct UX { static let buttonSize: CGFloat = 40 }`，並將使用處改為直接寫 40。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/WebEngineIntegration/BrowserWebUIDelegate.swift:42</code> completionHandler 缺少 @Sendable 標註可能導致 Swift 6 編譯警告</summary>

在 BrowserWebUIDelegate 中，`runJavaScriptAlertPanelWithMessage` 的 completionHandler 參數從 `@escaping @MainActor @Sendable () -> Void` 改為 `@escaping @MainActor () -> Void`，移除了 @Sendable。若此方法實作 WKUIDelegate 協定，而協定要求 @Sendable，可能導致編譯錯誤或警告。建議確認協定定義，若需要則保留 @Sendable。

**判斷依據**：diff 中該行由 `@escaping @MainActor @Sendable () -> Void` 改為 `@escaping @MainActor () -> Void`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10645 (cache hit 10624) ｜ completion tokens 961 ｜ PR #3</sub>