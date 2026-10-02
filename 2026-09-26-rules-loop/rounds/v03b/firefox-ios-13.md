<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 UI 測試：移除已停用的 testWhatsNewPage、在貼上流程中處理 iOS 的「允許貼上」系統提示、調整 OnboardingTests 的 tearDown 與 iPad 跳過邏輯，並將 ShareLongPressTests 中的一個測試方法改名（移除 test 前綴）。整體風險低，但有一個可能導致測試無法被 XCTest 發現的問題，以及一個潛在的測試不穩定點。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47` | [R06] 測試方法缺少 test 前綴，將不會被 XCTest 執行 | 0.90 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471` | 貼上權限提示處理可能不穩定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47</code> [R06] 測試方法缺少 test 前綴，將不會被 XCTest 執行</summary>

方法 `verifyBookmarksShareNormalWebsiteReminders()` 原本名為 `testBookmarksShareNormalWebsiteReminders()`，改名後缺少 `test` 前綴。XCTest 只會自動發現並執行以 `test` 開頭的方法，因此這個測試將被靜默跳過，導致測試涵蓋率下降。建議恢復 `test` 前綴，或若有意排除此測試，應使用 `XCTSkip` 或從測試計劃中移除。

**判斷依據**：diff 中將 `func testBookmarksShareNormalWebsiteReminders()` 改為 `func verifyBookmarksShareNormalWebsiteReminders()`，違反 XCTest 命名慣例。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471</code> 貼上權限提示處理可能不穩定</summary>

新增的 `springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)` 使用固定 0.5 秒等待系統提示出現。在慢速 CI 或裝置上，提示可能延遲出現，導致 tapIfExists 找不到按鈕而略過，後續 `mozWaitForValueContains` 可能因未允許貼上而失敗。建議改用較長的等待時間，或使用 `waitForExistence` 搭配條件點擊。

**判斷依據**：新增行使用 0.5 秒 timeout，系統提示出現時間可能超過此值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6062 (cache hit 6016) ｜ completion tokens 629 ｜ PR #13</sub>