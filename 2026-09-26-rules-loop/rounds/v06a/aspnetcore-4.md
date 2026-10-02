<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 Blazor 的 DisplayName 元件，用於顯示模型屬性的顯示名稱，並更新多個專案範本以使用該元件。主要風險在於 DisplayName 元件在 For 參數變更時未重新渲染，可能導致 UI 顯示過時的名稱；此外，ExpressionMemberAccessor 的快取在 Hot Reload 時僅清除成員資訊快取，未清除顯示名稱快取，可能造成不一致。整體而言，功能方向正確，但需修正上述問題以確保正確性。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/DisplayName.cs:46` | For 參數變更時未重新渲染，導致顯示名稱過時 | 0.90 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:9` | [R02] 使用檔案範圍命名空間宣告 | 0.80 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:19` | [R03] 私有欄位未使用底線前綴 camelCase | 0.80 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:28` | [R07] 公開屬性 For 缺少 XML 文件註解 | 0.80 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:35` | [R08] 非同步方法未使用 Async 後綴 | 0.80 |
| 🔸 | Minor | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:13` | [R14] 內部類別未標記 sealed | 0.80 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:9` | [R02] 使用檔案範圍命名空間宣告 | 0.80 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:159` | [R06] 測試方法缺少 Arrange-Act-Assert 註解 | 0.80 |
| 🔸 | Minor | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83` | Hot Reload 時未清除顯示名稱快取，可能導致不一致 | 0.70 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:35` | [R10] 非同步方法未提供 CancellationToken 參數 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:46</code> For 參數變更時未重新渲染，導致顯示名稱過時</summary>

在 SetParametersAsync 中，僅當 For 表達式與 _previousFieldAccessor 不同時才重新計算顯示名稱並渲染。然而，即使表達式相同，若目標屬性的顯示名稱屬性在執行階段發生變化（例如透過動態變更屬性或資源檔更新），元件不會重新渲染，導致 UI 顯示舊名稱。建議在每次 SetParametersAsync 時都重新計算並渲染，或至少提供機制以偵測顯示名稱的變更。

**判斷依據**：diff 中 DisplayName.cs 第 44-52 行顯示條件渲染邏輯，僅在表達式變更時才更新。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:9</code> [R02] 使用檔案範圍命名空間宣告</summary>

檔案 DisplayName.cs 使用傳統的區塊範圍命名空間宣告（namespace Microsoft.AspNetCore.Components.Forms { ... }），違反規範 R02。建議改為檔案範圍命名空間宣告（namespace Microsoft.AspNetCore.Components.Forms;）。

**判斷依據**：diff 中 DisplayName.cs 第 8 行顯示區塊範圍命名空間。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:19</code> [R03] 私有欄位未使用底線前綴 camelCase</summary>

私有欄位 _renderHandle、_previousFieldAccessor、_displayName 使用底線前綴 camelCase，符合規範 R03。但請確認其他私有欄位也遵循此慣例。

**判斷依據**：diff 中 DisplayName.cs 第 17-19 行顯示欄位命名。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:28</code> [R07] 公開屬性 For 缺少 XML 文件註解</summary>

公開屬性 For 僅有 <summary> 標籤，但缺少 <param> 標籤描述參數。根據規範 R07，公開 API 應包含完整的 XML 文件註解，包括適用的 <param> 標籤。

**判斷依據**：diff 中 DisplayName.cs 第 25-29 行顯示 For 屬性的文件註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:35</code> [R08] 非同步方法未使用 Async 後綴</summary>

方法 IComponent.SetParametersAsync 回傳 Task，但名稱未以 Async 結尾。根據規範 R08，所有回傳 Task 的方法應使用 Async 後綴。然而，此方法為介面實作，無法變更名稱，建議在實作中保持介面名稱，但可考慮在文件或註解中說明。

**判斷依據**：diff 中 DisplayName.cs 第 31 行顯示方法簽章。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:13</code> [R14] 內部類別未標記 sealed</summary>

內部類別 ExpressionMemberAccessor 未標記為 sealed。根據規範 R14，內部實作類別應標記為 sealed 以防止意外繼承。建議加上 sealed 修飾詞。

**判斷依據**：diff 中 ExpressionMemberAccessor.cs 第 14 行顯示類別宣告。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:9</code> [R02] 使用檔案範圍命名空間宣告</summary>

檔案 DisplayNameTest.cs 使用傳統的區塊範圍命名空間宣告（namespace Microsoft.AspNetCore.Components.Forms;），違反規範 R02。建議改為檔案範圍命名空間宣告。

**判斷依據**：diff 中 DisplayNameTest.cs 第 8 行顯示命名空間宣告。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:159</code> [R06] 測試方法缺少 Arrange-Act-Assert 註解</summary>

測試方法 SupportsLocalizationWithResourceType 缺少明確的 // Arrange、// Act、// Assert 註解，違反規範 R06。建議加入結構化註解以提升可讀性。

**判斷依據**：diff 中 DisplayNameTest.cs 第 124-137 行顯示測試方法缺少 AAA 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83</code> Hot Reload 時未清除顯示名稱快取，可能導致不一致</summary>

ClearCache 方法僅清除 _memberInfoCache，未清除 _displayNameCache。若 Hot Reload 期間屬性的顯示名稱屬性變更，快取中仍保留舊的顯示名稱，導致元件顯示過時資訊。建議同時清除 _displayNameCache。

**判斷依據**：diff 中 ExpressionMemberAccessor.cs 第 78-81 行顯示 ClearCache 僅清除 _memberInfoCache。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:35</code> [R10] 非同步方法未提供 CancellationToken 參數</summary>

方法 IComponent.SetParametersAsync 未提供 CancellationToken 參數。根據規範 R10，公開非同步方法應包含 CancellationToken 參數。但此方法為介面實作，無法變更簽章，建議在實作中忽略此規範。

**判斷依據**：diff 中 DisplayName.cs 第 31 行顯示方法簽章。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12496 (cache hit 10240) ｜ completion tokens 2181 ｜ PR #4</sub>