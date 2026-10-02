<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要刪除了兩個自動化測試（testCopyLink、testSetCustomURLAsHome），並對多個測試計畫檔移除對應的測試項目。同時調整了 ClipBoardTests 中三個輔助方法的存取層級為 public，以及修改 DisplaySettingsTests 中一個測試的斷言與 HomePageSettingsUITest 中一個測試的步驟順序。整體風險在於刪除測試可能降低覆蓋率，且 DisplaySettingsTests 的修改可能引入邏輯錯誤。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/DisplaySettingsTests.swift:53` | 測試斷言可能使用錯誤的 accessibility identifier | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/HomePageSettingsUITest.swift:155` | 測試步驟順序變更可能影響穩定性 | 0.60 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/XCUITests/ClipBoardTests.swift:11` | 輔助方法改為 public 可能違反封裝原則 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/DisplaySettingsTests.swift:53</code> 測試斷言可能使用錯誤的 accessibility identifier</summary>

在 `testCheckSystemThemeChanges` 中，原本檢查 `lightThemeView` 的 value，現在改為檢查 `darkThemeView`。但變數名稱仍為 `lightIsSelected`，且後續斷言 `XCTAssertEqual(lightIsSelected as? String, "1")` 可能與實際選取的主題不符。若測試目的是驗證選取 Light 模式後對應的按鈕狀態，應檢查 `lightThemeView` 而非 `darkThemeView`。建議確認此變更是否為預期，並修正變數名稱與斷言邏輯。

**判斷依據**：diff 中將 `lightThemeView` 改為 `darkThemeView`，但變數名稱未同步更新，且後續斷言仍使用 `lightIsSelected`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/HomePageSettingsUITest.swift:155</code> 測試步驟順序變更可能影響穩定性</summary>

在 `testDisableTopSitesSettingsRemovesSection` 中，原本先 `navigator.goto(NewTabScreen)` 再點擊 `Done`，現在改為先點擊 `Done` 再 `navigator.goto(NewTabScreen)`。此變更可能影響測試的時序，若 `Done` 按鈕的點擊需要在新分頁畫面出現後才能生效，可能導致測試不穩定。建議確認此順序調整是否為必要，並在 CI 中觀察測試結果。

**判斷依據**：diff 中將 `navigator.goto(NewTabScreen)` 移到 `app.buttons["Done"].waitAndTap()` 之後。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/ClipBoardTests.swift:11</code> 輔助方法改為 public 可能違反封裝原則</summary>

將 `checkUrl()`、`copyUrl()`、`checkCopiedUrl()` 三個方法從 internal 改為 public。這些方法僅在測試類別內部使用，若無外部呼叫需求，建議維持 internal 或改為 private，以符合最小暴露原則。

**判斷依據**：diff 中將三個方法的存取層級從無修飾改為 public。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6797 (cache hit 6784) ｜ completion tokens 876 ｜ PR #4</sub>