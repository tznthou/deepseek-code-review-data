<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正了 XmlCommentOperationTransformer 中 ModelMetadata 可能為 null 導致的 NullReferenceException，並新增了對控制器路由參數的 XML 註解支援測試。主要變更包括：在存取 metadata 屬性前加入 null 檢查、將參數名稱比對從 metadata.Name 改為 propertyName、調整 RequestBody.Description 的設定時機，以及新增測試與快照。整體風險低，但需注意 metadata 為 null 時的行為、參數名稱變更的相容性，以及 RequestBody.Description 設定順序的影響。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:444` | metadata 為 null 時可能遺漏 XML 註解套用 | 0.60 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452` | 參數名稱比對從 metadata.Name 改為 propertyName 可能影響既有行為 | 0.50 |
| 🔸 | Minor | `src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:440` | RequestBody.Description 設定順序變更可能影響範例處理 | 0.40 |

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:444</code> metadata 為 null 時可能遺漏 XML 註解套用</summary>

當 `metadata` 為 null 時，整個 `if` 區塊會被跳過，導致原本可能套用的 XML 註解（例如來自 `propertyComment`）不會被處理。雖然這避免了 NullReferenceException，但可能造成某些情況下註解遺失。建議確認 `metadata` 為 null 的實際情境，並考慮是否需要在 null 時採取其他處理（例如記錄警告或使用其他來源）。

**判斷依據**：diff 中將原本直接存取 `metadata.MetadataKind` 改為先檢查 `metadata is not null`，但未提供 null 時的替代邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452</code> 參數名稱比對從 metadata.Name 改為 propertyName 可能影響既有行為</summary>

原本使用 `metadata.Name` 來比對 operation.Parameters 中的參數名稱，現在改為 `propertyName`。若 `metadata.Name` 與 `propertyName` 不同（例如 metadata 是複雜型別的屬性，而 operation 參數名稱是另一個別名），可能導致找不到對應參數，進而將描述套用到 RequestBody 或完全遺漏。建議確認此變更是否為預期，並補充相關測試。

**判斷依據**：diff 中將 `p.Name == metadata.Name` 改為 `p.Name == propertyName`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:440</code> RequestBody.Description 設定順序變更可能影響範例處理</summary>

原本先設定 `operation.RequestBody.Description = description;` 再處理範例，現在改為先處理範例再設定描述。若範例處理中發生例外（例如 `jsonString.Parse()` 拋出），描述將不會被設定，而原本的行為是描述已設定。雖然 `Parse()` 方法內部已捕捉例外並回傳 null，但其他例外仍可能發生。建議確認此順序變更是否必要，或考慮將描述設定放在 finally 區塊。

**判斷依據**：diff 中將 `operation.RequestBody.Description = description;` 從 if 區塊開頭移至結尾。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 20129 (cache hit 20096) ｜ completion tokens 961 ｜ PR #8</sub>