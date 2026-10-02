<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將多個測試類別的 setUp/tearDown 改為 async 版本，並為部分 UI 相關測試類別加上 @MainActor，以符合 Swift 6 的 concurrency 要求。同時調整了 Mock 類別的 Sendable 標註，並將一個測試中的 XCTAssertTrue 改為 assert。整體改動方向正確，但需注意 async setUp/tearDown 的呼叫順序、assert 在測試中的適用性，以及 @MainActor 標註的完整性。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | 使用 assert 取代 XCTAssertTrue 可能導致測試失效 | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:16` | async setUp 中呼叫 super.setUp() 的順序可能影響測試隔離 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/SyncContentSettingsViewControllerTests.swift:24` | async tearDown 中呼叫 super.tearDown() 的順序可能影響資源釋放 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11` | 移除 @MainActor 可能導致測試在背景執行緒執行 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93` | completion handler 標註 @Sendable 可能造成不必要的限制 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockUserNotificationCenter.swift:9` | Mock 類別加上 @unchecked Sendable 可能隱藏執行緒安全問題 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> 使用 assert 取代 XCTAssertTrue 可能導致測試失效</summary>

在測試方法 `testRequestAuthorization` 中，將原本的 `XCTAssertTrue` 改為 Swift 標準庫的 `assert`。`assert` 在 Release 建置中會被編譯器移除，且 XCTest 不會將其視為測試斷言，因此即使條件為 false，測試仍會通過。這會讓測試失去驗證功能。建議改回 `XCTAssertTrue`，或使用 `XCTAssert` 系列斷言。

**判斷依據**：diff 中將 `XCTAssertTrue(granted)` 改為 `assert(granted, ...)`，且 `assert` 不屬於 XCTest 框架。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:16</code> async setUp 中呼叫 super.setUp() 的順序可能影響測試隔離</summary>

在 `setUp() async throws` 中，先呼叫 `try await super.setUp()` 再進行其他設定。若 super.setUp() 中有非同步操作，可能導致測試狀態初始化延遲。建議確認 super.setUp() 的實作，或考慮在設定完成後再呼叫 super.setUp()（若允許）。

**判斷依據**：diff 顯示 `try await super.setUp()` 位於設定程式碼之前。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/SyncContentSettingsViewControllerTests.swift:24</code> async tearDown 中呼叫 super.tearDown() 的順序可能影響資源釋放</summary>

在 `tearDown() async throws` 中，先執行清理動作（如 `DependencyHelperMock().reset()`）再呼叫 `try await super.tearDown()`。若 super.tearDown() 依賴某些資源尚未釋放，可能導致問題。建議確認 super.tearDown() 的實作，或考慮先呼叫 super.tearDown() 再進行清理。

**判斷依據**：diff 顯示 `try await super.tearDown()` 位於清理程式碼之後。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11</code> 移除 @MainActor 可能導致測試在背景執行緒執行</summary>

此測試類別原本有 `@MainActor`，但在此 PR 中被移除。若測試中涉及 UI 相關操作（如建立 UITableView），可能需要在主執行緒執行。建議確認測試內容，若涉及 UI 則應保留 @MainActor。

**判斷依據**：diff 顯示 `@MainActor` 被移除。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93</code> completion handler 標註 @Sendable 可能造成不必要的限制</summary>

將 `getQueuedTabs` 的 completion handler 加上 `@Sendable`，這會要求閉包內捕獲的變數也必須是 Sendable。若呼叫端傳入的閉包捕獲了非 Sendable 的狀態，可能導致編譯錯誤。建議確認所有呼叫端是否相容，或考慮移除 @Sendable。

**判斷依據**：diff 中新增了 `@Sendable`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockUserNotificationCenter.swift:9</code> Mock 類別加上 @unchecked Sendable 可能隱藏執行緒安全問題</summary>

將 `MockUserNotificationCenter` 標註為 `@unchecked Sendable`，這會跳過編譯器的執行緒安全檢查。若此 Mock 在測試中被跨執行緒使用，可能導致資料競爭。建議確認使用情境，或考慮實作真正的 Sendable 保證。

**判斷依據**：diff 中新增了 `@unchecked Sendable`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10001 (cache hit 9984) ｜ completion tokens 1508 ｜ PR #6</sub>