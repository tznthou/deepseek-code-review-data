<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 UI 測試：移除已停用的 testWhatsNewPage 測試、在貼上操作後處理系統「允許貼上」提示、調整 OnboardingTests 的 tearDown 與 iPad 跳過邏輯，並將 ShareLongPressTests 中的一個測試方法改名（移除 test 前綴）。整體風險低，但改名可能導致測試不再被 XCTest 執行，且 tearDown 的提前 return 可能跳過 app.terminate() 與 super.tearDown()，造成測試狀態污染。建議修正這兩個問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47` | [R06] 測試方法改名後不再以 test 開頭，將不會被 XCTest 執行 | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29` | tearDown 中提前 return 可能跳過 app.terminate() 與 super.tearDown() | 0.85 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471` | 貼上後處理系統提示的 tapIfExists 可能不夠穩健 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47</code> [R06] 測試方法改名後不再以 test 開頭，將不會被 XCTest 執行</summary>

方法 `testBookmarksShareNormalWebsiteReminders` 被改名為 `verifyBookmarksShareNormalWebsiteReminders`，失去 `test` 前綴。XCTest 只會自動執行以 `test` 開頭的方法，因此此測試將不再被執行，等同於被停用。若此為刻意停用，應使用 `XCTSkip` 或直接刪除；否則應保留 `test` 前綴。

**判斷依據**：diff 中將 `func testBookmarksShareNormalWebsiteReminders()` 改為 `func verifyBookmarksShareNormalWebsiteReminders()`，違反 XCTest 命名慣例。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29</code> tearDown 中提前 return 可能跳過 app.terminate() 與 super.tearDown()</summary>

在 `tearDown()` 中，若 `self.name.contains("testSelectBottomPlacement") || iPad()` 為真，會直接 `return`，導致後續的 `app.terminate()` 與 `try await super.tearDown()` 不會被執行。這可能造成應用程式未正確終止、測試狀態殘留，影響後續測試的可靠性。建議改為條件式執行主題切換，但保留清理邏輯。

**判斷依據**：diff 新增的 `return` 位於 `app.terminate()` 與 `super.tearDown()` 之前，會跳過這些必要的清理步驟。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471</code> 貼上後處理系統提示的 tapIfExists 可能不夠穩健</summary>

新增 `springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)` 來處理系統貼上權限提示。但此提示可能在不同 iOS 版本或地區有不同的文字（例如「允許貼上」），且 0.5 秒的等待可能不足以讓提示出現。建議使用更通用的定位方式（如 predicate 匹配按鈕類型）或增加等待時間，並考慮僅在提示存在時才點擊。

**判斷依據**：該行使用硬編碼的按鈕標題與短暫 timeout，可能因本地化或延遲而失敗。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6004 (cache hit 3968) ｜ completion tokens 957 ｜ PR #13</sub>