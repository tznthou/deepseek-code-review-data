<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 修正了 XmlCommentGenerator 中 ModelMetadata 可能為 null 導致的 NullReferenceException，並將 remarks 改寫入 Summary 而非 Description，同時調整了 RequestBody.Description 的設定時機。主要風險在於移除 MIT 授權標頭違反專案規範，以及將 remarks 寫入 Summary 可能造成語意不符。整體而言，修正方向正確，但需補回授權標頭並確認 remarks 的語意。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:1` | [R01] 缺少 MIT 授權標頭 | 0.99 |
| ⚠️ | Major | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382` | 將 remarks 寫入 Summary 可能造成語意不符 | 0.80 |
| ⚠️ | Major | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452` | 使用 propertyName 取代 metadata.Name 可能導致參數比對失敗 | 0.70 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479` | RequestBody.Description 設定時機變更可能影響既有行為 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:1</code> [R01] 缺少 MIT 授權標頭</summary>

此檔案開頭原有的 MIT 授權標頭被移除，違反專案規範 R01。所有 C# 檔案必須以標準的兩行授權註解開頭。請補回：
```
// Licensed to the .NET Foundation under one or more agreements.
// The .NET Foundation licenses this file to you under the MIT license.
```

**判斷依據**：diff 中刪除了兩行授權註解，且未新增替代內容。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382</code> 將 remarks 寫入 Summary 可能造成語意不符</summary>

原本將 `<remarks>` 內容寫入 `operation.Description`，現在改為寫入 `operation.Summary`。在 OpenAPI 中，Summary 應為簡短摘要，而 Description 為詳細說明。若 remarks 內容較長，放入 Summary 可能導致 API 文件顯示不當。建議確認此變更是否符合預期，或考慮同時設定兩者。

**判斷依據**：diff 中將 `operation.Description = remarks;` 改為 `operation.Summary = remarks;`

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452</code> 使用 propertyName 取代 metadata.Name 可能導致參數比對失敗</summary>

原本以 `metadata.Name` 比對 operation.Parameters 中的參數名稱，現在改為 `propertyName`。若 `metadata.Name` 與 `propertyName` 不同（例如 metadata.Name 可能包含前綴或不同大小寫），可能找不到對應參數，導致描述無法套用。請確認兩者在此情境下是否恆等。

**判斷依據**：diff 中將 `p.Name == metadata.Name` 改為 `p.Name == propertyName`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479</code> RequestBody.Description 設定時機變更可能影響既有行為</summary>

原本在處理 propertyComment.Examples 之前就設定 `operation.RequestBody.Description = description`，現在移到處理 Examples 之後。若 Examples 處理過程中發生例外或提前 continue，可能導致 Description 未被設定。建議確認此變更不會造成描述遺失。

**判斷依據**：diff 中將該行從 if 區塊開頭移至結尾。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13015 (cache hit 10752) ｜ completion tokens 905 ｜ PR #8</sub>