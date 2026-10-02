<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 Blazor 的 DisplayName 元件，用於顯示模型屬性的顯示名稱，並更新了多個專案範本以使用該元件。主要風險在於 DisplayName 元件在參數未變更時不會重新渲染，可能導致顯示名稱過期；此外，快取機制在 Hot Reload 時僅清除成員資訊快取，未清除顯示名稱快取，可能導致顯示名稱更新不及時。建議優先修正渲染邏輯與快取清除問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/Components/Web/src/Forms/DisplayName.cs:46` | 參數未變更時不會重新渲染，導致顯示名稱過期 | 0.95 |
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83` | Hot Reload 時未清除顯示名稱快取 | 0.80 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:9` | [R02] 應使用檔案範圍命名空間宣告 | 0.90 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:16` | [R14] 內部類別應標記為 sealed | 0.90 |
| 🔸 | Minor | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:13` | [R14] 內部類別應標記為 sealed | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:159` | [R06] 測試方法缺少 Arrange-Act-Assert 註解 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:46</code> 參數未變更時不會重新渲染，導致顯示名稱過期</summary>

在 `SetParametersAsync` 中，只有當 `For` 表達式與 `_previousFieldAccessor` 不同時才會重新計算顯示名稱並呼叫 `_renderHandle.Render`。然而，即使表達式相同，顯示名稱仍可能因其他因素（例如資源檔變更、文化特性變更）而需要更新。這會導致元件在這些情況下顯示過期的名稱。

建議：移除 `For != _previousFieldAccessor` 的條件，每次 `SetParametersAsync` 都重新計算並渲染，或至少加入對文化特性變更的偵測。

**判斷依據**：diff 中新增的 DisplayName.cs 第 47-55 行顯示條件渲染邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83</code> Hot Reload 時未清除顯示名稱快取</summary>

`ClearCache` 方法僅清除 `_memberInfoCache`，未清除 `_displayNameCache`。當 Hot Reload 套用中繼資料變更時，顯示名稱快取可能保留舊值，導致顯示名稱不正確。

建議：在 `ClearCache` 中同時清除 `_displayNameCache`。

**判斷依據**：diff 中 ExpressionMemberAccessor.cs 第 78-81 行顯示 ClearCache 僅清除 _memberInfoCache。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:9</code> [R02] 應使用檔案範圍命名空間宣告</summary>

此檔案使用傳統的區塊範圍命名空間宣告，但專案規範要求使用檔案範圍命名空間（C# 10+）。

建議：將命名空間宣告改為 `namespace Microsoft.AspNetCore.Components.Forms;` 並移除大括號。

**判斷依據**：diff 中 DisplayName.cs 第 8-13 行顯示區塊範圍命名空間。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:16</code> [R14] 內部類別應標記為 sealed</summary>

`DisplayName<TValue>` 是公開類別，但未標記為 `sealed`。雖然它不是內部類別，但若無意供繼承，建議標記為 `sealed` 以提升效能並明確設計意圖。

**判斷依據**：diff 中 DisplayName.cs 第 13 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:13</code> [R14] 內部類別應標記為 sealed</summary>

`ExpressionMemberAccessor` 是內部靜態類別，但未標記為 `sealed`。靜態類別無法被繼承，但加上 `sealed` 可更明確表達設計意圖。

**判斷依據**：diff 中 ExpressionMemberAccessor.cs 第 12 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:159</code> [R06] 測試方法缺少 Arrange-Act-Assert 註解</summary>

`SupportsLocalizationWithResourceType` 測試方法缺少 `// Arrange`、`// Act`、`// Assert` 註解，違反專案規範。

**判斷依據**：diff 中 DisplayNameTest.cs 第 232 行開始的測試方法。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12496 (cache hit 12416) ｜ completion tokens 1546 ｜ PR #4</sub>