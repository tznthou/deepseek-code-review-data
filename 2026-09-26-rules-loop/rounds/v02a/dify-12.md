<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 SQL LIKE 模式的跳脫邏輯集中到 `escape_like_pattern` 函式，並在多處查詢中套用，以降低萬用字元注入風險。整體方向正確，但存在幾個關鍵問題：1) `escape_like_pattern` 的跳脫順序錯誤，導致反斜線處理不正確；2) 多處呼叫未傳入 `escape` 參數，使跳脫失效；3) 部分查詢仍使用字串拼接而非參數化，且跳脫字元與資料庫預設不一致；4) 測試中大量重複的 import 與註解顯示可能有循環依賴問題，需進一步確認。建議先修正跳脫邏輯與一致性，再合併。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/libs/helper.py:64` | escape_like_pattern 跳脫順序錯誤，反斜線處理不正確 | 0.95 |
| ⚠️ | Major | `api/core/rag/retrieval/dataset_retrieval.py:1207` | notlike 未傳入 escape 參數，跳脫失效 | 0.90 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991` | LIKE 查詢使用字串拼接，且跳脫字元可能與資料庫預設不符 | 0.85 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/iris/iris_vector.py:298` | LIKE 查詢使用參數化，但跳脫字元可能與資料庫預設不符 | 0.85 |
| ⚠️ | Major | `api/services/workflow_app_service.py:92` | 移除 unicode_escape 處理可能改變搜尋行為 | 0.80 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_app_service.py:11` | 大量重複的延遲 import 可能暗示循環依賴問題 | 0.70 |
| 🔸 | Minor | `api/libs/helper.py:64` | 變數命名不符合 snake_case 慣例 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/libs/helper.py:64</code> escape_like_pattern 跳脫順序錯誤，反斜線處理不正確</summary>

函式先將 `\` 取代為 `\\`，再將 `%` 取代為 `\%`、`_` 取代為 `\_`。這會導致原本的反斜線被重複跳脫。例如輸入 `path\to\file` 會變成 `path\\to\\file`，但正確應為 `path\to\file`（每個反斜線前加一個反斜線）。正確順序應先跳脫 `%` 和 `_`，最後才跳脫 `\`，或使用單次取代。

**判斷依據**：diff 中新增的函式實作，行號 64。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> notlike 未傳入 escape 參數，跳脫失效</summary>

在 `not contains` 分支中，`json_field.notlike(f"%{escaped_value}%")` 沒有傳入 `escape="\\"`，因此跳脫字元不會被視為跳脫，`%` 和 `_` 仍會被當作萬用字元。這會導致搜尋結果不正確，且可能造成安全風險。

**判斷依據**：diff 中該行未加入 escape 參數，與其他分支不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991</code> LIKE 查詢使用字串拼接，且跳脫字元可能與資料庫預設不符</summary>

此處使用 f-string 拼接 SQL，雖然已對單引號做跳脫，但仍存在 SQL 注入風險。此外，`ESCAPE '\\\\'` 指定跳脫字元為反斜線，但若資料庫預設跳脫字元不同，可能導致行為不一致。建議改用參數化查詢，並確認資料庫的跳脫字元設定。

**判斷依據**：diff 中該行仍使用字串拼接，且跳脫字元可能與資料庫預設衝突。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/iris/iris_vector.py:298</code> LIKE 查詢使用參數化，但跳脫字元可能與資料庫預設不符</summary>

此處使用參數化查詢，但 `ESCAPE '|'` 指定跳脫字元為 `|`，而 `escape_like_pattern` 產生的跳脫字元是反斜線 `\`。這會導致跳脫失效，因為資料庫不會將反斜線視為跳脫字元。應統一使用反斜線作為跳脫字元，或修改 `escape_like_pattern` 以支援自訂跳脫字元。

**判斷依據**：diff 中該行指定 ESCAPE '|'，但跳脫函式使用反斜線。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/workflow_app_service.py:92</code> 移除 unicode_escape 處理可能改變搜尋行為</summary>

原本的程式碼使用 `keyword[:30].encode('unicode_escape').decode('utf-8')` 來處理關鍵字，這可能是為了處理非 ASCII 字元或特殊編碼。新程式碼直接使用 `escape_like_pattern`，可能導致對某些字元的處理不同，影響搜尋結果。需確認此變更是否會破壞現有功能。

**判斷依據**：diff 中移除了原本的 unicode_escape 處理，可能改變行為。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_app_service.py:11</code> 大量重複的延遲 import 可能暗示循環依賴問題</summary>

在測試檔案中，原本的 `from services.app_service import AppService` 被註解掉，改為在每個測試方法內延遲 import。這可能是為了避免循環依賴，但這種做法會降低程式碼可讀性，且可能掩蓋真正的架構問題。建議檢查並解決循環依賴，而不是用延遲 import 規避。

**判斷依據**：diff 中多處出現相同的延遲 import 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/helper.py:64</code> 變數命名不符合 snake_case 慣例</summary>

變數 `escapedPattern` 使用 camelCase，違反專案的 snake_case 命名慣例（R16）。應改為 `escaped_pattern`。

**判斷依據**：diff 中該行變數命名為 camelCase。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17505 (cache hit 1536) ｜ completion tokens 1731 ｜ PR #12</sub>