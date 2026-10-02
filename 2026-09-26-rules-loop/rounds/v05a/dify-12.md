<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 SQL LIKE 模式的跳脫邏輯集中到 `escape_like_pattern` 工具函式，並在多處查詢中套用，以降低萬用字元注入風險。整體方向正確，但存在幾個關鍵問題：部分資料庫（如 ClickZetta、IRIS）的 ESCAPE 子句語法可能不正確，導致查詢失敗或跳脫失效；`dataset_retrieval.py` 中 `not contains` 分支未傳入 `escape` 參數，跳脫形同虛設；`workflow_app_service.py` 移除了原有的 Unicode 跳脫處理，可能造成非 ASCII 字元搜尋行為改變。此外，測試檔案中大量延遲匯入 `AppService` 的改動與本 PR 目的無關，且可能掩蓋循環依賴問題。建議優先修正 ESCAPE 語法與遺漏的 `escape` 參數，並重新評估 Unicode 處理的移除。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:990` | ClickZetta 的 ESCAPE 子句語法可能無效 | 0.90 |
| 🛑 | Blocker | `api/core/rag/datasource/vdb/iris/iris_vector.py:298` | IRIS 的 ESCAPE 子句使用 '\|' 可能與跳脫字元不一致 | 0.85 |
| ⚠️ | Major | `api/core/rag/retrieval/dataset_retrieval.py:1207` | `not contains` 分支未傳入 `escape` 參數，跳脫失效 | 0.90 |
| ⚠️ | Major | `api/services/workflow_app_service.py:92` | 移除 Unicode 跳脫可能導致非 ASCII 字元搜尋行為改變 | 0.80 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_app_service.py:11` | 測試檔案中大量延遲匯入 AppService 可能掩蓋循環依賴 | 0.70 |
| 🔸 | Minor | `api/libs/helper.py:61` | `escape_like_pattern` 未處理 None 以外的非字串輸入 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:990</code> ClickZetta 的 ESCAPE 子句語法可能無效</summary>

在 ClickZetta 的 LIKE 查詢中，使用了 `ESCAPE '\\\\'`（在 Python 字串中為 `ESCAPE '\\'`，實際 SQL 為 `ESCAPE '\'`）。但 ClickZetta 可能不支援標準 SQL 的 ESCAPE 子句，或使用不同的跳脫字元。這可能導致查詢執行錯誤，或跳脫字元未被正確解析，使萬用字元注入防護失效。

**失敗情境**：當使用者搜尋包含 `%` 或 `_` 的字串時，若 ESCAPE 子句不被支援，查詢會拋出語法錯誤；若被忽略，則 `%` 仍會被視為萬用字元，導致搜尋結果不正確。

**建議**：查閱 ClickZetta 的文件，確認其 LIKE 語法是否支援 ESCAPE 子句，以及正確的跳脫字元。若不支援，應改用其他方式（如使用 `REGEXP_LIKE` 或參數化查詢）來達成精確匹配。

**判斷依據**：diff 中新增的 `ESCAPE '\\\\'` 子句，但未提供 ClickZetta 支援此語法的證據。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>api/core/rag/datasource/vdb/iris/iris_vector.py:298</code> IRIS 的 ESCAPE 子句使用 '|' 可能與跳脫字元不一致</summary>

在 IRIS 的 LIKE 查詢中，使用了 `ESCAPE '|'`，但 `escape_like_pattern` 函式產生的跳脫字元是反斜線 `\`。這導致跳脫字元與 ESCAPE 子句指定的字元不一致，跳脫將完全失效。

**失敗情境**：當使用者搜尋包含 `%` 或 `_` 的字串時，`escape_like_pattern` 會將其轉為 `\%` 或 `\_`，但資料庫會將 `|` 視為跳脫字元，因此 `\` 被當作普通字元，`%` 仍被視為萬用字元，導致搜尋結果錯誤。

**建議**：將 ESCAPE 子句改為 `ESCAPE '\'`（在 SQL 字串中為 `ESCAPE '\\'`），或修改 `escape_like_pattern` 以使用 `|` 作為跳脫字元。

**判斷依據**：diff 中新增的 `ESCAPE '|'` 與 `escape_like_pattern` 使用的反斜線跳脫不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> `not contains` 分支未傳入 `escape` 參數，跳脫失效</summary>

在 `process_metadata_filter_func` 的 `not contains` 分支中，呼叫 `json_field.notlike(f"%{escaped_value}%")` 時未傳入 `escape` 參數。這表示即使 `escaped_value` 已跳脫，資料庫仍會將 `%` 和 `_` 視為萬用字元，導致「不包含」的語意錯誤。

**失敗情境**：當使用者設定「不包含 `50%`」的過濾條件時，由於 `%` 未被視為字面字元，查詢會排除所有包含 `50` 開頭的字串，而非僅排除包含 `50%` 的字串。

**建議**：在 `notlike` 呼叫中加入 `escape="\\"` 參數，與其他分支保持一致。

**判斷依據**：diff 中 `not contains` 分支的 `notlike` 呼叫缺少 `escape` 參數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/workflow_app_service.py:92</code> 移除 Unicode 跳脫可能導致非 ASCII 字元搜尋行為改變</summary>

原本的程式碼對關鍵字進行了 `encode('unicode_escape')` 處理，並將 `\u` 替換為 `\\u`，這可能是為了在 JSON 欄位中正確搜尋 Unicode 字元。新的程式碼移除了這項處理，僅使用 `escape_like_pattern` 跳脫 LIKE 特殊字元。這可能導致搜尋非 ASCII 字元（如中文、emoji）時無法正確匹配，因為資料庫中儲存的 JSON 可能使用 Unicode 跳脫序列。

**失敗情境**：當使用者搜尋包含中文的關鍵字時，若資料庫中的 JSON 欄位儲存的是 `\uXXXX` 形式，則新的查詢將無法匹配，導致搜尋結果遺漏。

**建議**：確認資料庫中 JSON 欄位的實際儲存格式。若確實需要 Unicode 跳脫，應保留原有處理，或將其整合到 `escape_like_pattern` 中。

**判斷依據**：diff 中移除了原有的 `encode('unicode_escape')` 和 `replace(r"\u", r"\\u")` 處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_app_service.py:11</code> 測試檔案中大量延遲匯入 AppService 可能掩蓋循環依賴</summary>

此 PR 在測試檔案中將 `from services.app_service import AppService` 改為在每個測試函式內延遲匯入，並註解「避免循環依賴」。然而，這與 PR 的主要目的（LIKE 跳脫）無關，且可能掩蓋了實際存在的循環依賴問題。若循環依賴確實存在，應在應用程式程式碼中解決，而非在測試中規避。

**建議**：若循環依賴是本次修改引入的，應找出根本原因並修復；若原本就存在，則不應在此 PR 中處理，以保持變更聚焦。

**判斷依據**：diff 中多處將頂層匯入改為函式內匯入，並附上避免循環依賴的註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/helper.py:61</code> `escape_like_pattern` 未處理 None 以外的非字串輸入</summary>

函式僅檢查 `if not pattern`，若傳入非字串（如整數、布林值），會直接呼叫 `.replace` 而拋出 `AttributeError`。雖然目前呼叫端大多傳入字串，但未來可能誤用。

**建議**：在函式開頭加入型別檢查，或使用 `isinstance(pattern, str)` 進行防禦。

**判斷依據**：函式未對輸入型別進行驗證，僅依賴 falsy 檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17424 (cache hit 13952) ｜ completion tokens 2278 ｜ PR #12</sub>