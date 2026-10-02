<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 Swift 6 遷移的一部分，主要將 XCUITests 中的 setUp/tearDown 改為 async throws 並加上 @MainActor 標註，以解決 main actor isolation 警告。整體變更一致且機械化，但發現兩個潛在問題：IpadOnlyTestCase.setUp 中呼叫 super.setUp() 時缺少 try，可能導致編譯錯誤；FeatureFlaggedTestSuite.setUp 中 setUpApp() 與 setUpExperimentVariables() 的順序變更可能影響測試行為。建議修正後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508` | IpadOnlyTestCase.setUp 中呼叫 super.setUp() 缺少 try | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48` | setUp 中 setUpApp() 與 setUpExperimentVariables() 順序變更可能影響測試 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508</code> IpadOnlyTestCase.setUp 中呼叫 super.setUp() 缺少 try</summary>

在 IpadOnlyTestCase 的 setUp 方法中，`super.setUp()` 現在是 async throws，但呼叫時沒有加上 `try`。這會導致編譯錯誤：`Call can throw but is not marked with 'try'`。

建議改為 `try await super.setUp()`。

**判斷依據**：diff 中 IpadOnlyTestCase.setUp 的變更：
```
-            super.setUp()
+            await super.setUp()
```
而 super.setUp() 的簽名已改為 `override func setUp() async throws`，因此必須使用 `try await`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48</code> setUp 中 setUpApp() 與 setUpExperimentVariables() 順序變更可能影響測試</summary>

原本的順序是先呼叫 `setUpExperimentVariables()` 再呼叫 `setUpApp()`，但變更後順序顛倒。如果 `setUpApp()` 依賴於實驗變數的設定（例如 launch arguments 中包含實驗變數），則可能導致測試行為不正確。

建議確認此順序變更是否為有意為之，若無必要請恢復原順序。

**判斷依據**：diff 中 FeatureFlaggedTestSuite.setUp 的變更：
```
-        setUpExperimentVariables()
         setUpApp()
+        setUpExperimentVariables()
```

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17289 (cache hit 1536) ｜ completion tokens 648 ｜ PR #2</sub>