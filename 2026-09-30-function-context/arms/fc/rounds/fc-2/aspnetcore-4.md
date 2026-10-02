<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 Blazor 的 `DisplayName<TValue>` 元件，用於顯示模型屬性的顯示名稱，並支援 `DisplayAttribute`、`DisplayNameAttribute` 及資源本地化。同時更新了專案範本中的表單標籤以使用此元件。整體設計合理，但存在一些潛在問題：`DisplayName<TValue>` 元件在參數未變更時不會重新渲染，可能導致顯示名稱過期；`ExpressionMemberAccessor` 的快取在 Hot Reload 時僅清除成員快取，未清除顯示名稱快取；此外，`DisplayName` 元件未處理 `For` 參數為 null 以外的情況，且測試程式碼中可能存在型別匹配問題。建議優先修正快取一致性與元件重新渲染邏輯。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/DisplayName.cs:46` | DisplayName 元件在參數未變更時不會重新渲染 | 0.80 |
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83` | Hot Reload 時未清除顯示名稱快取 | 0.75 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:39` | 未處理 For 參數為 null 以外的無效表達式 | 0.60 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:183` | 測試程式碼中型別匹配可能不正確 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:46</code> DisplayName 元件在參數未變更時不會重新渲染</summary>

在 `SetParametersAsync` 中，只有當 `For` 表達式與 `_previousFieldAccessor` 不同時才會重新計算顯示名稱並呼叫 `_renderHandle.Render`。如果父元件重新渲染但傳入相同的 `For` 表達式（例如父元件狀態變更但表達式相同），則此元件不會重新渲染。這可能導致顯示名稱過期，例如當顯示名稱依賴於某個會變更的資源或文化特性時。建議在每次 `SetParametersAsync` 呼叫時都重新計算並渲染，或至少提供一個機制來強制更新。

**判斷依據**：diff 中 `DisplayName.cs` 第 44-52 行顯示條件渲染邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83</code> Hot Reload 時未清除顯示名稱快取</summary>

`ClearCache` 方法僅清除 `_memberInfoCache`，未清除 `_displayNameCache`。當 Hot Reload 套用中繼資料變更時，顯示名稱快取可能保留過時的顯示名稱，導致顯示不正確。建議同時清除 `_displayNameCache`。

**判斷依據**：diff 中 `ExpressionMemberAccessor.cs` 第 84-87 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:39</code> 未處理 For 參數為 null 以外的無效表達式</summary>

`SetParametersAsync` 僅檢查 `For` 是否為 null，但未處理表達式無效的情況（例如表達式不是成員存取）。`ExpressionMemberAccessor.GetDisplayName` 會拋出 `ArgumentException`，但此例外可能未以有意義的方式處理，導致元件渲染失敗。建議在元件中捕獲並處理此例外，或提供更明確的錯誤訊息。

**判斷依據**：diff 中 `DisplayName.cs` 第 36-40 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:183</code> 測試程式碼中型別匹配可能不正確</summary>

在 `RenderAndGetOutput` 方法中，使用 `f.Component is DisplayName<string> or DisplayName<int> or DisplayName<DateTime>` 來尋找元件框架。但 `DisplayName<TValue>` 是泛型型別，實際執行時期的型別可能因 `TValue` 不同而不同，此模式可能無法正確匹配所有情況。建議改用更通用的方式，例如檢查 `f.Component` 是否為 `DisplayName<>` 的執行個體。

**判斷依據**：diff 中 `DisplayNameTest.cs` 第 218-220 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14753 (cache hit 14720) ｜ completion tokens 1201 ｜ PR #4</sub>