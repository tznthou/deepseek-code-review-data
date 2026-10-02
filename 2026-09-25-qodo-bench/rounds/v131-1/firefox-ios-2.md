<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 Swift 6 遷移的一部分，主要將 XCUITest 測試類別的 setUp/tearDown 改為 async throws，並為多個全域變數與函式加上 @MainActor 標註，以解決 main actor isolation 警告。整體變更方向正確，但需注意 IpadOnlyTestCase 中呼叫 super.setUp() 時漏掉 try，可能導致編譯錯誤；此外，部分 setUp 中呼叫 setUpApp() 與 setUpScreenGraph() 的順序在 FeatureFlaggedTestBase 中有所調整，需確認是否影響測試行為。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:512` | IpadOnlyTestCase 中呼叫 super.setUp() 缺少 try | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48` | setUp() 中 setUpApp() 與 setUpExperimentVariables() 順序變更可能影響測試 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:13` | 全域變數加上 @MainActor 可能造成初始化時機問題 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:512</code> IpadOnlyTestCase 中呼叫 super.setUp() 缺少 try</summary>

在 IpadOnlyTestCase 的 setUp() 中，呼叫 `await super.setUp()` 但未加上 `try`。由於父類別的 setUp() 現在是 `async throws`，此處會導致編譯錯誤。應改為 `try await super.setUp()`。

**判斷依據**：diff 中顯示 `-            super.setUp()` 改為 `+            await super.setUp()`，但未加上 try。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48</code> setUp() 中 setUpApp() 與 setUpExperimentVariables() 順序變更可能影響測試</summary>

原本的順序是 `setUpExperimentVariables()` 在 `setUpApp()` 之前，現在被調換。若 setUpExperimentVariables() 依賴 setUpApp() 設定的某些狀態，或反之，可能導致測試行為改變。需確認兩者之間是否有相依性。

**判斷依據**：diff 顯示 `-        setUpExperimentVariables()` 被移到 `+        setUpApp()` 之後。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:13</code> 全域變數加上 @MainActor 可能造成初始化時機問題</summary>

`urlBarAddress` 和 `homepageSearchBar` 等全域變數加上 @MainActor 後，若在非 main actor 環境中存取，可能導致 runtime crash 或編譯錯誤。需確認所有存取點都在 main actor 上。

**判斷依據**：diff 中新增 @MainActor 標註。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17253 (cache hit 1408) ｜ completion tokens 753 ｜ PR #2</sub>