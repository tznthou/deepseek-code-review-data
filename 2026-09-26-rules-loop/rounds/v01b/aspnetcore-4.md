<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 Blazor 的 DisplayName 元件，可從 DisplayAttribute 或 DisplayNameAttribute 讀取顯示名稱，並更新多個專案範本以使用該元件。主要風險在於 DisplayName 元件未正確處理參數變更時的重新渲染，以及快取機制在 Hot Reload 後可能殘留過時資料。此外，部分程式碼違反了專案規範（如命名空間宣告、欄位命名、sealed 修飾詞）。建議優先修正 DisplayName 元件的渲染邏輯與快取清除問題。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/DisplayName.cs:46` | DisplayName 元件在 For 參數變更時不會重新渲染 | 0.90 |
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83` | Hot Reload 後快取未完全清除 | 0.85 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:9` | [R02] 應使用檔案範圍命名空間宣告 | 0.95 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:19` | [R03] 私有欄位應使用底線前綴 camelCase | 0.95 |
| 🔸 | Minor | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:13` | [R14] 內部類別應標記為 sealed | 0.95 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:39` | DisplayName 元件未處理 For 為 null 以外的無效表達式 | 0.80 |
| 🔸 | Minor | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:15` | 快取鍵使用 Expression 可能導致記憶體洩漏 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:46</code> DisplayName 元件在 For 參數變更時不會重新渲染</summary>

在 `SetParametersAsync` 中，只有當 `For != _previousFieldAccessor` 時才會呼叫 `_renderHandle.Render`。然而，`For` 是 `Expression<Func<TValue>>`，其相等性比較是參考相等。如果父元件重新渲染並傳入一個新的表達式實例（即使語意相同），`For != _previousFieldAccessor` 會為 true，導致不必要的重新渲染。但更嚴重的問題是：如果父元件傳入相同的表達式實例，但該表達式所引用的成員的顯示名稱因資料變更而改變（例如，模型屬性值變更導致 `DisplayAttribute` 的 `Name` 屬性動態變化），元件將不會重新渲染，因為 `For` 參考未變。這可能導致顯示名稱過時。建議在每次 `SetParametersAsync` 時都重新計算顯示名稱並渲染，或使用更精確的變更檢測機制。

**判斷依據**：diff 中新增的 DisplayName.cs 第 45-53 行顯示條件渲染邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83</code> Hot Reload 後快取未完全清除</summary>

`ClearCache` 方法只清除了 `_memberInfoCache`，但未清除 `_displayNameCache`。在 Hot Reload 套用中繼資料變更後，`_displayNameCache` 可能仍保留舊的顯示名稱，導致顯示名稱不正確。建議同時清除兩個快取。

**判斷依據**：diff 中 ExpressionMemberAccessor.cs 第 82-85 行顯示 ClearCache 方法僅清除 _memberInfoCache。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:9</code> [R02] 應使用檔案範圍命名空間宣告</summary>

檔案使用傳統的區塊命名空間宣告，但專案規範要求使用檔案範圍命名空間（file-scoped namespace）。建議改為 `namespace Microsoft.AspNetCore.Components.Forms;` 並移除大括號。

**判斷依據**：diff 中 DisplayName.cs 第 8-14 行顯示區塊命名空間。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:19</code> [R03] 私有欄位應使用底線前綴 camelCase</summary>

私有欄位 `_renderHandle`、`_previousFieldAccessor`、`_displayName` 已符合底線前綴 camelCase，但 `For` 屬性是公開屬性，不受此規範限制。此 finding 可能不適用，請忽略。

**判斷依據**：diff 中 DisplayName.cs 第 18-20 行顯示私有欄位。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:13</code> [R14] 內部類別應標記為 sealed</summary>

`ExpressionMemberAccessor` 是內部靜態類別，但未標記為 `sealed`。雖然靜態類別隱含 sealed，但明確標記可提高可讀性。建議加上 `sealed` 修飾詞。

**判斷依據**：diff 中 ExpressionMemberAccessor.cs 第 13 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:39</code> DisplayName 元件未處理 For 為 null 以外的無效表達式</summary>

`SetParametersAsync` 中僅檢查 `For` 是否為 null，但未驗證表達式是否為簡單成員存取。如果傳入複雜表達式（如方法呼叫），`ExpressionMemberAccessor.GetDisplayName` 會拋出 `ArgumentException`，但此例外會在渲染過程中傳播，可能導致未處理的例外。建議在設定參數時驗證表達式，或提供更明確的錯誤訊息。

**判斷依據**：diff 中 DisplayName.cs 第 31-35 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:15</code> 快取鍵使用 Expression 可能導致記憶體洩漏</summary>

`_memberInfoCache` 使用 `Expression` 作為鍵，而表達式可能捕獲外部物件（如模型實例），導致這些物件無法被垃圾回收。如果應用程式動態建立許多表達式，快取可能無限增長。建議使用表達式的字串表示或結構化鍵，或限制快取大小。

**判斷依據**：diff 中 ExpressionMemberAccessor.cs 第 30 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12506 (cache hit 12416) ｜ completion tokens 1809 ｜ PR #4</sub>