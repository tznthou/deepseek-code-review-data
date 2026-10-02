<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 Blazor 的 DisplayName 元件，用於顯示模型屬性的顯示名稱，支援 DisplayAttribute、DisplayNameAttribute 及資源本地化。整體設計合理，但存在幾個問題：DisplayName 元件在 For 參數為 null 時拋出例外，但未在 SetParametersAsync 中處理可能的重複渲染；ExpressionMemberAccessor 的快取未在 Hot Reload 時清除 _displayNameCache；部分專案範本中的標籤缺少 class="form-label"，可能影響樣式一致性。最優先應修正快取清除問題，以避免 Hot Reload 後顯示名稱不更新。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83` | Hot Reload 時未清除 _displayNameCache，可能導致顯示名稱不更新 | 0.90 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:39` | For 參數為 null 時拋出例外，但未處理重複渲染可能導致的效能問題 | 0.80 |
| 🔸 | Minor | `src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Register.razor:32` | 缺少 class="form-label"，可能導致樣式不一致 | 0.70 |
| 🔸 | Minor | `src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/ResetPassword.razor:27` | 缺少 class="form-label"，可能導致樣式不一致 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83</code> Hot Reload 時未清除 _displayNameCache，可能導致顯示名稱不更新</summary>

在 Hot Reload 套用差異時，`ClearCache` 方法只清除了 `_memberInfoCache`，但未清除 `_displayNameCache`。如果屬性的顯示名稱在 Hot Reload 中變更（例如修改了 `[Display]` 屬性的值），`_displayNameCache` 仍會保留舊值，導致 UI 顯示過時的名稱。

建議在 `ClearCache` 中同時清除 `_displayNameCache`：
```csharp
private static void ClearCache()
{
    _memberInfoCache.Clear();
    _displayNameCache.Clear();
}
```

**判斷依據**：diff 中 `ClearCache` 方法只呼叫 `_memberInfoCache.Clear()`，未清除 `_displayNameCache`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:39</code> For 參數為 null 時拋出例外，但未處理重複渲染可能導致的效能問題</summary>

在 `SetParametersAsync` 中，當 `For` 為 null 時拋出 `InvalidOperationException`。這符合預期，但若父元件在渲染過程中多次設定參數，且 `For` 暫時為 null，可能導致不必要的例外。建議考慮使用 `[EditorRequired]` 屬性（已使用）並在文件或錯誤訊息中明確說明。此外，目前每次 `SetParametersAsync` 都會檢查 `For` 是否為 null，但若 `For` 不變，仍會執行 null 檢查，可考慮將檢查移至 `For` 變更時。

**判斷依據**：diff 中 `SetParametersAsync` 方法在每次呼叫時都檢查 `For` 是否為 null，且未對重複渲染進行最佳化。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/Register.razor:32</code> 缺少 class="form-label"，可能導致樣式不一致</summary>

在 `Register.razor` 中，`<label for="Input.Email">` 和 `<label for="Input.Password">` 缺少 `class="form-label"`，而其他標籤（如 `ConfirmPassword`）已加上。這可能導致 Bootstrap 樣式不一致。建議為所有標籤統一加上 `class="form-label"`。

**判斷依據**：diff 中 `Register.razor` 的 `Input.Email` 和 `Input.Password` 標籤未包含 `class="form-label"`，而 `Input.ConfirmPassword` 標籤已包含。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/ProjectTemplates/Web.ProjectTemplates/content/BlazorWeb-CSharp/BlazorWebCSharp.1/Components/Account/Pages/ResetPassword.razor:27</code> 缺少 class="form-label"，可能導致樣式不一致</summary>

在 `ResetPassword.razor` 中，`<label for="Input.Email">` 缺少 `class="form-label"`，而其他標籤（如 `Input.Password`）已加上。建議統一加上 `class="form-label"`。

**判斷依據**：diff 中 `ResetPassword.razor` 的 `Input.Email` 標籤未包含 `class="form-label"`，而 `Input.Password` 標籤已包含。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12516 (cache hit 12416) ｜ completion tokens 1280 ｜ PR #4</sub>