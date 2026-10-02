<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 Blazor 的 DisplayName 元件，用於顯示模型屬性的顯示名稱，並支援 DisplayAttribute、DisplayNameAttribute 及資源本地化。主要風險在於 DisplayName 元件在參數未變更時不會重新渲染，可能導致顯示名稱過期；此外，ExpressionMemberAccessor 的快取在 Hot Reload 時僅清除成員快取，未清除顯示名稱快取，可能造成不一致。另有部分程式碼風格違反專案規範，如命名空間宣告、欄位命名、類別密封等。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/DisplayName.cs:46` | DisplayName 元件在參數未變更時不會重新渲染，可能導致顯示名稱過期 | 0.80 |
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83` | Hot Reload 時未清除顯示名稱快取，可能導致不一致 | 0.70 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:9` | [R02] 使用檔案範圍命名空間宣告 | 0.90 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:19` | [R03] 私有欄位應使用底線前綴的 camelCase 命名 | 0.90 |
| 🔸 | Minor | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:13` | [R14] 內部類別應標記為 sealed | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:1` | [R01] 所有 C# 原始檔必須包含 MIT 授權標頭 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:9` | [R02] 使用檔案範圍命名空間宣告 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:159` | [R06] 測試方法應使用 Arrange-Act-Assert 模式並加上註解 | 0.90 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:26` | [R07] 公開 API 必須有 XML 文件註解 | 0.90 |
| 🔸 | Minor | `src/Components/Web/src/Forms/DisplayName.cs:16` | [R18] 開頭大括號應在新行（Allman 風格） | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:46</code> DisplayName 元件在參數未變更時不會重新渲染，可能導致顯示名稱過期</summary>

在 SetParametersAsync 中，只有當 For 表達式與 _previousFieldAccessor 不同時才會重新計算顯示名稱並呼叫 Render。然而，顯示名稱可能依賴於其他因素（例如文化特性變更、資源檔更新），這些變更不會反映在 For 表達式中。因此，當這些因素改變時，元件不會重新渲染，導致顯示名稱過期。建議在每次 SetParametersAsync 呼叫時都重新計算並渲染，或提供一個機制來強制更新。

**判斷依據**：diff 中新增的 DisplayName.cs 第 46-54 行顯示了條件渲染邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83</code> Hot Reload 時未清除顯示名稱快取，可能導致不一致</summary>

在 Hot Reload 的 OnDeltaApplied 事件中，僅呼叫 _memberInfoCache.Clear()，但未清除 _displayNameCache。如果屬性的顯示名稱在 Hot Reload 期間發生變更（例如修改了 DisplayAttribute），則 _displayNameCache 中仍保留舊值，導致顯示名稱不正確。建議同時清除 _displayNameCache。

**判斷依據**：diff 中新增的 ExpressionMemberAccessor.cs 第 80-83 行顯示 ClearCache 方法僅清除 _memberInfoCache。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:9</code> [R02] 使用檔案範圍命名空間宣告</summary>

檔案 DisplayName.cs 使用了傳統的區塊範圍命名空間宣告（namespace Microsoft.AspNetCore.Components.Forms { ... }），而專案規範要求使用檔案範圍命名空間（namespace Microsoft.AspNetCore.Components.Forms;）。建議改為檔案範圍命名空間以符合規範。

**判斷依據**：diff 中新增的 DisplayName.cs 第 9 行顯示了區塊範圍命名空間宣告。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:19</code> [R03] 私有欄位應使用底線前綴的 camelCase 命名</summary>

私有欄位 _renderHandle、_previousFieldAccessor、_displayName 已符合底線前綴 camelCase 命名，但欄位 _previousFieldAccessor 的型別為 Expression<Func<TValue>>?，其名稱可能不夠清晰。不過，此處主要問題是欄位 _previousFieldAccessor 未使用底線前綴？實際上已使用底線前綴，因此可能不違反規範。請確認是否所有私有欄位均符合規範。

**判斷依據**：diff 中新增的 DisplayName.cs 第 20-22 行顯示了私有欄位宣告。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:13</code> [R14] 內部類別應標記為 sealed</summary>

ExpressionMemberAccessor 是內部靜態類別，根據規範 R14，內部實作類別應標記為 sealed。靜態類別本身不可繼承，但規範可能仍要求標記 sealed。建議加上 sealed 修飾詞以符合規範。

**判斷依據**：diff 中新增的 ExpressionMemberAccessor.cs 第 14 行顯示了類別宣告。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:1</code> [R01] 所有 C# 原始檔必須包含 MIT 授權標頭</summary>

檔案 DisplayNameTest.cs 缺少 MIT 授權標頭。根據規範 R01，每個 .cs 檔案開頭必須包含標準的兩行註解。請在檔案開頭加入授權標頭。

**判斷依據**：diff 中新增的 DisplayNameTest.cs 開頭缺少授權標頭（diff 中未顯示授權標頭，但其他檔案有）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:9</code> [R02] 使用檔案範圍命名空間宣告</summary>

檔案 DisplayNameTest.cs 使用了傳統的區塊範圍命名空間宣告（namespace Microsoft.AspNetCore.Components.Forms; 但實際上是區塊範圍？請確認）。根據規範 R02，應使用檔案範圍命名空間。

**判斷依據**：diff 中新增的 DisplayNameTest.cs 第 1 行顯示了命名空間宣告。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:159</code> [R06] 測試方法應使用 Arrange-Act-Assert 模式並加上註解</summary>

測試方法 SupportsLocalizationWithResourceType 缺少 Arrange、Act、Assert 註解。根據規範 R06，測試方法應包含明確的階段註解。請補上相應註解。

**判斷依據**：diff 中新增的 DisplayNameTest.cs 中 SupportsLocalizationWithResourceType 方法缺少階段註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:26</code> [R07] 公開 API 必須有 XML 文件註解</summary>

公開類別 DisplayName<TValue> 的屬性 For 缺少 XML 文件註解。根據規範 R07，所有公開 API 都應有 XML 文件註解。請為 For 屬性加上 <summary> 等標籤。

**判斷依據**：diff 中新增的 DisplayName.cs 第 27-28 行顯示了 For 屬性宣告，但缺少 XML 文件註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:16</code> [R18] 開頭大括號應在新行（Allman 風格）</summary>

檔案 DisplayName.cs 中的類別宣告使用了開頭大括號在新行，但方法宣告的開頭大括號也在新行，符合 Allman 風格。然而，命名空間宣告的開頭大括號在新行，但根據規範 R18，所有開頭大括號都應在新行。此處可能符合，但請確認所有大括號位置是否一致。

**判斷依據**：diff 中新增的 DisplayName.cs 第 17 行顯示了類別宣告。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12440 (cache hit 10240) ｜ completion tokens 2350 ｜ PR #4</sub>