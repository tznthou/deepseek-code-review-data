<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正了 XmlCommentGenerator.Emitter.cs 中因 ModelMetadata 可能為 null 而導致的 NullReferenceException，並調整了 operation 的 Summary/Description 指派及參數名稱比對邏輯。主要風險在於將 Remarks 指派給 Summary 可能改變既有行為，以及移除 RequestBody.Description 指派後再重新加入的順序變更可能影響輸出。整體而言，修正方向正確，但需確認行為變更是否符合預期。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382` | 將 Remarks 指派給 Summary 可能改變既有行為 | 0.80 |
| ⚠️ | Major | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452` | 參數比對改用 propertyName 可能導致找不到對應參數 | 0.75 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479` | RequestBody.Description 指派順序變更可能影響範例設定 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382</code> 將 Remarks 指派給 Summary 可能改變既有行為</summary>

原本 `operation.Description = remarks;` 改為 `operation.Summary = remarks;`。若既有使用者依賴 Remarks 出現在 Description 欄位，此變更會造成 breaking change。建議確認此變更是否為預期，或考慮同時設定兩者。

**判斷依據**：diff 中 `- operation.Description = remarks;` 改為 `+ operation.Summary = remarks;`

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452</code> 參數比對改用 propertyName 可能導致找不到對應參數</summary>

原本 `p.Name == metadata.Name` 改為 `p.Name == propertyName`。若 metadata.Name 與 propertyName 不同（例如使用 BindProperty 或自訂名稱），可能無法正確比對到 operation parameter，導致描述遺失。建議確認此變更的必要性，或保留 metadata.Name 作為比對依據。

**判斷依據**：diff 中 `- var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == metadata.Name);` 改為 `+ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479</code> RequestBody.Description 指派順序變更可能影響範例設定</summary>

原本 `operation.RequestBody.Description = description;` 在範例處理之前，現在移到範例處理之後。若範例處理中發生例外，Description 可能不會被設定。建議確認此順序變更是否必要，或將 Description 指派保持在前面。

**判斷依據**：diff 中 `- operation.RequestBody.Description = description;` 被移除，並在範例處理後重新加入 `+ operation.RequestBody.Description = description;`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10794 (cache hit 1408) ｜ completion tokens 726 ｜ PR #8</sub>