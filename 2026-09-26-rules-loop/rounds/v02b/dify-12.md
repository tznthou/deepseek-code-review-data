<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多處 SQL LIKE 查詢改為使用集中式 escape_like_pattern 函式，以正確處理特殊字元（%、_、\），並在多個服務與控制器中套用。整體方向正確，能降低 LIKE 萬用字元造成的意外匹配或注入風險。但仍有幾處實作細節需要修正：部分呼叫未傳入 escape 參數，導致跳脫失效；ClickZetta 的 ESCAPE 子句可能因雙重跳脫而錯誤；workflow_app_service 中移除了原有的 unicode_escape 處理，可能改變對非 ASCII 字元的比對行為；此外，測試檔案中大量延遲匯入 AppService 的作法可能掩蓋了循環依賴問題，且部分測試的斷言過於寬鬆，無法有效驗證跳脫行為。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/rag/retrieval/dataset_retrieval.py:1207` | notlike 條件未傳入 escape 參數，跳脫失效 | 0.90 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:990` | ClickZetta LIKE 查詢的 ESCAPE 子句可能因雙重跳脫而錯誤 | 0.85 |
| ⚠️ | Major | `api/services/workflow_app_service.py:92` | 移除 unicode_escape 處理可能改變非 ASCII 字元的比對行為 | 0.80 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_app_service.py:11` | 大量延遲匯入 AppService 可能掩蓋循環依賴問題 | 0.70 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_workflow_app_service.py:316` | 測試斷言過於寬鬆，無法有效驗證跳脫行為 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> notlike 條件未傳入 escape 參數，跳脫失效</summary>

在 `case "not contains"` 分支中，`json_field.notlike(f"%{escaped_value}%")` 沒有傳入 `escape="\\"`。這會導致 `escaped_value` 中的反斜線被資料庫視為一般字元，而非跳脫字元，因此 `%` 和 `_` 仍會被當作萬用字元，造成「不包含」的語意錯誤。例如，若 value 為 `50%`，escaped_value 為 `50\%`，但因為沒有指定 escape，LIKE 模式會將 `\` 視為一般反斜線，而 `%` 仍為萬用字元，導致排除條件失效。

建議：將該行改為 `json_field.notlike(f"%{escaped_value}%", escape="\\")`。

**判斷依據**：diff 中該行未包含 escape 參數，而其他 like 呼叫均有 escape="\\"。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:990</code> ClickZetta LIKE 查詢的 ESCAPE 子句可能因雙重跳脫而錯誤</summary>

程式碼先呼叫 `escape_like_pattern(query)` 將 `\` 跳脫為 `\\`，再將單引號跳脫為 `''`，最後在 SQL 字串中加上 `ESCAPE '\\\\'`。但 `escape_like_pattern` 已將反斜線加倍，而 `ESCAPE '\\\\'` 在 SQL 字串中代表兩個反斜線字元（因為 Python 字串中 `\\\\` 是四個反斜線，但 SQL 解析後成為兩個），這可能導致跳脫字元被誤解。例如，若原始 query 為 `a\b`，escape_like_pattern 後為 `a\\b`，SQL 中 `LIKE '%a\\b%' ESCAPE '\\\\'` 會將 `\\` 視為跳脫後的反斜線，但 ESCAPE 字元本身是兩個反斜線，可能無法正確匹配。

建議：確認 ClickZetta 的 SQL 方言對 ESCAPE 子句的處理，並簡化跳脫邏輯，避免重複跳脫。

**判斷依據**：diff 中該行同時使用 escape_like_pattern 和 ESCAPE '\\\\'，可能造成雙重跳脫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/workflow_app_service.py:92</code> 移除 unicode_escape 處理可能改變非 ASCII 字元的比對行為</summary>

原本的程式碼使用 `keyword[:30].encode('unicode_escape').decode('utf-8')` 來處理關鍵字，這會將非 ASCII 字元轉換為 `\uXXXX` 形式，以符合資料庫中可能儲存的格式。新的程式碼直接使用 `escape_like_pattern(keyword_trimmed)`，不再進行 unicode_escape 轉換。如果資料庫中的 `inputs` 和 `outputs` 欄位是以 unicode_escape 格式儲存（例如 JSON 序列化時），則搜尋非 ASCII 字元（如中文）將無法匹配。

建議：確認資料庫中這些欄位的實際儲存格式，若仍為 unicode_escape，則需保留該轉換，或改用其他方式處理。

**判斷依據**：diff 中移除了原本的 unicode_escape 處理，且未提供替代方案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_app_service.py:11</code> 大量延遲匯入 AppService 可能掩蓋循環依賴問題</summary>

測試檔案中原本在頂部匯入 `AppService`，現在被註解掉，改為在每個測試方法內延遲匯入。這可能是為了避免循環依賴，但若循環依賴確實存在，應該從根本解決，而不是在測試中繞過。延遲匯入會降低程式碼可讀性，且可能隱藏實際的架構問題。

建議：調查循環依賴的根源，並在必要時重構程式碼結構，而不是在測試中大量使用延遲匯入。

**判斷依據**：diff 中多處測試方法內新增 `from services.app_service import AppService`，且頂部匯入被註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_workflow_app_service.py:316</code> 測試斷言過於寬鬆，無法有效驗證跳脫行為</summary>

在 `test_get_paginate_workflow_app_logs_with_special_characters_in_keyword` 中，多個斷言使用 `>= 1` 或 `in found_run_ids`，這只能確認至少找到一筆，無法驗證是否排除了不應匹配的記錄。例如，Test 3 中雖然檢查了 `workflow_run_4.id not in found_run_ids`，但若查詢結果包含其他未預期的記錄，測試仍可能通過。

建議：使用更精確的斷言，例如檢查 `result["total"] == 1` 且 `result["data"][0].workflow_run_id == workflow_run_1.id`，以確保跳脫行為正確。

**判斷依據**：diff 中多處使用 `>= 1` 和 `any` 斷言，而非精確比對。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17505 (cache hit 17408) ｜ completion tokens 1873 ｜ PR #12</sub>