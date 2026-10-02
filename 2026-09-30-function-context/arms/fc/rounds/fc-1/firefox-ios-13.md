<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 XCUITest 測試：移除已停用的 testWhatsNewPage、將 testBookmarksShareNormalWebsiteReminders 改名為 verifyBookmarksShareNormalWebsiteReminders、在貼上驗證流程中加入處理 iOS 貼上權限彈窗、調整 iPad 跳過邏輯，並改善長按分享選單的穩定性。整體風險低，但需注意 tearDown 中的提前 return 可能導致 app.terminate() 未執行，以及改名後的測試方法可能不再被 XCTest 自動執行。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29` | tearDown 中提前 return 可能導致 app.terminate() 未執行 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47` | 測試方法改名可能導致不再被 XCTest 執行 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471` | 貼上權限彈窗處理可能不穩定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29</code> tearDown 中提前 return 可能導致 app.terminate() 未執行</summary>

在 `tearDown()` 中，當 `self.name.contains("testSelectBottomPlacement") || iPad()` 為真時，會直接 `return`，跳過後續的 `app.terminate()`。這可能導致測試結束後應用程式仍在前景執行，影響後續測試的隔離性，甚至造成測試失敗。建議改為使用 `if` 條件包住主題切換邏輯，但保留 `app.terminate()` 的執行。

**判斷依據**：diff 中新增的 `return` 位於 `tearDown()` 內，且 `app.terminate()` 在其後方，因此提前返回會跳過終止應用程式的步驟。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47</code> 測試方法改名可能導致不再被 XCTest 執行</summary>

將 `testBookmarksShareNormalWebsiteReminders` 改名為 `verifyBookmarksShareNormalWebsiteReminders` 後，該方法不再以 `test` 開頭，XCTest 不會自動將其視為測試案例執行。若此方法仍應作為測試執行，請保留 `test` 前綴；若改為輔助方法，則應確認其被其他測試正確呼叫。

**判斷依據**：diff 中將方法名稱從 `testBookmarksShareNormalWebsiteReminders` 改為 `verifyBookmarksShareNormalWebsiteReminders`，違反 XCTest 命名慣例。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471</code> 貼上權限彈窗處理可能不穩定</summary>

新增的 `springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)` 使用固定 0.5 秒等待，若系統彈窗出現較慢，可能無法點擊，導致後續驗證失敗。建議使用更可靠的等待機制，例如 `mozWaitForElementToExist` 或增加重試邏輯。

**判斷依據**：diff 中新增此行，使用短暫 timeout 處理系統彈窗，可能因時序問題而失敗。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15416 (cache hit 1536) ｜ completion tokens 913 ｜ PR #13</sub>