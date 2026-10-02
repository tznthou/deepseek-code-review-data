<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多處 SQL LIKE 查詢改為使用統一的 escape_like_pattern 函式，並加入 escape 參數，以正確處理使用者輸入中的特殊字元（%、_、\），避免萬用字元注入。整體方向正確，但存在幾個關鍵問題：1) 部分查詢未傳入 escape 參數，導致跳脫失效；2) 在 ClickZetta 的 SQL 字串中，跳脫字元處理可能不正確；3) 在 Iris 的 LIKE 查詢中，escape 字元與跳脫後的字串可能不一致；4) 部分測試的斷言可能不嚴謹，無法真正驗證跳脫效果。建議優先修正上述問題，並確保所有使用 escape_like_pattern 的查詢都正確傳入 escape 參數。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/rag/retrieval/dataset_retrieval.py:1207` | not contains 條件未傳入 escape 參數，跳脫失效 | 0.95 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991` | ClickZetta LIKE 查詢的 escape 子句可能不正確 | 0.85 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/iris/iris_vector.py:298` | Iris LIKE 查詢的 escape 字元與跳脫後字串不一致 | 0.80 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_annotation_service.py:517` | 測試斷言可能無法驗證跳脫效果 | 0.70 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_app_service.py:1131` | 測試斷言可能無法驗證跳脫效果 | 0.70 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_tag_service.py:393` | 測試斷言可能無法驗證跳脫效果 | 0.70 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_workflow_app_service.py:467` | 測試斷言可能無法驗證跳脫效果 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> not contains 條件未傳入 escape 參數，跳脫失效</summary>

在 `case "not contains"` 分支中，`json_field.notlike(f"%{escaped_value}%")` 沒有傳入 `escape="\\"` 參數。這會導致跳脫字元（反斜線）被資料庫視為普通字元，而不是跳脫字元，因此 `%` 和 `_` 仍會被當作萬用字元，造成查詢結果不正確。

**失敗情境**：當使用者輸入包含 `%` 或 `_` 時，例如搜尋 `"50%"`，`not contains` 條件會將 `%` 視為萬用字元，導致排除掉所有包含 `50` 開頭的字串，而非僅排除包含字面 `50%` 的字串。

**建議修法**：與其他分支一致，加入 `escape="\\"` 參數：
```python
filters.append(json_field.notlike(f"%{escaped_value}%", escape="\\"))
```

**判斷依據**：diff 中該行新增，且未包含 escape 參數，與同檔案其他 like 條件不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991</code> ClickZetta LIKE 查詢的 escape 子句可能不正確</summary>

在 ClickZetta 的 `_search_by_like` 方法中，SQL 字串使用了 `ESCAPE '\\\\'`，但 `escape_like_pattern` 函式跳脫時使用的是單一反斜線。這可能導致跳脫字元不一致：如果資料庫將 `ESCAPE '\\\\'` 解釋為跳脫字元為兩個反斜線，則跳脫後的字串中的單一反斜線將無法正確跳脫後續的 `%` 或 `_`。

**失敗情境**：當使用者輸入包含 `%` 時，例如 `"50%"`，跳脫後的字串為 `"50\%"`，但若資料庫期望跳脫字元為 `\\`（兩個反斜線），則 `\%` 不會被視為跳脫的 `%`，而可能被解釋為字面反斜線後跟萬用字元 `%`，導致查詢結果錯誤。

**建議修法**：確認 ClickZetta 資料庫的 escape 語法，並確保 `ESCAPE` 子句中的字元與 `escape_like_pattern` 使用的跳脫字元一致。通常應使用 `ESCAPE '\'`（單一反斜線）。

**判斷依據**：diff 中該行新增，且 escape 子句使用了四個反斜線，而 escape_like_pattern 只使用單一反斜線。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/iris/iris_vector.py:298</code> Iris LIKE 查詢的 escape 字元與跳脫後字串不一致</summary>

在 Iris 的 `search_by_full_text` 方法中，SQL 使用了 `ESCAPE '|'`，但 `escape_like_pattern` 函式跳脫時使用的是反斜線 `\`。這會導致跳脫後的字串中的反斜線被資料庫視為普通字元，而不是跳脫字元，因此 `%` 和 `_` 仍會被當作萬用字元。

**失敗情境**：當使用者輸入包含 `%` 時，例如 `"50%"`，跳脫後的字串為 `"50\%"`，但由於 escape 字元是 `|`，資料庫不會將 `\%` 視為跳脫的 `%`，而是將 `\` 視為字面反斜線，`%` 視為萬用字元，導致查詢結果錯誤。

**建議修法**：將 `ESCAPE` 子句改為 `ESCAPE '\'`，或修改 `escape_like_pattern` 以使用 `|` 作為跳脫字元（但後者會影響其他查詢）。

