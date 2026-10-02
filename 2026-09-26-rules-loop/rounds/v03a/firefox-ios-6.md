<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將多個 XCTest 測試類別從同步的 setUp/tearDown 遷移至 async throws 版本，並為部分 UI 相關測試類別加上 @MainActor 標註，以符合 Swift 6 的 concurrency 要求。此外，也調整了 Mock 類別的 Sendable 遵從性，並將一個 Mock 類別標記為 final。整體而言，變更方向正確，但需注意 async setUp/tearDown 中呼叫 super 的順序、@MainActor 標註的一致性，以及測試中改用 assert 可能造成的行為差異。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | 測試中改用 assert 可能導致測試在 Release 建置中失效 | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:16` | async setUp 中呼叫 super.setUp() 的順序可能影響測試狀態 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/SyncContentSettingsViewControllerTests.swift:24` | async tearDown 中呼叫 super.tearDown() 的順序可能影響資源釋放 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11` | 移除 @MainActor 可能導致測試在背景執行緒執行 UI 操作 | 0.60 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93` | completion handler 標註 @Sendable 可能造成不必要的限制 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> 測試中改用 assert 可能導致測試在 Release 建置中失效</summary>

將原本的 XCTAssertTrue 改為 Swift 標準庫的 assert，這在 Release 建置（-O）中會被編譯器移除，導致測試永遠通過，失去驗證效果。建議改回 XCTest 的斷言，或使用 XCTAssertTrue 並搭配適當的訊息。

**判斷依據**：diff 中將 XCTAssertTrue 改為 assert，且 assert 在 Release 模式下會被優化掉。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:16</code> async setUp 中呼叫 super.setUp() 的順序可能影響測試狀態</summary>

在 async setUp 中，先呼叫 try await super.setUp() 再進行其他設定。若 super.setUp() 中有非同步操作，可能導致後續設定延遲。建議確認 super.setUp() 的實作，或考慮將 super.setUp() 放在最後呼叫。

**判斷依據**：diff 顯示 setUp 改為 async throws，並先呼叫 super.setUp()。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/SyncContentSettingsViewControllerTests.swift:24</code> async tearDown 中呼叫 super.tearDown() 的順序可能影響資源釋放</summary>

在 async tearDown 中，先執行自訂清理再呼叫 try await super.tearDown()。若 super.tearDown() 中有非同步操作，可能導致資源釋放延遲。建議確認 super.tearDown() 的實作，或考慮將 super.tearDown() 放在最後呼叫。

**判斷依據**：diff 顯示 tearDown 改為 async throws，並在最後呼叫 super.tearDown()。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11</code> 移除 @MainActor 可能導致測試在背景執行緒執行 UI 操作</summary>

原本類別有 @MainActor 標註，但在此 PR 中被移除。若測試中有 UI 相關操作，可能導致執行緒安全問題。建議確認此測試類別是否真的不需要 @MainActor，或考慮保留標註。

**判斷依據**：diff 顯示移除了 @MainActor 標註。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93</code> completion handler 標註 @Sendable 可能造成不必要的限制</summary>

將 completion handler 標註為 @Sendable，但若 handler 內部不需要跨 actor 傳遞，可能造成不必要的限制。建議確認此變更是否為 Swift 6 編譯器要求，或可考慮其他解決方案。

**判斷依據**：diff 顯示新增 @Sendable 標註。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10011 (cache hit 7936) ｜ completion tokens 1229 ｜ PR #6</sub>