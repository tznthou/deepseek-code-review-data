<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 Swift 6 遷移的一部分，主要將 XCUITests 中的 setUp/tearDown 改為 async throws，並為大量 UI 相關的類別、函式與全域變數加上 @MainActor 標註。整體方向正確，符合 Swift 6 的 concurrency 要求。但需注意：IpadOnlyTestCase.setUp 中呼叫 super.setUp() 時漏了 try，可能導致編譯錯誤；A11yUtils.swift 移除了 MPL 授權標頭，違反專案規範 R01；部分 @MainActor 標註加在全域變數上，需確認其初始化時機與執行緒安全性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:510` | IpadOnlyTestCase.setUp 呼叫 super.setUp() 缺少 try | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1` | [R01] 移除 MPL 授權標頭 | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:13` | 全域變數加上 @MainActor 可能造成初始化時機問題 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/TodayWidgetTests.swift:16` | 全域變數改為 @MainActor 可能導致跨執行緒存取問題 | 0.75 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:47` | setUp 中呼叫順序變更可能影響測試行為 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:510</code> IpadOnlyTestCase.setUp 呼叫 super.setUp() 缺少 try</summary>

在 `IpadOnlyTestCase` 的 `setUp` 中，`super.setUp()` 現在是 `async throws`，但呼叫時沒有加上 `try`。這會導致編譯錯誤。

```swift
override func setUp() async throws {
    specificForPlatform = .pad
    if iPad() {
        await super.setUp()
    }
}
```

應改為 `try await super.setUp()`。

**判斷依據**：diff 中 BaseTestCase.swift 的 IpadOnlyTestCase.setUp 區塊，新增的 `await super.setUp()` 缺少 `try`，而 super.setUp() 已改為 `async throws`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1</code> [R01] 移除 MPL 授權標頭</summary>

此檔案原本有 Mozilla Public License 標頭，但在此 PR 中被移除。根據專案規範 R01，所有 Swift 檔案必須包含 MPL 標頭。請恢復標頭。

**判斷依據**：diff 顯示 A11yUtils.swift 刪除了三行 MPL 標頭，且未新增替代內容。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:13</code> 全域變數加上 @MainActor 可能造成初始化時機問題</summary>

`urlBarAddress` 和 `homepageSearchBar` 是全域變數，加上 `@MainActor` 後，其初始化將在主執行緒上進行。若這些變數在非主執行緒環境中被存取，可能導致 runtime crash。需確認所有存取點皆已在 MainActor 隔離的環境中。

**判斷依據**：diff 中 BaseTestCase.swift 頂部新增了 @MainActor 於兩個全域 let 變數上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/TodayWidgetTests.swift:16</code> 全域變數改為 @MainActor 可能導致跨執行緒存取問題</summary>

多個全域變數（如 `goToCopiedLink`、`newPrivateSearch` 等）從 `nonisolated(unsafe)` 改為 `@MainActor`。這雖然提升了安全性，但若這些變數在非主執行緒的 context 中被使用，會觸發 Swift concurrency 檢查錯誤。需確認所有使用這些變數的函式或閉包皆已標註 @MainActor 或透過 await 存取。

**判斷依據**：diff 中 TodayWidgetTests.swift 將原本的 nonisolated(unsafe) 改為 @MainActor。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:47</code> setUp 中呼叫順序變更可能影響測試行為</summary>

原本 `setUpExperimentVariables()` 在 `setUpApp()` 之前呼叫，現在順序對調。若 `setUpApp()` 依賴實驗變數已設定，可能導致測試行為改變。請確認此順序變更是有意為之且不會造成問題。

**判斷依據**：diff 中 FeatureFlaggedTestBase.swift 的 setUp 方法內，呼叫順序由 setUpExperimentVariables() 在 setUpApp() 之前改為之後。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 18136 (cache hit 17280) ｜ completion tokens 1431 ｜ PR #2</sub>