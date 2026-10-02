<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正了 XmlCommentGenerator.Emitter.cs 中 ModelMetadata 可能為 null 導致的 NullReferenceException，並將 remarks 改寫入 Summary 而非 Description。同時新增了控制器路由參數的測試。整體方向正確，但需注意 metadata 為 null 時的行為、remarks 語意變更，以及測試覆蓋範圍。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382` | 將 remarks 指派給 Summary 可能改變 API 文件語意 | 0.80 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:444` | metadata 為 null 時直接跳過，可能遺漏文件產生 | 0.70 |
| 🔸 | Minor | `src/OpenApi/test/Microsoft.AspNetCore.OpenApi.SourceGenerators.Tests/OperationTests.Controllers.cs:141` | 測試方法缺少 Arrange/Act/Assert 結構，且未驗證 Summary | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382</code> 將 remarks 指派給 Summary 可能改變 API 文件語意</summary>

原本 `operation.Description = remarks;` 改為 `operation.Summary = remarks;`。在 OpenAPI 中，Summary 是簡短摘要，Description 是詳細說明。若 remarks 內容較長，放入 Summary 可能導致文件品質下降。建議確認此變更是否為預期行為，或考慮同時設定兩者。

**判斷依據**：diff 中 `- operation.Description = remarks;` 改為 `+ operation.Summary = remarks;`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:444</code> metadata 為 null 時直接跳過，可能遺漏文件產生</summary>

新增 `metadata is not null` 檢查後，若 `parameterDescription.ModelMetadata` 為 null，則整個 if 區塊跳過，不會嘗試從其他來源取得文件。若此情況常見，可能導致部分參數缺少描述。建議確認 null 是否為預期狀態，或考慮記錄警告。

**判斷依據**：diff 中新增 `metadata is not null` 條件

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/test/Microsoft.AspNetCore.OpenApi.SourceGenerators.Tests/OperationTests.Controllers.cs:141</code> 測試方法缺少 Arrange/Act/Assert 結構，且未驗證 Summary</summary>

測試 `SupportsRouteParametersFromControllers` 直接驗證 `path.Parameters[0].Description`，但未驗證 Summary 是否正確。若 PR 同時修改了 Summary 行為，此測試可能無法捕捉回歸。建議增加對 Summary 的斷言。

**判斷依據**：測試僅驗證 Description，未驗證 Summary

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10830 (cache hit 10752) ｜ completion tokens 679 ｜ PR #8</sub>