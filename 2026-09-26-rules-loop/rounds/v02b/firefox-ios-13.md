<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要調整 XCUITest 測試：移除已停用的 testWhatsNewPage、在 iPad 上跳過 testSelectBottomPlacement、調整 tearDown 的 theme 切換邏輯、在貼上操作後處理系統「允許貼上」提示，以及將 ShareLongPressTests 中的一個測試方法改名（但未加上 test 前綴，可能導致測試不被執行）。主要風險在於改名後的測試方法可能不再被 XCTest 執行，以及 tearDown 中提前 return 可能略過 app.terminate() 與 super.tearDown()，影響測試隔離。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47` | [R06] 測試方法缺少 'test' 前綴，將不會被 XCTest 執行 | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29` | tearDown 中提前 return 可能略過 app.terminate() 與 super.tearDown() | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:349` | XCTSkipIf 的使用方式可簡化 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47</code> [R06] 測試方法缺少 'test' 前綴，將不會被 XCTest 執行</summary>

方法 `verifyBookmarksShareNormalWebsiteReminders()` 被改名，但沒有以 `test` 開頭。XCTest 只會自動執行以 `test` 開頭的實例方法，因此這個測試將被靜默跳過，導致測試涵蓋率下降。建議改回 `testBookmarksShareNormalWebsiteReminders()` 或加上 `test` 前綴。

**判斷依據**：diff 中將 `func testBookmarksShareNormalWebsiteReminders()` 改為 `func verifyBookmarksShareNormalWebsiteReminders()`，違反 XCTest 命名慣例。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29</code> tearDown 中提前 return 可能略過 app.terminate() 與 super.tearDown()</summary>

在 `tearDown()` 中，當 `self.name.contains("testSelectBottomPlacement") || iPad()` 時直接 `return`，這會跳過後續的 `app.terminate()` 和 `try await super.tearDown()`。這可能導致應用程式未正確終止，影響後續測試的隔離性，甚至造成測試不穩定。建議改用 `if` 條件包住 theme 切換，而不是直接 return，確保清理邏輯總會執行。

**判斷依據**：diff 顯示在 tearDown 中新增了提前 return 的邏輯，且 return 位於 app.terminate() 之前。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:349</code> XCTSkipIf 的使用方式可簡化</summary>

程式碼使用 `let shouldSkipTest = true` 再傳入 `XCTSkipIf`，但可以直接寫 `try XCTSkipIf(iPad(), "Toolbar option not available for iPad")`，更為簡潔。此外，原本的 `guard !iPad() else { throw XCTSkip(...) }` 寫法也同樣有效，此改動並未帶來明顯好處。

**判斷依據**：diff 顯示新增了 `let shouldSkipTest = true` 並用於 XCTSkipIf，但條件本身即為布林值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6052 (cache hit 6016) ｜ completion tokens 961 ｜ PR #13</sub>