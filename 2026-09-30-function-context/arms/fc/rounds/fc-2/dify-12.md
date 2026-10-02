<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 SQL LIKE 模式的跳脫邏輯集中到 `escape_like_pattern` 函式，並在多處查詢中套用，以提升安全性與一致性。整體方向正確，但存在幾個關鍵問題：`dataset_retrieval.py` 的 `not contains` 分支未加上 `escape` 參數，導致跳脫失效；`iris_vector.py` 使用 `|` 作為跳脫字元，但 `escape_like_pattern` 預設跳脫 `\`，可能造成行為不一致；`clickzetta_vector.py` 的 SQL 字串中跳脫字元處理可能不正確。此外，部分測試的斷言過於寬鬆，無法有效驗證跳脫行為。建議優先修正上述功能性問題，並補強測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/rag/retrieval/dataset_retrieval.py:1207` | `not contains` 分支未指定 escape 參數，跳脫失效 | 0.90 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/iris/iris_vector.py:298` | 跳脫字元不一致：使用 `\|` 但 `escape_like_pattern` 預設跳脫 `\` | 0.85 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991` | SQL 字串中的跳脫字元可能不正確 | 0.80 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_workflow_app_service.py:420` | 測試斷言過於寬鬆，無法有效驗證跳脫行為 | 0.70 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_app_service.py:1131` | 測試斷言未驗證不匹配項目 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> `not contains` 分支未指定 escape 參數，跳脫失效</summary>

在 `process_metadata_filter_func` 的 `not contains` 分支中，`json_field.notlike(f"%{escaped_value}%")` 沒有傳入 `escape="\\"`。這會導致 `escaped_value` 中的 `\%` 或 `\_` 被資料庫視為一般字元，而非跳脫序列，因此使用者輸入的 `%` 或 `_` 仍會被當作萬用字元，造成查詢結果錯誤，且可能被利用來進行萬用字元注入。

**失敗情境**：當使用者搜尋 `not contains` 條件且值包含 `%` 時，例如值為 `50%`，跳脫後為 `50\%`，但因為沒有指定 escape，資料庫會將 `\%` 視為兩個字元（`\` 和 `%`），其中 `%` 仍為萬用字元，導致比對到不應包含的資料。

**建議修法**：與其他分支一致，加上 `escape="\\"`：
```python
filters.append(json_field.notlike(f"%{escaped_value}%", escape="\\"))
```

**判斷依據**：diff 中該行未包含 escape 參數，而其他分支（如 `contains`）都有加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/iris/iris_vector.py:298</code> 跳脫字元不一致：使用 `|` 但 `escape_like_pattern` 預設跳脫 `\`</summary>

在 `search_by_full_text` 的 LIKE 查詢中，SQL 語句指定 `ESCAPE '|'`，但 `escape_like_pattern` 函式跳脫時使用的是反斜線 `\`。這會導致跳脫序列不被資料庫識別，例如輸入 `50%` 會被跳脫成 `50\%`，但因為 escape 字元是 `|`，資料庫會將 `\` 視為一般字元，`%` 仍為萬用字元，造成查詢結果錯誤。

**失敗情境**：當使用者搜尋包含 `%` 或 `_` 的字串時，跳脫完全失效，可能回傳過多或錯誤的結果。

**建議修法**：統一使用反斜線作為跳脫字元，將 SQL 改為 `ESCAPE '\\'`，或修改 `escape_like_pattern` 使其可接受自訂跳脫字元。

**判斷依據**：diff 中該行使用 `ESCAPE '|'`，而 `escape_like_pattern` 的實作固定使用 `\` 作為跳脫字元。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991</code> SQL 字串中的跳脫字元可能不正確</summary>

在 `_search_by_like` 中，SQL 字串為 `LIKE '%{escaped_query}%' ESCAPE '\\\\'`。`escaped_query` 已經由 `escape_like_pattern` 跳脫，其中反斜線被加倍。但此處的 `ESCAPE '\\\\'` 在 Python 字串中代表兩個反斜線，可能導致資料庫將跳脫字元視為兩個字元，而非單一反斜線，造成跳脫失效。

**失敗情境**：當查詢包含 `%` 或 `_` 時，跳脫可能不正確，導致萬用字元被當作一般字元或反之。

**建議修法**：確認資料庫的跳脫字元規範，並確保 Python 字串中的反斜線數量正確。通常應使用 `ESCAPE '\\'` 來表示單一反斜線。

**判斷依據**：diff 中該行使用了四個反斜線，可能過度跳脫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_workflow_app_service.py:420</code> 測試斷言過於寬鬆，無法有效驗證跳脫行為</summary>

在 `test_get_paginate_workflow_app_logs_with_special_characters_in_keyword` 中，多個斷言使用 `>= 1` 而非精確數量，例如 `assert result["total"] >= 1`。這可能導致測試無法捕捉到跳脫失效的情況，因為即使跳脫未生效，查詢仍可能回傳多筆資料，而測試只檢查至少有一筆。

**失敗情境**：若跳脫失效，搜尋 `50%` 可能同時匹配到 `50%` 和 `100%` 的資料，但測試只驗證 `total >= 1`，因此不會失敗。

**建議修法**：改為精確斷言，例如 `assert result["total"] == 1`，並驗證回傳的資料中不包含不應匹配的項目。

**判斷依據**：diff 中多處使用 `>= 1` 而非精確值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_app_service.py:1131</code> 測試斷言未驗證不匹配項目</summary>

在 `test_get_apps_with_special_characters_in_name` 的 Test 4 中，斷言 `assert all("50%" in app.name for app in paginated_apps.items)` 只檢查回傳的 app 名稱包含 `50%`，但未驗證回傳的 app 數量是否正確，也未驗證不應匹配的 app（如 `100% different`）是否被排除。

**失敗情境**：若跳脫失效，搜尋 `50%` 可能同時匹配到 `50% discount` 和 `100% different`，但測試只檢查所有回傳的 app 名稱都包含 `50%`，因此即使多回傳了 `100% different`，測試仍會通過。

**建議修法**：增加斷言驗證回傳的 app 數量為 1，且名稱不包含 `100%`。

**判斷依據**：diff 中該斷言未檢查數量或排除不匹配項目。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 28381 (cache hit 28288) ｜ completion tokens 1964 ｜ PR #12</sub>