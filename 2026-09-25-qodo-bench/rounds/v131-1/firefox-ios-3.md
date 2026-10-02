<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將專案與多個 target 的 Swift 版本從 5.0 升級至 6.0，並為多個閉包參數加上 @MainActor 與 @Sendable 標註，以符合 Swift 6 的嚴格並行檢查。主要風險在於 LaunchCoordinator 中將原本同步的 onActionTap 閉包改為包在 Task 中執行，可能改變執行順序與時機，且未處理 Task 的取消與錯誤。另外，部分閉包標註的變更可能導致 API 不相容，需要確認所有呼叫端都已更新。整體而言，升級方向正確，但需謹慎處理非同步行為的改變。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:274` | 將同步閉包改為 Task 可能改變執行順序與時機 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/WebEngineIntegration/BrowserWebUIDelegate.swift:42` | 移除 @Sendable 可能導致並行檢查錯誤 | 0.70 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192` | 魔法數字取代常數降低可讀性 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:274</code> 將同步閉包改為 Task 可能改變執行順序與時機</summary>

原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。這會將原本同步的呼叫變成非同步，可能導致呼叫端預期完成後立即執行的程式碼延後執行，或與其他非同步操作產生競態。此外，Task 未處理取消或錯誤，若 handleAction 拋出錯誤，可能導致未處理的錯誤。建議確認此變更的必要性，並考慮使用 Task { @MainActor in ... } 確保在主執行緒執行，或保留同步呼叫並調整閉包標註。

**判斷依據**：diff 中 onActionTap 閉包內容從直接呼叫改為包在 Task 中，且未見任何錯誤處理或取消機制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/WebEngineIntegration/BrowserWebUIDelegate.swift:42</code> 移除 @Sendable 可能導致並行檢查錯誤</summary>

在 BrowserWebUIDelegate.swift 中，completionHandler 的型別從 `@escaping @MainActor @Sendable () -> Void` 改為 `@escaping @MainActor () -> Void`，移除了 @Sendable。若此閉包需要跨 actor 傳遞，移除 @Sendable 可能導致 Swift 6 的並行檢查錯誤。請確認此變更是否必要，並檢查所有呼叫端是否相容。

**判斷依據**：diff 中該行從原本的 @Sendable 移除，但其他類似 delegate 方法仍保留 @Sendable。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192</code> 魔法數字取代常數降低可讀性</summary>

原本使用 `UX.buttonSize` 常數，現在直接使用數字 40。雖然功能不變，但失去語意，未來修改時容易遺漏。建議保留常數或使用有意義的名稱。

**判斷依據**：diff 中刪除了 `struct UX { static let buttonSize: CGFloat = 40 }`，並將使用處改為直接寫 40。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8598 (cache hit 1408) ｜ completion tokens 914 ｜ PR #3</sub>