<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 Blazor 的 DisplayName 元件，可從 DisplayAttribute 或 DisplayNameAttribute 讀取顯示名稱，並更新了多個專案範本以使用該元件。主要風險在於 DisplayName 元件未實作 IDisposable，可能導致記憶體洩漏；ExpressionMemberAccessor 的快取在 Hot Reload 時僅清除成員快取，未清除顯示名稱快取，可能造成顯示名稱過期；此外，部分測試方法未遵循 Arrange-Act-Assert 註解慣例。建議優先修正記憶體洩漏與快取問題。

### Findings（9 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/DisplayName.cs:16` | DisplayName 元件未實作 IDisposable，可能導致記憶體洩漏 | 0.80 |
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:22` | Hot Reload 時未清除顯示名稱快取，可能導致顯示名稱過期 | 0.75 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:159` | [R06] 測試方法 SupportsLocalizationWithResourceType 缺少 Arrange-Act-Assert 註解 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:126` | [R06] 測試方法 WorksWithDifferentPropertyTypes 缺少 Arrange-Act-Assert 註解 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:103` | [R06] 測試方法 DisplayAttributeTakesPrecedenceOverDisplayNameAttribute 缺少 Arrange-Act-Assert 註 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:81` | [R06] 測試方法 DisplaysDisplayNameAttributeName 缺少 Arrange-Act-Assert 註解 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:59` | [R06] 測試方法 DisplaysDisplayAttributeName 缺少 Arrange-Act-Assert 註解 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:37` | [R06] 測試方法 DisplaysPropertyNameWhenNoAttributePresent 缺少 Arrange-Act-Assert 註解 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:14` | [R06] 測試方法 ThrowsIfNoForParameterProvided 缺少 Arrange-Act-Assert 註解 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:16</code> DisplayName 元件未實作 IDisposable，可能導致記憶體洩漏</summary>

DisplayName 元件在 Attach 時取得 RenderHandle，但未實作 IDisposable 來釋放資源。若元件在 RenderHandle 釋放後仍被保留（例如在動態渲染或元件移除時），可能導致記憶體洩漏。建議實作 IDisposable 並在 Dispose 中釋放 RenderHandle。

**判斷依據**：DisplayName.cs 第 14 行宣告類別僅實作 IComponent，未實作 IDisposable。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:22</code> Hot Reload 時未清除顯示名稱快取，可能導致顯示名稱過期</summary>

在 Hot Reload 的 OnDeltaApplied 事件中，僅清除 _memberInfoCache，未清除 _displayNameCache。若屬性的 DisplayAttribute 或 DisplayNameAttribute 在 Hot Reload 中變更，顯示名稱快取仍保留舊值，導致 UI 顯示過期的名稱。建議同時清除 _displayNameCache。

**判斷依據**：ExpressionMemberAccessor.cs 第 16 行註冊 ClearCache，但 ClearCache 方法僅清除 _memberInfoCache（第 84 行）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:159</code> [R06] 測試方法 SupportsLocalizationWithResourceType 缺少 Arrange-Act-Assert 註解</summary>

測試方法 SupportsLocalizationWithResourceType 未包含明確的 // Arrange、// Act、// Assert 註解，違反專案規範 R06。建議加入結構化註解以提升可讀性。

**判斷依據**：DisplayNameTest.cs 第 116 行開始的測試方法缺少 AAA 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:126</code> [R06] 測試方法 WorksWithDifferentPropertyTypes 缺少 Arrange-Act-Assert 註解</summary>

測試方法 WorksWithDifferentPropertyTypes 未包含明確的 // Arrange、// Act、// Assert 註解，違反專案規範 R06。建議加入結構化註解以提升可讀性。

**判斷依據**：DisplayNameTest.cs 第 132 行開始的測試方法缺少 AAA 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:103</code> [R06] 測試方法 DisplayAttributeTakesPrecedenceOverDisplayNameAttribute 缺少 Arrange-Act-Assert 註解</summary>

測試方法 DisplayAttributeTakesPrecedenceOverDisplayNameAttribute 未包含明確的 // Arrange、// Act、// Assert 註解，違反專案規範 R06。建議加入結構化註解以提升可讀性。

**判斷依據**：DisplayNameTest.cs 第 160 行開始的測試方法缺少 AAA 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:81</code> [R06] 測試方法 DisplaysDisplayNameAttributeName 缺少 Arrange-Act-Assert 註解</summary>

測試方法 DisplaysDisplayNameAttributeName 未包含明確的 // Arrange、// Act、// Assert 註解，違反專案規範 R06。建議加入結構化註解以提升可讀性。

**判斷依據**：DisplayNameTest.cs 第 180 行開始的測試方法缺少 AAA 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:59</code> [R06] 測試方法 DisplaysDisplayAttributeName 缺少 Arrange-Act-Assert 註解</summary>

測試方法 DisplaysDisplayAttributeName 未包含明確的 // Arrange、// Act、// Assert 註解，違反專案規範 R06。建議加入結構化註解以提升可讀性。

**判斷依據**：DisplayNameTest.cs 第 200 行開始的測試方法缺少 AAA 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:37</code> [R06] 測試方法 DisplaysPropertyNameWhenNoAttributePresent 缺少 Arrange-Act-Assert 註解</summary>

測試方法 DisplaysPropertyNameWhenNoAttributePresent 未包含明確的 // Arrange、// Act、// Assert 註解，違反專案規範 R06。建議加入結構化註解以提升可讀性。

**判斷依據**：DisplayNameTest.cs 第 220 行開始的測試方法缺少 AAA 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:14</code> [R06] 測試方法 ThrowsIfNoForParameterProvided 缺少 Arrange-Act-Assert 註解</summary>

測試方法 ThrowsIfNoForParameterProvided 未包含明確的 // Arrange、// Act、// Assert 註解，違反專案規範 R06。建議加入結構化註解以提升可讀性。

**判斷依據**：DisplayNameTest.cs 第 240 行開始的測試方法缺少 AAA 註解。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12516 (cache hit 10240) ｜ completion tokens 1825 ｜ PR #4</sub>