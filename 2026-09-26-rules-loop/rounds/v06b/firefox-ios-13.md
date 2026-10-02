<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 UI 測試：移除已停用的 testWhatsNewPage、在貼上流程中處理系統貼上權限提示、調整 OnboardingTests 的 tearDown 與 iPad 跳過邏輯，並將 ShareLongPressTests 中的一個測試方法改名（使其不再被 XCTest 自動執行）。整體風險低，但需注意：改名後的 verifyBookmarksShareNormalWebsiteReminders 不再作為測試執行，可能導致測試涵蓋率下降；tearDown 中的提前 return 可能跳過 super.tearDown() 的清理；新增的 tapIfExists 呼叫若元素不存在可能造成測試不穩定。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47` | 測試方法改名導致不再被 XCTest 執行 | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29` | tearDown 中提前 return 可能跳過 super.tearDown() | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471` | tapIfExists 可能隱藏貼上權限提示未出現的問題 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47</code> 測試方法改名導致不再被 XCTest 執行</summary>

將 `testBookmarksShareNormalWebsiteReminders` 改名為 `verifyBookmarksShareNormalWebsiteReminders` 後，XCTest 不再將此方法視為測試案例（因為缺少 `test` 前綴），因此該測試將不會被執行。這可能導致測試涵蓋率下降，且若原本依賴此測試驗證功能，可能遺漏回歸。建議若需保留測試，應維持 `test` 前綴，或改用其他機制（如 `XCTestCase` 的 `invocation` 或 `testInvocations`）來控制執行。

**判斷依據**：diff 中將原本的 `func testBookmarksShareNormalWebsiteReminders()` 改為 `func verifyBookmarksShareNormalWebsiteReminders()`，違反 XCTest 命名慣例（R06）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29</code> tearDown 中提前 return 可能跳過 super.tearDown()</summary>

在 `tearDown()` 中，若 `self.name.contains("testSelectBottomPlacement") || iPad()` 為真，會直接 `return`，導致後續的 `app.terminate()` 和 `try await super.tearDown()` 不會被執行。這可能造成測試狀態未清理，影響後續測試的獨立性。建議改為使用 `if` 條件包住主題切換，但保留 `app.terminate()` 和 `super.tearDown()` 的呼叫。

**判斷依據**：diff 顯示新增的 `return` 位於 `tearDown()` 中，且後續仍有 `app.terminate()` 和 `try await super.tearDown()`，提前返回會跳過這些清理步驟。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471</code> tapIfExists 可能隱藏貼上權限提示未出現的問題</summary>

新增的 `springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)` 會在按鈕存在時點擊，但若按鈕未出現（例如系統未顯示提示），測試仍會繼續，可能導致後續步驟失敗或測試不穩定。建議確認此提示是否必定出現，或增加等待與斷言，以確保測試意圖明確。

**判斷依據**：diff 中新增此行，使用 `tapIfExists` 而非 `waitAndTap`，可能忽略提示未出現的情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6042 (cache hit 6016) ｜ completion tokens 1006 ｜ PR #13</sub>