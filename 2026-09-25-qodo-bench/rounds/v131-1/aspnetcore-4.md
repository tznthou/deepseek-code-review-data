<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 Blazor 的 `DisplayName<TValue>` 元件，用於顯示模型屬性的顯示名稱，並在專案範本中替換了多處硬編碼的標籤。整體設計合理，但存在一些潛在問題：`DisplayName` 元件在參數未變更時不會重新渲染，可能導致顯示名稱過時；`ExpressionMemberAccessor` 的快取在 Hot Reload 時僅清除成員資訊快取，未清除顯示名稱快取，可能導致顯示名稱不更新；此外，部分範本中的標籤缺少 `class="form-label"`，可能影響樣式一致性。建議優先處理快取清除問題，並考慮改進元件的重新渲染邏輯。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/DisplayName.cs:46` | 參數未變更時不會重新渲染，可能導致顯示名稱過時 | 0.80 |
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83` | Hot Reload 時未清除顯示名稱快取，可能導致顯示名稱不更新 | 0.80 |
| 🔸 | Minor | `src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Register.razor:32` | 標籤缺少 class="form-label"，可能影響樣式一致性 | 0.70 |
| 🔸 | Minor | `src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Login.razor:34` | 縮排不一致 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:46</code> 參數未變更時不會重新渲染，可能導致顯示名稱過時</summary>

在 `SetParametersAsync` 中，只有當 `For` 表達式與 `_previousFieldAccessor` 不同時才會重新計算顯示名稱並渲染。然而，如果 `For` 表達式相同，但目標屬性的顯示名稱可能因其他因素（例如資源檔變更、動態屬性變更）而改變，元件將不會更新。這可能導致顯示名稱與實際屬性不一致。建議在每次 `SetParametersAsync` 呼叫時都重新計算顯示名稱，或提供一種機制來強制更新。

**判斷依據**：diff 中 `DisplayName.cs` 第 43-51 行顯示了條件渲染邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83</code> Hot Reload 時未清除顯示名稱快取，可能導致顯示名稱不更新</summary>

`ClearCache` 方法僅清除了 `_memberInfoCache`，但未清除 `_displayNameCache`。當 Hot Reload 應用程式碼變更時，如果屬性的顯示名稱（例如透過 `DisplayAttribute` 或 `DisplayNameAttribute`）發生變化，快取中的舊值將繼續被使用，導致顯示名稱不正確。建議同時清除 `_displayNameCache`。

**判斷依據**：diff 中 `ExpressionMemberAccessor.cs` 第 80-83 行顯示了 `ClearCache` 方法。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Register.razor:32</code> 標籤缺少 class="form-label"，可能影響樣式一致性</summary>

在 `Register.razor` 中，Email 和 Password 欄位的標籤原本沒有 `class="form-label"`，但其他欄位（如 ConfirmPassword）有。此 PR 在替換時未統一加上該 class，可能導致樣式不一致。建議為所有標籤加上 `class="form-label"`。

**判斷依據**：diff 中 `Register.razor` 第 32-34 行顯示了 Email 標籤的變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Login.razor:34</code> 縮排不一致</summary>

在 `Login.razor` 中，Password 欄位的 `InputText` 和 `ValidationMessage` 的縮排與其他欄位不一致，可能影響可讀性。建議調整縮排以保持程式碼整潔。

**判斷依據**：diff 中 `Login.razor` 第 28-32 行顯示了縮排不一致。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10285 (cache hit 1408) ｜ completion tokens 1239 ｜ PR #4</sub>