<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多處 SQL LIKE 查詢改為使用集中式 escape_like_pattern 函式，以正確處理特殊字元（%、_、\），避免萬用字元注入。整體方向正確，但存在幾個關鍵問題：1) 在 dataset_retrieval.py 的 'not contains' 分支未傳入 escape 參數，導致跳脫失效；2) 在 clickzetta_vector.py 中，escape_like_pattern 的輸出被再次 replace("'", "''")，可能破壞跳脫序列；3) 在 iris_vector.py 中，使用 '|' 作為 ESCAPE 字元，但 escape_like_pattern 使用反斜線，兩者不一致；4) 部分檔案使用延遲匯入，可能違反架構規範；5) 測試檔案中大量重複的延遲匯入可能掩蓋循環依賴問題。建議優先修正上述功能性問題，並考慮將匯入移至模組頂部。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/rag/retrieval/dataset_retrieval.py:1207` | not contains 分支未傳入 escape 參數，跳脫失效 | 0.95 |
| 🛑 | Blocker | `api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:990` | escape_like_pattern 後再 replace 單引號可能破壞跳脫序列 | 0.90 |
| 🛑 | Blocker | `api/core/rag/datasource/vdb/iris/iris_vector.py:298` | ESCAPE 字元與 escape_like_pattern 使用的不一致 | 0.90 |
| ⚠️ | Major | `api/controllers/console/app/conversation.py:346` | 延遲匯入可能違反架構規範 | 0.80 |
| ⚠️ | Major | `api/services/app_service.py:58` | 延遲匯入可能違反架構規範 | 0.80 |
| ⚠️ | Major | `api/services/workflow_app_service.py:89` | 延遲匯入可能違反架構規範 | 0.80 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_app_service.py:12` | 測試檔案中大量延遲匯入可能掩蓋循環依賴 | 0.70 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_workflow_app_service.py:15` | 測試檔案中大量延遲匯入可能掩蓋循環依賴 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> not contains 分支未傳入 escape 參數，跳脫失效</summary>

在 `case "not contains":` 分支中，呼叫 `json_field.notlike(f"%{escaped_value}%")` 時未傳入 `escape="\\"`。這會導致跳脫字元被視為普通字元，使用者輸入的 `%` 或 `_` 仍會被當作萬用字元，造成查詢結果錯誤，甚至可能被利用進行萬用字元注入。

**失敗情境**：當使用者搜尋包含 `%` 的字串時，例如 `value = "50%"`，`escaped_value` 會是 `"50\\%"`，但由於沒有指定 escape，資料庫會將 `\\` 視為普通字元，`%` 仍為萬用字元，導致匹配到所有包含 `50` 的記錄。

**建議修法**：將該行改為 `filters.append(json_field.notlike(f"%{escaped_value}%", escape="\\"))`。

**判斷依據**：diff 中該行新增，且未包含 escape 參數，與其他分支（如 contains）不一致。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:990</code> escape_like_pattern 後再 replace 單引號可能破壞跳脫序列</summary>

程式碼先呼叫 `escape_like_pattern(query)`，然後再對結果執行 `.replace("'", "''")`。如果原始查詢中包含反斜線，`escape_like_pattern` 會將其轉為雙反斜線，但後續的 replace 不會影響反斜線，因此不會破壞跳脫序列。然而，如果原始查詢中包含單引號，`escape_like_pattern` 不會處理單引號，後續 replace 將其轉為兩個單引號，這在 SQL 中是正確的。但問題在於，如果原始查詢中包含 `\'`（反斜線後跟單引號），`escape_like_pattern` 會先將反斜線轉為 `\\`，然後 replace 將單引號轉為 `''`，結果為 `\\''`，這可能導致 SQL 解析錯誤或跳脫失效。

**失敗情境**：使用者搜尋包含 `\'` 的字串時，最終 SQL 中的 LIKE 模式可能無法正確匹配。

**建議修法**：應先進行單引號跳脫，再進行 LIKE 特殊字元跳脫，或使用參數化查詢。

**判斷依據**：diff 中該行新增，且順序可能導致跳脫問題。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>api/core/rag/datasource/vdb/iris/iris_vector.py:298</code> ESCAPE 字元與 escape_like_pattern 使用的不一致</summary>

在 SQL 查詢中使用了 `ESCAPE '|'`，但 `escape_like_pattern` 函式使用反斜線 `\` 作為跳脫字元。這導致跳脫序列無法被資料庫正確識別，使用者輸入的 `%` 或 `_` 仍會被當作萬用字元。

**失敗情境**：當使用者搜尋包含 `%` 的字串時，`escaped_query` 會是 `50\%`，但由於 ESCAPE 指定為 `|`，資料庫會將 `\` 視為普通字元，`%` 仍為萬用字元，導致匹配到所有包含 `50` 的記錄。

**建議修法**：將 SQL 中的 `ESCAPE '|'` 改為 `ESCAPE '\\'`，或修改 `escape_like_pattern` 使用 `|` 作為跳脫字元。

**判斷依據**：diff 中該行新增，且與 escape_like_pattern 的跳脫字元不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/controllers/console/app/conversation.py:346</code> 延遲匯入可能違反架構規範</summary>

在函式內部進行 `from libs.helper import escape_like_pattern` 匯入，這可能違反專案的 import-linter 規則（R18），且可能導致循環依賴。建議將匯入移至模組頂部。

**判斷依據**：diff 中多處在函式內新增匯入，可能違反架構規範。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/app_service.py:58</code> 延遲匯入可能違反架構規範</summary>

在函式內部進行 `from libs.helper import escape_like_pattern` 匯入，這可能違反專案的 import-linter 規則（R18），且可能導致循環依賴。建議將匯入移至模組頂部。

**判斷依據**：diff 中多處在函式內新增匯入，可能違反架構規範。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/workflow_app_service.py:89</code> 延遲匯入可能違反架構規範</summary>

在函式內部進行 `from libs.helper import escape_like_pattern` 匯入，這可能違反專案的 import-linter 規則（R18），且可能導致循環依賴。建議將匯入移至模組頂部。

**判斷依據**：diff 中多處在函式內新增匯入，可能違反架構規範。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_app_service.py:12</code> 測試檔案中大量延遲匯入可能掩蓋循環依賴</summary>

測試檔案中將 `from services.app_service import AppService` 註解掉，並在每個測試方法內延遲匯入，這可能掩蓋了實際的循環依賴問題。建議調查並解決循環依賴，而不是在測試中規避。

**判斷依據**：diff 中多處測試方法內新增延遲匯入，且頂部匯入被註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_workflow_app_service.py:15</code> 測試檔案中大量延遲匯入可能掩蓋循環依賴</summary>

測試檔案中將 `from services.app_service import AppService` 註解掉，並在每個測試方法內延遲匯入，這可能掩蓋了實際的循環依賴問題。建議調查並解決循環依賴，而不是在測試中規避。

**判斷依據**：diff 中多處測試方法內新增延遲匯入，且頂部匯入被註解。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17514 (cache hit 17408) ｜ completion tokens 2208 ｜ PR #12</sub>