<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 Blazor 的 DisplayName 元件，用於顯示模型屬性的顯示名稱，並整合了 DisplayAttribute 與 DisplayNameAttribute 的讀取邏輯。整體設計合理，但存在幾個關鍵問題：DisplayName 元件在 For 參數變更時未重新渲染，可能導致顯示名稱過期；ExpressionMemberAccessor 的快取未在 Hot Reload 時清除顯示名稱快取，可能造成中繼資料更新後顯示舊值；此外，部分專案範本中的標籤缺少 class 屬性，可能影響樣式一致性。建議優先修正渲染邏輯與快取清除問題。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/DisplayName.cs:46` | For 參數變更時未重新渲染 | 0.90 |
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83` | Hot Reload 時未清除顯示名稱快取 | 0.85 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:9` | [R02] 應使用檔案範圍命名空間宣告 | 0.80 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:19` | [R03] 私有欄位命名不符合底線前綴慣例 | 0.80 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:26` | [R07] 公開屬性 For 缺少 XML 文件 | 0.70 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:11` | [R05] 測試類別命名不符合慣例 | 0.70 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:14` | [R06] 測試方法缺少 Arrange-Act-Assert 註解 | 0.70 |
| 🔸 | Minor | `src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Login.razor:35` | 標籤缺少 class 屬性可能影響樣式 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:46</code> For 參數變更時未重新渲染</summary>

在 `SetParametersAsync` 中，僅當 `For != _previousFieldAccessor` 時才重新計算顯示名稱並渲染。然而，`For` 是 `Expression<Func<TValue>>`，其相等性比較是參考相等。若父元件重新渲染並傳入一個新的表達式實例（即使語意相同），此條件會成立並重新渲染，這可能導致不必要的渲染。但更嚴重的問題是：若 `For` 參數未變更（參考相同），但顯示名稱的來源（例如屬性上的 `DisplayAttribute`）因動態變更而需要更新時，元件不會重新渲染。例如，若使用本地化且文化特性變更，顯示名稱可能不會更新。建議移除 `_previousFieldAccessor` 檢查，或在每次 `SetParametersAsync` 時都重新計算並渲染，以確保顯示名稱始終反映最新狀態。

**判斷依據**：diff 中新增的 `DisplayName.cs` 第 44-52 行顯示了條件渲染邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83</code> Hot Reload 時未清除顯示名稱快取</summary>

`ClearCache` 方法僅清除 `_memberInfoCache`，但未清除 `_displayNameCache`。當 Hot Reload 套用中繼資料更新（例如變更屬性的 `DisplayAttribute`）時，`_displayNameCache` 中舊的顯示名稱仍會被使用，導致顯示過期的名稱。建議在 `ClearCache` 中同時清除 `_displayNameCache`。

**判斷依據**：diff 中 `ExpressionMemberAccessor.cs` 第 80-83 行顯示 `ClearCache` 僅清除 `_memberInfoCache`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:9</code> [R02] 應使用檔案範圍命名空間宣告</summary>

此檔案使用了傳統的區塊範圍命名空間宣告，但專案規範要求使用檔案範圍命名空間（file-scoped namespace）。建議改為 `namespace Microsoft.AspNetCore.Components.Forms;` 並移除大括號。

**判斷依據**：diff 中 `DisplayName.cs` 第 1-8 行顯示了區塊範圍命名空間。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:19</code> [R03] 私有欄位命名不符合底線前綴慣例</summary>

私有欄位 `_renderHandle`、`_previousFieldAccessor`、`_displayName` 已使用底線前綴，符合規範。但 `For` 屬性為公開屬性，不受此規範限制。此 finding 可能不成立，請忽略。

**判斷依據**：diff 中 `DisplayName.cs` 第 17-19 行顯示了私有欄位。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:26</code> [R07] 公開屬性 For 缺少 XML 文件</summary>

公開屬性 `For` 缺少 XML 文件註解。雖然類別有文件，但屬性本身應有 `<summary>` 說明其用途。建議新增文件以符合規範。

**判斷依據**：diff 中 `DisplayName.cs` 第 30-31 行顯示了 `For` 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:11</code> [R05] 測試類別命名不符合慣例</summary>

測試類別 `DisplayNameTest` 未以 `Tests` 結尾。根據規範，測試類別應遵循命名慣例，例如 `DisplayNameTests`。建議重新命名以符合規範。

**判斷依據**：diff 中 `DisplayNameTest.cs` 第 10 行顯示了類別宣告。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:14</code> [R06] 測試方法缺少 Arrange-Act-Assert 註解</summary>

測試方法 `ThrowsIfNoForParameterProvided` 缺少明確的 `// Arrange`、`// Act`、`// Assert` 註解。雖然有部分註解，但未完整遵循規範。建議補齊結構化註解。

**判斷依據**：diff 中 `DisplayNameTest.cs` 第 15-33 行顯示了測試方法。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Login.razor:35</code> 標籤缺少 class 屬性可能影響樣式</summary>

在 `Login.razor` 中，密碼欄位的 `<label>` 元素缺少 `class="form-label"`，而其他欄位都有。這可能導致樣式不一致。建議補上 `class="form-label"`。

**判斷依據**：diff 中 `Login.razor` 第 31-33 行顯示了密碼欄位的標籤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11271 (cache hit 10240) ｜ completion tokens 2132 ｜ PR #4</sub>