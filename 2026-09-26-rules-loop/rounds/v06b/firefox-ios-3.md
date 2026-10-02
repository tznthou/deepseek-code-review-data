<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將專案與測試 target 的 Swift 版本從 5.0 升級至 6.0，並為多個閉包與方法加上 @MainActor 與 @Sendable 標註，以符合 Swift 6 的嚴格並行檢查。主要風險在於 LaunchCoordinator 中將原本同步的 onboardingService.handleAction 呼叫包進 Task 後，completion 的執行時機與執行緒可能改變，且未處理錯誤；此外，DownloadToast 中將 UX.buttonSize 常數改為魔法數字 40，違反專案規範 R13。整體而言，變更方向正確，但需確認並行標註的一致性與錯誤處理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271` | 將 handleAction 包進 Task 可能導致 completion 在非預期執行緒執行或延遲 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192` | [R13] 魔法數字 40 應定義在 UX struct 中 | 0.90 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/BrowserViewController/WebEngineIntegration/BrowserWebUIDelegate.swift:42` | 移除 @Sendable 可能導致 Swift 6 並行檢查警告 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271</code> 將 handleAction 包進 Task 可能導致 completion 在非預期執行緒執行或延遲</summary>

原本 onActionTap 閉包標註為 @MainActor，且直接呼叫 onboardingService.handleAction，其 completion 應在主執行緒同步或非同步回呼。現在改為在 Task 中呼叫，但 Task 的執行環境取決於啟動時的 actor context。若此閉包本身在主執行緒被呼叫，Task 會繼承主執行緒 actor，但若 handleAction 內部有非同步操作，completion 可能仍在主執行緒；然而，若 Task 在非主執行緒啟動，completion 將在背景執行緒執行，可能導致 UI 更新問題。此外，completion 的呼叫時機可能延遲，影響使用者體驗。建議確認 handleAction 的實作與 completion 的執行緒需求，或明確指定 Task 的 actor（如 Task { @MainActor in ... }）。

**判斷依據**：diff 中 onActionTap 閉包從原本直接呼叫改為包在 Task 中，且閉包本身不再標註 @MainActor（但外部參數類型已改為 @MainActor）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192</code> [R13] 魔法數字 40 應定義在 UX struct 中</summary>

原本的 UX.buttonSize 常數被移除，改為直接使用數字 40。這違反了專案規範 R13（UI 常數應定義在巢狀 UX struct 中），且降低可讀性與可維護性。建議保留 UX struct 並定義 static let buttonSize: CGFloat = 40，然後使用 UX.buttonSize。

**判斷依據**：diff 中刪除了 struct UX 及其 buttonSize 屬性，並在約束中直接使用 40。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/WebEngineIntegration/BrowserWebUIDelegate.swift:42</code> 移除 @Sendable 可能導致 Swift 6 並行檢查警告</summary>

在 BrowserWebUIDelegate.swift 中，completionHandler 的型別從 `@escaping @MainActor @Sendable () -> Void` 改為 `@escaping @MainActor () -> Void`，移除了 @Sendable。若此方法實作 WKUIDelegate 協定，而協定要求 @Sendable，則可能導致編譯錯誤或警告。建議確認協定定義，若需要 @Sendable 則保留。

**判斷依據**：diff 中該行從原本的 @MainActor @Sendable 改為只有 @MainActor。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10683 (cache hit 10624) ｜ completion tokens 1021 ｜ PR #3</sub>