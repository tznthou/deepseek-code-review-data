<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正了 XmlCommentGenerator.Emitter.cs 中 ModelMetadata 可能為 null 導致的 NullReferenceException，並調整了 operation.Description 與 operation.Summary 的指派，以及參數名稱的比對。同時新增了對應的測試與快照。主要風險在於刪除了 Emitter.cs 的 MIT 授權標頭，違反 R01；其餘變更大致符合規範。

### Findings（1 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:1` | [R01] 缺少 MIT 授權標頭 | 0.95 |

<details><summary>⚠️ <b>Major</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:1</code> [R01] 缺少 MIT 授權標頭</summary>

此檔案開頭原本有 MIT 授權標頭，但在此 PR 中被刪除。根據規範 R01，所有 C# 原始檔必須以標準的 .NET Foundation MIT 授權標頭開頭。請恢復授權標頭。

**判斷依據**：diff 顯示刪除了以下兩行：
-// Licensed to the .NET Foundation under one or more agreements.
-// The .NET Foundation licenses this file to you under the MIT license.
且未新增替代標頭。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13052 (cache hit 12928) ｜ completion tokens 315 ｜ PR #8</sub>