<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 XCUITest 測試：移除已停用的 testWhatsNewPage、在 iPad 上跳過 testSelectBottomPlacement、修正貼上權限彈窗處理、將 testBookmarksShareNormalWebsiteReminders 改名為 verifyBookmarksShareNormalWebsiteReminders（可能導致測試不被執行），並改用 pressWithRetry 提升穩定性。主要風險在於測試方法改名後可能不再被 XCTest 執行，以及 tearDown 中提前 return 可能略過 app.terminate() 與 super.tearDown()，影響測試隔離。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47` | [R06] 測試方法改名後可能不再被 XCTest 執行 | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29` | tearDown 中提前 return 可能略過 app.terminate() 與 super.tearDown() | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471` | 新增的貼上權限處理可能不穩定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47</code> [R06] 測試方法改名後可能不再被 XCTest 執行</summary>

將 `testBookmarksShareNormalWebsiteReminders` 改名為 `verifyBookmarksShareNormalWebsiteReminders`，但 XCTest 只會自動執行以 `test` 開頭的方法。此方法將不再被視為測試案例，導致測試覆蓋率下降。建議改回 `test` 前綴，或確認是否有其他機制（如測試計劃）會呼叫此方法。

**判斷依據**：diff 中將 `func testBookmarksShareNormalWebsiteReminders()` 改為 `func verifyBookmarksShareNormalWebsiteReminders()`，且未見其他呼叫點。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29</code> tearDown 中提前 return 可能略過 app.terminate() 與 super.tearDown()</summary>

在 `tearDown()` 中，當條件成立時直接 `return`，導致 `app.terminate()` 和 `try await super.tearDown()` 不會被執行。這可能造成測試狀態殘留，影響後續測試的隔離性。建議改為使用 `if` 條件包住主題切換，但保留後續清理步驟，或使用 `defer` 確保清理必定執行。

**判斷依據**：diff 中新增的 `return` 位於 `tearDown()` 內，且其後仍有 `app.terminate()` 與 `try await super.tearDown()`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471</code> 新增的貼上權限處理可能不穩定</summary>

新增 `springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)` 來處理貼上權限彈窗。但此彈窗可能在不同 iOS 版本或地區有不同的按鈕文字，且 0.5 秒的等待時間可能不足以讓彈窗出現。建議確認此處理是否涵蓋所有測試情境，或考慮使用更穩健的等待機制。

**判斷依據**：diff 中新增此行，且無條件判斷或版本檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6052 (cache hit 1536) ｜ completion tokens 906 ｜ PR #13</sub>