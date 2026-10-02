<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 Swift 版本從 5.0 升級至 6.0，並在多個閉包與協定屬性上加入 @MainActor 與 @Sendable 標註，以符合 Swift 6 的嚴格並行檢查。主要風險在於 LaunchCoordinator 中將原本同步的 onActionTap 閉包改為包在 Task 內執行，可能造成執行順序與錯誤處理的改變；另外，部分閉包標註的變更可能影響呼叫端的型別推斷，需要確認所有使用點都已更新。整體而言，變更方向正確，但需謹慎驗證非同步行為的改變。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271` | 將 onActionTap 閉包內容包在 Task 中可能改變執行順序與錯誤處理 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:79` | spamCallback 參數新增 @Sendable 可能造成不必要的限制 | 0.60 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192` | 移除 UX.buttonSize 常數改為魔法數字 40 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271</code> 將 onActionTap 閉包內容包在 Task 中可能改變執行順序與錯誤處理</summary>

原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。這會使得 handleAction 的執行變成非同步，可能導致呼叫端預期的同步行為失效。例如，若 handleAction 內部有需要立即完成的狀態更新，或 completion 需要在特定時序被呼叫，延遲可能造成 UI 不一致。此外，Task 中未處理可能的錯誤（如 handleAction 拋錯），可能導致錯誤被吞掉。建議確認 handleAction 是否為非同步設計，或考慮使用 Task { @MainActor in ... } 並明確處理錯誤。

**判斷依據**：diff 中顯示原本直接呼叫的程式碼被包進 Task { } 區塊，且未見錯誤處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:79</code> spamCallback 參數新增 @Sendable 可能造成不必要的限制</summary>

spamCallback 被標註為 @Sendable，但此閉包僅在 MainActor 上使用，且未跨執行緒傳遞。加上 @Sendable 可能導致呼叫端必須傳入符合 Sendable 的閉包，增加不必要的限制。建議確認是否有跨執行緒需求，若無則移除 @Sendable。

**判斷依據**：diff 中將原本的 @escaping () -> Void 改為 @escaping @MainActor @Sendable () -> Void，但此閉包僅在 handleJavaScriptAlert 內部使用，未見跨執行緒傳遞。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192</code> 移除 UX.buttonSize 常數改為魔法數字 40</summary>

原本使用 UX.buttonSize 常數，現在直接寫死為 40。這降低了可讀性與可維護性，若未來需要調整按鈕大小，需修改多處。建議保留常數或使用有意義的名稱。

**判斷依據**：diff 中刪除了 struct UX 中的 buttonSize 常數，並將使用處改為直接寫 40。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8634 (cache hit 1536) ｜ completion tokens 920 ｜ PR #3</sub>