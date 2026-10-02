<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 Swift 6 遷移的一部分，將 XCUITests 中的 setUp/tearDown 改為 async throws，並在多個全域變數與函式加上 @MainActor 標註，以解決 main actor isolation 警告。整體變更範圍廣但機械化，主要風險在於非同步 override 的呼叫方式是否正確（例如 IpadOnlyTestCase 中 await super.setUp() 缺少 try），以及 @MainActor 標註是否可能造成隱含的隔離問題。建議優先修正 IpadOnlyTestCase 的錯誤，並確認所有非同步 override 的錯誤處理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:512` | IpadOnlyTestCase.setUp() 呼叫 super.setUp() 缺少 try | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48` | setUp() 中 setUpApp() 與 setUpExperimentVariables() 順序變更可能影響測試行為 | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/registerSettingsNavigation.swift:8` | @MainActor 與 swiftlint 指令在同一行可能導致 lint 失效 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:512</code> IpadOnlyTestCase.setUp() 呼叫 super.setUp() 缺少 try</summary>

在 `IpadOnlyTestCase` 的 `setUp()` 中，`super.setUp()` 現在是 `async throws`，但呼叫時僅使用 `await super.setUp()`，缺少 `try`。這會導致編譯錯誤，因為 throwing 函式必須以 `try` 呼叫。

建議改為 `try await super.setUp()`。

**判斷依據**：diff 中 BaseTestCase.swift 的 IpadOnlyTestCase 區塊：
```
-            super.setUp()
+            await super.setUp()
```
而其他類別（如 IphoneOnlyTestCase）皆使用 `try await super.setUp()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48</code> setUp() 中 setUpApp() 與 setUpExperimentVariables() 順序變更可能影響測試行為</summary>

原本 `setUpExperimentVariables()` 在 `setUpApp()` 之前呼叫，現在順序對調。若 `setUpApp()` 依賴實驗變數已設定（例如啟動參數或功能旗標），可能導致測試行為不一致。

建議確認此順序變更是否為必要，或恢復原順序。

**判斷依據**：diff 中 FeatureFlaggedTestBase.swift：
```
-        setUpExperimentVariables()
         setUpApp()
+        setUpExperimentVariables()
```

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/registerSettingsNavigation.swift:8</code> @MainActor 與 swiftlint 指令在同一行可能導致 lint 失效</summary>

將 `@MainActor` 與 `// swiftlint:disable:next function_body_length` 放在同一行，可能使 swiftlint 無法正確解析 disable 指令，導致 function_body_length 警告重新出現。

建議將 swiftlint 指令移至下一行，或確認 lint 設定。

**判斷依據**：diff 中 registerSettingsNavigation.swift：
```
-// swiftlint:disable:next function_body_length
+@MainActor // swiftlint:disable:next function_body_length
```

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17253 (cache hit 17152) ｜ completion tokens 867 ｜ PR #2</sub>