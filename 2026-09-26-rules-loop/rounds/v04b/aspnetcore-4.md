<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 Blazor 的 DisplayName 元件，可從 DisplayAttribute 或 DisplayNameAttribute 取得顯示名稱，並更新了多個專案範本以使用該元件。主要風險在於 DisplayName 元件在 For 參數變更時未重新渲染，可能導致顯示名稱過期；此外，ExpressionMemberAccessor 的快取在 Hot Reload 時僅清除成員快取，未清除顯示名稱快取，可能造成不一致。另有數個次要問題，包括缺少 XML 文件、命名空間風格不一致、測試方法缺少 Arrange-Act-Assert 註解，以及測試輔助方法可能因多個文字框架而失敗。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/DisplayName.cs:46` | For 參數變更時未重新渲染 | 0.85 |
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83` | Hot Reload 時未清除顯示名稱快取 | 0.80 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:26` | [R07] 缺少 XML 文件註解 | 0.90 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:9` | [R02] 應使用檔案範圍命名空間 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:159` | [R06] 測試方法缺少 Arrange-Act-Assert 註解 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:188` | 測試輔助方法可能因多個文字框架而失敗 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:46</code> For 參數變更時未重新渲染</summary>

在 `SetParametersAsync` 中，只有當 `For` 表達式與 `_previousFieldAccessor` 不同時才重新計算顯示名稱並渲染。然而，即使表達式相同，其引用的成員屬性值可能已變更（例如模型屬性名稱變更），但顯示名稱不會更新。建議移除 `_previousFieldAccessor` 檢查，或在每次 `SetParametersAsync` 時都重新計算並渲染。

**判斷依據**：diff 中第 44-52 行顯示僅在表達式變更時才渲染，未考慮屬性值變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83</code> Hot Reload 時未清除顯示名稱快取</summary>

`ClearCache` 方法僅清除 `_memberInfoCache`，未清除 `_displayNameCache`。若 Hot Reload 變更了屬性的顯示名稱（例如修改 DisplayAttribute），顯示名稱快取將保留舊值，導致顯示不正確。建議同時清除兩個快取。

**判斷依據**：diff 中第 79-82 行顯示僅清除成員快取。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:26</code> [R07] 缺少 XML 文件註解</summary>

公開類別 `DisplayName<TValue>` 的 `For` 屬性缺少 XML 文件註解。根據規範 R07，所有公開成員都應有文件。建議為 `For` 屬性添加 `<summary>` 說明。

**判斷依據**：diff 中第 25-26 行顯示 `For` 屬性沒有 XML 文件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:9</code> [R02] 應使用檔案範圍命名空間</summary>

檔案 `DisplayName.cs` 使用區塊範圍命名空間，但規範 R02 要求使用檔案範圍命名空間。建議改為 `namespace Microsoft.AspNetCore.Components.Forms;` 並移除大括號。

**判斷依據**：diff 中第 12 行顯示區塊範圍命名空間。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:159</code> [R06] 測試方法缺少 Arrange-Act-Assert 註解</summary>

測試方法 `SupportsLocalizationWithResourceType` 缺少 Arrange-Act-Assert 結構註解。根據規範 R06，測試方法應包含明確的結構註解。建議添加 `// Arrange`、`// Act`、`// Assert` 註解。

**判斷依據**：diff 中第 15-16 行顯示該方法沒有結構註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:188</code> 測試輔助方法可能因多個文字框架而失敗</summary>

`RenderAndGetOutput` 方法使用 `First(f => f.FrameType == RenderTree.RenderTreeFrameType.Text)` 取得文字框架，但若元件渲染多個文字框架（例如包含多個 DisplayName 元件），可能取到錯誤的文字。建議改用更精確的定位方式，例如透過元件參考或框架索引。

**判斷依據**：diff 中第 196-197 行顯示使用 `First` 取得文字框架。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11271 (cache hit 11264) ｜ completion tokens 1376 ｜ PR #4</sub>