<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將專案層級與 Client/ClientTest targets 的 Swift 版本從 5.0 升級至 6.0，並為多個閉包與方法加上 @MainActor 與 @Sendable 標註以符合 Swift 6 的嚴格並行檢查。主要風險在於 LaunchCoordinator 中將原本同步的 onActionTap 閉包改為包在 Task 中執行，可能改變執行順序與錯誤處理；另外 DownloadToast 將原本的 UX.buttonSize 常數改為魔法數字 40，違反專案規範 R13。整體而言，大部分變更為必要的並行標註，但需確認 Task 包裝的影響與修正魔法數字。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271` | onActionTap 閉包改為 Task 包裝可能改變執行順序與錯誤處理 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192` | [R13] 魔法數字 40 取代 UX.buttonSize 常數 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271</code> onActionTap 閉包改為 Task 包裝可能改變執行順序與錯誤處理</summary>

原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。這會使 handleAction 的執行變成非同步，可能導致呼叫端預期的同步行為改變（例如 completion 的呼叫時機、錯誤處理的順序）。此外，Task 未指定優先權或取消處理，若 self 在 Task 執行前被釋放，guard let 會失敗並直接 return，但 completion 不會被呼叫，可能造成呼叫端永遠等待。建議確認 handleAction 是否為非同步設計，或考慮使用 Task { @MainActor in ... } 並確保 completion 在所有路徑都被呼叫。

**判斷依據**：diff 中 onActionTap 閉包從直接呼叫改為 Task 包裝，且未處理 self 為 nil 時 completion 的呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192</code> [R13] 魔法數字 40 取代 UX.buttonSize 常數</summary>

原本使用 UX.buttonSize 常數來設定 closeButton 的寬高，現在改為直接使用魔法數字 40。這違反了專案規範 R13（UI 常數應定義在巢狀 UX struct 中）。建議保留 UX struct 並使用 UX.buttonSize，或將 40 定義為具名常數。

**判斷依據**：diff 中刪除了 UX struct 中的 buttonSize 定義，並在約束中使用 40。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10645 (cache hit 8576) ｜ completion tokens 728 ｜ PR #3</sub>