<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 UI 測試：移除已停用的 testWhatsNewPage、在貼上流程中處理 iOS 的「允許貼上」系統提示、調整 OnboardingTests 的 tearDown 與 iPad 跳過邏輯，並將 ShareLongPressTests 中的一個測試方法改名（可能使其不再被 XCTest 執行）。整體風險中等，最需要注意的是方法改名可能導致測試不再被執行，以及 tearDown 中提前 return 可能跳過 super.tearDown() 的清理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47` | [R06] 測試方法改名後不再以 test 開頭，可能導致測試不被執行 | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29` | tearDown 中提前 return 可能跳過 super.tearDown() 的清理 | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471` | tapIfExists 可能隱藏貼上權限提示未出現的問題 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47</code> [R06] 測試方法改名後不再以 test 開頭，可能導致測試不被執行</summary>

將 `testBookmarksShareNormalWebsiteReminders` 改名為 `verifyBookmarksShareNormalWebsiteReminders`，違反 XCTest 的命名慣例（測試方法必須以 `test` 開頭）。這會導致該方法不再被 XCTest 自動執行，測試涵蓋率下降。建議保留 `test` 前綴，或使用 `@Test` 屬性（若專案採用 Swift Testing）。

**判斷依據**：diff 中 `-    func testBookmarksShareNormalWebsiteReminders() {` 改為 `+    func verifyBookmarksShareNormalWebsiteReminders() {`

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29</code> tearDown 中提前 return 可能跳過 super.tearDown() 的清理</summary>

在 `tearDown()` 中，當條件成立時直接 `return`，這會跳過後續的 `app.terminate()` 和 `try await super.tearDown()`。若 `super.tearDown()` 包含必要的清理（如釋放資源、重置狀態），可能導致測試污染或資源洩漏。建議改用 `if` 包住主題切換邏輯，而不是提前 return，確保清理程式碼總會執行。

**判斷依據**：diff 中新增的 `return` 位於 `tearDown()` 內，且後續仍有 `app.terminate()` 與 `try await super.tearDown()`

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471</code> tapIfExists 可能隱藏貼上權限提示未出現的問題</summary>

新增 `springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)` 用於處理系統貼上權限提示。若提示未在 0.5 秒內出現，測試仍會繼續，可能導致後續步驟失敗，但錯誤訊息可能不明確。建議考慮使用更明確的等待與斷言，或增加日誌以利除錯。

**判斷依據**：diff 中新增該行，且 `tapIfExists` 通常用於可選元素，若元素未出現不會失敗

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6004 (cache hit 5888) ｜ completion tokens 918 ｜ PR #13</sub>