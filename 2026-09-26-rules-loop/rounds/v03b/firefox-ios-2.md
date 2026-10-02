<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Swift 6 遷移的一部分，主要將 XCUITest 測試套件中的 setUp/tearDown 改為 async throws，並為 UI 相關的類別、函式與全域變數加上 @MainActor 標註，以解決 main actor isolation 警告。整體變更範圍大但模式一致，風險主要在於非同步 setUp/tearDown 的呼叫順序與錯誤處理，以及 @MainActor 標註可能遺漏或誤用。最需要優先確認的是 IpadOnlyTestCase 中 `await super.setUp()` 缺少 try，以及 FeatureFlaggedTestBase 中 setUp 順序變更是否會影響測試行為。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:112` | IpadOnlyTestCase 中 `await super.setUp()` 缺少 try，可能導致錯誤未被處理 | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48` | setUp 中呼叫順序變更可能影響測試行為 | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1` | [R01] 移除 MPL 授權標頭 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:13` | [R09] 全域變數加上 @MainActor 可能導致其他檔案存取時需隔離 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/TodayWidgetTests.swift:15` | [R09] 全域變數從 nonisolated(unsafe) 改為 @MainActor 可能影響跨執行緒存取 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/registerSettingsNavigation.swift:8` | [R02] SwiftLint 指令與 @MainActor 放在同一行可能違反格式規範 | 0.60 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ScreenGraphTest.swift:53` | 新增空白行可能為意外變更 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:112</code> IpadOnlyTestCase 中 `await super.setUp()` 缺少 try，可能導致錯誤未被處理</summary>

在 `IpadOnlyTestCase` 的 `setUp()` 中，呼叫 `super.setUp()` 時使用了 `await` 但沒有 `try`。由於 `super.setUp()` 現在是 `async throws`，若其拋出錯誤，此處將無法編譯（Swift 要求必須處理錯誤）。這會導致所有繼承自 `IpadOnlyTestCase` 的測試無法建置。

建議改為 `try await super.setUp()`。

**判斷依據**：diff 中 BaseTestCase.swift 的 IpadOnlyTestCase 類別，新增的 async throws setUp 內呼叫 `await super.setUp()`，但缺少 `try`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48</code> setUp 中呼叫順序變更可能影響測試行為</summary>

在 `FeatureFlaggedTestSuite` 的 `setUp()` 中，原本的順序是 `setUpExperimentVariables()` 在 `setUpApp()` 之前，但變更後順序顛倒。若 `setUpExperimentVariables()` 依賴於 `setUpApp()` 所設定的某些狀態（例如 launchArguments 或 app 實例），此變更可能導致測試行為不一致或失敗。

建議確認此順序變更是否為必要，或恢復原本順序。

**判斷依據**：diff 中 FeatureFlaggedTestBase.swift 的 setUp 方法，原本 `setUpExperimentVariables()` 在 `setUpApp()` 之前，現在被移到之後。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1</code> [R01] 移除 MPL 授權標頭</summary>

此檔案原本包含 Mozilla Public License 標頭，但在 diff 中被移除。根據專案規範 R01，所有 Swift 檔案必須包含 MPL 標頭。請確認此移除是否為有意為之，否則應恢復。

**判斷依據**：diff 中 A11yUtils.swift 的開頭，原本的 MPL 標頭被刪除。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:13</code> [R09] 全域變數加上 @MainActor 可能導致其他檔案存取時需隔離</summary>

`urlBarAddress` 和 `homepageSearchBar` 被加上 `@MainActor`，這表示任何存取這些變數的程式碼都必須在主執行緒上執行。若其他檔案（未標註 @MainActor）直接使用這些變數，將產生編譯錯誤或需要額外隔離。請確認所有使用這些變數的程式碼都已正確處理 main actor 隔離。

**判斷依據**：diff 中 BaseTestCase.swift 的兩個全域變數被加上 @MainActor。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/TodayWidgetTests.swift:15</code> [R09] 全域變數從 nonisolated(unsafe) 改為 @MainActor 可能影響跨執行緒存取</summary>

原本使用 `nonisolated(unsafe)` 的全域變數（如 `goToCopiedLink`）被改為 `@MainActor`。這會限制這些變數只能在主執行緒存取。若測試程式碼在其他執行緒（例如背景佇列）中使用這些變數，將導致編譯錯誤或執行時崩潰。請確認所有使用這些變數的程式碼都在主執行緒上執行。

**判斷依據**：diff 中 TodayWidgetTests.swift 的多個全域變數從 nonisolated(unsafe) 改為 @MainActor。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/registerSettingsNavigation.swift:8</code> [R02] SwiftLint 指令與 @MainActor 放在同一行可能違反格式規範</summary>

在 `registerSettingsNavigation` 函式前，原本的 `// swiftlint:disable:next function_body_length` 被改為 `@MainActor // swiftlint:disable:next function_body_length`。這可能違反 SwiftLint 的格式規則（例如行長度或註解位置）。建議將 SwiftLint 指令放在單獨一行，或確認此寫法不會觸發警告。

**判斷依據**：diff 中 registerSettingsNavigation.swift 的該行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ScreenGraphTest.swift:53</code> 新增空白行可能為意外變更</summary>

在 `wait(forElement:timeout:)` 方法中，`expectation(for:evaluatedWith:)` 之後新增了一個空白行。這可能是無意的格式變更，建議移除以保持程式碼整潔。

**判斷依據**：diff 中 ScreenGraphTest.swift 的該處新增空白行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 19358 (cache hit 19328) ｜ completion tokens 1819 ｜ PR #2</sub>