<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多處 LIKE 查詢改為使用集中式 escape_like_pattern 函式，並加入 escape 參數，以正確處理特殊字元。整體方向正確，但存在幾個關鍵問題：部分資料庫（如 IRIS）使用不同的 escape 字元，但程式碼未一致調整；部分查詢未傳入 escape 參數，導致跳脫失效；此外，測試中對 backslash 的處理可能因 Python 字串轉義而產生誤判。建議修正這些不一致處後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/rag/datasource/vdb/iris/iris_vector.py:298` | LIKE 查詢使用錯誤的 escape 字元 | 0.95 |
| ⚠️ | Major | `api/core/rag/retrieval/dataset_retrieval.py:1207` | notlike 查詢未傳入 escape 參數 | 0.90 |
| ⚠️ | Major | `api/services/workflow_app_service.py:94` | 移除 unicode_escape 可能導致搜尋行為改變 | 0.85 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_annotation_service.py:475` | 測試中對 backslash 的處理可能不正確 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/rag/datasource/vdb/iris/iris_vector.py:298</code> LIKE 查詢使用錯誤的 escape 字元</summary>

在 IRIS 向量資料庫的 LIKE 查詢中，escape 字元指定為 '|'，但 escape_like_pattern 函式使用反斜線 '\' 進行跳脫。這會導致跳脫序列無法被資料庫正確解析，特殊字元（如 %、_）仍會被視為萬用字元，造成查詢結果錯誤或潛在的 SQL 注入風險。

建議：將 escape 字元改為 '\\'，或修改 escape_like_pattern 以支援自訂 escape 字元。

**判斷依據**：diff 中新增的 ESCAPE '|' 與 escape_like_pattern 使用的 '\' 不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> notlike 查詢未傳入 escape 參數</summary>

在 'not contains' 條件中，使用了 notlike 但未傳入 escape 參數。這會導致跳脫後的反斜線被資料庫視為普通字元，而非跳脫字元，使得 % 和 _ 仍被當作萬用字元，造成查詢結果不正確。

建議：在 notlike 呼叫中加入 escape="\\"。

**判斷依據**：diff 中該行未包含 escape 參數，而其他 like 呼叫均有。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/workflow_app_service.py:94</code> 移除 unicode_escape 可能導致搜尋行為改變</summary>

原本的程式碼將關鍵字進行 unicode_escape 編碼，以處理非 ASCII 字元。新程式碼直接使用原始關鍵字，可能導致對包含非 ASCII 字元的搜尋行為改變，特別是在資料庫儲存為 unicode escape 格式時。

建議：確認此變更不會影響現有功能，或保留必要的編碼處理。

**判斷依據**：diff 中刪除了原本的 unicode_escape 處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_annotation_service.py:475</code> 測試中對 backslash 的處理可能不正確</summary>

測試資料中的 backslash 在 Python 字串中可能被轉義，導致實際儲存的內容與預期不同。例如，"path\\to\\file" 在 Python 中代表 "path\to\file"，但測試斷言可能未考慮到這點。

建議：使用 raw string 或明確的轉義來確保測試資料正確。

**判斷依據**：diff 中測試資料的 backslash 可能被 Python 轉義。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14790 (cache hit 1408) ｜ completion tokens 1009 ｜ PR #12</sub>