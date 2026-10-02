<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 SQL LIKE 模式的跳脫邏輯集中至 `escape_like_pattern` 函式，並在多處查詢中套用，以降低萬用字元注入風險。整體方向正確，但存在幾個關鍵問題：`dataset_retrieval.py` 的 `not contains` 分支未傳入 `escape` 參數，導致跳脫失效；`clickzetta_vector.py` 的 SQL 字串拼接仍存在 SQL 注入風險；`iris_vector.py` 使用 `ESCAPE '|'` 但跳脫函式使用反斜線，可能造成行為不一致。此外，部分檔案未使用 `helper.escape_like_pattern` 的別名，可能違反匯入慣例。建議優先修正上述問題，並補齊測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/rag/retrieval/dataset_retrieval.py:1207` | not contains 分支未傳入 escape 參數，跳脫失效 | 0.95 |
| 🛑 | Blocker | `api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991` | SQL 字串拼接仍存在注入風險 | 0.90 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/iris/iris_vector.py:298` | ESCAPE 字元與跳脫函式不一致 | 0.80 |
| 🔸 | Minor | `api/services/dataset_service.py:147` | 未使用 helper 別名，可能違反匯入慣例 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> not contains 分支未傳入 escape 參數，跳脫失效</summary>

在 `case "not contains"` 分支中，呼叫 `json_field.notlike(f"%{escaped_value}%")` 時未傳入 `escape="\\"` 參數。這會導致跳脫字元（反斜線）被視為一般字元，使得 `%` 和 `_` 仍被當作萬用字元，無法達成預期的跳脫效果。攻擊者可利用此漏洞進行萬用字元注入，繞過過濾條件。

建議修正：
```python
filters.append(json_field.notlike(f"%{escaped_value}%", escape="\\"))
```

**判斷依據**：diff 中該行未包含 escape 參數，與其他分支（如 contains）不一致。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991</code> SQL 字串拼接仍存在注入風險</summary>

此處使用 f-string 將 `escaped_query` 直接嵌入 SQL 查詢，雖然已對 LIKE 特殊字元進行跳脫，但未對單引號進行參數化處理。攻擊者若輸入包含單引號的字串（例如 `' OR 1=1 --`），仍可能破壞 SQL 語法並注入任意條件。建議改用參數化查詢，或至少使用資料庫驅動提供的安全跳脫函式。

**判斷依據**：diff 中該行仍使用字串拼接，且 `escaped_query` 僅跳脫 LIKE 特殊字元，未處理單引號。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/iris/iris_vector.py:298</code> ESCAPE 字元與跳脫函式不一致</summary>

此處使用 `ESCAPE '|'`，但 `escape_like_pattern` 函式使用反斜線（`\`）作為跳脫字元。這會導致跳脫序列無法被正確解析，例如輸入 `%` 會被跳脫為 `\%`，但資料庫會將 `|` 視為跳脫字元，因此 `\%` 中的 `%` 仍會被當作萬用字元。建議統一使用反斜線作為跳脫字元，或修改跳脫函式以支援自訂跳脫字元。

**判斷依據**：diff 中該行指定 ESCAPE '|'，而 escape_like_pattern 使用反斜線。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/services/dataset_service.py:147</code> 未使用 helper 別名，可能違反匯入慣例</summary>

此處直接使用 `helper.escape_like_pattern`，但其他檔案多使用 `from libs.helper import escape_like_pattern` 後直接呼叫。雖然功能上無誤，但可能違反專案的匯入風格（R02）。建議統一使用直接匯入的方式。

**判斷依據**：diff 中該行使用 `helper.escape_like_pattern`，而其他檔案（如 conversation.py）使用直接匯入。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17504 (cache hit 17408) ｜ completion tokens 1173 ｜ PR #12</sub>