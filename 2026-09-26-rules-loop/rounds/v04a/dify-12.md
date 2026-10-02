<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多處 LIKE 查詢改為使用統一的 escape_like_pattern 函式，並加上 escape 參數，以正確處理特殊字元。整體方向正確，但存在幾個關鍵問題：1) 部分呼叫未傳入 escape 參數，導致跳脫失效；2) 在 dataset_retrieval.py 中 'not contains' 分支未傳入 escape 參數；3) 在 clickzetta_vector.py 中 ESCAPE 子句的跳脫字元可能不正確；4) 在 workflow_app_service.py 中移除了原有的 unicode_escape 處理，可能改變行為；5) 測試檔案中大量延遲匯入 AppService 以避免循環依賴，但這可能違反架構規範。建議修正上述問題後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/rag/retrieval/dataset_retrieval.py:1207` | not contains 分支未傳入 escape 參數，跳脫失效 | 0.90 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991` | ESCAPE 子句的跳脫字元可能不正確 | 0.85 |
| ⚠️ | Major | `api/services/workflow_app_service.py:94` | 移除 unicode_escape 處理可能改變搜尋行為 | 0.80 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_app_service.py:11` | [R18] 延遲匯入 AppService 可能違反架構規範 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> not contains 分支未傳入 escape 參數，跳脫失效</summary>

在 `case "not contains"` 分支中，呼叫 `json_field.notlike(f"%{escaped_value}%")` 時未傳入 `escape="\\"` 參數。這會導致跳脫字元被視為一般字元，使用者輸入的 `%` 或 `_` 仍會被當作萬用字元，造成查詢結果不正確。

建議：將該行改為 `json_field.notlike(f"%{escaped_value}%", escape="\\")`。

**判斷依據**：diff 中該行新增，但未包含 escape 參數，與其他分支不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991</code> ESCAPE 子句的跳脫字元可能不正確</summary>

在 ClickZetta 向量資料庫的 LIKE 查詢中，使用了 `ESCAPE '\\\\'`。但 `escape_like_pattern` 函式是使用反斜線 `\` 作為跳脫字元，因此 ESCAPE 子句應指定 `'\\'`（在 SQL 字串中表示單一反斜線）。目前程式碼中的 `'\\\\'` 在 SQL 中可能代表兩個反斜線，導致跳脫行為不符合預期。

建議：確認 ClickZetta 的 SQL 方言，並將 ESCAPE 子句改為 `ESCAPE '\\'`。

**判斷依據**：diff 中新增的 ESCAPE 子句使用了四個反斜線，而 escape_like_pattern 使用單一反斜線跳脫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/workflow_app_service.py:94</code> 移除 unicode_escape 處理可能改變搜尋行為</summary>

原本的程式碼對 keyword 進行了 `encode('unicode_escape').decode('utf-8')` 處理，並將 `\u` 替換為 `\\u`，這可能是為了處理 JSON 欄位中的 Unicode 跳脫序列。新的程式碼直接使用 `escape_like_pattern`，移除了這項處理，可能導致搜尋包含 Unicode 跳脫序列的 JSON 欄位時無法匹配。

建議：確認此處的 unicode_escape 處理是否必要，若必要則應保留並與 escape_like_pattern 結合。

**判斷依據**：diff 中刪除了原本的 unicode_escape 處理，改為直接使用 escape_like_pattern。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_app_service.py:11</code> [R18] 延遲匯入 AppService 可能違反架構規範</summary>

測試檔案中將原本的頂層匯入 `from services.app_service import AppService` 改為在每個測試方法內延遲匯入，以避免循環依賴。這可能違反專案的 import-linter 規則（R18），且可能掩蓋了實際的循環依賴問題。

建議：調查循環依賴的根本原因，並考慮調整架構以允許頂層匯入。

**判斷依據**：diff 中註解掉了頂層匯入，並在每個測試方法內新增延遲匯入。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16065 (cache hit 13952) ｜ completion tokens 1229 ｜ PR #12</sub>