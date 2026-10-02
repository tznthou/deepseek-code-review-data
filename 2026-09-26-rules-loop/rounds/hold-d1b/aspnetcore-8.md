<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

本次 PR 主要修正 XmlCommentGenerator.Emitter.cs 中 ModelMetadata 可能為 null 導致的 NullReferenceException，並調整 operation.Description 與 operation.Summary 的指派，以及將 RequestBody.Description 的設定延後。同時新增了對應的測試與快照。整體變更合理，但違反了多項 repo 規範：移除 MIT 授權標頭（R01）、測試方法缺少 Arrange-Act-Assert 註解（R06）、非同步方法未使用 ConfigureAwait(false)（R09）、非同步方法未提供 CancellationToken 參數（R10）、控制流程缺少大括號（R17）、大括號風格不符 Allman 風格（R18）。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:1` | [R01] 移除 MIT 授權標頭 | 0.95 |
| 🔸 | Minor | `src/OpenApi/test/Microsoft.AspNetCore.OpenApi.SourceGenerators.Tests/OperationTests.Controllers.cs:100` | [R06] 測試方法缺少 Arrange-Act-Assert 註解 | 0.90 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:444` | [R17] 控制流程缺少大括號 | 0.90 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:444` | [R18] 大括號風格不符 Allman 風格 | 0.90 |
| 🔸 | Minor | `src/OpenApi/test/Microsoft.AspNetCore.OpenApi.SourceGenerators.Tests/snapshots/OperationTests.SupportsRouteParametersFromControllers#OpenApiXmlCommentSupport.generated.verified.cs:346` | [R09] 非同步方法未使用 ConfigureAwait(false) | 0.85 |
| 🔸 | Minor | `src/OpenApi/test/Microsoft.AspNetCore.OpenApi.SourceGenerators.Tests/snapshots/OperationTests.SupportsRouteParametersFromControllers#OpenApiXmlCommentSupport.generated.verified.cs:346` | [R10] 非同步方法未提供 CancellationToken 參數 | 0.85 |

<details><summary>⚠️ <b>Major</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:1</code> [R01] 移除 MIT 授權標頭</summary>

檔案開頭的 MIT 授權標頭被移除，違反規範 R01。所有 C# 檔案必須以標準的 .NET Foundation MIT 授權標頭開頭。請恢復授權標頭。

**判斷依據**：diff 顯示刪除了兩行授權標頭：
-// Licensed to the .NET Foundation under one or more agreements.
-// The .NET Foundation licenses this file to you under the MIT license.

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/test/Microsoft.AspNetCore.OpenApi.SourceGenerators.Tests/OperationTests.Controllers.cs:100</code> [R06] 測試方法缺少 Arrange-Act-Assert 註解</summary>

新增的測試方法 SupportsRouteParametersFromControllers 未包含明確的 '// Arrange'、'// Act'、'// Assert' 註解，違反規範 R06。請加入對應的階段註解以提升可讀性。

**判斷依據**：diff 中新增的測試方法沒有 AAA 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:444</code> [R17] 控制流程缺少大括號</summary>

if 陳述式沒有使用大括號，違反規範 R17。請為所有控制流程加上大括號，即使只有單行。

**判斷依據**：diff 中新增的 if 條件沒有大括號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:444</code> [R18] 大括號風格不符 Allman 風格</summary>

if 陳述式的大括號位置不符合 Allman 風格（開頭大括號應在新行）。請調整大括號位置。

**判斷依據**：diff 中新增的 if 條件沒有大括號，但若加上大括號，應遵循 Allman 風格。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/test/Microsoft.AspNetCore.OpenApi.SourceGenerators.Tests/snapshots/OperationTests.SupportsRouteParametersFromControllers#OpenApiXmlCommentSupport.generated.verified.cs:346</code> [R09] 非同步方法未使用 ConfigureAwait(false)</summary>

TransformAsync 方法內沒有 await 表達式，因此不直接違反 R09。但若未來加入 await，應使用 ConfigureAwait(false)。目前無需變更。

**判斷依據**：方法簽章沒有 async 修飾詞，且方法體中沒有 await。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/test/Microsoft.AspNetCore.OpenApi.SourceGenerators.Tests/snapshots/OperationTests.SupportsRouteParametersFromControllers#OpenApiXmlCommentSupport.generated.verified.cs:346</code> [R10] 非同步方法未提供 CancellationToken 參數</summary>

TransformAsync 方法已包含 CancellationToken 參數，符合規範 R10。

**判斷依據**：方法簽章包含 CancellationToken 參數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13052 (cache hit 12928) ｜ completion tokens 1223 ｜ PR #8</sub>