<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 XCUITests 套件中的 setUp/tearDown 改為 async throws，並為多個 UI 相關的類別、函式與全域變數加上 @MainActor，以符合 Swift 6 的 main actor isolation 要求。整體方向正確，但存在兩個主要風險：IpadOnlyTestCase.setUp 中呼叫 super.setUp() 時漏掉 try，可能導致編譯錯誤；A11yUtils.swift 移除了 MPL 授權標頭，違反專案規範。此外，部分 @MainActor 標註可能不必要，且 setUp 中呼叫順序的變更需確認無副作用。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:510` | IpadOnlyTestCase.setUp 呼叫 super.setUp() 時缺少 try | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1` | [R01] 移除 Mozilla Public License 標頭 | 0.90 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48` | setUp 中 setUpApp() 與 setUpExperimentVariables() 順序變更 | 0.60 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:13` | 全域變數 urlBarAddress 與 homepageSearchBar 的 @MainActor 標註可能不必要 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:510</code> IpadOnlyTestCase.setUp 呼叫 super.setUp() 時缺少 try</summary>

在 `IpadOnlyTestCase` 的 `setUp` 中，`super.setUp()` 現在是 `async throws`，但呼叫處沒有加上 `try`。這會導致編譯錯誤。

```swift
override func setUp() async throws {
    specificForPlatform = .pad
    if iPad() {
        await super.setUp()
    }
}
```

應改為 `try await super.setUp()`。

**判斷依據**：diff 中 BaseTestCase.swift 的 IpadOnlyTestCase.setUp 內，`super.setUp()` 前只有 `await`，沒有 `try`，而父類別的 `setUp` 已改為 `async throws`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1</code> [R01] 移除 Mozilla Public License 標頭</summary>

此 PR 刪除了 A11yUtils.swift 開頭的 MPL 授權標頭，違反專案規範 R01。所有 Swift 檔案必須包含標準 MPL 標頭。請恢復該標頭。

**判斷依據**：diff 顯示 A11yUtils.swift 的開頭從 MPL 標頭改為直接 import XCTest，且未新增其他授權標頭。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48</code> setUp 中 setUpApp() 與 setUpExperimentVariables() 順序變更</summary>

原本 `setUpExperimentVariables()` 在 `setUpApp()` 之前呼叫，現在順序對調。若 `setUpApp()` 依賴實驗變數已設定，可能導致測試行為改變。請確認此順序變更是有意且安全的。

**判斷依據**：diff 顯示 FeatureFlaggedTestBase.swift 中，`setUpApp()` 被移到 `setUpExperimentVariables()` 之前。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:13</code> 全域變數 urlBarAddress 與 homepageSearchBar 的 @MainActor 標註可能不必要</summary>

這兩個全域變數初始化時建立 `XCUIApplication()` 並存取其屬性，可能已隱含 main actor 隔離。加上 `@MainActor` 可能導致其他未標註的程式碼在存取時產生編譯錯誤。請確認是否真的需要，或改用其他方式（如 lazy var 或函式）。

**判斷依據**：diff 中 BaseTestCase.swift 為這兩個全域變數加上 @MainActor，但未見其他程式碼因缺少 @MainActor 而無法存取。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 19338 (cache hit 19328) ｜ completion tokens 1122 ｜ PR #2</sub>