<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 UI 測試：移除已停用的 testWhatsNewPage、在貼上流程中處理 iOS 的「允許貼上」系統提示、調整 OnboardingTests 的 tearDown 與 iPad 跳過邏輯，並將 ShareLongPressTests 中的一個測試方法改名為 verify 開頭。整體風險偏低，但 tearDown 的提前 return 可能導致 app.terminate() 與 super.tearDown() 未被執行，造成測試狀態殘留；此外，verify 開頭的方法可能不會被 XCTest 自動執行，需確認是否有其他呼叫點。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29` | tearDown 提前 return 可能略過清理步驟 | 0.85 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47` | 測試方法改名為 verify 開頭可能導致不被 XCTest 執行 | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471` | 貼上後處理系統提示的時機可能不穩定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29</code> tearDown 提前 return 可能略過清理步驟</summary>

在 `tearDown()` 中，當條件成立時直接 `return`，導致後續的 `app.terminate()` 和 `super.tearDown()` 不會被執行。這可能造成測試狀態殘留，影響後續測試的可靠性。建議改為使用 `if` 條件包住主題切換，但不要提前 return，確保清理步驟總會執行。

**判斷依據**：diff 中新增的 `return` 位於 `app.terminate()` 之前，若條件成立則跳過後續清理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47</code> 測試方法改名為 verify 開頭可能導致不被 XCTest 執行</summary>

將 `testBookmarksShareNormalWebsiteReminders` 改名為 `verifyBookmarksShareNormalWebsiteReminders`。XCTest 預設只會執行以 `test` 開頭的方法，因此這個方法可能不再被當作測試執行。若這是刻意為之（例如改為輔助方法），請確認沒有其他測試呼叫它；否則應保留 `test` 前綴。

**判斷依據**：diff 中方法名稱從 `testBookmarksShareNormalWebsiteReminders` 改為 `verifyBookmarksShareNormalWebsiteReminders`，違反 XCTest 命名慣例。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471</code> 貼上後處理系統提示的時機可能不穩定</summary>

新增 `springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)` 來處理 iOS 的貼上權限提示。但此提示可能延遲出現，0.5 秒的等待可能不足，導致測試偶發失敗。建議增加等待時間或使用更可靠的等待機制。

**判斷依據**：diff 中新增的這一行使用固定 0.5 秒 timeout，可能不足以等待系統提示出現。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4840 (cache hit 3968) ｜ completion tokens 878 ｜ PR #13</sub>