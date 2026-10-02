<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 XCUITests 中的 setUp/tearDown 改為 async throws 並加上 @MainActor 標註，以符合 Swift 6 的 main actor isolation 要求。整體改動方向正確，但 IpadOnlyTestCase 的 setUp 中呼叫 super.setUp() 未使用 try await，可能導致編譯錯誤或行為不一致。此外，A11yUtils.swift 移除了 MPL 授權標頭，違反專案規範 R01。建議修正上述問題後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508` | IpadOnlyTestCase 的 setUp 中呼叫 super.setUp() 未使用 try await | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1` | [R01] 移除 MPL 授權標頭 | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508` | IpadOnlyTestCase 的 setUp 中呼叫 super.setUp() 未使用 try | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508</code> IpadOnlyTestCase 的 setUp 中呼叫 super.setUp() 未使用 try await</summary>

在 `IpadOnlyTestCase` 的 `setUp()` 中，呼叫 `super.setUp()` 時未加上 `try await`。由於 `BaseTestCase` 的 `setUp()` 已改為 `async throws`，此處會導致編譯錯誤（缺少 await）或未正確處理錯誤。建議改為 `try await super.setUp()`。

**判斷依據**：diff 中 IpadOnlyTestCase 的 setUp 內：
```
-            super.setUp()
+            await super.setUp()
```
但實際 diff 顯示為 `await super.setUp()`，未使用 `try`，且未處理 throws。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1</code> [R01] 移除 MPL 授權標頭</summary>

此檔案原本包含 Mozilla Public License 標頭，但在此 PR 中被移除。根據專案規範 R01，所有 Swift 檔案必須包含 MPL 授權標頭。請恢復授權標頭。

**判斷依據**：diff 顯示刪除了以下三行：
```
-// This Source Code Form is subject to the terms of the Mozilla Public
-// License, v. 2.0. If a copy of the MPL was not distributed with this
-// file, You can obtain one at http://mozilla.org/MPL/2.0/
```

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508</code> IpadOnlyTestCase 的 setUp 中呼叫 super.setUp() 未使用 try</summary>

在 `IpadOnlyTestCase` 的 `setUp()` 中，呼叫 `super.setUp()` 時未加上 `try`。由於 `BaseTestCase` 的 `setUp()` 已改為 `throws`，此處應使用 `try await` 來處理可能的錯誤。建議改為 `try await super.setUp()`。

**判斷依據**：diff 中 IpadOnlyTestCase 的 setUp 內：
```
-            super.setUp()
+            await super.setUp()
```
未使用 `try`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 18136 (cache hit 18048) ｜ completion tokens 851 ｜ PR #2</sub>