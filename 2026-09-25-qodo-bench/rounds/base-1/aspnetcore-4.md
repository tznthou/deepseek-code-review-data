<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 Blazor 的 DisplayName 元件，用於顯示模型屬性的顯示名稱，並在專案範本中替換了硬編碼的標籤。主要風險在於 DisplayName 元件在參數更新時的快取邏輯可能導致顯示名稱不更新，以及 ExpressionMemberAccessor 的快取在 Hot Reload 時未清除顯示名稱快取。建議優先修正快取邏輯，並考慮增加測試覆蓋。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/DisplayName.cs:46` | DisplayName 元件在 For 參數變更時可能不會更新顯示名稱 | 0.80 |
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83` | Hot Reload 時未清除顯示名稱快取 | 0.70 |
| 🔸 | Minor | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:44` | GetMemberInfo 方法可能拋出不明確的例外 | 0.60 |
| 🔸 | Minor | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:20` | DisplayName 元件未實作 IDisposable | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:46</code> DisplayName 元件在 For 參數變更時可能不會更新顯示名稱</summary>

在 `SetParametersAsync` 中，只有當 `For` 表達式與 `_previousFieldAccessor` 不同時才會重新計算顯示名稱。然而，如果 `For` 表達式相同但底層模型屬性的顯示名稱因動態變更（例如資源檔更新或屬性變更）而改變，元件不會重新渲染。這可能導致顯示名稱過時。建議在每次 `SetParametersAsync` 時都重新計算，或提供一個方法來強制更新。

**判斷依據**：diff 中的 DisplayName.cs 第 42-50 行顯示了條件判斷和快取邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83</code> Hot Reload 時未清除顯示名稱快取</summary>

在靜態建構函式中，當 Hot Reload 的 MetadataUpdateSupported 為 true 時，訂閱了 OnDeltaApplied 事件並呼叫 ClearCache。但 ClearCache 只清除了 `_memberInfoCache`，沒有清除 `_displayNameCache`。這可能導致在 Hot Reload 後顯示名稱仍然使用舊的快取值。建議在 ClearCache 中同時清除兩個快取。

**判斷依據**：diff 中的 ExpressionMemberAccessor.cs 第 16 行顯示 ClearCache 方法只清除了 _memberInfoCache。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:44</code> GetMemberInfo 方法可能拋出不明確的例外</summary>

當表達式不是 MemberExpression 時，會拋出 ArgumentException，但訊息中使用了 `accessorBody.GetType().Name`，這可能不夠明確。建議提供更具體的錯誤訊息，例如包含表達式的實際內容。

**判斷依據**：diff 中的 ExpressionMemberAccessor.cs 第 25-27 行顯示了例外訊息。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:20</code> DisplayName 元件未實作 IDisposable</summary>

元件訂閱了 Hot Reload 事件，但未實作 IDisposable 來取消訂閱。這可能導致記憶體洩漏。建議在元件中實作 IDisposable 並在 Dispose 中取消訂閱。

**判斷依據**：diff 中的 ExpressionMemberAccessor.cs 第 16-19 行顯示了事件訂閱。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10321 (cache hit 1536) ｜ completion tokens 1047 ｜ PR #4</sub>