<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 XCUITests 套件中的 setUp/tearDown 改為 async throws 並加上 @MainActor 標註，以符合 Swift 6 的 main actor isolation 要求。整體改動方向正確，但存在兩個主要風險：IpadOnlyTestCase.setUp 中呼叫 super.setUp() 缺少 try 關鍵字，可能導致編譯錯誤；A11yUtils.swift 移除了 Mozilla Public License 標頭，違反專案規範 R01。建議修正後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:112` | [R06] IpadOnlyTestCase.setUp 呼叫 async super.setUp() 缺少 try | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1` | [R01] 移除 Mozilla Public License 標頭 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:112</code> [R06] IpadOnlyTestCase.setUp 呼叫 async super.setUp() 缺少 try</summary>

在 `IpadOnlyTestCase` 的 `setUp()` 中，`super.setUp()` 現在是 async throws 方法，但呼叫時沒有加上 `try`。這會導致編譯錯誤：`call can throw but is not marked with 'try'`。

建議改為 `try await super.setUp()`。

**判斷依據**：diff 中 `IpadOnlyTestCase` 的 `setUp` 內：`-            super.setUp()` 改為 `+            await super.setUp()`，但未加 `try`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/A11yUtils.swift:1</code> [R01] 移除 Mozilla Public License 標頭</summary>

此檔案原本有 Mozilla Public License 標頭，但在此 PR 中被移除。根據專案規範 R01，所有 Swift 檔案必須包含此標頭。

建議恢復標頭。

**判斷依據**：diff 顯示刪除了三行 MPL 標頭，且未在檔案開頭重新加入。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 19348 (cache hit 17280) ｜ completion tokens 539 ｜ PR #2</sub>