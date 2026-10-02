<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多處 LIKE 查詢改為使用統一的 escape_like_pattern 函式，並加入 escape 參數，以正確處理特殊字元。整體方向正確，但存在幾個關鍵問題：1) 部分查詢（如 dataset_retrieval.py 的 not contains）未加上 escape 參數，導致跳脫失效；2) clickzetta_vector.py 的 ESCAPE 子句可能因雙重跳脫而產生語法錯誤；3) 新增測試中對 backslash 的處理可能因 Python 字串轉義而與實際不符。建議修正上述問題後再合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/rag/retrieval/dataset_retrieval.py:1207` | not contains 條件未指定 escape 參數，導致跳脫失效 | 0.95 |
| 🛑 | Blocker | `api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991` | ESCAPE 子句可能因雙重跳脫而產生語法錯誤 | 0.90 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/iris/iris_vector.py:298` | ESCAPE 子句使用 '\|' 但跳脫函式使用反斜線，可能導致跳脫不一致 | 0.80 |
| ⚠️ | Major | `api/tests/test_containers_integration_tests/services/test_annotation_service.py:474` | 測試中對 backslash 的處理可能因 Python 字串轉義而與實際不符 | 0.75 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_app_service.py:1071` | 測試中對 backslash 的處理可能因 Python 字串轉義而與實際不符 | 0.70 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_tag_service.py:354` | 測試中對 backslash 的處理可能因 Python 字串轉義而與實際不符 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> not contains 條件未指定 escape 參數，導致跳脫失效</summary>

在 `case "not contains"` 分支中，`json_field.notlike(f"%{escaped_value}%")` 未傳入 `escape="\\"`。這會使資料庫將跳脫後的反斜線視為一般字元，而非跳脫字元，導致 `%` 和 `_` 仍被當作萬用字元。例如，若 `value` 為 `50%`，`escaped_value` 為 `50\%`，但查詢會匹配到任何以 `50` 開頭且後面接任意字元的字串，而非僅匹配字面 `50%`。這會造成搜尋結果不正確，且可能被利用來繞過預期的過濾邏輯。

**判斷依據**：diff 中該行未包含 escape 參數，與其他分支（如 contains）形成對比。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991</code> ESCAPE 子句可能因雙重跳脫而產生語法錯誤</summary>

程式碼使用 `escape_like_pattern(query).replace("'", "''")` 後，再將結果放入 SQL 字串，並加上 `ESCAPE '\\\\'`。但 `escape_like_pattern` 已將反斜線跳脫為 `\\`，而 `ESCAPE '\\\\'` 在 SQL 中代表跳脫字元為單一反斜線。這可能導致查詢中的跳脫序列被錯誤解析，甚至產生語法錯誤。例如，若 query 為 `path\to\file`，escaped_query 會是 `path\\to\\file`，而 SQL 中的 `ESCAPE '\\\\'` 可能使資料庫將 `\\` 視為跳脫後的反斜線，造成模式匹配錯誤。

**判斷依據**：diff 中該行明確加入 ESCAPE 子句，但與 escape_like_pattern 的跳脫方式可能衝突。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/iris/iris_vector.py:298</code> ESCAPE 子句使用 '|' 但跳脫函式使用反斜線，可能導致跳脫不一致</summary>

在 Iris 向量資料庫的 LIKE 查詢中，程式碼使用 `ESCAPE '|'`，但 `escape_like_pattern` 函式使用反斜線作為跳脫字元。這會導致跳脫後的反斜線被資料庫視為一般字元，而 `|` 被當作跳脫字元，但跳脫後的字串中並未使用 `|`，因此 `%` 和 `_` 仍會被當作萬用字元。例如，若 query 為 `50%`，escaped_query 為 `50\%`，但資料庫會將 `\` 視為兩個字元，而 `%` 仍為萬用字元，導致匹配到所有以 `50` 開頭的字串。

**判斷依據**：diff 中該行加入 ESCAPE '|'，但 escape_like_pattern 使用反斜線，兩者不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/tests/test_containers_integration_tests/services/test_annotation_service.py:474</code> 測試中對 backslash 的處理可能因 Python 字串轉義而與實際不符</summary>

在測試 `test_get_annotation_list_by_app_id_with_special_characters_in_keyword` 中，建立 annotation 時使用 `"path\\to\\file"`，這在 Python 中代表字串 `path\to\file`（單一反斜線）。但測試搜尋時使用 `keyword="path\\to\\file"`，同樣代表單一反斜線。然而，`escape_like_pattern` 會將單一反斜線跳脫為雙反斜線，而資料庫在 `ESCAPE '\\'` 下會將雙反斜線解讀為單一反斜線，因此匹配應該正確。但若測試環境的資料庫驅動或設定不同，可能導致跳脫行為不一致，使測試不穩定。

**判斷依據**：diff 中該測試使用雙反斜線字串，但實際儲存和搜尋時可能因轉義而產生差異。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_app_service.py:1071</code> 測試中對 backslash 的處理可能因 Python 字串轉義而與實際不符</summary>

在測試 `test_get_apps_with_special_characters_in_name` 中，建立 app 時使用 `"path\\to\\app"`，代表字串 `path\to\app`。但搜尋時使用 `args = {"name": "path\\to\\app", ...}`，同樣代表單一反斜線。這可能導致測試在實際環境中因跳脫不一致而失敗。

**判斷依據**：diff 中該測試使用雙反斜線字串，但實際儲存和搜尋時可能因轉義而產生差異。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_tag_service.py:354</code> 測試中對 backslash 的處理可能因 Python 字串轉義而與實際不符</summary>

在測試 `test_get_tags_with_special_characters_in_keyword` 中，建立 tag 時使用 `"path\\to\\tag"`，代表字串 `path\to\tag`。但搜尋時使用 `keyword="path\\to\\tag"`，同樣代表單一反斜線。這可能導致測試在實際環境中因跳脫不一致而失敗。

**判斷依據**：diff 中該測試使用雙反斜線字串，但實際儲存和搜尋時可能因轉義而產生差異。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14790 (cache hit 14720) ｜ completion tokens 1930 ｜ PR #12</sub>