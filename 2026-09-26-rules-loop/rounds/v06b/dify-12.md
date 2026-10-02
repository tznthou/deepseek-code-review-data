<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多處 LIKE 查詢改為使用集中式 escape_like_pattern 函式，並加入 escape 參數，以正確處理 %、_、\ 等特殊字元，避免萬用字元注入。整體方向正確，但存在幾個關鍵問題：1) 部分查詢未傳入 escape 參數，導致跳脫失效；2) 部分資料庫（如 IRIS）使用自訂跳脫字元 '|'，但跳脫函式固定使用反斜線，可能造成行為不一致；3) 部分程式碼在函式內延遲匯入，可能違反架構規範；4) 測試中大量重複匯入 AppService，可能掩蓋循環依賴問題。建議優先修正跳脫邏輯不一致與缺失 escape 參數的問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/rag/retrieval/dataset_retrieval.py:1207` | not contains 分支未傳入 escape 參數，跳脫失效 | 0.95 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/iris/iris_vector.py:298` | IRIS 使用自訂跳脫字元 '\|'，但跳脫函式固定使用反斜線 | 0.85 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991` | ClickZetta 查詢中跳脫字元可能不正確 | 0.80 |
| ⚠️ | Major | `api/controllers/console/app/conversation.py:346` | 延遲匯入可能違反架構規範 | 0.80 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_app_service.py:1003` | 測試中大量重複匯入 AppService，可能掩蓋循環依賴 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> not contains 分支未傳入 escape 參數，跳脫失效</summary>

在 `case "not contains"` 中，`json_field.notlike(f"%{escaped_value}%")` 沒有傳入 `escape="\\"`。這會導致跳脫字元被視為一般字元，使用者輸入的 `%` 或 `_` 仍會被當作萬用字元，造成查詢結果錯誤，且可能被用於萬用字元注入。

**失敗情境**：使用者搜尋 `not contains` 條件為 `50%`，預期排除包含 `50%` 的文件，但因為 `%` 未被跳脫，實際上會排除包含 `50` 開頭任意字串的文件。

**建議**：加上 `escape="\\"` 參數，與其他分支一致。

**判斷依據**：diff 中該行缺少 escape 參數，而其他分支（contains、start with、end with）都有傳入 escape="\\"。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/iris/iris_vector.py:298</code> IRIS 使用自訂跳脫字元 '|'，但跳脫函式固定使用反斜線</summary>

在 IRIS 的 LIKE 查詢中，SQL 使用 `ESCAPE '|'`，但 `escape_like_pattern` 函式固定使用反斜線 `\` 作為跳脫字元。這會導致跳脫序列不被資料庫識別，使用者輸入的 `%`、`_` 仍會被當作萬用字元，跳脫完全失效。

**失敗情境**：使用者搜尋 `test_data`，預期只匹配包含 `test_data` 的文件，但因為 `_` 未被正確跳脫，實際上會匹配 `testXdata` 等任意字元。

**建議**：修改 `escape_like_pattern` 使其接受跳脫字元參數，或在此處改用反斜線作為 ESCAPE 字元（需確認 IRIS 是否支援）。

**判斷依據**：diff 中該行使用 ESCAPE '|'，而 escape_like_pattern 函式固定使用反斜線。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991</code> ClickZetta 查詢中跳脫字元可能不正確</summary>

在 ClickZetta 的 LIKE 查詢中，使用 `ESCAPE '\\\\'`（SQL 字串中表示單一反斜線），但 `escape_like_pattern` 函式會將反斜線跳脫為 `\\`（兩個反斜線）。這可能導致跳脫序列不匹配，使跳脫失效。

**失敗情境**：使用者搜尋包含反斜線的字串，例如 `path\to\file`，預期精確匹配，但可能因為跳脫字元處理不一致而無法正確匹配。

**建議**：確認 ClickZetta 的 ESCAPE 語法，並調整跳脫函式或此處的 ESCAPE 子句以保持一致。

**判斷依據**：diff 中該行使用 ESCAPE '\\\\'，而 escape_like_pattern 函式將反斜線跳脫為兩個反斜線。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/controllers/console/app/conversation.py:346</code> 延遲匯入可能違反架構規範</summary>

在函式內使用 `from libs.helper import escape_like_pattern` 延遲匯入，可能違反 R18（Backend Architecture Must Follow Import Layer Constraints）。雖然延遲匯入可以避免循環依賴，但若無正當理由，應將匯入移至模組頂部。

**建議**：確認是否存在循環依賴，若無，請將匯入移至檔案頂部。

**判斷依據**：diff 中多處在函式內延遲匯入，可能違反架構規範。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_app_service.py:1003</code> 測試中大量重複匯入 AppService，可能掩蓋循環依賴</summary>

在測試檔案中，多個測試函式內重複 `from services.app_service import AppService`，且頂部註解掉原本的匯入。這可能是為了避免循環依賴，但大量重複匯入會降低可讀性，且可能掩蓋真正的循環依賴問題。

**建議**：若循環依賴存在，應從根本解決，而非在測試中規避。

**判斷依據**：diff 中多處在測試函式內重複匯入 AppService。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17494 (cache hit 17408) ｜ completion tokens 1584 ｜ PR #12</sub>