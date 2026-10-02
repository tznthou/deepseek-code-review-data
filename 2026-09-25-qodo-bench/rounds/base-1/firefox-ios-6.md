<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試類別從同步 setUp/tearDown 遷移至 async 版本，並加上 @MainActor 標註，以符合 Swift 6 的 concurrency 要求。整體變更一致且風險低，但 NotificationManagerTests 中將 XCTAssertTrue 改為 assert 會導致測試在 release 建置中失效，且失去 XCTest 的失敗報告功能，應改回 XCTAssertTrue。

### Findings（1 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | 使用 assert 取代 XCTAssertTrue 會使測試在 release 建置中失效 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> 使用 assert 取代 XCTAssertTrue 會使測試在 release 建置中失效</summary>

在測試方法中，將 `XCTAssertTrue` 改為 `assert` 會導致斷言在 release 建置（`-O` 或 `-Ounchecked`）中被編譯器移除，使得測試永遠通過，無法驗證行為。此外，`assert` 失敗時會直接 crash 而非記錄測試失敗，破壞 XCTest 的報告機制。

建議改回 `XCTAssertTrue`，並保留原本的訊息參數。

**判斷依據**：diff 中將原本的 `XCTAssertTrue(granted)` 和 `XCTAssertTrue(self.center.requestAuthorizationWasCalled)` 改為 `assert(...)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7942 (cache hit 1536) ｜ completion tokens 396 ｜ PR #6</sub>