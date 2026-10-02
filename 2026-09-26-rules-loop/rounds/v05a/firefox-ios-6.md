<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將多個測試類別的 setUp/tearDown 改為 async 版本，並為部分 UI 相關測試類別加上 @MainActor，以符合 Swift 6 的 concurrency 要求。改動範圍廣泛但模式一致，風險主要在於 async setUp/tearDown 的執行順序與 @MainActor 標註是否正確。另外，NotificationManagerTests 中將 XCTAssert 改為 assert，可能導致測試失效。整體而言，改動方向正確，但需確認測試邏輯未被破壞。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | 使用 assert 取代 XCTAssert 可能導致測試失效 | 0.90 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93` | completion handler 標註 @Sendable 可能造成不必要的限制 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockUserNotificationCenter.swift:9` | Mock 類別加上 @unchecked Sendable 可能隱藏執行緒安全問題 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:16` | setUp 改為 async 後，super.setUp 呼叫順序可能影響測試 | 0.60 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11` | 移除 @MainActor 可能導致測試在背景執行緒執行 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> 使用 assert 取代 XCTAssert 可能導致測試失效</summary>

在 testRequestAuthorization 中，原本使用 XCTAssertTrue 進行斷言，現在改為 assert。在 XCTest 中，assert 來自 Swift 標準庫，在 debug 模式下會中止程式，但在 release 模式下會被忽略。測試 target 通常以 debug 模式建置，因此 assert 仍會執行，但若測試以 release 模式執行，斷言將不會生效。此外，assert 失敗時不會產生 XCTest 的失敗記錄，而是直接 crash，這會讓測試結果難以診斷。建議改回 XCTAssertTrue 或使用 XCTFail 搭配條件判斷。

**判斷依據**：diff 中將原本的 XCTAssertTrue(granted) 和 XCTAssertTrue(self.center.requestAuthorizationWasCalled) 改為 assert(...)。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93</code> completion handler 標註 @Sendable 可能造成不必要的限制</summary>

getQueuedTabs 的 completion handler 從 @escaping @MainActor ([ShareItem]) -> Void 改為 @MainActor @Sendable @escaping ([ShareItem]) -> Void。新增 @Sendable 可能導致呼叫端必須傳入 Sendable closure，若原本的 closure 捕獲非 Sendable 狀態，會產生編譯錯誤。此處為 mock，影響有限，但需確認所有使用此 mock 的測試仍能編譯。

**判斷依據**：diff 中新增 @Sendable 標註。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockUserNotificationCenter.swift:9</code> Mock 類別加上 @unchecked Sendable 可能隱藏執行緒安全問題</summary>

MockUserNotificationCenter 被加上 @unchecked Sendable，這表示編譯器不會檢查其內部狀態的執行緒安全。若此 mock 在多執行緒環境下被使用，可能導致資料競爭。但此為測試 mock，通常只在單一執行緒使用，風險較低。建議確認是否有必要加上此標註，或改用 actor 或鎖定機制。

**判斷依據**：diff 中新增 @unchecked Sendable。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:16</code> setUp 改為 async 後，super.setUp 呼叫順序可能影響測試</summary>

原本 setUpWithError 中先呼叫 super.setUpWithError() 再進行設定，現在改為 async setUp 並先呼叫 try await super.setUp()。在 XCTest 中，async setUp 的 super 呼叫必須在進行其他設定之前，此處順序正確。但需注意若 super.setUp 失敗，後續設定不會執行，這與原本行為一致。

**判斷依據**：diff 中 setUp 改為 async throws 並呼叫 super.setUp()。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11</code> 移除 @MainActor 可能導致測試在背景執行緒執行</summary>

原本 EditBookmarkViewModelTests 有 @MainActor 標註，現在被移除。若此測試類別中的程式碼涉及 UI 或需要主執行緒，移除後可能導致測試在背景執行緒執行而失敗。需確認此測試類別是否真的不需要 @MainActor。

**判斷依據**：diff 中移除了 @MainActor 標註。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9953 (cache hit 7936) ｜ completion tokens 1306 ｜ PR #6</sub>