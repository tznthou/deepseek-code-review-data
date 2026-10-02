<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多處 SQL LIKE 查詢改為使用集中式 escape_like_pattern 函式，以正確跳脫特殊字元（%、_、\），並在部分查詢中加入 escape 參數。整體方向正確，能降低 LIKE 萬用字元造成的意外匹配或注入風險。但仍有幾處實作不一致：部分查詢未加上 escape 參數、部分使用不同跳脫字元（如 '|'）、以及 ClickZetta 的 ESCAPE 子句可能因雙重跳脫而失效。此外，測試中對 backslash 的處理可能因 Python 字串轉義而與實際不符。建議先修正這些不一致處再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991` | ESCAPE 子句中的反斜線可能被雙重跳脫，導致跳脫失效 | 0.80 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/iris/iris_vector.py:298` | ESCAPE 子句使用 '\|' 與 escape_like_pattern 產生的反斜線跳脫不一致 | 0.75 |
| ⚠️ | Major | `api/core/rag/retrieval/dataset_retrieval.py:1207` | not contains 條件未加上 escape 參數，導致跳脫失效 | 0.70 |
| 🔸 | Minor | `api/libs/helper.py:35` | 函式缺少型別註記，違反 R01 | 0.60 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_annotation_service.py:475` | 測試中對 backslash 的處理可能因 Python 字串轉義而與實際不符 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991</code> ESCAPE 子句中的反斜線可能被雙重跳脫，導致跳脫失效</summary>

在 `filter_clauses.append(f"{Field.CONTENT_KEY} LIKE '%{escaped_query}%' ESCAPE '\\\\'")` 中，`ESCAPE '\\\\'` 在 Python f-string 中會變成 `ESCAPE '\\'`，傳給資料庫後可能被解讀為兩個反斜線，而非單一反斜線。這會使 `escape_like_pattern` 產生的跳脫序列（如 `\%`）無法被正確解析，導致 `%` 仍被視為萬用字元。

**失敗情境**：當使用者搜尋包含 `%` 的字串時，例如 `50%`，`escaped_query` 會是 `50\%`，但若 ESCAPE 字元不是單一反斜線，資料庫可能將 `\%` 視為跳脫的反斜線後接萬用字元 `%`，造成匹配所有含 `50` 後接任意字元的結果。

**建議**：確認 ClickZetta 資料庫的 ESCAPE 語法，並使用單一反斜線作為跳脫字元。可考慮使用參數化查詢或直接使用 `ESCAPE '\\'`（在 Python 字串中表示單一反斜線）。

**判斷依據**：diff 中新增的這一行，ESCAPE 子句使用了四個反斜線，可能導致跳脫字元不正確。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/iris/iris_vector.py:298</code> ESCAPE 子句使用 '|' 與 escape_like_pattern 產生的反斜線跳脫不一致</summary>

在 `WHERE text LIKE ? ESCAPE '|'` 中，跳脫字元被指定為 `|`，但 `escape_like_pattern` 函式是使用反斜線 `\` 來跳脫特殊字元。這會導致跳脫序列無法被正確解析，例如 `escaped_query` 中的 `\%` 會被資料庫視為反斜線字元後接萬用字元 `%`，而不是跳脫的 `%`。

**失敗情境**：當使用者搜尋包含 `%` 或 `_` 的字串時，這些字元仍會被當作萬用字元，導致搜尋結果不正確。

**建議**：將 ESCAPE 子句改為 `ESCAPE '\\'`（在 Python 字串中表示單一反斜線），或修改 `escape_like_pattern` 使其使用 `|` 作為跳脫字元。

**判斷依據**：diff 中新增的 ESCAPE 子句使用 '|'，與 escape_like_pattern 的跳脫字元不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> not contains 條件未加上 escape 參數，導致跳脫失效</summary>

在 `case "not contains"` 分支中，`filters.append(json_field.notlike(f"%{escaped_value}%"))` 沒有傳入 `escape="\\"` 參數。這使得 `escaped_value` 中的跳脫序列（如 `\%`）不會被資料庫視為跳脫，而是被當作一般字元，導致 `%` 和 `_` 仍具有萬用字元功能。

**失敗情境**：當使用者使用「not contains」條件搜尋包含 `%` 的字串時，例如 `50%`，`escaped_value` 會是 `50\%`，但因為沒有指定 escape，資料庫可能將 `\%` 解讀為反斜線後接萬用字元 `%`，導致排除條件不正確。

**建議**：在 `notlike` 呼叫中加入 `escape="\\"` 參數，與其他分支保持一致。

**判斷依據**：diff 中此分支未加上 escape 參數，而其他分支（如 contains）有加上。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/helper.py:35</code> 函式缺少型別註記，違反 R01</summary>

根據專案規範 R01，所有 Python 函式必須包含型別註記。`escape_like_pattern` 的參數 `pattern` 和回傳值都缺少型別標註。

**建議**：加上型別註記，例如 `def escape_like_pattern(pattern: str) -> str:`。

**判斷依據**：diff 中新增的函式定義沒有型別註記。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_annotation_service.py:475</code> 測試中對 backslash 的處理可能因 Python 字串轉義而與實際不符</summary>

在測試資料中，`"question": "Question with path\\to\\file"` 實際上在 Python 中會被解讀為 `path\to\file`（單一反斜線）。但 `escape_like_pattern` 函式會將單一反斜線跳脫為雙反斜線，因此搜尋時使用的關鍵字 `"path\\to\\file"` 在 Python 中也是單一反斜線，經過跳脫後會變成雙反斜線。這可能導致測試無法正確驗證跳脫行為。

**建議**：確認測試資料和搜尋關鍵字的實際字串內容，並使用 raw string（如 `r"path\to\file"`）來避免混淆。

**判斷依據**：diff 中測試資料使用雙反斜線，但 Python 字串轉義可能導致實際值與預期不同。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17504 (cache hit 5888) ｜ completion tokens 1801 ｜ PR #12</sub>