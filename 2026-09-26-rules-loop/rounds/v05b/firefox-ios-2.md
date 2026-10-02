<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 XCUITests 套件中的 setUp/tearDown 改為 async throws，並為多個 UI 相關的全域變數與函式加上 @MainActor 標註，以符合 Swift 6 的 main actor isolation 要求。整體改動方向正確，但存在兩個主要風險：IpadOnlyTestCase.setUp 中呼叫 super.setUp() 時漏掉 try，可能導致編譯錯誤；A11yUtils.swift 移除了 MPL 授權標頭，違反專案規範。建議修正後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508` | IpadOnlyTestCase.setUp 呼叫 async super.setUp() 時缺少 try | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1` | [R01] 移除 Mozilla Public License 標頭 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508</code> IpadOnlyTestCase.setUp 呼叫 async super.setUp() 時缺少 try</summary>

在 `IpadOnlyTestCase` 的 `setUp()` 中，`super.setUp()` 現在是 `async throws`，但呼叫處只寫了 `await super.setUp()`，沒有加上 `try`。這會導致編譯錯誤：`call can throw but is not marked with 'try'`。

建議改為 `try await super.setUp()`。

**判斷依據**：diff 中 BaseTestCase.swift 的 IpadOnlyTestCase.setUp 區塊：
```
-            super.setUp()
+            await super.setUp()
```
而 super.setUp() 的簽名已改為 `override func setUp() async throws`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1</code> [R01] 移除 Mozilla Public License 標頭</summary>

此檔案原本有 MPL 2.0 授權標頭，但在此 PR 中被刪除。根據專案規範 R01，所有 Swift 檔案必須包含標準 MPL 標頭。

請恢復授權標頭。

**判斷依據**：diff 中 A11yUtils.swift 的開頭：
```
-// This Source Code Form is subject to the terms of the Mozilla Public
-// License, v. 2.0. If a copy of the MPL was not distributed with this
-// file, You can obtain one at http://mozilla.org/MPL/2.0/
-
 import XCTest
```

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 19300 (cache hit 19200) ｜ completion tokens 670 ｜ PR #2</sub>