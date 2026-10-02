<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 XCUITest 測試：移除已停用的 testWhatsNewPage、修正 iPad 的 toolbar 測試跳過邏輯、處理貼上權限彈窗、以及將一個測試方法改名為 verify 開頭（可能使其不再被 XCTest 自動執行）。整體風險低，但需確認改名後的測試是否仍會被執行，以及 tearDown 的提前 return 是否會跳過必要的清理。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47` | 測試方法改名後可能不再被 XCTest 執行 | 0.90 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29` | tearDown 提前 return 可能跳過必要的清理 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47</code> 測試方法改名後可能不再被 XCTest 執行</summary>

將 `testBookmarksShareNormalWebsiteReminders` 改名為 `verifyBookmarksShareNormalWebsiteReminders`。XCTest 只會自動執行以 `test` 開頭的方法，因此改名後此測試將不會被包含在任何測試計劃中，等同於被停用。若此為刻意停用，建議直接刪除或使用 `XCTSkip`；否則應保留 `test` 前綴。

**判斷依據**：diff 中將 `func testBookmarksShareNormalWebsiteReminders()` 改為 `func verifyBookmarksShareNormalWebsiteReminders()`，且未見其他機制（如 `@Test` 或手動呼叫）使其仍被執行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29</code> tearDown 提前 return 可能跳過必要的清理</summary>

在 `tearDown` 中，若測試名稱包含 `testSelectBottomPlacement` 或裝置為 iPad，會直接 `return`，跳過 `switchThemeToDarkOrLight` 與 `app.terminate()`。若測試中途失敗，可能殘留應用程式狀態影響後續測試。建議將 `app.terminate()` 移至 `return` 之前，或使用 `defer` 確保清理必定執行。

**判斷依據**：diff 新增的 `return` 會跳過後續的 `app.terminate()` 與 `super.tearDown()` 呼叫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3957 (cache hit 3840) ｜ completion tokens 658 ｜ PR #13</sub>