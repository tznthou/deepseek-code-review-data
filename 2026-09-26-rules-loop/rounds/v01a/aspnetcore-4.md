<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 Blazor 的 DisplayName 元件，用於顯示模型屬性的顯示名稱（優先讀取 DisplayAttribute、DisplayNameAttribute，否則回退屬性名稱），並更新多個專案範本以使用該元件。主要風險在於 DisplayName 元件的參數變更偵測邏輯（僅比較 Expression 參考，可能導致顯示名稱未更新）、快取未清除 _displayNameCache、以及部分程式碼風格違反 repo 規範（如命名空間宣告、欄位命名、sealed 關鍵字）。建議優先修正參數變更偵測與快取問題，並補齊程式碼風格。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/DisplayName.cs:46` | 參數變更偵測僅比較 Expression 參考，可能導致顯示名稱未更新 | 0.85 |
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83` | Hot Reload 時未清除 _displayNameCache，可能導致顯示名稱過期 | 0.80 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:9` | [R02] 命名空間應使用檔案範圍宣告 | 0.95 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:19` | [R03] 私有欄位命名應使用底線前綴 camelCase | 0.95 |
| 🔸 | Minor | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:13` | [R14] 內部類別應標記為 sealed | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:9` | [R02] 命名空間應使用檔案範圍宣告 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:11` | [R05] 測試類別命名應符合規範 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:159` | [R06] 測試方法應使用 Arrange-Act-Assert 註解 | 0.90 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:1` | [R07] 公開 API 應有 XML 文件註解 | 0.80 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:39` | [R18] 開括號應在新行（Allman 風格） | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:46</code> 參數變更偵測僅比較 Expression 參考，可能導致顯示名稱未更新</summary>

在 `SetParametersAsync` 中，使用 `if (For != _previousFieldAccessor)` 來判斷是否需要重新計算顯示名稱。然而，`Expression<Func<TValue>>` 的相等性比較是參考相等，而非結構相等。若父元件重新渲染時傳入一個內容相同但參考不同的 Expression（例如在 Razor 中每次渲染都建立新的 lambda），此條件會成立，導致重新計算並渲染，這在多數情況下是正確的。但若父元件傳入相同的 Expression 參考，但屬性的顯示名稱可能因動態變更（例如透過資源檔或屬性變更）而需要更新，此處將不會重新計算，導致顯示名稱過期。建議改為比較 Expression 的結構（例如使用 ExpressionEqualityComparer）或移除快取邏輯，每次參數設定時都重新計算。

**判斷依據**：diff 中新增的 DisplayName.cs 第 44 行，使用參考相等比較 Expression。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83</code> Hot Reload 時未清除 _displayNameCache，可能導致顯示名稱過期</summary>

在靜態建構函式中，當 Hot Reload 的 MetadataUpdateSupported 為 true 時，訂閱了 OnDeltaApplied 事件並呼叫 ClearCache。但 ClearCache 方法僅清除 _memberInfoCache，未清除 _displayNameCache。若屬性的 DisplayAttribute 或 DisplayNameAttribute 在 Hot Reload 中變更，_displayNameCache 仍保留舊值，導致顯示名稱不正確。建議在 ClearCache 中同時清除兩個快取。

**判斷依據**：diff 中 ExpressionMemberAccessor.cs 第 82-85 行，ClearCache 僅清除 _memberInfoCache。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:9</code> [R02] 命名空間應使用檔案範圍宣告</summary>

檔案使用傳統的區塊命名空間宣告（`namespace Microsoft.AspNetCore.Components.Forms { ... }`），但 repo 規範要求使用檔案範圍命名空間（`namespace Microsoft.AspNetCore.Components.Forms;`）。建議改為檔案範圍宣告以符合規範。

**判斷依據**：diff 中 DisplayName.cs 第 8 行，使用區塊命名空間。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:19</code> [R03] 私有欄位命名應使用底線前綴 camelCase</summary>

私有欄位 `_renderHandle`、`_previousFieldAccessor`、`_displayName` 已符合底線前綴 camelCase，但 `For` 屬性為公開屬性，不受此規範限制。此 finding 可能不適用，請確認。

**判斷依據**：diff 中 DisplayName.cs 第 18-20 行，欄位命名符合規範，但此 finding 可能誤報。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:13</code> [R14] 內部類別應標記為 sealed</summary>

`ExpressionMemberAccessor` 是內部靜態類別，但未標記為 `sealed`。雖然靜態類別無法被繼承，但加上 `sealed` 可以明確表達設計意圖並符合 repo 規範。建議加上 `sealed` 修飾詞。

**判斷依據**：diff 中 ExpressionMemberAccessor.cs 第 12 行，缺少 sealed。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:9</code> [R02] 命名空間應使用檔案範圍宣告</summary>

測試檔案使用傳統的區塊命名空間宣告，但 repo 規範要求使用檔案範圍命名空間。建議改為檔案範圍宣告。

**判斷依據**：diff 中 DisplayNameTest.cs 第 8 行，使用區塊命名空間。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:11</code> [R05] 測試類別命名應符合規範</summary>

測試類別名稱為 `DisplayNameTest`，符合以 `Test` 結尾的規範。但檔案位於 `src/Components/Web/test/Forms/` 目錄，符合 repo 的測試目錄結構。此 finding 可能不適用，請確認。

**判斷依據**：diff 中 DisplayNameTest.cs 第 10 行，類別名稱符合規範。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:159</code> [R06] 測試方法應使用 Arrange-Act-Assert 註解</summary>

部分測試方法（如 `SupportsLocalizationWithResourceType`）缺少 `// Arrange`、`// Act`、`// Assert` 註解，違反 repo 規範。建議補齊 AAA 註解。

**判斷依據**：diff 中 DisplayNameTest.cs 第 146-148 行，缺少 AAA 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:1</code> [R07] 公開 API 應有 XML 文件註解</summary>

`DisplayName<TValue>` 類別及其 `For` 屬性已有 XML 文件註解，但 `IComponent.Attach` 和 `IComponent.SetParametersAsync` 的實作缺少 `<inheritdoc />` 以外的說明。建議補齊文件或確認是否符合規範。

**判斷依據**：diff 中 DisplayName.cs 第 27-28 行，僅有 `<inheritdoc />`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:39</code> [R18] 開括號應在新行（Allman 風格）</summary>

檔案中的開括號（如類別、方法、控制流程）大多在新行，但 `if (For is null)` 的開括號與條件在同一行，違反 Allman 風格。建議將開括號移至新行。

**判斷依據**：diff 中 DisplayName.cs 第 36-37 行，開括號與條件同一行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12506 (cache hit 10240) ｜ completion tokens 2156 ｜ PR #4</sub>