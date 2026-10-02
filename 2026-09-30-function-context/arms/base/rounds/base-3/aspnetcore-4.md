<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 Blazor 的 DisplayName 元件，用於顯示模型屬性的顯示名稱，並更新了多個專案範本以使用該元件。主要風險在於 DisplayName 元件在 For 參數變更時不會重新渲染，可能導致顯示名稱過期；此外，快取機制在 Hot Reload 時僅清除成員資訊快取，未清除顯示名稱快取，可能造成不一致。建議優先修正重新渲染邏輯，並考慮快取清除的完整性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/DisplayName.cs:46` | For 參數變更時不會重新渲染 | 0.90 |
| 🔸 | Minor | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83` | Hot Reload 時未清除顯示名稱快取 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:46</code> For 參數變更時不會重新渲染</summary>

在 `SetParametersAsync` 中，只有當 `For` 表達式與 `_previousFieldAccessor` 不同時才會重新計算並渲染。然而，如果 `For` 表達式相同但底層模型屬性值變更（例如屬性名稱不變但顯示名稱依賴於其他狀態），元件不會重新渲染，導致顯示名稱過期。

**失敗情境**：假設 `For` 表達式為 `() => model.Name`，且 `model.Name` 的顯示名稱依賴於某個可變狀態（例如語言切換），當語言變更時，`For` 表達式不變，元件不會重新渲染，顯示名稱仍為舊語言。

**建議**：移除 `_previousFieldAccessor` 檢查，每次 `SetParametersAsync` 都重新計算並渲染，或至少提供一個機制讓外部觸發重新渲染。

**判斷依據**：diff 中新增的 `DisplayName.cs` 第 43-51 行顯示了條件渲染邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83</code> Hot Reload 時未清除顯示名稱快取</summary>

`ClearCache` 方法僅清除 `_memberInfoCache`，未清除 `_displayNameCache`。如果 Hot Reload 期間屬性的顯示名稱屬性發生變更，`_displayNameCache` 可能返回舊值。

**失敗情境**：開發者在 Hot Reload 中修改了屬性的 `[Display]` 屬性，但由於 `_displayNameCache` 未清除，元件仍顯示舊名稱。

**建議**：在 `ClearCache` 中同時清除 `_displayNameCache`。

**判斷依據**：diff 中 `ExpressionMemberAccessor.cs` 第 80-83 行顯示 `ClearCache` 僅清除 `_memberInfoCache`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10321 (cache hit 10240) ｜ completion tokens 770 ｜ PR #4</sub>