<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將專案與測試 target 的 Swift 版本從 5.0 升級至 6.0，並為多個閉包加上 @MainActor 與 @Sendable 標註以符合 Swift 6 的嚴格並發檢查。主要風險在於大量閉包型別變更可能導致呼叫端未同步更新而編譯失敗，且部分標註（如 @Sendable）可能隱藏資料競爭或造成不必要的限制。建議先確認所有呼叫端已配合修改，並評估 @Sendable 的必要性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271` | onActionTap 閉包內使用 Task 可能造成執行順序不確定 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:79` | spamCallback 加上 @Sendable 可能限制閉包捕獲非 Sendable 值 | 0.60 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:112` | completion 閉包加上 @MainActor 可能造成呼叫端需調整 | 0.50 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/TabScrollController/TabProviderAdapter.swift:14` | onLoadingStateChanged 加上 @Sendable 可能限制賦值 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271</code> onActionTap 閉包內使用 Task 可能造成執行順序不確定</summary>

原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。這會讓 handleAction 的執行延後到非同步佇列，可能改變原本的同步執行順序。若 handleAction 內部有依賴呼叫順序的邏輯（例如更新 UI 或狀態），可能導致行為不一致。建議確認 handleAction 是否必須在原本的同步上下文中執行，或改用 MainActor.assumeIsolated 等方式保留同步性。

**判斷依據**：diff 中 onActionTap 閉包從直接呼叫改為包在 Task { } 內，且閉包本身已標註 @MainActor，但 Task 會在新的非結構化任務中執行，可能脫離原本的同步執行流。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:79</code> spamCallback 加上 @Sendable 可能限制閉包捕獲非 Sendable 值</summary>

spamCallback 參數新增 @Sendable 標註，但此閉包僅在 MainActor 上執行，且呼叫端可能捕獲非 Sendable 的物件（如 self）。若捕獲的物件未遵循 Sendable，編譯器會發出警告或錯誤，可能迫使呼叫端進行不必要的修改。建議確認此閉包是否真的需要跨 actor 傳遞，若無必要可移除 @Sendable。

**判斷依據**：diff 中 spamCallback 型別從 @escaping () -> Void 改為 @escaping @MainActor @Sendable () -> Void，但此閉包僅在 MainActor 上使用，@Sendable 可能過度限制。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:112</code> completion 閉包加上 @MainActor 可能造成呼叫端需調整</summary>

DownloadToast 的 init 中 completion 參數新增 @MainActor 標註，但此閉包可能從非 MainActor 的 context 呼叫。若呼叫端未在 MainActor 上，編譯器會要求使用 await 或標註，可能造成不必要的改動。建議確認所有呼叫端是否皆在 MainActor 上，或考慮使用 @escaping (Bool) -> Void 並在內部處理 actor 切換。

**判斷依據**：diff 中 completion 型別從 @escaping (Bool) -> Void 改為 @MainActor @escaping (Bool) -> Void，但未提供呼叫端上下文，可能導致編譯錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/TabScrollController/TabProviderAdapter.swift:14</code> onLoadingStateChanged 加上 @Sendable 可能限制賦值</summary>

onLoadingStateChanged 屬性型別新增 @Sendable，但此屬性可能被賦予捕獲非 Sendable 值的閉包。若賦值的閉包捕獲了非 Sendable 物件，編譯器會報錯，迫使呼叫端修改。建議確認此閉包是否真的需要跨 actor 傳遞，若無必要可移除 @Sendable。

**判斷依據**：diff 中 onLoadingStateChanged 型別從 (() -> Void)? 改為 (@MainActor @Sendable () -> Void)?，但未提供賦值端上下文。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8634 (cache hit 8576) ｜ completion tokens 1210 ｜ PR #3</sub>