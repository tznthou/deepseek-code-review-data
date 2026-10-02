<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將多個測試類別的 setUp/tearDown 改為 async 版本，並為部分 UI 相關測試類別加上 @MainActor 標註，以符合 Swift 6 的 concurrency 要求。整體變更方向正確，但有一個測試斷言從 XCTest 的 XCTAssertTrue 改為 Swift 標準庫的 assert，這會導致測試在 release 建置中失效，且無法正確回報失敗，屬於必須修正的問題。

### Findings（1 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | [R06] 使用 assert 取代 XCTest 斷言導致測試失效 | 0.95 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> [R06] 使用 assert 取代 XCTest 斷言導致測試失效</summary>

在測試方法 `testRequestAuthorization` 中，原本使用 `XCTAssertTrue` 進行斷言，但被改為 Swift 標準庫的 `assert`。`assert` 在 release 建置中會被編譯器移除，且即使觸發也只會導致程式崩潰，不會被 XCTest 框架記錄為測試失敗。這會讓測試失去驗證功能，可能造成假性通過。

建議改回使用 `XCTAssertTrue` 或 `XCTAssert` 系列斷言。

**判斷依據**：diff 中將 `XCTAssertTrue(granted)` 改為 `assert(granted, ...)`，且 `XCTAssertTrue(self.center.requestAuthorizationWasCalled)` 改為 `assert(center?.requestAuthorizationWasCalled ?? false, ...)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9991 (cache hit 7936) ｜ completion tokens 439 ｜ PR #6</sub>