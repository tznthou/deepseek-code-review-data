<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將專案層級與 Client/ClientTests target 的 Swift 版本從 5.0 升級至 6.0，並為多個閉包與 delegate 方法加上 @MainActor、@Sendable 標註以符合 Swift 6 的嚴格並發檢查。主要風險在於 LaunchCoordinator 中 onActionTap 閉包改用 Task 包裝，可能造成執行順序與完成回呼的時序改變；此外，部分閉包標註不一致（如 BrowserWebUIDelegate 移除 @Sendable）可能導致編譯錯誤或並發安全漏洞。建議優先確認 Task 包裝的必要性與潛在的資料競爭，並統一閉包標註。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:130` | onActionTap 閉包改用 Task 包裝可能造成執行順序與完成回呼時序改變 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/WebEngineIntegration/BrowserWebUIDelegate.swift:42` | BrowserWebUIDelegate 中 runJavaScriptAlertPanelWithMessage 的 completionHandler 移除 @Sendable | 0.70 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:79` | handleJavaScriptAlert 的 spamCallback 參數標註 @MainActor @Sendable，但呼叫處未明確標註 | 0.60 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:112` | DownloadToast 的 completion 閉包標註 @MainActor，但未確認所有呼叫點是否在主執行緒 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:130</code> onActionTap 閉包改用 Task 包裝可能造成執行順序與完成回呼時序改變</summary>

原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為 `Task { ... }` 包裝。由於 Task 是異步執行，handleAction 內部的同步操作（如 completion(.success(.none))）可能延後執行，導致 UI 更新延遲。此外，若 handleAction 內部有依賴 MainActor 的狀態，Task 預設會繼承當前 actor context，但若閉包本身非 @MainActor，可能造成資料競爭。建議確認 handleAction 是否為 @MainActor，並考慮使用 `Task { @MainActor in ... }` 明確標註。

**判斷依據**：diff 中 onActionTap 閉包從直接呼叫改為 Task 包裝，且 handleAction 的 completion 參數型別改為 @Sendable @escaping @MainActor，但 Task 本身未標註 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/WebEngineIntegration/BrowserWebUIDelegate.swift:42</code> BrowserWebUIDelegate 中 runJavaScriptAlertPanelWithMessage 的 completionHandler 移除 @Sendable 可能導致編譯錯誤</summary>

WKUIDelegate 的 runJavaScriptAlertPanelWithMessage 方法要求 completionHandler 為 @escaping @MainActor @Sendable () -> Void，但此處將 @Sendable 移除，可能導致 Swift 6 編譯錯誤。建議確認 WKUIDelegate 的實際簽名，並保留 @Sendable。

**判斷依據**：diff 中該行從 `@escaping @MainActor @Sendable () -> Void` 改為 `@escaping @MainActor () -> Void`，與其他 delegate 方法（如 runJavaScriptConfirmPanelWithMessage）不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:79</code> handleJavaScriptAlert 的 spamCallback 參數標註 @MainActor @Sendable，但呼叫處未明確標註</summary>

handleJavaScriptAlert 的 spamCallback 參數型別改為 @escaping @MainActor @Sendable () -> Void，但呼叫 handleSpammedJSAlert 時傳入的 closure 未明確標註 @MainActor，可能導致編譯警告或錯誤。建議確認所有呼叫點是否正確。

**判斷依據**：diff 中 handleJavaScriptAlert 的參數型別變更，但未看到呼叫處的相應調整。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:112</code> DownloadToast 的 completion 閉包標註 @MainActor，但未確認所有呼叫點是否在主執行緒</summary>

DownloadToast 的 init 中 completion 參數改為 @MainActor @escaping (Bool) -> Void，但 buttonPressed 方法中呼叫 completionHandler 時未明確在主執行緒，可能導致執行緒安全問題。建議確認所有呼叫點是否在主執行緒，或使用 DispatchQueue.main.async 包裝。

**判斷依據**：diff 中 init 的 completion 參數型別變更，但 buttonPressed 方法中呼叫 completionHandler 的程式碼未變更。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 33731 (cache hit 33664) ｜ completion tokens 1222 ｜ PR #3</sub>