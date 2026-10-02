<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將多個測試類別的 setUp/tearDown 改為 async 版本，並為部分 UI 測試類別加上 @MainActor，以符合 Swift 6 的 concurrency 要求。整體改動方向正確，但 NotificationManagerTests 中將 XCTAssert 改為 assert 可能導致測試失效，且部分類別未加上 @MainActor 可能仍有執行緒安全疑慮。建議優先修正 assert 的使用，並確認所有 UI 相關測試類別都有 @MainActor 標註。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | [R06] 使用 assert 取代 XCTAssert 導致測試失效 | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/FxAWebViewModelTests.swift:14` | [R09] 測試類別未標註 @MainActor | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:26` | [R09] 測試類別未標註 @MainActor | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:96` | [R11] 屬性缺少明確的 access control | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> [R06] 使用 assert 取代 XCTAssert 導致測試失效</summary>

在測試方法中，將原本的 `XCTAssertTrue` 改為 Swift 標準庫的 `assert`。`assert` 在 Release 建置中會被編譯器移除，且即使觸發也只會 crash 而不會被 XCTest 視為測試失敗。這會導致測試永遠通過，失去驗證功能。請改回使用 `XCTAssertTrue` 或 `XCTAssert`。

**判斷依據**：diff 中將 `XCTAssertTrue(granted)` 改為 `assert(granted, ...)`，違反 R06 規範中「使用 XCTAssert family of assertions」的要求。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/FxAWebViewModelTests.swift:14</code> [R09] 測試類別未標註 @MainActor</summary>

此測試類別涉及 UI 相關的 ViewModel（FxAWebViewModel），但未加上 `@MainActor`。在 Swift 6 嚴格 concurrency 下，若 ViewModel 或相關 API 被標註為 @MainActor，測試方法可能需要在主執行緒執行。建議加上 `@MainActor` 以確保執行緒安全。

**判斷依據**：diff 中此類別未加上 @MainActor，而其他 UI 相關測試類別（如 StoriesFeedDiffableDataSourceTests）已加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:26</code> [R09] 測試類別未標註 @MainActor</summary>

此測試類別涉及 NotificationManager，可能與 UI 或 main actor 相關，但未加上 `@MainActor`。建議確認是否需要加上以避免 concurrency 問題。

**判斷依據**：diff 中此類別未加上 @MainActor，而其他 UI 相關測試類別已加上。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:96</code> [R11] 屬性缺少明確的 access control</summary>

`getQueuedTabsCalled` 屬性在 MockTabQueue 中似乎沒有明確的 access control 修飾詞。根據 R11，所有屬性應有明確的修飾詞（如 private、internal）。請確認此屬性是否需要加上 `private(set)` 或 `internal`。

**判斷依據**：diff 中顯示 `getQueuedTabsCalled` 被使用，但未見其宣告，可能缺少修飾詞。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9953 (cache hit 9856) ｜ completion tokens 993 ｜ PR #6</sub>