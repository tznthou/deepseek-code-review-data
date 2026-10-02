<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 SQL LIKE 模式的跳脫邏輯集中至 `escape_like_pattern` 函式，並在多處查詢中套用，以降低萬用字元注入風險。整體方向正確，但存在幾個關鍵問題：`escape_like_pattern` 的跳脫順序可能導致雙重跳脫；部分呼叫點未傳入 `escape` 參數，使跳脫失效；ClickZetta 的 SQL 字串拼接仍存在注入風險；測試檔案中大量延遲匯入 `AppService` 可能掩蓋循環依賴問題。建議優先修正跳脫邏輯與不一致的 `escape` 參數使用。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/libs/helper.py:64` | 跳脫順序錯誤導致雙重跳脫 | 0.95 |
| 🛑 | Blocker | `api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991` | ClickZetta 查詢仍使用字串拼接，存在 SQL 注入風險 | 0.90 |
| ⚠️ | Major | `api/core/rag/retrieval/dataset_retrieval.py:1207` | `not contains` 條件未傳入 `escape` 參數，跳脫失效 | 0.85 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/iris/iris_vector.py:298` | IRIS 查詢使用 `ESCAPE '\|'` 但跳脫字元為反斜線 | 0.80 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_app_service.py:12` | 測試檔案中大量延遲匯入 `AppService` 可能掩蓋循環依賴 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/libs/helper.py:64</code> 跳脫順序錯誤導致雙重跳脫</summary>

`escape_like_pattern` 先將反斜線跳脫為 `\\`，再將 `%` 和 `_` 跳脫為 `\%` 和 `\_`。這會導致輸入中原本就包含反斜線的字元被錯誤處理。例如輸入 `"test\\%_value"`，預期結果應為 `"test\\\\\\%\\_value"`（每個特殊字元前加一個反斜線），但實際輸出為 `"test\\\\\\%\\_value"`（反斜線被重複跳脫）。這會使 LIKE 查詢無法正確匹配包含反斜線的資料。

建議修正：先跳脫 `%` 和 `_`，再跳脫反斜線，或使用正規表達式一次完成。

**判斷依據**：函式實作中，`replace("\\", "\\\\")` 先執行，導致後續跳脫 `%` 和 `_` 時，新加入的反斜線不會被再次跳脫，但原本的反斜線已被加倍。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991</code> ClickZetta 查詢仍使用字串拼接，存在 SQL 注入風險</summary>

在 `_search_by_like` 方法中，`filter_clauses.append(f"{Field.CONTENT_KEY} LIKE '%{escaped_query}%' ESCAPE '\\\\'")` 仍使用 f-string 拼接 SQL。雖然 `escaped_query` 經過 `escape_like_pattern` 和單引號跳脫，但這種方式無法完全防止 SQL 注入，尤其是當 `query` 包含其他特殊字元或資料庫特定的跳脫序列時。應改用參數化查詢（如 `cursor.execute` 的參數綁定）來徹底消除風險。

**判斷依據**：diff 中顯示該行仍使用 f-string 拼接，且 `escaped_query` 僅做簡單替換，未使用參數化。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> `not contains` 條件未傳入 `escape` 參數，跳脫失效</summary>

在 `process_metadata_filter_func` 的 `not contains` 分支中，`filters.append(json_field.notlike(f"%{escaped_value}%"))` 未傳入 `escape="\\"`。這會導致 `escaped_value` 中的反斜線被資料庫視為普通字元，而非跳脫字元，使得 `%` 和 `_` 仍被當作萬用字元，跳脫完全失效。應與其他分支一致，加上 `escape="\\"`。

**判斷依據**：diff 中該行缺少 `escape` 參數，而其他分支均有。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/iris/iris_vector.py:298</code> IRIS 查詢使用 `ESCAPE '|'` 但跳脫字元為反斜線</summary>

在 `search_by_full_text` 的 LIKE 查詢中，SQL 語句指定 `ESCAPE '|'`，但 `escape_like_pattern` 產生的跳脫字元是反斜線 `\`。這會導致跳脫序列無法被資料庫正確解析，`%` 和 `_` 仍可能被當作萬用字元。應將 `ESCAPE` 子句改為 `ESCAPE '\\'` 或調整跳脫函式以使用 `|`。

**判斷依據**：diff 中 SQL 字串使用 `ESCAPE '|'`，但 `escape_like_pattern` 使用反斜線。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_app_service.py:12</code> 測試檔案中大量延遲匯入 `AppService` 可能掩蓋循環依賴</summary>

在 `test_app_service.py` 中，原本的頂層匯入 `from services.app_service import AppService` 被註解掉，改為在每個測試方法內延遲匯入。這可能是為了避免循環依賴，但這種做法會降低程式碼可讀性，且若循環依賴確實存在，應從架構層面解決，而非在測試中規避。建議調查循環依賴的根本原因並修正。

**判斷依據**：diff 中顯示頂層匯入被註解，並在每個測試方法內新增延遲匯入。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17424 (cache hit 17408) ｜ completion tokens 1546 ｜ PR #12</sub>