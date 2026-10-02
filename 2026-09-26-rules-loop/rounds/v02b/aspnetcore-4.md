<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 Blazor 的 DisplayName 元件，可從 DisplayAttribute 或 DisplayNameAttribute 讀取顯示名稱，並更新多個專案範本以使用該元件。主要風險在於 DisplayName 元件的快取機制可能導致 Hot Reload 後顯示名稱未更新，以及部分範本中缺少 [Display] 屬性可能造成回歸。建議先修正快取清除邏輯，並補齊範本中的屬性。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83` | Hot Reload 後顯示名稱可能未更新 | 0.90 |
| ⚠️ | Major | `src/Components/Web/src/Forms/DisplayName.cs:9` | [R02] 使用傳統命名空間宣告而非檔案範圍命名空間 | 0.85 |
| ⚠️ | Major | `src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Login.razor:34` | 缺少 [Display] 屬性可能導致顯示名稱回歸 | 0.85 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:16` | 類別未標記為 sealed | 0.80 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:19` | 欄位命名不符合規範 | 0.75 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:39` | 參數驗證可改用 ThrowHelper | 0.70 |
| 🔸 | Minor | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:18` | 靜態建構函式訂閱 HotReload 事件可能導致記憶體洩漏 | 0.70 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:11` | [R05] 測試類別命名不符合規範 | 0.70 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:13` | [R06] 測試方法缺少 Arrange-Act-Assert 註解 | 0.70 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:188` | 測試輔助方法可能無法正確取得文字內容 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83</code> Hot Reload 後顯示名稱可能未更新</summary>

`ClearCache` 方法僅清除 `_memberInfoCache`，未清除 `_displayNameCache`。當 Hot Reload 套用中繼資料變更（例如修改屬性的 `[Display]` 屬性）時，`_displayNameCache` 仍保留舊的顯示名稱，導致 UI 顯示過時資訊。

**失敗情境**：開發者在 Hot Reload 期間變更屬性的 `[Display(Name = "...")]` 值，重新載入後元件仍顯示舊名稱。

**建議**：在 `ClearCache` 中同時清除 `_displayNameCache`。

**判斷依據**：diff 中 `ClearCache` 方法只呼叫 `_memberInfoCache.Clear()`，未清除 `_displayNameCache`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:9</code> [R02] 使用傳統命名空間宣告而非檔案範圍命名空間</summary>

此檔案使用傳統的區塊式命名空間宣告（`namespace Microsoft.AspNetCore.Components.Forms { ... }`），違反專案規範 R02。應改為檔案範圍命名空間（`namespace Microsoft.AspNetCore.Components.Forms;`）。

**判斷依據**：diff 中顯示 `namespace Microsoft.AspNetCore.Components.Forms` 後有 `{`，而非分號。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Login.razor:34</code> 缺少 [Display] 屬性可能導致顯示名稱回歸</summary>

在 `Login.razor` 中，`Input.Password` 屬性原本有標籤「Password」，但未新增 `[Display(Name = "Password")]`。使用 `<DisplayName For="() => Input.Password" />` 後，若無 Display 屬性，將回退到屬性名稱「Password」，可能仍正確，但若屬性名稱與顯示名稱不同（例如「Password」與「Password」相同），則無影響。然而，其他範本如 `Register.razor` 的 `Input.ConfirmPassword` 原本標籤為「Confirm Password」，但屬性名稱為 `ConfirmPassword`，若未加 `[Display]`，將顯示「ConfirmPassword」而非「Confirm Password」，造成回歸。

**判斷依據**：diff 中顯示 `Input.Password` 未新增 `[Display]` 屬性，而其他檔案如 `Register.razor` 的 `Input.ConfirmPassword` 也未新增，但原本標籤為「Confirm Password」。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:16</code> 類別未標記為 sealed</summary>

`DisplayName<TValue>` 是公開類別，但未標記為 `sealed`。雖然它可能被視為可擴充的元件，但根據專案規範 R14，內部實作類別應為 sealed。此處為公開 API，可能不適用，但若無意讓使用者繼承，建議加上 `sealed`。

**判斷依據**：diff 中類別宣告為 `public class DisplayName<TValue> : IComponent`，沒有 `sealed` 修飾詞。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:19</code> 欄位命名不符合規範</summary>

私有欄位 `_renderHandle`、`_previousFieldAccessor`、`_displayName` 使用底線前綴加 camelCase，符合規範 R03。但 `_previousFieldAccessor` 和 `_displayName` 未初始化，可能導致 null 參考。建議在宣告時初始化或使用 nullable 並檢查。

**判斷依據**：diff 中欄位宣告未初始化。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:39</code> 參數驗證可改用 ThrowHelper</summary>

在 `SetParametersAsync` 中，對 `For` 為 null 的檢查使用手動拋出 `InvalidOperationException`。雖然不是 `ArgumentNullException`，但可考慮使用 `ArgumentNullException.ThrowIfNull` 或自訂 helper 以符合規範 R04 的精神。

**判斷依據**：diff 中顯示手動 null 檢查並拋出例外。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:18</code> 靜態建構函式訂閱 HotReload 事件可能導致記憶體洩漏</summary>

靜態建構函式中訂閱 `HotReloadManager.Default.OnDeltaApplied` 事件，但沒有取消訂閱的機制。由於是靜態類別，應用程式生命週期內不會釋放，可能不是問題，但若 HotReloadManager 被重新建立，可能導致多個訂閱。

**判斷依據**：diff 中顯示靜態建構函式訂閱事件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:11</code> [R05] 測試類別命名不符合規範</summary>

測試類別名稱為 `DisplayNameTest`，符合規範 R05（以 Test 結尾）。但檔案位於 `test/Forms` 目錄，符合規範。無需變更。

**判斷依據**：diff 中類別名稱以 Test 結尾。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:13</code> [R06] 測試方法缺少 Arrange-Act-Assert 註解</summary>

測試方法 `ThrowsIfNoForParameterProvided` 使用 `// Arrange` 和 `// Act & Assert` 註解，符合規範 R06。但其他測試方法如 `DisplaysPropertyNameWhenNoAttributePresent` 有 `// Arrange`、`// Act`、`// Assert`，符合。整體符合。

**判斷依據**：diff 中顯示測試方法有 AAA 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:188</code> 測試輔助方法可能無法正確取得文字內容</summary>

`RenderAndGetOutput` 方法中，使用 `batch.ReferenceFrames.First(f => f.FrameType == RenderTree.RenderTreeFrameType.Text)` 取得第一個文字框架，但可能不是 DisplayName 元件的輸出。若元件輸出包含其他文字，可能導致測試不穩定。建議更精確地定位。

**判斷依據**：diff 中顯示使用 First 取得文字框架。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12506 (cache hit 12416) ｜ completion tokens 2372 ｜ PR #4</sub>