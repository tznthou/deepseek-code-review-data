<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正了 XmlCommentGenerator.Emitter.cs 中 ModelMetadata 可能為 null 導致的 NullReferenceException，並將 remarks 改寫入 Summary 而非 Description。同時新增了控制器路由參數的測試。主要風險在於將 remarks 改寫入 Summary 可能改變既有 API 文件行為，且測試僅驗證了參數描述，未涵蓋 remarks 的變更。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382` | 將 remarks 寫入 Summary 可能改變既有 API 文件行為 | 0.80 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452` | 使用 propertyName 取代 metadata.Name 可能導致參數名稱不一致 | 0.60 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479` | RequestBody.Description 設定位置變更可能影響範例處理 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382</code> 將 remarks 寫入 Summary 可能改變既有 API 文件行為</summary>

原本 `operation.Description = remarks;` 改為 `operation.Summary = remarks;`。這會將 `<remarks>` 的內容放到 OpenAPI 的 `summary` 欄位，而非 `description`。若既有使用者依賴 `description` 來顯示備註，此變更會造成文件內容遺失或錯置。建議確認此變更是否符合預期，或考慮同時設定兩者。

**判斷依據**：diff 中 `- operation.Description = remarks;` 改為 `+ operation.Summary = remarks;`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452</code> 使用 propertyName 取代 metadata.Name 可能導致參數名稱不一致</summary>

原本 `p.Name == metadata.Name` 改為 `p.Name == propertyName`。若 `metadata.Name` 與 `propertyName` 不同（例如使用別名或序列化名稱），可能找不到對應的參數。建議確認兩者是否永遠相同，或保留原本的比對方式。

**判斷依據**：diff 中 `- var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == metadata.Name);` 改為 `+ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479</code> RequestBody.Description 設定位置變更可能影響範例處理</summary>

原本 `operation.RequestBody.Description = description;` 在 if 區塊開頭，現在移到範例處理之後。若 `propertyComment.Examples` 存在但 `content` 為 null，會執行 `continue`，導致 `Description` 不會被設定。建議確認此情境是否會發生，或將 Description 設定保持在區塊開頭。

**判斷依據**：diff 中 `- operation.RequestBody.Description = description;` 被移除，並在範例處理後新增 `+ operation.RequestBody.Description = description;`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10830 (cache hit 1536) ｜ completion tokens 757 ｜ PR #8</sub>