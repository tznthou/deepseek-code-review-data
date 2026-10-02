<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多處 SQL LIKE 查詢改為使用集中式 escape_like_pattern 函式，並加入 escape 參數，以正確處理特殊字元。整體方向正確，但存在幾個關鍵問題：1) 部分程式碼未使用 escape 參數，導致跳脫失效；2) ClickZetta 的 ESCAPE 子句語法可能錯誤；3) 測試中對反斜線的處理可能不正確；4) 部分 import 延遲可能造成可讀性問題。建議修正上述問題後再合併。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/rag/retrieval/dataset_retrieval.py:1207` | notlike 未使用 escape 參數，跳脫失效 | 0.90 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991` | ClickZetta 的 ESCAPE 子句語法可能錯誤 | 0.80 |
| ⚠️ | Major | `api/tests/test_containers_integration_tests/services/test_annotation_service.py:474` | 測試中反斜線處理可能不正確 | 0.80 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_app_service.py:1071` | 測試中反斜線處理可能不正確 | 0.70 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_tag_service.py:354` | 測試中反斜線處理可能不正確 | 0.70 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_workflow_app_service.py:350` | 測試中反斜線處理可能不正確 | 0.70 |
| 🔸 | Minor | `api/services/app_service.py:57` | 延遲 import 可能造成可讀性問題 | 0.60 |
| 🔸 | Minor | `api/services/dataset_service.py:147` | 使用 helper 模組但未明確 import | 0.60 |
| 🔸 | Minor | `api/services/dataset_service.py:3420` | 使用 helper 模組但未明確 import | 0.60 |
| 🔸 | Minor | `api/services/dataset_service.py:3450` | 使用 helper 模組但未明確 import | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> notlike 未使用 escape 參數，跳脫失效</summary>

在 `case "not contains"` 分支中，`json_field.notlike(f"%{escaped_value}%")` 沒有傳入 `escape="\\"`。這會導致 `escaped_value` 中的反斜線被視為一般字元，無法正確跳脫 `%` 和 `_`，使得搜尋結果可能包含不應匹配的資料。

建議修改為：
```python
filters.append(json_field.notlike(f"%{escaped_value}%", escape="\\"))
```

**判斷依據**：diff 中新增的 `escaped_value = escape_like_pattern(str(value))` 後，`notlike` 呼叫未加上 `escape` 參數，與其他分支（如 `contains`）不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991</code> ClickZetta 的 ESCAPE 子句語法可能錯誤</summary>

在 ClickZetta 的 LIKE 查詢中，使用了 `ESCAPE '\\\\'`。但根據常見 SQL 語法，ESCAPE 子句應指定單一字元，例如 `ESCAPE '\\'`。目前寫法可能導致語法錯誤或跳脫行為不符預期。

建議確認 ClickZetta 的文件，並將 ESCAPE 子句改為正確的單一字元表示。

**判斷依據**：diff 中新增的 `ESCAPE '\\\\'` 與其他檔案中使用的 `escape="\\"` 不一致，且可能不符合 SQL 標準。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/tests/test_containers_integration_tests/services/test_annotation_service.py:474</code> 測試中反斜線處理可能不正確</summary>

在測試 `test_get_annotation_list_by_app_id_with_special_characters_in_keyword` 中，建立 annotation 時使用了 `"path\\to\\file"`，但 Python 字串中 `\\` 代表單一反斜線，因此實際存入的內容是 `path\to\file`。搜尋時使用 `keyword="path\\to\\file"` 也是單一反斜線，但 `escape_like_pattern` 會將反斜線跳脫為 `\\`，再配合 `escape="\\"` 應該能正確匹配。然而，測試的斷言 `assert "path\\to\\file" in ...` 可能因字串表示問題而失敗。

建議檢查測試資料的實際內容，並確認斷言中的字串與資料一致。

**判斷依據**：diff 中測試資料使用 `"path\\to\\file"`，但 Python 會將其解讀為 `path\to\file`，而斷言中可能使用了不同的表示方式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_app_service.py:1071</code> 測試中反斜線處理可能不正確</summary>

在 `test_get_apps_with_special_characters_in_name` 中，建立 app 時使用了 `"path\\to\\app"`，但 Python 字串中 `\\` 代表單一反斜線，因此實際名稱是 `path\to\app`。搜尋時使用 `args = {"name": "path\\to\\app", ...}` 也是單一反斜線，但 `escape_like_pattern` 會將反斜線跳脫為 `\\`，再配合 `escape="\\"` 應該能正確匹配。然而，測試的斷言 `assert paginated_apps.items[0].name == "path\\to\\app"` 可能因字串表示問題而失敗。

建議檢查測試資料的實際內容，並確認斷言中的字串與資料一致。

**判斷依據**：diff 中測試資料使用 `"path\\to\\app"`，但 Python 會將其解讀為 `path\to\app`，而斷言中可能使用了不同的表示方式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_tag_service.py:354</code> 測試中反斜線處理可能不正確</summary>

在 `test_get_tags_with_special_characters_in_keyword` 中，建立 tag 時使用了 `"path\\to\\tag"`，但 Python 字串中 `\\` 代表單一反斜線，因此實際名稱是 `path\to\tag`。搜尋時使用 `keyword="path\\to\\tag"` 也是單一反斜線，但 `escape_like_pattern` 會將反斜線跳脫為 `\\`，再配合 `escape="\\"` 應該能正確匹配。然而，測試的斷言 `assert result[0].name == "path\\to\\tag"` 可能因字串表示問題而失敗。

建議檢查測試資料的實際內容，並確認斷言中的字串與資料一致。

**判斷依據**：diff 中測試資料使用 `"path\\to\\tag"`，但 Python 會將其解讀為 `path\to\tag`，而斷言中可能使用了不同的表示方式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_workflow_app_service.py:350</code> 測試中反斜線處理可能不正確</summary>

在 `test_get_paginate_workflow_app_logs_with_special_characters_in_keyword` 中，建立 workflow run 時使用了 `"50% discount"` 和 `"test_data_value"`，但未測試反斜線。然而，測試中對 `%` 和 `_` 的處理可能因 `escape_like_pattern` 的跳脫而正確。但需注意，測試中未包含反斜線案例，可能遺漏了對反斜線跳脫的驗證。

建議增加反斜線的測試案例，以確保 `escape_like_pattern` 對反斜線的處理正確。

**判斷依據**：diff 中測試僅包含 `%` 和 `_`，未包含反斜線，可能無法完整驗證跳脫邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/services/app_service.py:57</code> 延遲 import 可能造成可讀性問題</summary>

在 `get_paginate_apps` 方法中，`from libs.helper import escape_like_pattern` 被放在條件區塊內。雖然可以避免循環依賴，但這種延遲 import 可能降低程式碼可讀性，且若未來有其他程式碼路徑需要使用該函式，可能遺漏 import。

建議將 import 移至檔案頂部，除非有明確的循環依賴問題。

**判斷依據**：diff 中新增的 import 位於條件區塊內，與其他檔案的 import 風格不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/services/dataset_service.py:147</code> 使用 helper 模組但未明確 import</summary>

在 `get_datasets` 方法中，使用了 `helper.escape_like_pattern(search)`，但檔案中未明確 import `helper` 模組。這可能導致 `NameError`，除非 `helper` 已在其他地方被 import 並可用。

建議確認 `helper` 模組是否已正確 import，或改為明確的 `from libs.helper import escape_like_pattern`。

**判斷依據**：diff 中新增的程式碼使用了 `helper.escape_like_pattern`，但未見對應的 import 語句。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/services/dataset_service.py:3420</code> 使用 helper 模組但未明確 import</summary>

在 `get_child_chunks` 方法中，使用了 `helper.escape_like_pattern(keyword)`，但檔案中未明確 import `helper` 模組。這可能導致 `NameError`，除非 `helper` 已在其他地方被 import 並可用。

建議確認 `helper` 模組是否已正確 import，或改為明確的 `from libs.helper import escape_like_pattern`。

**判斷依據**：diff 中新增的程式碼使用了 `helper.escape_like_pattern`，但未見對應的 import 語句。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/services/dataset_service.py:3450</code> 使用 helper 模組但未明確 import</summary>

在 `get_segments` 方法中，使用了 `helper.escape_like_pattern(keyword)`，但檔案中未明確 import `helper` 模組。這可能導致 `NameError`，除非 `helper` 已在其他地方被 import 並可用。

建議確認 `helper` 模組是否已正確 import，或改為明確的 `from libs.helper import escape_like_pattern`。

**判斷依據**：diff 中新增的程式碼使用了 `helper.escape_like_pattern`，但未見對應的 import 語句。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 28381 (cache hit 1536) ｜ completion tokens 2841 ｜ PR #12</sub>