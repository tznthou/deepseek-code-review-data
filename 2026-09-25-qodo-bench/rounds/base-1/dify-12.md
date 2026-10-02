<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多處 LIKE 查詢改為使用集中式 escape_like_pattern 函式，以正確處理特殊字元（%、_、\），並在多個服務中套用。整體方向正確，但存在幾個關鍵問題：1) 部分呼叫未傳入 escape 參數，導致跳脫失效；2) 在 ClickZetta 的 SQL 字串中，跳脫後的反斜線可能被 Python 字串處理吃掉，造成 SQL 語法錯誤或注入風險；3) 測試中對反斜線的處理可能因 Python 字串轉義而失真。建議優先修正 escape 參數缺失與 ClickZetta 的跳脫邏輯。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:990` | ClickZetta 的 LIKE 跳脫可能因 Python 字串處理而失效 | 0.85 |
| ⚠️ | Major | `api/core/rag/retrieval/dataset_retrieval.py:1207` | notlike 未傳入 escape 參數，跳脫失效 | 0.90 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/iris/iris_vector.py:298` | IRIS 的 LIKE 查詢使用 ESCAPE '\|' 但跳脫函式使用反斜線 | 0.80 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_annotation_service.py:475` | 測試中反斜線字串可能因 Python 轉義而失真 | 0.70 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_app_service.py:1030` | 測試中反斜線字串可能因 Python 轉義而失真 | 0.70 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_tag_service.py:340` | 測試中反斜線字串可能因 Python 轉義而失真 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:990</code> ClickZetta 的 LIKE 跳脫可能因 Python 字串處理而失效</summary>

程式碼先呼叫 `escape_like_pattern(query)` 得到含反斜線的字串，再 `.replace("'", "''")`，最後以 f-string 嵌入 SQL。但 Python 字串中的反斜線在 f-string 中不會被特殊處理，因此產生的 SQL 可能包含未跳脫的反斜線，導致 SQL 語法錯誤或跳脫失效。例如，若 query 為 `a\b`，escape_like_pattern 會回傳 `a\\b`，但 f-string 會直接輸出 `a\\b`，而 SQL 中需要 `a\\\\b` 才能正確表示。建議改用參數化查詢或明確處理反斜線。

**判斷依據**：diff 中該行使用 f-string 拼接，且 ESCAPE 子句為 '\\\\'，但 Python 字串中反斜線的處理可能導致最終 SQL 不正確。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> notlike 未傳入 escape 參數，跳脫失效</summary>

在 `case "not contains"` 分支中，`json_field.notlike(f"%{escaped_value}%")` 沒有傳入 `escape="\\"`。這會導致跳脫字元被視為一般字元，使用者輸入的 `%` 或 `_` 仍會被當作萬用字元，造成搜尋結果不正確，且可能被用於繞過預期的過濾邏輯。

**判斷依據**：diff 中該行未包含 escape 參數，而其他 like 呼叫均有。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/iris/iris_vector.py:298</code> IRIS 的 LIKE 查詢使用 ESCAPE '|' 但跳脫函式使用反斜線</summary>

程式碼使用 `escape_like_pattern` 跳脫，該函式以反斜線作為跳脫字元，但 SQL 中指定 `ESCAPE '|'`，兩者不一致。這會導致跳脫字元不被識別，使用者輸入的 `%` 或 `_` 仍會被當作萬用字元。應將 ESCAPE 子句改為 `ESCAPE '\\'` 或修改跳脫函式以使用 `|`。

**判斷依據**：diff 中該行指定 ESCAPE '|'，但 escape_like_pattern 使用反斜線。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_annotation_service.py:475</code> 測試中反斜線字串可能因 Python 轉義而失真</summary>

測試資料使用 `"path\\to\\file"`，在 Python 中這代表 `path\to\file`（兩個反斜線），但實際資料庫中可能儲存為單一反斜線。這可能導致測試無法正確驗證反斜線的跳脫行為。建議使用 raw string 或明確的雙反斜線來表示單一反斜線。

**判斷依據**：diff 中該行使用雙反斜線，但註解與測試目的可能期望單一反斜線。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_app_service.py:1030</code> 測試中反斜線字串可能因 Python 轉義而失真</summary>

測試資料使用 `"name": "path\\to\\app"`，在 Python 中這代表 `path\to\app`（兩個反斜線），但實際應用中可能儲存為單一反斜線。這可能導致測試無法正確驗證反斜線的跳脫行為。建議使用 raw string 或明確的雙反斜線來表示單一反斜線。

**判斷依據**：diff 中該行使用雙反斜線，但測試目的可能期望單一反斜線。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_tag_service.py:340</code> 測試中反斜線字串可能因 Python 轉義而失真</summary>

測試資料使用 `"name": "path\\to\\tag"`，在 Python 中這代表 `path\to\tag`（兩個反斜線），但實際應用中可能儲存為單一反斜線。這可能導致測試無法正確驗證反斜線的跳脫行為。建議使用 raw string 或明確的雙反斜線來表示單一反斜線。

**判斷依據**：diff 中該行使用雙反斜線，但測試目的可能期望單一反斜線。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14826 (cache hit 1536) ｜ completion tokens 1636 ｜ PR #12</sub>