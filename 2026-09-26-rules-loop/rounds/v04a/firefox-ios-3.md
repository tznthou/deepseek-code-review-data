<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將專案與 Client/ClientTests target 的 Swift 版本從 5.0 升級至 6.0，並為多個閉包加上 @MainActor 與 @Sendable 標註以符合 Swift 6 的嚴格並行檢查。主要風險在於 LaunchCoordinator 中將原本同步的 onActionTap 閉包改為包在 Task 中執行，可能改變執行時序與錯誤處理；此外，部分閉包標註不一致（如 BrowserWebUIDelegate 移除了 @Sendable）可能導致編譯錯誤。整體方向正確，但需確認所有呼叫端已同步更新。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271` | 將 onActionTap 閉包內容包在 Task 中可能改變執行時序與錯誤處理 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/WebEngineIntegration/BrowserWebUIDelegate.swift:42` | 移除 @Sendable 可能導致與 WKUIDelegate 協定不一致 | 0.75 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192` | [R13] 魔法數字 40 應定義在 UX struct 中 | 0.90 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/TabScrollController/TabProviderAdapter.swift:14` | onLoadingStateChanged 型別變更可能影響所有實作與呼叫端 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271</code> 將 onActionTap 閉包內容包在 Task 中可能改變執行時序與錯誤處理</summary>

原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。這會使 handleAction 的執行延後到非同步佇列，可能導致呼叫端預期的同步行為失效。此外，若 handleAction 內部有錯誤拋出，原本可能由閉包捕獲，現在則可能遺失。建議確認 handleAction 是否為非同步設計，或改為使用 async/await 並保留錯誤傳遞。

**判斷依據**：diff 中新增 Task 包裹原本同步的 handleAction 呼叫，且未處理可能的錯誤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/WebEngineIntegration/BrowserWebUIDelegate.swift:42</code> 移除 @Sendable 可能導致與 WKUIDelegate 協定不一致</summary>

此處將 completionHandler 的型別從 `@escaping @MainActor @Sendable () -> Void` 改為 `@escaping @MainActor () -> Void`，移除了 @Sendable。但 WKUIDelegate 的協定方法要求該閉包為 @Sendable，這可能導致編譯錯誤或執行時問題。建議確認協定定義並保持一致。

**判斷依據**：diff 中移除了 @Sendable，而其他類似方法（如 BrowserViewController+WebViewDelegates.swift）仍保留 @Sendable。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192</code> [R13] 魔法數字 40 應定義在 UX struct 中</summary>

原本的 `UX.buttonSize` 被移除，改為直接使用數字 40。這違反了專案規範 R13（UI 常數應定義在巢狀 UX struct 中）。建議保留 UX struct 並使用 `UX.buttonSize`。

**判斷依據**：diff 中刪除了 `struct UX { static let buttonSize: CGFloat = 40 }`，並將使用處改為直接寫 40。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/TabScrollController/TabProviderAdapter.swift:14</code> onLoadingStateChanged 型別變更可能影響所有實作與呼叫端</summary>

將 `onLoadingStateChanged` 的型別從 `(() -> Void)?` 改為 `(@MainActor @Sendable () -> Void)?`，這會影響所有實作此協定的型別以及賦值給此屬性的程式碼。若呼叫端未使用 @MainActor 或 @Sendable 閉包，可能導致編譯錯誤。建議全面搜尋並更新相關程式碼。

**判斷依據**：diff 中協定與實作均修改了型別，但未顯示其他實作或呼叫端的更新。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9481 (cache hit 8576) ｜ completion tokens 1126 ｜ PR #3</sub>