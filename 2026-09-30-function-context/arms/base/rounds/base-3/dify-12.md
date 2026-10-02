<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多處 LIKE 查詢改為使用統一的 escape_like_pattern 函式，並加上 ESCAPE 子句，以正確處理特殊字元。整體方向正確，但存在兩個關鍵問題：1) 在 dataset_retrieval.py 的 'not contains' 分支中，呼叫 notlike 時未傳入 escape 參數，導致跳脫字元失效，可能造成非預期的萬用字元匹配；2) 在 clickzetta_vector.py 中，escape_like_pattern 的輸出被直接嵌入 SQL 字串，且未使用參數化查詢，仍存在 SQL 注入風險。此外，部分檔案使用延遲匯入以避免循環依賴，但測試檔案中的延遲匯入可能掩蓋了實際的循環依賴問題。建議優先修正上述兩個問題，並考慮將 escape_like_pattern 的匯入移至模組頂部。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991` | SQL 注入風險：escape_like_pattern 的輸出被直接嵌入 SQL 字串 | 0.95 |
| ⚠️ | Major | `api/core/rag/retrieval/dataset_retrieval.py:1207` | 'not contains' 分支未傳入 escape 參數，跳脫字元失效 | 0.90 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/iris/iris_vector.py:298` | ESCAPE 子句使用 '\|' 但 escape_like_pattern 使用 '\' 作為跳脫字元 | 0.80 |
| 🔸 | Minor | `api/services/workflow_app_service.py:94` | 移除 unicode_escape 編碼可能改變搜尋行為 | 0.70 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_app_service.py:11` | 延遲匯入 AppService 可能掩蓋循環依賴問題 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991</code> SQL 注入風險：escape_like_pattern 的輸出被直接嵌入 SQL 字串</summary>

此處將 `escaped_query` 直接以 f-string 嵌入 SQL 查詢，且未使用參數化查詢。雖然 `escape_like_pattern` 會跳脫 LIKE 特殊字元，但攻擊者仍可透過注入單引號等方式破壞查詢結構。例如，輸入 `' OR '1'='1` 會導致 `escaped_query` 為 `' OR ''1''=''1`，但由於未參數化，最終 SQL 可能變成 `... LIKE '%' OR ''1''=''1%'`，造成邏輯錯誤或資料外洩。建議改用參數化查詢，將 `escaped_query` 作為綁定參數傳入，而非直接拼接。

**判斷依據**：diff 中該行使用 f-string 拼接，且未使用參數化查詢。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> 'not contains' 分支未傳入 escape 參數，跳脫字元失效</summary>

在 'not contains' 條件中，呼叫 `json_field.notlike(f"%{escaped_value}%")` 時未傳入 `escape="\\"`。這會導致 `escaped_value` 中的反斜線被視為一般字元，而非跳脫字元，因此 `%` 和 `_` 仍會被當作萬用字元。例如，若 value 為 "50%"，escaped_value 為 "50\\%"，但由於未指定 escape，資料庫會將 "\\" 視為普通字元，而 "%" 仍為萬用字元，導致查詢結果不符合預期。建議改為 `json_field.notlike(f"%{escaped_value}%", escape="\\")`。

**判斷依據**：diff 中該行新增，且未包含 escape 參數，與其他分支（如 contains）不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/iris/iris_vector.py:298</code> ESCAPE 子句使用 '|' 但 escape_like_pattern 使用 '\' 作為跳脫字元</summary>

在 IRIS 向量資料庫的 LIKE 查詢中，ESCAPE 子句指定 '|' 作為跳脫字元，但 `escape_like_pattern` 函式使用反斜線 '\' 進行跳脫。這會導致跳脫字元不一致：例如，輸入 "50%" 會被轉成 "50\\%"，但資料庫會將 '|' 視為跳脫字元，因此 '\\' 不會被視為跳脫，而 '%' 仍會被當作萬用字元。建議將 ESCAPE 子句改為 '\\'，或修改 escape_like_pattern 以使用 '|'。

**判斷依據**：diff 中新增 ESCAPE '|'，但 escape_like_pattern 使用 '\'。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/services/workflow_app_service.py:94</code> 移除 unicode_escape 編碼可能改變搜尋行為</summary>

原本的程式碼將關鍵字進行 unicode_escape 編碼，並將 "\\u" 替換為 "\\\\u"，這可能是為了處理 JSON 欄位中的 Unicode 表示。新程式碼直接使用原始關鍵字，可能導致搜尋行為不一致。例如，若輸入包含非 ASCII 字元，原本的編碼可能使其與 JSON 中的 Unicode 轉義序列匹配，而新程式碼則無法匹配。建議確認此變更是否會影響現有功能，並考慮保留必要的編碼處理。

**判斷依據**：diff 中刪除了原本的 unicode_escape 處理，改為直接使用 escape_like_pattern。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_app_service.py:11</code> 延遲匯入 AppService 可能掩蓋循環依賴問題</summary>

測試檔案中將 `from services.app_service import AppService` 改為在每個測試方法內延遲匯入，並註解說明是為了避免循環依賴。然而，循環依賴通常表示模組結構有問題，延遲匯入只是暫時的解決方案。建議調查並解決根本的循環依賴，而不是在測試中規避。

**判斷依據**：diff 中新增註解並移除頂部匯入。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14826 (cache hit 14720) ｜ completion tokens 1580 ｜ PR #12</sub>