<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將專案與多個 target 的 Swift 版本從 5.0 升級至 6.0，並為大量閉包加上 @MainActor 與 @Sendable 標註以符合 Swift 6 的嚴格並行檢查。主要風險在於：1) 將 SWIFT_VERSION 設為 6.0 會啟用完整並行檢查，可能導致其他未修改的程式碼出現大量編譯錯誤；2) 部分閉包標註的變更可能改變執行緒行為（例如 LaunchCoordinator 中將原本同步的 onActionTap 包進 Task，可能造成競態或順序問題）；3) 移除 DownloadToast 中的 UX struct 違反專案規範 R13。建議先確認 CI 是否通過，並仔細檢視所有 @MainActor 標註的正確性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271` | 將 onActionTap 閉包內容包進 Task 可能造成執行緒與順序問題 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client.xcodeproj/project.pbxproj:27951` | 將 SWIFT_VERSION 設為 6.0 可能導致大量編譯錯誤 | 0.70 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192` | [R13] 移除 UX struct 並使用魔法數字 40 | 0.90 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/BrowserViewController/WebEngineIntegration/BrowserWebUIDelegate.swift:42` | 移除 @Sendable 可能導致並行檢查警告 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271</code> 將 onActionTap 閉包內容包進 Task 可能造成執行緒與順序問題</summary>

原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。由於 Task 預設會繼承當前 actor 的隔離（此處為 @MainActor），因此 handleAction 仍會在主執行緒執行，但執行時機變成非同步。若呼叫端預期閉包執行完畢後某些狀態已更新，可能會出現競態。此外，completion 閉包現在可能在 Task 完成後才被呼叫，若呼叫端未預期非同步行為，可能導致 UI 更新延遲或順序錯誤。建議確認 handleAction 是否為非同步設計，或考慮直接將 onActionTap 標註為 @MainActor 並保持同步呼叫。

**判斷依據**：diff 中 LaunchCoordinator.swift 的 onActionTap 閉包從直接呼叫改為包在 Task 中，且閉包本身未標註 @MainActor，但外部參數已標註 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client.xcodeproj/project.pbxproj:27951</code> 將 SWIFT_VERSION 設為 6.0 可能導致大量編譯錯誤</summary>

將專案層級的 SWIFT_VERSION 從 5.0 改為 6.0 會啟用 Swift 6 的完整並行檢查。雖然此 PR 修改了部分程式碼以符合要求，但可能仍有其他未修改的程式碼會因嚴格並行檢查而無法編譯。建議先在 CI 中驗證所有 target 都能成功編譯，或考慮先使用 Swift 5 模式搭配 upcoming features 逐步遷移。

**判斷依據**：diff 中多處將 SWIFT_VERSION 從 5.0 改為 6.0，且未提供完整的編譯驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192</code> [R13] 移除 UX struct 並使用魔法數字 40</summary>

原本的 UX struct 定義了 buttonSize 常數，現在被移除，並在約束中直接使用數字 40。這違反了專案規範 R13（UI 常數應定義在巢狀 UX struct 中）。建議保留 UX struct 並使用 UX.buttonSize。

**判斷依據**：diff 中刪除了 struct UX { static let buttonSize: CGFloat = 40 }，並在約束中直接使用 40。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/WebEngineIntegration/BrowserWebUIDelegate.swift:42</code> 移除 @Sendable 可能導致並行檢查警告</summary>

在 BrowserWebUIDelegate.swift 中，completionHandler 的型別從 @escaping @MainActor @Sendable () -> Void 改為 @escaping @MainActor () -> Void，移除了 @Sendable。這可能導致在 Swift 6 模式下出現並行檢查警告或錯誤，因為 WKUIDelegate 的方法要求 completionHandler 為 @Sendable。建議確認此變更是否必要，或保留 @Sendable。

**判斷依據**：diff 中 BrowserWebUIDelegate.swift 的 runJavaScriptAlertPanelWithMessage 方法簽名移除了 @Sendable。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10703 (cache hit 10624) ｜ completion tokens 1263 ｜ PR #3</sub>