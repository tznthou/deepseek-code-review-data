<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正了 XmlCommentGenerator.Emitter.cs 中 ModelMetadata 可能為 null 導致的 NullReferenceException，並新增了對應的測試與快照。主要變更包括：在存取 metadata.MetadataKind 前加入 null 檢查、將 operation.Description 改為 operation.Summary、使用 propertyName 取代 metadata.Name 來尋找參數，以及調整 RequestBody.Description 的設定位置。整體風險低，但需注意移除檔案開頭的 MIT 授權標頭違反了專案規範 R01，且測試方法缺少 Arrange-Act-Assert 註解（R06）。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:1` | [R01] 移除 MIT 授權標頭 | 0.95 |
| 🔸 | Minor | `src/OpenApi/test/Microsoft.AspNetCore.OpenApi.SourceGenerators.Tests/OperationTests.Controllers.cs:100` | [R06] 測試方法缺少 Arrange-Act-Assert 註解 | 0.90 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382` | 將 Remarks 指派給 Summary 可能改變語意 | 0.70 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452` | 使用 propertyName 取代 metadata.Name 可能影響參數匹配 | 0.70 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479` | RequestBody.Description 設定位置變更可能影響行為 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:1</code> [R01] 移除 MIT 授權標頭</summary>

檔案開頭的 MIT 授權標頭被移除，違反專案規範 R01。所有 C# 原始檔必須以標準的 .NET Foundation MIT 授權標頭開頭。請恢復授權標頭。

**判斷依據**：diff 中刪除了前兩行授權註解，且新增內容以 using 開頭。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/test/Microsoft.AspNetCore.OpenApi.SourceGenerators.Tests/OperationTests.Controllers.cs:100</code> [R06] 測試方法缺少 Arrange-Act-Assert 註解</summary>

新增的測試方法 SupportsRouteParametersFromControllers 未包含明確的 // Arrange、// Act、// Assert 註解，違反專案規範 R06。建議加入結構化註解以提升可讀性。

**判斷依據**：diff 中新增的測試方法沒有 AAA 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382</code> 將 Remarks 指派給 Summary 可能改變語意</summary>

原本將 methodComment.Remarks 指派給 operation.Description，現在改為 operation.Summary。這可能改變 OpenAPI 文件中 remarks 的呈現位置，需確認是否符合預期。

**判斷依據**：diff 中此行由 operation.Description = remarks 改為 operation.Summary = remarks。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452</code> 使用 propertyName 取代 metadata.Name 可能影響參數匹配</summary>

原本使用 metadata.Name 來尋找 operation.Parameters 中的參數，現在改為 propertyName。若 metadata.Name 與 propertyName 不同，可能導致找不到參數而將描述套用到 RequestBody。需確認此變更符合預期。

**判斷依據**：diff 中此行由 p.Name == metadata.Name 改為 p.Name == propertyName。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479</code> RequestBody.Description 設定位置變更可能影響行為</summary>

原本在 if (operation.RequestBody is not null) 區塊開頭就設定 operation.RequestBody.Description = description，現在移到區塊結尾。若中間有 continue 或例外，可能導致描述未被設定。需確認此變更不會造成遺漏。

**判斷依據**：diff 中此行從區塊開頭移至結尾。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13015 (cache hit 12928) ｜ completion tokens 1003 ｜ PR #8</sub>