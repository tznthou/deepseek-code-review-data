<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 XCUITests 套件中的 setUp/tearDown 改為 async throws，並為大量 UI 相關的類別、函式與全域變數加上 @MainActor，以符合 Swift 6 的 main actor isolation 要求。整體方向正確，但存在幾個需要修正的問題：IpadOnlyTestCase.setUp 中呼叫 super.setUp 缺少 try，會導致編譯錯誤；A11yUtils.swift 移除了 MPL 授權標頭，違反專案規範；FeatureFlaggedTestSuite.setUp 中 setUpApp 與 setUpExperimentVariables 的順序被調換，可能影響測試行為；此外，部分 @MainActor 標註可能不必要，但影響不大。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:510` | IpadOnlyTestCase.setUp 中呼叫 super.setUp 缺少 try | 0.98 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1` | [R01] 移除 Mozilla Public License 標頭 | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48` | setUp 中 setUpApp 與 setUpExperimentVariables 順序調換可能影響測試 | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:13` | 全域變數 urlBarAddress 與 homepageSearchBar 的 @MainActor 標註可能不必要 | 0.60 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/TodayWidgetTests.swift:15` | 全域變數的 @MainActor 標註可能導致初始化時機問題 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:510</code> IpadOnlyTestCase.setUp 中呼叫 super.setUp 缺少 try</summary>

在 `IpadOnlyTestCase` 的 `setUp` 中，`super.setUp()` 現在是 async throws，但呼叫處沒有加上 `try`，會導致編譯錯誤。

```swift
override func setUp() async throws {
    specificForPlatform = .pad
    if iPad() {
        await super.setUp()
    }
}
```

應改為 `try await super.setUp()`。

**判斷依據**：diff 中 `IpadOnlyTestCase` 的 `setUp` 方法內，`super.setUp()` 前只有 `await`，沒有 `try`，而父類別的 `setUp` 已改為 `async throws`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1</code> [R01] 移除 Mozilla Public License 標頭</summary>

此檔案原本有 MPL 授權標頭，但在此 PR 中被移除。根據專案規範 R01，所有 Swift 檔案必須包含 Mozilla Public License v2.0 標頭。請恢復標頭。

**判斷依據**：diff 顯示刪除了三行 MPL 標頭，且沒有新增替代的標頭。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48</code> setUp 中 setUpApp 與 setUpExperimentVariables 順序調換可能影響測試</summary>

原本的順序是先 `setUpExperimentVariables()` 再 `setUpApp()`，但此 PR 將其調換。如果 `setUpApp()` 依賴實驗變數的設定，可能導致測試行為改變。請確認此順序變更是有意為之，且不會造成問題。

**判斷依據**：diff 顯示 `setUpExperimentVariables()` 被移到 `setUpApp()` 之後。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:13</code> 全域變數 urlBarAddress 與 homepageSearchBar 的 @MainActor 標註可能不必要</summary>

這兩個全域變數是 `XCUIApplication` 的屬性，而 `XCUIApplication` 本身可能已標註為 @MainActor，因此額外的 @MainActor 可能多餘。但若編譯器要求，則保留。

**判斷依據**：diff 中新增了 @MainActor 標註。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/TodayWidgetTests.swift:15</code> 全域變數的 @MainActor 標註可能導致初始化時機問題</summary>

這些全域變數在檔案載入時即初始化，若 @MainActor 隔離，可能延後初始化至首次存取時，若在多執行緒環境下可能造成競態。但由於測試皆在主執行緒執行，風險低。

**判斷依據**：diff 中將原本的 `nonisolated(unsafe)` 改為 `@MainActor`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 19348 (cache hit 19328) ｜ completion tokens 1284 ｜ PR #2</sub>