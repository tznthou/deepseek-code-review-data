<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 XCUITests 中的 setUp/tearDown 改為 async throws 並加上 @MainActor 標註，以符合 Swift 6 的 main actor isolation 要求。整體改動方向正確，但發現兩處潛在問題：IpadOnlyTestCase 的 setUp 中呼叫 super.setUp() 時缺少 try，可能導致編譯錯誤；FeatureFlaggedTestSuite 的 setUp 中 setUpApp() 與 setUpExperimentVariables() 的順序變更可能影響測試行為。建議修正後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508` | IpadOnlyTestCase.setUp() 呼叫 super.setUp() 缺少 try | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48` | setUpApp() 與 setUpExperimentVariables() 順序變更可能影響測試行為 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508</code> IpadOnlyTestCase.setUp() 呼叫 super.setUp() 缺少 try</summary>

在 `IpadOnlyTestCase` 的 `setUp()` 中，`super.setUp()` 現在是 `async throws`，但呼叫時沒有加上 `try`。這會導致編譯錯誤。

建議改為：
```swift
try await super.setUp()
```

**判斷依據**：diff 中 IpadOnlyTestCase 的 setUp 改為 async throws，但呼叫 super.setUp() 時只加了 await，沒有 try。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48</code> setUpApp() 與 setUpExperimentVariables() 順序變更可能影響測試行為</summary>

原本的順序是先 `setUpExperimentVariables()` 再 `setUpApp()`，現在改成先 `setUpApp()` 再 `setUpExperimentVariables()`。如果 `setUpApp()` 依賴實驗變數的設定，這個順序變更可能導致測試行為改變。建議確認此變更是否為刻意為之，並確保不會影響測試結果。

**判斷依據**：diff 中 FeatureFlaggedTestSuite 的 setUp 內，setUpApp() 和 setUpExperimentVariables() 的順序對調。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17289 (cache hit 17280) ｜ completion tokens 584 ｜ PR #2</sub>