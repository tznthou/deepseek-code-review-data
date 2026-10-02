<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 UI 測試：移除已停用的 testWhatsNewPage、在貼上流程中處理系統「允許貼上」提示、調整 iPad 的測試跳過邏輯、以及將一個測試方法改名為 verify 開頭。整體風險低，但 tearDown 的 early return 可能導致 app.terminate() 與 super.tearDown() 被跳過，影響測試隔離；此外 verify 開頭的方法可能被 XCTest 忽略，需確認意圖。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29` | tearDown 中的 early return 可能跳過必要的清理步驟 | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47` | 測試方法改名為 verify 開頭可能導致 XCTest 無法識別 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29</code> tearDown 中的 early return 可能跳過必要的清理步驟</summary>

在 `tearDown()` 中，當 `self.name.contains("testSelectBottomPlacement") || iPad()` 為真時直接 `return`，這會跳過後面的 `app.terminate()` 和 `super.tearDown()`。這可能導致應用程式未正確終止，影響後續測試的隔離性，甚至造成測試不穩定。建議改為使用 `if` 條件包住 `switchThemeToDarkOrLight`，但不要提前返回，確保清理邏輯總是被執行。

**判斷依據**：diff 中新增的 `return` 語句位於 `tearDown()` 內，且後續仍有 `app.terminate()` 和 `try await super.tearDown()`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47</code> 測試方法改名為 verify 開頭可能導致 XCTest 無法識別</summary>

將 `testBookmarksShareNormalWebsiteReminders` 改名為 `verifyBookmarksShareNormalWebsiteReminders`。XCTest 預設只會執行以 `test` 開頭的方法，因此這個方法可能不再被當作測試執行。若這是刻意為之（例如改為輔助方法），則應確認呼叫處；否則應保留 `test` 前綴。

**判斷依據**：diff 中將方法名稱從 `testBookmarksShareNormalWebsiteReminders` 改為 `verifyBookmarksShareNormalWebsiteReminders`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4840 (cache hit 4736) ｜ completion tokens 680 ｜ PR #13</sub>