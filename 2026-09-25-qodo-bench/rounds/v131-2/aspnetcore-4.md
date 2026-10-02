<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 Blazor 的 `DisplayName<TValue>` 元件，用於顯示模型屬性的顯示名稱，並支援 `DisplayAttribute`、`DisplayNameAttribute` 及資源本地化。整體設計合理，但存在幾個需要修正的問題：`DisplayName<TValue>` 元件在 `For` 參數為 null 時拋出例外，但未在 `SetParametersAsync` 中處理非同步例外；`ExpressionMemberAccessor` 的快取未在 Hot Reload 時清除 `_displayNameCache`，可能導致顯示名稱過期；測試程式碼中的 `RenderAndGetOutput` 方法假設只有一個文字框架，可能因多個文字內容而失敗；此外，部分專案範本中的標籤缺少 `class="form-label"`，可能影響樣式一致性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/DisplayName.cs:39` | 非同步例外未正確處理 | 0.80 |
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83` | Hot Reload 時未清除顯示名稱快取 | 0.75 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:188` | 測試輔助方法假設單一文字框架 | 0.70 |
| 🔸 | Minor | `src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Register.razor:32` | 標籤缺少 class="form-label" | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:39</code> 非同步例外未正確處理</summary>

在 `SetParametersAsync` 中，當 `For` 為 null 時直接拋出 `InvalidOperationException`。由於此方法為非同步，例外會被包裝在返回的 `Task` 中，但呼叫端（如 Blazor 渲染器）可能未正確觀察該例外，導致元件狀態不一致或未處理的例外。建議改為在方法開頭同步驗證參數，或使用 `Task.FromException` 返回失敗的任務。

**判斷依據**：diff 中新增的 `DisplayName.cs` 第 42-45 行顯示在非同步方法中直接拋出例外。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83</code> Hot Reload 時未清除顯示名稱快取</summary>

`ClearCache` 方法僅清除 `_memberInfoCache`，未清除 `_displayNameCache`。當 Hot Reload 套用中繼資料變更時，顯示名稱快取可能保留過時的屬性名稱或屬性值，導致 UI 顯示不正確。建議同時清除兩個快取。

**判斷依據**：diff 中 `ExpressionMemberAccessor.cs` 的 `ClearCache` 方法僅清除 `_memberInfoCache`，未處理 `_displayNameCache`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:188</code> 測試輔助方法假設單一文字框架</summary>

`RenderAndGetOutput` 方法使用 `First(f => f.FrameType == RenderTree.RenderTreeFrameType.Text)` 取得文字框架，但若元件渲染多個文字節點（例如包含空白或註解），可能取到錯誤的文字。建議改用更精確的查詢，例如根據元件 ID 或使用 `FindComponent` 後再取得其內容。

**判斷依據**：diff 中 `DisplayNameTest.cs` 的 `RenderAndGetOutput` 方法使用 `First` 取得文字框架，未考慮多個文字節點的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Register.razor:32</code> 標籤缺少 class="form-label"</summary>

在 `Register.razor` 中，`<label for="Input.Email">` 和 `<label for="Input.Password">` 未加上 `class="form-label"`，與其他頁面的標籤不一致，可能影響 Bootstrap 樣式。建議補上該 class。

**判斷依據**：diff 中 `Register.razor` 的標籤缺少 `class="form-label"`，而其他頁面（如 `Login.razor`）的標籤均有此 class。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10285 (cache hit 10240) ｜ completion tokens 1157 ｜ PR #4</sub>