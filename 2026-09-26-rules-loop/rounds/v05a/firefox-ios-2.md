<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 Swift 6 遷移的一部分，主要將 XCUITest 測試套件中的 setUp/tearDown 改為 async throws，並為 UI 相關的類別、函式與全域變數加上 @MainActor 標註，以解決 main actor isolation 警告。整體改動方向正確，但存在幾個需要修正的問題：IpadOnlyTestCase.setUp 中呼叫 super.setUp() 缺少 try，會導致編譯錯誤；A11yUtils.swift 移除了 MPL 授權標頭，違反專案規範 R01；FeatureFlaggedTestSuite.setUp 中 setUpApp() 與 setUpExperimentVariables() 的呼叫順序被調換，可能影響測試行為；此外，部分 @MainActor 標註的放置位置可能不符合 Swift 慣例，且未涵蓋所有 UI 相關程式碼。建議優先修正編譯錯誤與授權標頭問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508` | IpadOnlyTestCase.setUp 呼叫 super.setUp() 缺少 try | 0.99 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1` | [R01] 移除 MPL 授權標頭 | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48` | setUp 中 setUpApp() 與 setUpExperimentVariables() 順序調換 | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:12` | @MainActor 標註位置不符合 Swift 慣例 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:16` | 全域變數 homepageSearchBar 未標註 @MainActor | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508</code> IpadOnlyTestCase.setUp 呼叫 super.setUp() 缺少 try</summary>

在 `IpadOnlyTestCase` 的 `setUp` 中，`super.setUp()` 現在是 `async throws`，但呼叫時沒有加上 `try`，會導致編譯錯誤。

```swift
override func setUp() async throws {
    specificForPlatform = .pad
    if iPad() {
        await super.setUp()
    }
}
```

應改為 `try await super.setUp()`。

**判斷依據**：diff 中 BaseTestCase.swift 的 IpadOnlyTestCase.setUp 內，`super.setUp()` 前只有 `await` 而沒有 `try`，但父類別的 `setUp` 已改為 `async throws`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1</code> [R01] 移除 MPL 授權標頭</summary>

此檔案原本有 Mozilla Public License 標頭，但在此 PR 中被移除。根據專案規範 R01，所有 Swift 檔案必須包含 MPL 標頭。請加回標準標頭：

```swift
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
```

**判斷依據**：diff 顯示 A11yUtils.swift 開頭的 MPL 標頭被刪除，僅留下 import 與 class 宣告。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48</code> setUp 中 setUpApp() 與 setUpExperimentVariables() 順序調換</summary>

原本的順序是先 `setUpExperimentVariables()` 再 `setUpApp()`，但此 PR 將兩者調換。如果 `setUpApp()` 依賴實驗變數的設定（例如 launch arguments），可能導致測試行為改變。請確認此順序變更是否為預期，若非必要請恢復原順序。

**判斷依據**：diff 中 FeatureFlaggedTestBase.swift 的 setUp 內，原本的 `setUpExperimentVariables()` 被移到 `setUpApp()` 之後。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:12</code> @MainActor 標註位置不符合 Swift 慣例</summary>

在 `BaseTestCase.swift` 中，`@MainActor` 被放在全域變數宣告之前，但 Swift 慣例是將屬性標註放在宣告的同一行或緊鄰其上方。例如：

```swift
@MainActor
let urlBarAddress = ...
```

建議改為：

```swift
@MainActor let urlBarAddress = ...
```

或維持分行但確保格式一致。

**判斷依據**：diff 中 BaseTestCase.swift 的 `@MainActor` 與 `let` 分行，但其他檔案（如 FxScreenGraph.swift）也是分行，此處僅為風格建議。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:16</code> 全域變數 homepageSearchBar 未標註 @MainActor</summary>

`homepageSearchBar` 也是 UI 相關的全域變數，但未加上 `@MainActor`。雖然可能因為其型別本身是 main actor isolated，但為求一致性與明確性，建議也加上標註。

**判斷依據**：diff 中 `homepageSearchBar` 的宣告沒有 `@MainActor`，但同一檔案中的 `urlBarAddress` 有加上。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 19300 (cache hit 17280) ｜ completion tokens 1457 ｜ PR #2</sub>