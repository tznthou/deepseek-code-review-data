<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 Blazor 的 `DisplayName<TValue>` 元件，用於顯示模型屬性的顯示名稱，並支援 `DisplayAttribute`、`DisplayNameAttribute` 及資源本地化。整體設計合理，但存在一些問題：`ExpressionMemberAccessor` 的快取未在 Hot Reload 時清除 `_displayNameCache`，可能導致顯示名稱過期；`DisplayName<TValue>` 元件在 `For` 參數為 null 時拋出例外，但未提供預設內容，可能造成頁面中斷；部分專案範本中的標籤缺少 `class="form-label"`，可能影響樣式一致性。建議優先修正快取清除問題，並考慮為元件提供更友善的錯誤處理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83` | Hot Reload 時未清除 _displayNameCache，可能導致顯示名稱過期 | 0.80 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:39` | For 參數為 null 時拋出例外，可能導致頁面中斷 | 0.70 |
| 🔸 | Minor | `src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Register.razor:32` | 部分標籤缺少 class="form-label"，可能影響樣式一致性 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83</code> Hot Reload 時未清除 _displayNameCache，可能導致顯示名稱過期</summary>

`ClearCache` 方法只清除了 `_memberInfoCache`，但 `_displayNameCache` 未被清除。當 Hot Reload 套用中繼資料變更（例如修改屬性的 `DisplayAttribute`）時，`_displayNameCache` 中快取的舊顯示名稱將繼續被使用，導致 UI 顯示過期的名稱。

**失敗情境**：開發者在 Hot Reload 期間修改了某個屬性的 `DisplayAttribute.Name`，但頁面仍顯示舊名稱。

**建議**：在 `ClearCache` 中同時清除 `_displayNameCache`。

**判斷依據**：diff 中 `ClearCache` 方法僅呼叫 `_memberInfoCache.Clear()`，未處理 `_displayNameCache`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:39</code> For 參數為 null 時拋出例外，可能導致頁面中斷</summary>

當 `For` 參數未提供時，元件會拋出 `InvalidOperationException`。這可能導致整個頁面渲染失敗，而不是僅顯示空白或預設內容。雖然測試中預期此行為，但對於生產應用程式，更友善的做法是記錄警告並渲染空內容，或提供預設顯示名稱。

**失敗情境**：開發者忘記設定 `For` 參數，頁面直接崩潰。

**建議**：考慮改為記錄警告並渲染空字串，或提供可設定的預設值。

**判斷依據**：diff 中 `DisplayName<TValue>` 的 `SetParametersAsync` 方法在 `For` 為 null 時拋出例外。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Register.razor:32</code> 部分標籤缺少 class="form-label"，可能影響樣式一致性</summary>

在 `Register.razor` 中，`Input.Email` 和 `Input.Password` 的 `<label>` 元素未加上 `class="form-label"`，而其他欄位（如 `Input.ConfirmPassword`）有加上。這可能導致樣式不一致，尤其是在使用 Bootstrap 等 CSS 框架時。

**失敗情境**：使用者看到 Email 和 Password 欄位的標籤樣式與其他欄位不同。

**建議**：為所有 `<label>` 元素統一加上 `class="form-label"`。

**判斷依據**：diff 中 `Register.razor` 的 Email 和 Password 標籤缺少 `class="form-label"`，而 ConfirmPassword 標籤有。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14753 (cache hit 1536) ｜ completion tokens 1068 ｜ PR #4</sub>