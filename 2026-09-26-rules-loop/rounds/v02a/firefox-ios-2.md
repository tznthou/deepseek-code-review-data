<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 XCUITests 中的 setUp/tearDown 改為 async throws，並在多個 UI 相關的類別、函式與全域變數加上 @MainActor，以符合 Swift 6 的 main actor isolation 要求。整體方向正確，但存在幾個需要修正的問題：A11yUtils.swift 移除了 MPL 授權標頭（違反 R01）；IpadOnlyTestCase.setUp 中呼叫 super.setUp() 時誤用 await 而非 try await（會導致編譯錯誤）；FeatureFlaggedTestSuite.setUp 調整了 setUpApp 與 setUpExperimentVariables 的呼叫順序，可能影響測試行為；此外，部分全域變數加上 @MainActor 後，若從非 main actor 的 context 存取可能造成編譯錯誤或 runtime crash。建議先修正 blocker 問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1` | [R01] 移除 MPL 授權標頭 | 0.99 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:516` | IpadOnlyTestCase.setUp 中誤用 await 呼叫 super.setUp() | 0.99 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48` | setUp 中呼叫順序變更可能影響測試行為 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/TodayWidgetTests.swift:15` | 全域變數加上 @MainActor 可能導致非主執行緒存取 crash | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:13` | 全域變數加上 @MainActor 可能影響非主執行緒使用 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1</code> [R01] 移除 MPL 授權標頭</summary>

此檔案原本有 Mozilla Public License 2.0 標頭，但在此 diff 中被刪除。根據規範 R01，所有 Swift 檔案必須包含 MPL 標頭。請恢復標頭。

**判斷依據**：diff 顯示刪除了三行 MPL 標頭，且未新增任何替代標頭。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:516</code> IpadOnlyTestCase.setUp 中誤用 await 呼叫 super.setUp()</summary>

在 `IpadOnlyTestCase` 的 `setUp` 中，呼叫 `super.setUp()` 時使用了 `await`，但 `super.setUp()` 是 `async throws`，必須使用 `try await`。這會導致編譯錯誤。請改為 `try await super.setUp()`。

**判斷依據**：diff 中該行從 `super.setUp()` 改為 `await super.setUp()`，但其他 override 均使用 `try await super.setUp()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48</code> setUp 中呼叫順序變更可能影響測試行為</summary>

原本 `setUp` 先呼叫 `setUpExperimentVariables()` 再呼叫 `setUpApp()`，現在順序對調。若 `setUpApp()` 依賴實驗變數已設定（例如 launch arguments 中包含實驗相關參數），此變更可能導致測試行為不同。請確認此順序變更是有意為之且不會造成問題。

**判斷依據**：diff 顯示兩行順序互換。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/TodayWidgetTests.swift:15</code> 全域變數加上 @MainActor 可能導致非主執行緒存取 crash</summary>

這些全域變數（如 `goToCopiedLink`）現在標記為 `@MainActor`，但若在非 main actor 的 context 中存取（例如某些非同步 callback），會觸發 runtime crash 或編譯錯誤。請確認所有存取點都在 main actor 上，或考慮使用 `nonisolated(unsafe)` 並確保 thread safety。

**判斷依據**：diff 將原本的 `nonisolated(unsafe)` 改為 `@MainActor`，但未提供其他同步機制。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:13</code> 全域變數加上 @MainActor 可能影響非主執行緒使用</summary>

`urlBarAddress` 和 `homepageSearchBar` 現在是 `@MainActor`，若在非 main actor 的 context 中初始化或使用，可能造成問題。請確認這些變數的使用情境。

**判斷依據**：diff 新增了 `@MainActor` 屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 19348 (cache hit 1536) ｜ completion tokens 1226 ｜ PR #2</sub>