<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 XCUITests 套件中的 setUp/tearDown 改為 async throws 版本，並在多個 UI 相關的類別、函式與全域變數加上 @MainActor 標註，以符合 Swift 6 的 main actor isolation 要求。整體改動方向正確，但存在幾個需要修正的問題：A11yUtils.swift 移除了 MPL 授權標頭（違反 R01）；IpadOnlyTestCase.setUp 中呼叫 super.setUp() 時誤用 await 而非 try await，可能導致編譯錯誤；FeatureFlaggedTestSuite.setUp 調整了 setUpExperimentVariables 與 setUpApp 的呼叫順序，可能影響測試行為；此外，部分 @MainActor 標註加在全域變數上，需確認其執行緒安全性與初始化時機。建議修正上述問題後再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1` | [R01] 缺少 Mozilla Public License 標頭 | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:510` | IpadOnlyTestCase.setUp 中誤用 await 呼叫 super.setUp() | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/TodayWidgetTests.swift:15` | 全域變數標註 @MainActor 可能導致初始化時機問題 | 0.75 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48` | setUp 中呼叫順序變更可能影響測試行為 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/registerSettingsNavigation.swift:8` | SwiftLint 停用註解位置可能失效 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1</code> [R01] 缺少 Mozilla Public License 標頭</summary>

此檔案原本有 MPL 2.0 授權標頭，但在本次 diff 中被移除。根據規範 R01，所有 Swift 檔案必須包含 Mozilla Public License 標頭。請恢復授權標頭。

**判斷依據**：diff 顯示刪除了以下三行：
- // This Source Code Form is subject to the terms of the Mozilla Public
- // License, v. 2.0. If a copy of the MPL was not distributed with this
- // file, You can obtain one at http://mozilla.org/MPL/2.0/

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:510</code> IpadOnlyTestCase.setUp 中誤用 await 呼叫 super.setUp()</summary>

在 IpadOnlyTestCase 的 setUp 中，呼叫 super.setUp() 時使用了 `await super.setUp()`，但 super.setUp() 是 async throws 函式，應使用 `try await super.setUp()`。這會導致編譯錯誤。

**判斷依據**：diff 中顯示：
-            super.setUp()
+            await super.setUp()
而 super.setUp() 的簽章已改為 `override func setUp() async throws`，因此必須使用 try await。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/TodayWidgetTests.swift:15</code> 全域變數標註 @MainActor 可能導致初始化時機問題</summary>

多個全域變數（如 goToCopiedLink、newPrivateSearch 等）從 `nonisolated(unsafe)` 改為 `@MainActor`。這些變數在檔案載入時即初始化，而 @MainActor 隔離的全域變數在 Swift 6 中可能延遲初始化，若在非主執行緒存取可能導致 crash 或資料競爭。請確認這些變數的存取皆在主執行緒，或考慮改為其他安全方式。

**判斷依據**：diff 顯示原本使用 nonisolated(unsafe)，現在改為 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48</code> setUp 中呼叫順序變更可能影響測試行為</summary>

原本的順序是 `setUpExperimentVariables()` 在 `setUpApp()` 之前，現在被調換為 `setUpApp()` 在前。如果 setUpExperimentVariables 依賴 setUpApp 所設定的某些狀態，或反之，此變更可能導致測試失敗。請確認此順序變更是有意為之且不會造成問題。

**判斷依據**：diff 顯示：
-        setUpExperimentVariables()
         setUpApp()
+        setUpExperimentVariables()
順序被調換。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/registerSettingsNavigation.swift:8</code> SwiftLint 停用註解位置可能失效</summary>

原本的 `// swiftlint:disable:next function_body_length` 被改為 `@MainActor // swiftlint:disable:next function_body_length`。SwiftLint 的 disable:next 指令必須單獨一行，若與其他程式碼在同一行可能無法正確停用規則，導致 lint 警告。建議將註解移至 @MainActor 的下一行。

**判斷依據**：diff 顯示此行變更。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 19348 (cache hit 19328) ｜ completion tokens 1356 ｜ PR #2</sub>