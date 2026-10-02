<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 XCUITest 測試：移除已停用的 testWhatsNewPage、修正 iPad 的 toolbar 測試跳過邏輯、處理貼上權限彈窗、並將一個測試方法改名為 verify 開頭（可能使其不再被 XCTest 自動執行）。整體風險低，但需確認改名是否為刻意為之，以及 tearDown 的提前 return 是否會跳過必要的清理。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47` | 測試方法改名後可能不再被 XCTest 執行 | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29` | tearDown 提前 return 可能跳過 super.tearDown() | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47</code> 測試方法改名後可能不再被 XCTest 執行</summary>

將 `testBookmarksShareNormalWebsiteReminders` 改名為 `verifyBookmarksShareNormalWebsiteReminders`。XCTest 只會自動執行以 `test` 開頭的方法，因此改名後此測試將不再被包含在測試套件中，除非有另外透過 `testInvocations` 或 `allTests` 手動註冊。若此測試仍應執行，請保留 `test` 前綴；若刻意停用，建議改用 `XCTSkip` 或註解說明原因。

**判斷依據**：diff 中將 `func testBookmarksShareNormalWebsiteReminders()` 改為 `func verifyBookmarksShareNormalWebsiteReminders()`，且未見其他註冊機制。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29</code> tearDown 提前 return 可能跳過 super.tearDown()</summary>

在 `tearDown()` 中，當條件成立時直接 `return`，這會跳過後續的 `app.terminate()` 和 `super.tearDown()`。若 `super.tearDown()` 包含必要的清理（如釋放資源、重設狀態），可能導致測試環境污染。建議改為 `if`/`else` 結構，確保 `super.tearDown()` 總是被呼叫。

**判斷依據**：diff 顯示在 `tearDown()` 中新增了提前 `return` 的邏輯，且 `app.terminate()` 和 `super.tearDown()` 位於其後。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3993 (cache hit 3968) ｜ completion tokens 677 ｜ PR #13</sub>