<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 UI 測試：移除已停用的 testWhatsNewPage、在貼上流程中處理系統「允許貼上」提示、調整 OnboardingTests 的 tearDown 與 iPad 跳過邏輯，並將 ShareLongPressTests 中的一個測試方法改名（使其不再被 XCTest 自動執行）。整體風險低，但需注意：改名後的 verifyBookmarksShareNormalWebsiteReminders 不再以 test 開頭，將不會被 XCTest 執行，可能導致測試覆蓋率下降；另外 tearDown 中直接 return 可能略過後續清理，但影響有限。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47` | [R06] 測試方法改名後不再以 test 開頭，將不會被 XCTest 執行 | 0.90 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29` | tearDown 中直接 return 可能略過後續清理 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47</code> [R06] 測試方法改名後不再以 test 開頭，將不會被 XCTest 執行</summary>

原方法 `testBookmarksShareNormalWebsiteReminders` 改名為 `verifyBookmarksShareNormalWebsiteReminders`，但 XCTest 僅自動執行以 `test` 開頭的方法。此改名會導致該測試不再被執行，等同於刪除測試。若此為刻意停用，應使用 `XCTSkip` 或註解，而非改名；否則應保留 `test` 前綴。

**判斷依據**：diff 中將 `func testBookmarksShareNormalWebsiteReminders()` 改為 `func verifyBookmarksShareNormalWebsiteReminders()`，且未見其他機制（如手動呼叫）來執行此方法。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29</code> tearDown 中直接 return 可能略過後續清理</summary>

在 `tearDown()` 中，若 `self.name.contains("testSelectBottomPlacement") || iPad()` 為真，則直接 `return`，跳過 `app.terminate()` 與 `super.tearDown()`。這可能導致應用程式未終止或 XCTest 清理未執行，影響後續測試的獨立性。建議改為條件式執行主題切換，但仍執行必要的清理。

**判斷依據**：diff 顯示在 tearDown 中新增了提前 return 的分支，且 return 位於 app.terminate() 與 super.tearDown() 之前。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6062 (cache hit 3968) ｜ completion tokens 704 ｜ PR #13</sub>