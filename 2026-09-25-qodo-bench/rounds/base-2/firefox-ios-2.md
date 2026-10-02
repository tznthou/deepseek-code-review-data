<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 XCUITests 中的 setUp/tearDown 改為 async throws 並加上 @MainActor 標註，以符合 Swift 6 的 main actor isolation 要求。整體變更一致且範圍明確，但需注意 IpadOnlyTestCase 中呼叫 super.setUp() 未加 try await，可能導致編譯錯誤或行為不一致。此外，部分全域變數加上 @MainActor 可能影響其他未標註的程式碼，需確認編譯無誤。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508` | IpadOnlyTestCase 中呼叫 super.setUp() 缺少 try await | 0.90 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:12` | 全域變數加上 @MainActor 可能影響其他未標註的程式碼 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508</code> IpadOnlyTestCase 中呼叫 super.setUp() 缺少 try await</summary>

在 IpadOnlyTestCase 的 setUp() 中，呼叫 `super.setUp()` 時未加上 `try await`，但父類別的 setUp() 已改為 async throws。這會導致編譯錯誤，或若編譯器允許，則可能造成非同步呼叫未正確等待。建議改為 `try await super.setUp()`。

**判斷依據**：diff 中 IpadOnlyTestCase 的 setUp() 內 `await super.setUp()` 沒有 `try`，而其他類似類別如 IphoneOnlyTestCase 使用 `try await super.setUp()`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:12</code> 全域變數加上 @MainActor 可能影響其他未標註的程式碼</summary>

將 `urlBarAddress` 和 `homepageSearchBar` 加上 @MainActor 後，任何在非 main actor 環境中存取這些變數的程式碼都需要 await 或標註 @MainActor。需確認所有使用這些變數的地方都已正確處理，否則可能導致編譯錯誤。

**判斷依據**：diff 中新增 @MainActor 於全域變數，但未檢查所有使用點。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17289 (cache hit 17280) ｜ completion tokens 578 ｜ PR #2</sub>