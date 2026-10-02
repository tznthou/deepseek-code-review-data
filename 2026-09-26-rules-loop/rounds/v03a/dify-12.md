<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多處 SQL LIKE 查詢改為使用集中式 escape_like_pattern 函式，以正確處理特殊字元並防止 LIKE 萬用字元注入。整體方向正確，但存在幾個關鍵問題：1) 部分資料庫（如 ClickZetta、IRIS）的 ESCAPE 子句語法可能不正確或與 escape 字元不一致；2) 部分呼叫未傳入 escape 參數，導致轉義失效；3) 新函式缺少型別註記，違反專案規範 R01；4) 測試中大量使用延遲匯入來規避循環依賴，可能掩蓋架構問題。建議優先修正 ESCAPE 子句與 escape 參數的一致性，並補上型別註記。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991` | ClickZetta LIKE 查詢的 ESCAPE 子句語法可能錯誤 | 0.90 |
| 🛑 | Blocker | `api/core/rag/datasource/vdb/iris/iris_vector.py:298` | IRIS LIKE 查詢的 ESCAPE 子句與 escape 字元不一致 | 0.85 |
| ⚠️ | Major | `api/core/rag/retrieval/dataset_retrieval.py:1207` | not contains 條件未傳入 escape 參數 | 0.80 |
| 🔸 | Minor | `api/libs/helper.py:35` | [R01] escape_like_pattern 缺少型別註記 | 0.95 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_app_service.py:12` | 測試中大量延遲匯入 AppService 可能掩蓋循環依賴 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991</code> ClickZetta LIKE 查詢的 ESCAPE 子句語法可能錯誤</summary>

在 ClickZetta 的 `_search_by_like` 中，新增的 ESCAPE 子句為 `ESCAPE '\\\\'`，但 Python 字串中 `'\\\\'` 實際代表兩個反斜線字元（`\\`），而 SQL 標準的 ESCAPE 子句應為單一字元。這可能導致 SQL 語法錯誤或轉義行為不符預期。

**失敗情境**：當使用者搜尋包含 `%` 或 `_` 的字串時，ClickZetta 資料庫可能無法正確解析 ESCAPE 子句，導致查詢失敗或將特殊字元視為萬用字元。

**建議**：確認 ClickZetta 的 SQL 方言對 ESCAPE 子句的要求，並使用正確的 escape 字元（例如 `ESCAPE '\\'` 在 Python 中應寫為 `ESCAPE '\\'`）。

**判斷依據**：diff 中新增的 ESCAPE 子句使用了四個反斜線，可能與 SQL 標準不符。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>api/core/rag/datasource/vdb/iris/iris_vector.py:298</code> IRIS LIKE 查詢的 ESCAPE 子句與 escape 字元不一致</summary>

在 IRIS 的 `search_by_full_text` 中，SQL 使用 `ESCAPE '|'`，但 `escape_like_pattern` 函式預設使用反斜線 `\` 作為 escape 字元。這導致轉義後的字串（例如 `50\%`）在資料庫中不會被正確解讀，因為資料庫期望的 escape 字元是 `|`。

**失敗情境**：當使用者搜尋包含 `%` 或 `_` 的字串時，IRIS 資料庫會將 `\%` 視為兩個字元（反斜線和 `%`），而不是跳脫後的 `%`，導致查詢結果不正確。

**建議**：將 `escape_like_pattern` 的 escape 字元改為 `|`，或將 SQL 中的 `ESCAPE` 改為 `'\\'` 以與函式一致。

**判斷依據**：diff 中新增的 ESCAPE 子句使用 `|`，但 `escape_like_pattern` 使用 `\`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> not contains 條件未傳入 escape 參數</summary>

在 `process_metadata_filter_func` 的 `not contains` 分支中，呼叫 `json_field.notlike(f"%{escaped_value}%")` 時未傳入 `escape="\\"` 參數。這導致 `escaped_value` 中的反斜線不會被視為 escape 字元，轉義失效。

**失敗情境**：當 metadata 值包含 `%` 或 `_` 時，`not contains` 條件會將它們視為萬用字元，導致過濾結果不正確。

**建議**：在 `notlike` 呼叫中同樣加入 `escape="\\"` 參數。

**判斷依據**：diff 中該行未包含 escape 參數，而其他 like 呼叫均有。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/helper.py:35</code> [R01] escape_like_pattern 缺少型別註記</summary>

新函式 `escape_like_pattern` 的參數 `pattern` 和回傳值均缺少型別註記，違反專案規範 R01（Python Functions Must Include Type Annotations）。

**建議**：加上型別註記，例如 `def escape_like_pattern(pattern: str) -> str:`。

**判斷依據**：diff 中函式定義沒有型別註記。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_app_service.py:12</code> 測試中大量延遲匯入 AppService 可能掩蓋循環依賴</summary>

在測試檔案中，原本的頂層匯入 `from services.app_service import AppService` 被註解掉，改為在每個測試方法內延遲匯入。這可能是為了避免循環依賴，但這種做法會掩蓋實際的架構問題，且增加重複程式碼。

**建議**：調查並解決循環依賴的根本原因，恢復頂層匯入。

**判斷依據**：diff 中多處將頂層匯入改為延遲匯入。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17514 (cache hit 13952) ｜ completion tokens 1572 ｜ PR #12</sub>