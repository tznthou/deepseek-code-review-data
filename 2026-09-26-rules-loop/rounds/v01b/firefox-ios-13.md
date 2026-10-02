<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 UI 測試：移除已停用的 testWhatsNewPage、在貼上流程處理系統允許貼上對話框、調整 OnboardingTests 的 tearDown 與 iPad 跳過邏輯、將 ShareLongPressTests 中的一個測試方法改名（可能使其不再被 XCTest 執行），並改用 pressWithRetry 改善穩定性。整體風險中等：測試方法改名可能導致測試不再被執行，需確認意圖；其餘變更多為測試穩定度改善。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47` | [R06] 測試方法改名後不再以 'test' 開頭，可能導致測試不被 XCTest 執行 | 0.90 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29` | tearDown 中提前 return 可能跳過 super.tearDown() 呼叫 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471` | 貼上允許對話框處理可能不穩定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47</code> [R06] 測試方法改名後不再以 'test' 開頭，可能導致測試不被 XCTest 執行</summary>

方法 `testBookmarksShareNormalWebsiteReminders` 被改名為 `verifyBookmarksShareNormalWebsiteReminders`，不再符合 XCTest 的命名慣例（必須以 `test` 開頭）。這會導致該測試方法不再被 XCTest 自動發現與執行，等同於移除了這個測試。若此為有意為之，應直接刪除方法或使用 `XCTSkip`；否則應保留 `test` 前綴。

**判斷依據**：diff 中將 `func testBookmarksShareNormalWebsiteReminders()` 改為 `func verifyBookmarksShareNormalWebsiteReminders()`，違反 R06 規範。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29</code> tearDown 中提前 return 可能跳過 super.tearDown() 呼叫</summary>

在 `tearDown()` 中，當條件成立時直接 `return`，這會跳過後續的 `app.terminate()` 與 `try await super.tearDown()`。若 `super.tearDown()` 包含必要的清理邏輯（例如釋放資源、重設狀態），此處提前返回可能導致測試環境污染。建議改為使用 `if` 條件包住主題切換，但保留 `app.terminate()` 與 `super.tearDown()` 的呼叫。

**判斷依據**：diff 中新增的 `return` 位於 `tearDown()` 內，且後續仍有 `app.terminate()` 與 `try await super.tearDown()`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471</code> 貼上允許對話框處理可能不穩定</summary>

新增 `springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)` 來處理系統貼上權限對話框。此對話框的出現時機可能因 iOS 版本或應用狀態而異，固定 0.5 秒的等待可能不足或過長。建議使用更穩健的等待機制（例如 `mozWaitForElementToExist`）或確認此對話框是否總是在此步驟出現。

**判斷依據**：diff 中新增此行，使用固定 timeout 處理系統對話框。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6052 (cache hit 6016) ｜ completion tokens 937 ｜ PR #13</sub>