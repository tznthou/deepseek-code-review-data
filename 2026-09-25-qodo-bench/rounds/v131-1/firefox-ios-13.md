<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 XCUITest 測試：移除已停用的 testWhatsNewPage、調整 iPad 的測試跳過邏輯、新增貼上權限彈窗處理，並將一個測試方法改名為 verify 開頭。整體風險低，但 tearDown 中的提前 return 可能導致 app.terminate() 與 super.tearDown() 被略過，影響測試隔離；另外 verify 開頭的方法可能不會被 XCTest 自動執行，需確認測試計畫是否已更新。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29` | tearDown 中提前 return 可能略過清理步驟 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47` | 測試方法改名為 verify 開頭可能導致不被 XCTest 執行 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29</code> tearDown 中提前 return 可能略過清理步驟</summary>

在 `tearDown()` 中，當 `self.name.contains("testSelectBottomPlacement") || iPad()` 成立時直接 `return`，導致後續的 `app.terminate()` 與 `super.tearDown()` 不會被執行。這可能造成測試狀態殘留，影響後續測試的隔離性。建議改為使用 `if` 條件包住主題切換，但保留 `app.terminate()` 與 `super.tearDown()` 的執行。

**判斷依據**：diff 中新增的 `return` 位於 `tearDown()` 內，且後續仍有 `app.terminate()` 與 `try await super.tearDown()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47</code> 測試方法改名為 verify 開頭可能導致不被 XCTest 執行</summary>

將 `testBookmarksShareNormalWebsiteReminders` 改名為 `verifyBookmarksShareNormalWebsiteReminders`。XCTest 預設只會執行以 `test` 開頭的方法，除非測試計畫明確列出此方法，否則此測試將不會被執行。請確認相關 `.xctestplan` 檔案是否已更新包含此新名稱，或考慮保留 `test` 前綴。

**判斷依據**：diff 中方法名稱從 `testBookmarksShareNormalWebsiteReminders` 改為 `verifyBookmarksShareNormalWebsiteReminders`，且未見測試計畫檔案同步更新。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3957 (cache hit 1408) ｜ completion tokens 687 ｜ PR #13</sub>