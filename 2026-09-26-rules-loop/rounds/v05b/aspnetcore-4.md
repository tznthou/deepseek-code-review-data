<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 Blazor 的 DisplayName 元件，可從 DisplayAttribute 或 DisplayNameAttribute 取得顯示名稱，並更新多個專案範本以使用該元件。主要風險在於 DisplayName 元件未實作 IDisposable，可能導致記憶體洩漏；ExpressionMemberAccessor 的快取未清除 _displayNameCache，在 Hot Reload 後可能回傳過時資料；以及部分測試方法缺少 Arrange/Act/Assert 註解。建議優先修正記憶體洩漏與快取問題。

### Findings（9 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web/src/Forms/DisplayName.cs:16` | DisplayName 元件未實作 IDisposable，可能導致記憶體洩漏 | 0.80 |
| ⚠️ | Major | `src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83` | Hot Reload 後 _displayNameCache 未清除，可能回傳過時資料 | 0.70 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:159` | [R06] 測試方法缺少 Arrange/Act/Assert 註解 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:14` | [R06] 測試方法缺少 Arrange/Act/Assert 註解 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:37` | [R06] 測試方法缺少 Arrange/Act/Assert 註解 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:59` | [R06] 測試方法缺少 Arrange/Act/Assert 註解 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:81` | [R06] 測試方法缺少 Arrange/Act/Assert 註解 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:103` | [R06] 測試方法缺少 Arrange/Act/Assert 註解 | 0.90 |
| 🔸 | Minor | `src/Components/Web/test/Forms/DisplayNameTest.cs:126` | [R06] 測試方法缺少 Arrange/Act/Assert 註解 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/DisplayName.cs:16</code> DisplayName 元件未實作 IDisposable，可能導致記憶體洩漏</summary>

DisplayName 元件在 Attach 時取得 RenderHandle，但未實作 IDisposable 以在元件移除時釋放資源。若元件在應用程式生命週期中動態新增/移除，可能造成記憶體洩漏。建議實作 IDisposable 並在 Dispose 中釋放 RenderHandle（或至少將 _renderHandle 設為 null）。

**判斷依據**：DisplayName 類別僅實作 IComponent，未實作 IDisposable。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83</code> Hot Reload 後 _displayNameCache 未清除，可能回傳過時資料</summary>

ClearCache 方法僅清除 _memberInfoCache，未清除 _displayNameCache。若在 Hot Reload 後屬性上的 DisplayAttribute 變更，GetDisplayName 可能仍回傳舊值。建議在 ClearCache 中同時清除 _displayNameCache。

**判斷依據**：ClearCache 方法僅清除 _memberInfoCache，未清除 _displayNameCache。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:159</code> [R06] 測試方法缺少 Arrange/Act/Assert 註解</summary>

多個測試方法（如 SupportsLocalizationWithResourceType）缺少明確的 '// Arrange'、'// Act'、'// Assert' 註解，違反專案規範 R06。建議補上對應註解以提升可讀性。

**判斷依據**：SupportsLocalizationWithResourceType 方法未包含 AAA 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:14</code> [R06] 測試方法缺少 Arrange/Act/Assert 註解</summary>

多個測試方法（如 ThrowsIfNoForParameterProvided）缺少明確的 '// Arrange'、'// Act'、'// Assert' 註解，違反專案規範 R06。建議補上對應註解以提升可讀性。

**判斷依據**：ThrowsIfNoForParameterProvided 方法僅有 '// Arrange' 註解，缺少 '// Act' 與 '// Assert'。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:37</code> [R06] 測試方法缺少 Arrange/Act/Assert 註解</summary>

多個測試方法（如 DisplaysPropertyNameWhenNoAttributePresent）缺少明確的 '// Arrange'、'// Act'、'// Assert' 註解，違反專案規範 R06。建議補上對應註解以提升可讀性。

**判斷依據**：DisplaysPropertyNameWhenNoAttributePresent 方法僅有 '// Arrange' 註解，缺少 '// Act' 與 '// Assert'。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:59</code> [R06] 測試方法缺少 Arrange/Act/Assert 註解</summary>

多個測試方法（如 DisplaysDisplayAttributeName）缺少明確的 '// Arrange'、'// Act'、'// Assert' 註解，違反專案規範 R06。建議補上對應註解以提升可讀性。

**判斷依據**：DisplaysDisplayAttributeName 方法僅有 '// Arrange' 註解，缺少 '// Act' 與 '// Assert'。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:81</code> [R06] 測試方法缺少 Arrange/Act/Assert 註解</summary>

多個測試方法（如 DisplaysDisplayNameAttributeName）缺少明確的 '// Arrange'、'// Act'、'// Assert' 註解，違反專案規範 R06。建議補上對應註解以提升可讀性。

**判斷依據**：DisplaysDisplayNameAttributeName 方法僅有 '// Arrange' 註解，缺少 '// Act' 與 '// Assert'。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:103</code> [R06] 測試方法缺少 Arrange/Act/Assert 註解</summary>

多個測試方法（如 DisplayAttributeTakesPrecedenceOverDisplayNameAttribute）缺少明確的 '// Arrange'、'// Act'、'// Assert' 註解，違反專案規範 R06。建議補上對應註解以提升可讀性。

**判斷依據**：DisplayAttributeTakesPrecedenceOverDisplayNameAttribute 方法僅有 '// Arrange' 註解，缺少 '// Act' 與 '// Assert'。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web/test/Forms/DisplayNameTest.cs:126</code> [R06] 測試方法缺少 Arrange/Act/Assert 註解</summary>

多個測試方法（如 WorksWithDifferentPropertyTypes）缺少明確的 '// Arrange'、'// Act'、'// Assert' 註解，違反專案規範 R06。建議補上對應註解以提升可讀性。

**判斷依據**：WorksWithDifferentPropertyTypes 方法僅有 '// Arrange' 註解，缺少 '// Act' 與 '// Assert'。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12440 (cache hit 12416) ｜ completion tokens 1920 ｜ PR #4</sub>