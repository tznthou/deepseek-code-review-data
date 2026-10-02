<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 UI 測試：移除已停用的 testWhatsNewPage、在貼上流程中處理系統貼上權限彈窗、調整 OnboardingTests 的 tearDown 與 iPad 跳過邏輯，以及將 ShareLongPressTests 中的測試方法改名為 verify 開頭（可能導致其不再被 XCTest 執行）。整體風險集中在測試方法改名可能使測試失效，以及 tearDown 中提前 return 可能跳過 super.tearDown() 的清理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47` | [R06] 測試方法改名為 verify 開頭將不再被 XCTest 執行 | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29` | tearDown 中提前 return 可能跳過 super.tearDown() 與 app.terminate() | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471` | 貼上權限彈窗處理可能不穩定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47</code> [R06] 測試方法改名為 verify 開頭將不再被 XCTest 執行</summary>

XCTest 只會將名稱以 `test` 開頭的方法視為測試案例。將 `testBookmarksShareNormalWebsiteReminders` 改名為 `verifyBookmarksShareNormalWebsiteReminders` 後，此方法將不再被 XCTest 自動執行，導致測試覆蓋率下降。建議保留 `test` 前綴，或使用 `XCTestCase` 的 `allTests` 手動註冊（不建議）。

**判斷依據**：diff 中將原本的 `func testBookmarksShareNormalWebsiteReminders()` 改為 `func verifyBookmarksShareNormalWebsiteReminders()`，違反 XCTest 命名慣例。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29</code> tearDown 中提前 return 可能跳過 super.tearDown() 與 app.terminate()</summary>

在 `tearDown()` 中，若 `self.name.contains("testSelectBottomPlacement") || iPad()` 成立，會直接 `return`，導致後續的 `app.terminate()` 與 `try await super.tearDown()` 不會被執行。這可能造成測試環境未正確清理，影響後續測試的獨立性。建議改為使用 `if` 條件包住主題切換，但不要提前 return，確保清理邏輯一定執行。

**判斷依據**：diff 顯示在 tearDown 中新增了提前 return 的分支，且 return 位於 app.terminate() 與 super.tearDown() 之前。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471</code> 貼上權限彈窗處理可能不穩定</summary>

新增的 `springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)` 依賴系統彈窗的出現時機與按鈕標題。若系統語言非英文或彈窗延遲超過 0.5 秒，可能無法正確點擊，導致測試不穩定。建議增加等待時間或使用更穩定的定位方式。

**判斷依據**：diff 中新增此行，使用固定 timeout 0.5 秒且依賴英文按鈕標題。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6042 (cache hit 3968) ｜ completion tokens 924 ｜ PR #13</sub>