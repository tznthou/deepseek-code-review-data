<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Swift 6 遷移的一部分，將 XCUITest 測試套件中的 setUp/tearDown 改為 async throws，並在多個全域變數與函式加上 @MainActor 標註，以解決 main actor isolation 警告。主要風險在於非同步 setUp 的呼叫順序與錯誤處理，以及 @MainActor 標註可能造成的編譯或執行期問題。整體變更範圍大但模式一致，建議合併前確認所有測試類別的正確性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:112` | IpadOnlyTestCase.setUp 中 await super.setUp() 缺少 try | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48` | setUp 中呼叫順序變更可能影響測試初始化 | 0.75 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:13` | 全域變數加上 @MainActor 可能造成初始化時機問題 | 0.60 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/TodayWidgetTests.swift:16` | 全域變數從 nonisolated(unsafe) 改為 @MainActor 可能影響並發安全 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:112</code> IpadOnlyTestCase.setUp 中 await super.setUp() 缺少 try</summary>

在 `IpadOnlyTestCase` 的 `setUp` 中，呼叫 `await super.setUp()` 但沒有加上 `try`。由於 `super.setUp()` 現在是 `async throws`，若其拋出錯誤，此處會因未處理而導致編譯錯誤或執行期崩潰。建議改為 `try await super.setUp()`。

**判斷依據**：diff 中 BaseTestCase.swift 的 IpadOnlyTestCase 類別內，`await super.setUp()` 未加上 `try`，而其他類似呼叫均有 `try await`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48</code> setUp 中呼叫順序變更可能影響測試初始化</summary>

原本 `setUpExperimentVariables()` 在 `setUpApp()` 之前呼叫，現在順序對調。若 `setUpApp()` 依賴實驗變數已設定，可能導致測試行為錯誤。請確認此順序變更是有意為之且不會影響測試。

**判斷依據**：diff 中 FeatureFlaggedTestBase.swift 的 setUp 方法內，兩行順序對調。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:13</code> 全域變數加上 @MainActor 可能造成初始化時機問題</summary>

`urlBarAddress` 和 `homepageSearchBar` 等全域變數加上 `@MainActor` 後，其初始化將在主執行緒進行。若這些變數在非主執行緒環境中被存取，可能導致執行期錯誤。請確認所有存取點皆在主執行緒。

**判斷依據**：diff 中 BaseTestCase.swift 頂部新增 @MainActor 標註於全域變數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/TodayWidgetTests.swift:16</code> 全域變數從 nonisolated(unsafe) 改為 @MainActor 可能影響並發安全</summary>

原本使用 `nonisolated(unsafe)` 的全域變數改為 `@MainActor`，這會限制其存取在主執行緒。若這些變數在非主執行緒的 context 中被使用，可能導致編譯錯誤或執行期問題。請確認所有使用情境。

**判斷依據**：diff 中 TodayWidgetTests.swift 的多個全域變數由 nonisolated(unsafe) 改為 @MainActor。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17289 (cache hit 17280) ｜ completion tokens 1000 ｜ PR #2</sub>