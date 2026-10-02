<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正了 XmlCommentOperationTransformer 中 ModelMetadata 可能為 null 導致的 NullReferenceException，並新增了對控制器路由參數的 XML 註解支援測試。主要變更包括：在存取 metadata 前加入 null 檢查、將參數名稱比對從 metadata.Name 改為 propertyName、調整 RequestBody.Description 的設定時機，以及新增測試與快照。整體風險低，但需注意 metadata 為 null 時的行為、參數名稱變更可能影響既有功能，以及測試覆蓋範圍。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:444` | metadata 為 null 時可能遺漏 XML 註解套用 | 0.60 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452` | 參數名稱比對從 metadata.Name 改為 propertyName 可能影響既有功能 | 0.50 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479` | RequestBody.Description 設定時機變更可能影響範例處理 | 0.40 |

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:444</code> metadata 為 null 時可能遺漏 XML 註解套用</summary>

當 `metadata` 為 null 時，整個 if 區塊會被跳過，導致該參數的 XML 註解（例如 `<param>` 或屬性註解）不會被套用。雖然這避免了 NullReferenceException，但可能造成 OpenAPI 文件中缺少描述。建議確認 `metadata` 為 null 的情境是否合理，若可能發生，應考慮其他處理方式（例如記錄警告或使用替代資訊）。

**判斷依據**：diff 中新增了 `metadata is not null` 條件，但未處理 null 時的行為。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452</code> 參數名稱比對從 metadata.Name 改為 propertyName 可能影響既有功能</summary>

原本使用 `metadata.Name` 來比對 operation.Parameters 中的參數名稱，現在改為 `propertyName`。若 `metadata.Name` 與 `propertyName` 不同（例如使用別名或繫結名稱不同），可能導致找不到對應的參數，進而將描述套用到 RequestBody 或完全遺漏。建議確認此變更是否為預期行為，並補充相關測試。

**判斷依據**：diff 中將 `p.Name == metadata.Name` 改為 `p.Name == propertyName`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479</code> RequestBody.Description 設定時機變更可能影響範例處理</summary>

原本先設定 `operation.RequestBody.Description = description`，再處理範例；現在改為先處理範例，再設定 Description。若範例處理過程中發生例外（例如 `jsonString.Parse()` 失敗），Description 將不會被設定，可能導致部分資訊遺失。建議確認此變更是否為預期，並考慮將 Description 設定放在 finally 或確保例外處理。

**判斷依據**：diff 中將 `operation.RequestBody.Description = description;` 從範例處理前移至範例處理後。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 20129 (cache hit 1536) ｜ completion tokens 828 ｜ PR #8</sub>