<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正了 XmlCommentGenerator.Emitter.cs 中 ModelMetadata 可能為 null 導致的 NullReferenceException，並將 remarks 的指派從 Description 改為 Summary。同時新增了針對控制器路由參數的測試。主要風險在於 metadata 為 null 時的行為變更（跳過處理）可能導致部分 XML 註解遺失，以及 remarks 語意變更可能影響既有輸出。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382` | 將 remarks 指派給 Summary 可能改變既有 API 文件語意 | 0.80 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:444` | metadata 為 null 時跳過處理可能遺失部分 XML 註解 | 0.60 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452` | 使用 propertyName 取代 metadata.Name 可能影響參數比對 | 0.50 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479` | RequestBody.Description 指派位置變更可能影響範例處理 | 0.40 |

<details><summary>⚠️ <b>Major</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382</code> 將 remarks 指派給 Summary 可能改變既有 API 文件語意</summary>

原本 `operation.Description = remarks;` 改為 `operation.Summary = remarks;`。在 OpenAPI 中，Summary 與 Description 有不同用途：Summary 通常較簡短，Description 較詳細。若既有 XML 註解中 `<remarks>` 內容較長，此變更可能導致產生的 OpenAPI 文件不符合預期。建議確認此變更為有意為之，並考慮是否應同時設定兩者或保留原行為。

**判斷依據**：diff 中 `- operation.Description = remarks;` 改為 `+ operation.Summary = remarks;`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:444</code> metadata 為 null 時跳過處理可能遺失部分 XML 註解</summary>

新增 `metadata is not null` 條件後，當 `parameterDescription.ModelMetadata` 為 null 時會直接跳過整個區塊。若此情況在實際執行中可能發生（例如某些參數沒有對應的 ModelMetadata），則原本可能套用的 XML 註解將不再套用。建議確認此行為是否符合預期，或考慮在 null 時採取其他處理方式。

**判斷依據**：diff 中新增 `metadata is not null &&` 條件

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452</code> 使用 propertyName 取代 metadata.Name 可能影響參數比對</summary>

原本 `p.Name == metadata.Name` 改為 `p.Name == propertyName`。若 `metadata.Name` 與 `propertyName` 可能不同（例如 metadata 名稱經過轉換），此變更可能導致找不到對應的 operation parameter，進而將描述套用到 RequestBody 而非參數。建議確認兩者在此情境下是否恆等。

**判斷依據**：diff 中 `- var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == metadata.Name);` 改為 `+ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479</code> RequestBody.Description 指派位置變更可能影響範例處理</summary>

原本 `operation.RequestBody.Description = description;` 在處理範例之前，現在移到範例處理之後。若 `propertyComment.Examples` 存在且解析失敗，原本仍會設定 Description，現在則可能不會。建議確認此順序變更是否會造成行為差異。

**判斷依據**：diff 中 `- operation.RequestBody.Description = description;` 被移除，並在範例處理後新增 `+ operation.RequestBody.Description = description;`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10830 (cache hit 10752) ｜ completion tokens 980 ｜ PR #8</sub>