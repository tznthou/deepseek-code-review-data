<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 XCUITest 測試：移除已停用的 testWhatsNewPage、將 testBookmarksShareNormalWebsiteReminders 改名為 verifyBookmarksShareNormalWebsiteReminders（可能使其不再被 XCTest 執行）、在 iPad 上跳過 testSelectBottomPlacement、調整 tearDown 的 theme 重置邏輯，並在貼上驗證中加入 Allow Paste 處理。主要風險在於測試方法改名可能導致測試不再被執行，以及 tearDown 中提前 return 可能跳過 app.terminate()，造成測試狀態污染。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47` | 測試方法改名可能導致測試不再被執行 | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29` | tearDown 中提前 return 可能跳過 app.terminate() | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471` | 使用 springboard 全域變數可能未初始化 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47</code> 測試方法改名可能導致測試不再被執行</summary>

將 `testBookmarksShareNormalWebsiteReminders` 改名為 `verifyBookmarksShareNormalWebsiteReminders`。XCTest 僅自動執行以 `test` 開頭的方法，改名後此方法將不再被視為測試案例，除非有明確的呼叫或設定。這會導致該測試涵蓋的功能失去自動化驗證。建議保留 `test` 前綴，或確認此方法已被其他測試呼叫。

**判斷依據**：diff 中將原本的 `func testBookmarksShareNormalWebsiteReminders()` 改為 `func verifyBookmarksShareNormalWebsiteReminders()`，且未見其他呼叫點。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29</code> tearDown 中提前 return 可能跳過 app.terminate()</summary>

在 `tearDown()` 中，若 `self.name.contains("testSelectBottomPlacement") || iPad()` 成立，會直接 `return`，導致後續的 `app.terminate()` 不會被執行。這可能使應用程式在測試結束後仍保持執行狀態，影響後續測試的隔離性。建議將 `app.terminate()` 移至條件判斷之前，或使用 `defer` 確保其總會被執行。

**判斷依據**：diff 中新增的條件區塊包含 `return`，而原本的 `app.terminate()` 位於該區塊之後。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471</code> 使用 springboard 全域變數可能未初始化</summary>

新增的 `springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)` 使用了 `springboard`，但此變數在 `BaseTestCase` 中未見定義或初始化。若它是一個全域變數，需確認其已正確設定；否則可能導致測試執行時崩潰。建議確認 `springboard` 的來源，或改用 `XCUIApplication(bundleIdentifier: "com.apple.springboard")`。

**判斷依據**：diff 中新增此行，但未見 `springboard` 的定義。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15416 (cache hit 15360) ｜ completion tokens 916 ｜ PR #13</sub>