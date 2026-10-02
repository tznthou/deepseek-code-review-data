<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 Blazor 的 DisplayName 元件，用於顯示模型屬性的顯示名稱，並更新了多個專案範本以使用該元件。主要風險在於 DisplayName 元件的實作細節：快取機制可能導致記憶體洩漏、參數變更時未重新渲染、以及缺少對非成員存取運算式的處理。此外，部分測試方法未遵循 AAA 模式，且 E2E 測試可能因資源檔問題而失敗。建議優先修正 DisplayName 元件的快取與渲染邏輯，並補齊測試結構。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:15` | 快取未清除可能導致記憶體洩漏 | 0.80 |
| ⚠️ | Major | `src/Components/Web/src/Forms/DisplayName.cs:46` | 參數變更時未重新渲染 | 0.75 |
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:42` | 未處理非成員存取運算式 | 0.70 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:159` | [R06] 測試方法未遵循 Arrange-Act-Assert 模式 | 0.90 |
| 🔸 | Minor | `src/Components/test/E2ETest/Tests/FormsTest.cs:580` | E2E 測試可能因資源檔問題而失敗 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:15</code> 快取未清除可能導致記憶體洩漏</summary>

`_memberInfoCache` 和 `_displayNameCache` 是靜態 ConcurrentDictionary，但 `ClearCache` 方法僅清除 `_memberInfoCache`，未清除 `_displayNameCache`。在 Hot Reload 或動態載入情境下，舊的 MemberInfo 可能仍被快取，導致記憶體洩漏或顯示過時的名稱。建議在 `ClearCache` 中同時清除兩個快取。

**判斷依據**：diff 中新增的 `ClearCache` 方法僅呼叫 `_memberInfoCache.Clear()`，未處理 `_displayNameCache`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:46</code> 參數變更時未重新渲染</summary>

在 `SetParametersAsync` 中，僅當 `For` 表達式與 `_previousFieldAccessor` 不同時才重新計算並渲染。若 `For` 表達式相同但其他參數（如 `ChildContent`）變更，元件不會重新渲染，可能導致 UI 未更新。建議移除 `_previousFieldAccessor` 檢查，或改為比較所有參數。

**判斷依據**：diff 中顯示僅在表達式變更時才呼叫 `_renderHandle.Render`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:42</code> 未處理非成員存取運算式</summary>

`GetMemberInfo` 方法僅處理 `MemberExpression`，若傳入的運算式不是成員存取（例如方法呼叫或常數），會拋出 `ArgumentException`。但此例外未在 `DisplayName` 元件中捕獲，可能導致元件渲染失敗。建議在元件中捕獲並提供更友善的錯誤訊息，或放寬限制。

**判斷依據**：diff 中顯示僅支援 MemberExpression，且未在呼叫端處理例外。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:159</code> [R06] 測試方法未遵循 Arrange-Act-Assert 模式</summary>

`SupportsLocalizationWithResourceType` 測試方法缺少明確的 `// Arrange`、`// Act`、`// Assert` 註解，違反了專案規範 R06。建議補齊三段式註解以提升可讀性。

**判斷依據**：diff 中該方法缺少 AAA 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/test/E2ETest/Tests/FormsTest.cs:580</code> E2E 測試可能因資源檔問題而失敗</summary>

E2E 測試 `DisplayNameReadsAttributesCorrectly` 檢查本地化標籤時，預期顯示 "Product Name"，但若測試環境的語言不是英文，或資源檔未正確載入，測試可能失敗。建議在測試中明確設定文化特性，或使用不依賴本地化的屬性。

**判斷依據**：diff 中顯示測試依賴於資源檔的英文內容。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12506 (cache hit 1536) ｜ completion tokens 1431 ｜ PR #4</sub>