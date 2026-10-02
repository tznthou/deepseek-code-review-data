<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 XCUITest 測試：移除已停用的 testWhatsNewPage、在貼上流程處理系統「允許貼上」提示、調整 iPad 的跳過邏輯與分享選單的點擊方式。整體風險低，但 tearDown 的提前 return 可能導致 app.terminate() 與 super.tearDown() 未執行，造成測試狀態殘留；此外 verifyBookmarksShareNormalWebsiteReminders 改名後不再是 test 前綴，可能導致該測試不再被 XCTest 執行。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29` | tearDown 提前 return 可能略過清理與父類別 tearDown | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47` | 測試方法改名後失去 test 前綴，可能不再被 XCTest 執行 | 0.75 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471` | 貼上後處理系統提示的時機可能不穩定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29</code> tearDown 提前 return 可能略過清理與父類別 tearDown</summary>

在 `tearDown()` 中，當 `self.name.contains("testSelectBottomPlacement") || iPad()` 成立時直接 `return`，導致後續的 `app.terminate()` 與 `try await super.tearDown()` 不會被執行。這可能造成測試狀態殘留，影響後續測試的獨立性。建議改為使用 `if` 條件包住 `switchThemeToDarkOrLight`，而不是提前 return，確保清理邏輯總會執行。

**判斷依據**：diff 中新增的 `return` 位於 `app.terminate()` 與 `super.tearDown()` 之前，若條件成立則會跳過這些必要的清理步驟。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47</code> 測試方法改名後失去 test 前綴，可能不再被 XCTest 執行</summary>

方法 `testBookmarksShareNormalWebsiteReminders` 被改名為 `verifyBookmarksShareNormalWebsiteReminders`，但 XCTest 只會自動執行以 `test` 開頭的方法。若沒有其他機制（例如手動呼叫或使用 `XCTestCase` 的 `testInvocations` 覆寫），此測試將不再被執行，等同於被停用。建議保留 `test` 前綴，或確認此方法是否由其他測試輔助呼叫。

**判斷依據**：diff 中將原本的 `func testBookmarksShareNormalWebsiteReminders()` 改為 `func verifyBookmarksShareNormalWebsiteReminders()`，且未見其他呼叫點。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471</code> 貼上後處理系統提示的時機可能不穩定</summary>

新增 `springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)` 來處理 iOS 的貼上權限提示。但此提示可能延遲出現，0.5 秒的等待時間可能不足，導致測試偶發失敗。建議增加等待時間或使用更可靠的等待機制（例如 `mozWaitForElementToExist`）。

**判斷依據**：該行使用固定 0.5 秒 timeout，而系統提示的出現時間可能因裝置狀態而異。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3993 (cache hit 3968) ｜ completion tokens 941 ｜ PR #13</sub>