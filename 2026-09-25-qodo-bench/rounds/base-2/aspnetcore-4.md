<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了 Blazor 的 `DisplayName<TValue>` 元件，用於顯示模型屬性的顯示名稱，並整合了 `DisplayAttribute`、`DisplayNameAttribute` 與資源本地化。整體設計合理，測試涵蓋主要情境，但存在幾個需要修正的問題：`DisplayName<TValue>` 元件在 `For` 參數未變更時不會重新渲染，可能導致顯示名稱過期；`ExpressionMemberAccessor` 的快取在 Hot Reload 時只清除成員快取，未清除顯示名稱快取，可能造成不一致；此外，部分專案範本中的標籤缺少 `class="form-label"`，影響樣式一致性。建議修正後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/DisplayName.cs:46` | 當 `For` 參數未變更時，元件不會重新渲染，導致顯示名稱可能過期 | 0.90 |
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83` | Hot Reload 時未清除顯示名稱快取，可能導致顯示名稱不一致 | 0.85 |
| 🔸 | Minor | `src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Register.razor:32` | 標籤缺少 `class="form-label"`，可能影響樣式 | 0.80 |
| 🔸 | Minor | `src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Login.razor:34` | 縮排不一致 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:46</code> 當 `For` 參數未變更時，元件不會重新渲染，導致顯示名稱可能過期</summary>

在 `SetParametersAsync` 中，只有當 `For != _previousFieldAccessor` 時才會重新計算並渲染。如果父元件重新渲染但傳入相同的 `For` 表達式，且顯示名稱的來源（例如資源檔或屬性）已變更，此元件不會更新。例如，若使用本地化且使用者切換語言，但 `For` 表達式相同，顯示名稱將保持舊語言。建議移除條件判斷，或在每次 `SetParametersAsync` 時都重新計算並渲染。

**判斷依據**：diff 中 `DisplayName.cs` 第 45-53 行顯示條件渲染邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83</code> Hot Reload 時未清除顯示名稱快取，可能導致顯示名稱不一致</summary>

`ClearCache` 方法僅清除 `_memberInfoCache`，未清除 `_displayNameCache`。若在 Hot Reload 期間修改了屬性的 `DisplayAttribute` 或 `DisplayNameAttribute`，`_displayNameCache` 仍保留舊值，導致顯示名稱錯誤。建議同時清除 `_displayNameCache`。

**判斷依據**：diff 中 `ExpressionMemberAccessor.cs` 第 82-85 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Register.razor:32</code> 標籤缺少 `class="form-label"`，可能影響樣式</summary>

在 `Register.razor` 中，第一個 `<label>` 標籤缺少 `class="form-label"`，而其他標籤都有。這可能導致樣式不一致。建議加上 `class="form-label"`。

**判斷依據**：diff 中 `Register.razor` 第 32-34 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Login.razor:34</code> 縮排不一致</summary>

在 `Login.razor` 中，密碼欄位的 `<InputText>` 和相關標籤的縮排與其他欄位不一致，可能影響可讀性。建議調整縮排以保持一致性。

**判斷依據**：diff 中 `Login.razor` 第 31-35 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10321 (cache hit 10240) ｜ completion tokens 1178 ｜ PR #4</sub>