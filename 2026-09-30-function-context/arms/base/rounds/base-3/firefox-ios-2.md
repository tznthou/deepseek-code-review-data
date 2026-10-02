<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 XCUITests 中的 setUp/tearDown 改為 async throws 並加上 @MainActor 標註，以符合 Swift 6 的 concurrency 要求。整體改動一致且必要，但 IpadOnlyTestCase.setUp 中呼叫 super.setUp() 缺少 try 關鍵字，會導致編譯錯誤。此外，部分全域變數加上 @MainActor 可能影響跨執行緒存取，需確認測試執行緒。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508` | IpadOnlyTestCase.setUp 中呼叫 super.setUp() 缺少 try | 0.99 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:13` | 全域變數加上 @MainActor 可能造成跨執行緒存取問題 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48` | setUp 中呼叫順序變更可能影響測試行為 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508</code> IpadOnlyTestCase.setUp 中呼叫 super.setUp() 缺少 try</summary>

在 `IpadOnlyTestCase` 的 `setUp` 中，`super.setUp()` 現在是 `async throws`，但呼叫處沒有加上 `try`，會導致編譯錯誤。請改為 `try await super.setUp()`。

**判斷依據**：diff 中顯示 `IpadOnlyTestCase` 的 `setUp` 內呼叫 `await super.setUp()`，但 `BaseTestCase.setUp` 已改為 `async throws`，因此需要 `try await`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:13</code> 全域變數加上 @MainActor 可能造成跨執行緒存取問題</summary>

`urlBarAddress` 和 `homepageSearchBar` 等全域變數被加上 `@MainActor`，但若在其他非主執行緒的 context 中存取（例如某些測試輔助函式），可能導致編譯錯誤或 runtime crash。請確認所有存取點都在主執行緒，或改用其他同步機制。

**判斷依據**：diff 中新增 `@MainActor` 於全域變數，但未提供其他執行緒存取的保護。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48</code> setUp 中呼叫順序變更可能影響測試行為</summary>

原本 `setUpExperimentVariables()` 在 `setUpApp()` 之前呼叫，現在順序對調。若 `setUpApp()` 依賴實驗變數已設定，可能導致測試行為改變。請確認此順序變更是有意且安全的。

**判斷依據**：diff 顯示 `setUpExperimentVariables()` 和 `setUpApp()` 的順序被交換。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17289 (cache hit 17280) ｜ completion tokens 792 ｜ PR #2</sub>