**判斷依據**：diff 中該行新增，且 escape 字元為 '|'，而 escape_like_pattern 使用反斜線。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_annotation_service.py:517</code> 測試斷言可能無法驗證跳脫效果</summary>

在 `test_get_annotation_list_by_app_id_with_special_characters_in_keyword` 測試中，Test 4 的斷言 `assert all("50%" in (item.question or "") or "50%" in (item.content or "") for item in annotation_list)` 只檢查結果中包含 "50%"，但沒有驗證結果中不包含 "100%"。如果跳脫失效，查詢 "50%" 會匹配到 "100% different"，但該斷言仍會通過，因為 "100% different" 中也包含 "50%" 子字串。

**失敗情境**：如果跳脫未正確處理，查詢 "50%" 會返回包含 "100% different" 的記錄，但測試仍會通過，無法發現缺陷。

**建議修法**：增加斷言以確保結果中不包含 "100%"，例如：
```python
assert all("50%" in (item.question or "") or "50%" in (item.content or "") for item in annotation_list)
assert all("100%" not in (item.question or "") and "100%" not in (item.content or "") for item in annotation_list)
```

**判斷依據**：diff 中該行新增，且斷言未排除包含 "100%" 的記錄。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_app_service.py:1131</code> 測試斷言可能無法驗證跳脫效果</summary>

在 `test_get_apps_with_special_characters_in_name` 測試中，Test 4 的斷言 `assert all("50%" in app.name for app in paginated_apps.items)` 只檢查結果中包含 "50%"，但沒有驗證結果中不包含 "100%"。如果跳脫失效，查詢 "50%" 會匹配到 "100% different"，但該斷言仍會通過，因為 "100% different" 中也包含 "50%" 子字串。

**失敗情境**：如果跳脫未正確處理，查詢 "50%" 會返回包含 "100% different" 的應用程式，但測試仍會通過，無法發現缺陷。

**建議修法**：增加斷言以確保結果中不包含 "100%"，例如：
```python
assert all("50%" in app.name for app in paginated_apps.items)
assert all("100%" not in app.name for app in paginated_apps.items)
```

**判斷依據**：diff 中該行新增，且斷言未排除包含 "100%" 的記錄。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_tag_service.py:393</code> 測試斷言可能無法驗證跳脫效果</summary>

在 `test_get_tags_with_special_characters_in_keyword` 測試中，Test 4 的斷言 `assert all("50%" in item.name for item in result)` 只檢查結果中包含 "50%"，但沒有驗證結果中不包含 "100%"。如果跳脫失效，查詢 "50%" 會匹配到 "100% different"，但該斷言仍會通過，因為 "100% different" 中也包含 "50%" 子字串。

**失敗情境**：如果跳脫未正確處理，查詢 "50%" 會返回包含 "100% different" 的標籤，但測試仍會通過，無法發現缺陷。

**建議修法**：增加斷言以確保結果中不包含 "100%"，例如：
```python
assert all("50%" in item.name for item in result)
assert all("100%" not in item.name for item in result)
```

**判斷依據**：diff 中該行新增，且斷言未排除包含 "100%" 的記錄。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_workflow_app_service.py:467</code> 測試斷言可能無法驗證跳脫效果</summary>

在 `test_get_paginate_workflow_app_logs_with_special_characters_in_keyword` 測試中，Test 3 的斷言 `assert workflow_run_4.id not in found_run_ids` 是正確的，但前面的 `assert result["total"] >= 1` 和 `assert len(result["data"]) >= 1` 可能不夠嚴格。如果跳脫失效，查詢 "50%" 會匹配到 "100% different"，但 `workflow_run_4.id not in found_run_ids` 仍會失敗，因此測試仍能發現問題。然而，如果查詢 "50%" 同時匹配到 "50% discount" 和 "100% different"，則 `workflow_run_4.id not in found_run_ids` 會失敗，測試會正確失敗。因此此測試可能有效，但建議增加更明確的斷言以確保結果中不包含 "100%"。

**失敗情境**：如果跳脫未正確處理，查詢 "50%" 會返回包含 "100% different" 的記錄，但測試可能仍會通過，因為 `workflow_run_4.id not in found_run_ids` 可能因其他原因而通過（例如查詢結果未包含該記錄）。

**建議修法**：增加斷言以確保結果中不包含 "100%"，例如：
```python
assert all("100%" not in log.workflow_run.inputs and "100%" not in log.workflow_run.outputs for log in result["data"])
```

**判斷依據**：diff 中該行新增，且斷言可能無法完全驗證跳脫效果。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17494 (cache hit 13952) ｜ completion tokens 3023 ｜ PR #12</sub>