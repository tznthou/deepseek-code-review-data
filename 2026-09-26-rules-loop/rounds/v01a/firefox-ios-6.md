<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將多個測試類別的 setUp/tearDown 改為 async throws 版本，並為部分 UI 相關測試類別加上 @MainActor，以符合 Swift 6 的並發要求。同時調整了 NotificationManagerTests 中的斷言寫法，以及將 MockURLAuthenticationChallengeSender 標記為 final。整體改動方向正確，但需注意 setUp/tearDown 中呼叫 super 的順序、@MainActor 標註的一致性，以及 NotificationManagerTests 中斷言可能失效的風險。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | 測試斷言可能失效：使用 assert 而非 XCTAssert | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:26` | 捕獲列表使用 [center] 可能造成強引用循環 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:16` | setUp 中呼叫 super 的順序可能導致問題 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11` | 移除 @MainActor 可能導致並發問題 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93` | completion handler 標註 @Sendable 可能導致不必要的限制 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockUserNotificationCenter.swift:9` | 標註 @unchecked Sendable 可能隱藏並發問題 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> 測試斷言可能失效：使用 assert 而非 XCTAssert</summary>

在測試方法中將原本的 `XCTAssertTrue` 改為 `assert`，這會導致在 Release 建置（或啟用最佳化）時斷言被移除，測試將無法驗證行為。此外，`assert` 失敗時會直接終止程式，而非記錄測試失敗，這會使測試結果不準確。建議改回使用 `XCTAssertTrue` 或 `XCTAssertEqual`。

**判斷依據**：diff 中將原本的 `XCTAssertTrue(granted)` 和 `XCTAssertTrue(self.center.requestAuthorizationWasCalled)` 改為 `assert`，這會使測試在 Release 模式下失去驗證能力。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:26</code> 捕獲列表使用 [center] 可能造成強引用循環</summary>

閉包捕獲列表使用 `[center]`，但 `center` 是 `self.center` 的屬性，若 `self` 持有該閉包，可能形成強引用循環。建議使用 `[weak self]` 並在閉包內安全解包，或直接使用 `self?.center`。

**判斷依據**：diff 中將原本的 `{ (granted, error) in` 改為 `{ [center] (granted, error) in`，捕獲了 `center` 屬性，但未見弱化處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:16</code> setUp 中呼叫 super 的順序可能導致問題</summary>

在 `setUp() async throws` 中，先呼叫 `try await super.setUp()` 再進行其他設定。若 super 的實作依賴於某些狀態，或後續設定可能拋出錯誤，建議將 super 呼叫放在最後，以確保測試環境完全準備好。

**判斷依據**：diff 中顯示 `super.setUp()` 被移至方法開頭，但其他測試類別（如 RatingPromptManagerTests）則將 super 呼叫放在最後，順序不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11</code> 移除 @MainActor 可能導致並發問題</summary>

原本類別標註了 `@MainActor`，但此次移除。若該類別或其方法涉及 UI 操作，移除後可能導致背景執行緒更新 UI 的風險。請確認此測試類別是否真的不需要 @MainActor。

**判斷依據**：diff 中刪除了 `@MainActor` 標註，但未提供理由。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93</code> completion handler 標註 @Sendable 可能導致不必要的限制</summary>

將 `completion` 參數標註為 `@Sendable`，這會要求閉包必須是 Sendable，可能導致呼叫端需要額外處理。若此閉包僅在主執行緒呼叫，可能不需要 @Sendable。請確認此變更是否必要。

**判斷依據**：diff 中新增了 `@Sendable` 標註。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockUserNotificationCenter.swift:9</code> 標註 @unchecked Sendable 可能隱藏並發問題</summary>

將類別標註為 `@unchecked Sendable` 會跳過編譯器的並發安全檢查，若此類別實際上非執行緒安全，可能導致資料競爭。建議確認其內部狀態是否真的安全，或改用更精確的並發控制。

**判斷依據**：diff 中新增了 `@unchecked Sendable`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10001 (cache hit 7936) ｜ completion tokens 1491 ｜ PR #6</sub>