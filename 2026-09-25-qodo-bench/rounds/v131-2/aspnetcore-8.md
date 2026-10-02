<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正了 XmlCommentGenerator.Emitter.cs 中因 ModelMetadata 可能為 null 而導致的 NullReferenceException，並新增了對控制器路由參數的 XML 註解支援。主要變更包括：在存取 metadata 前加入 null 檢查、將 remarks 指派給 Summary 而非 Description、修正參數名稱比對邏輯、調整 RequestBody.Description 的設定時機，並新增對應的測試與快照。整體風險低，但需注意 remarks 語意變更可能影響既有行為，以及參數名稱比對邏輯的變更是否涵蓋所有情境。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382` | 將 remarks 指派給 Summary 可能改變既有語意 | 0.80 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452` | 參數名稱比對改用 propertyName 可能導致找不到對應參數 | 0.70 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479` | RequestBody.Description 設定時機延後可能影響範例處理 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382</code> 將 remarks 指派給 Summary 可能改變既有語意</summary>

原本將 methodComment.Remarks 指派給 operation.Description，現在改為指派給 operation.Summary。這可能導致既有使用 Description 欄位的用戶端行為改變。若 remarks 原本用於提供較長的說明，現在放在 Summary 可能不符合 OpenAPI 慣例（Summary 應簡短）。建議確認此變更是否為預期行為，或考慮同時設定兩者。

**判斷依據**：diff 中將 `operation.Description = remarks;` 改為 `operation.Summary = remarks;`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452</code> 參數名稱比對改用 propertyName 可能導致找不到對應參數</summary>

原本使用 `metadata.Name` 來比對 operation.Parameters 中的參數名稱，現在改為使用 `propertyName`。若 `metadata.Name` 與 `propertyName` 不同（例如 metadata.Name 可能包含前綴或不同大小寫），可能導致找不到對應的參數，進而將描述誤設到 RequestBody。建議確認兩者是否總是一致，或保留 fallback 邏輯。

**判斷依據**：diff 中將 `p.Name == metadata.Name` 改為 `p.Name == propertyName`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479</code> RequestBody.Description 設定時機延後可能影響範例處理</summary>

原本在設定範例之前就設定 RequestBody.Description，現在移到範例處理之後。若範例處理過程中發生例外（例如 jsonString.Parse() 失敗），Description 將不會被設定。建議確認此變更是否為預期，或考慮在 try-catch 中處理。

**判斷依據**：diff 中將 `operation.RequestBody.Description = description;` 從範例處理前移至範例處理後

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10794 (cache hit 10752) ｜ completion tokens 772 ｜ PR #8</sub>