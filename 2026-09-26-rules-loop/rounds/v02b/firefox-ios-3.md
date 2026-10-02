<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將專案 Swift 版本從 5.0 升級至 6.0，並在多個閉包型別上加入 @MainActor 與 @Sendable 標註以符合 Swift 6 的嚴格並行檢查。主要風險在於 LaunchCoordinator 中將原本同步的 onActionTap 閉包改為包在 Task 內執行，可能改變執行順序與時序；另外 DownloadToast 移除了 UX 常數結構，違反專案規範 R13。整體而言，升級方向正確，但需確認並行標註的完整性與行為變更的影響。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271` | onActionTap 閉包改為非同步執行可能改變行為 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192` | [R13] 魔法數字 40 應定義在 UX 結構中 | 0.90 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/BrowserViewController/WebEngineIntegration/BrowserWebUIDelegate.swift:42` | completionHandler 缺少 @Sendable 標註 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271</code> onActionTap 閉包改為非同步執行可能改變行為</summary>

原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在被包在 `Task { ... }` 中，導致 handleAction 的執行延後到下一次 run loop，且不再阻塞當前呼叫者。若呼叫端依賴同步完成（例如在閉包返回後立即讀取狀態），可能出現競態。建議確認 handleAction 是否為非同步設計，或改為在閉包內直接呼叫（若 handleAction 本身已為 @MainActor 且非同步）。

**判斷依據**：diff 中將原本的直接呼叫改為 Task 包覆，且未見任何 await 或明確的非同步需求。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192</code> [R13] 魔法數字 40 應定義在 UX 結構中</summary>

原本的 `UX.buttonSize` 常數被移除，改為直接使用數字 40。根據專案規範 R13，UI 常數應定義在巢狀 UX struct 中。建議保留 `struct UX { static let buttonSize: CGFloat = 40 }` 並使用 `UX.buttonSize`。

**判斷依據**：diff 中刪除了 `struct UX { static let buttonSize: CGFloat = 40 }`，並在約束中直接使用 40。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/WebEngineIntegration/BrowserWebUIDelegate.swift:42</code> completionHandler 缺少 @Sendable 標註</summary>

此處的 completionHandler 型別從 `@escaping @MainActor @Sendable () -> Void` 改為 `@escaping @MainActor () -> Void`，移除了 @Sendable。在 Swift 6 嚴格並行模式下，若此閉包可能跨隔離域傳遞，缺少 @Sendable 可能導致編譯錯誤或資料競爭。建議確認此閉包是否真的不需要 @Sendable，或保留原標註。

**判斷依據**：diff 中將原本的 `@escaping @MainActor @Sendable () -> Void` 改為 `@escaping @MainActor () -> Void`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10693 (cache hit 10624) ｜ completion tokens 912 ｜ PR #3</sub>