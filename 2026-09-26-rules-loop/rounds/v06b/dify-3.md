<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 TemplateTransformNode 的 Jinja2 渲染邏輯抽象為 Jinja2TemplateRenderer 協定，並新增 CodeExecutorJinja2TemplateRenderer 實作，同時在 NodeFactory 中注入 renderer。整體重構方向合理，但存在一個關鍵缺陷：render_template 可能回傳 None，導致後續 len() 呼叫拋出 TypeError，且該例外未被捕捉，可能造成節點執行崩潰。此外，測試檔新增大量測試但部分測試的 mock 設定與實際行為不符，可能掩蓋問題。建議優先修正 None 處理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/workflow/nodes/template_transform/template_transform_node.py:68` | render_template 可能回傳 None，導致 len() 拋出未捕捉的 TypeError | 0.90 |
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_renderer.py:37` | render_template 未處理 result 為 None 的情況，可能導致下游錯誤 | 0.80 |
| 🔸 | Minor | `api/tests/unit_tests/core/workflow/nodes/template_transform/template_transform_node_spec.py:449` | 測試中 mock 的 render_template 回傳值與實際協定不符 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/workflow/nodes/template_transform/template_transform_node.py:68</code> render_template 可能回傳 None，導致 len() 拋出未捕捉的 TypeError</summary>

在 `_run` 方法中，呼叫 `self._template_renderer.render_template(...)` 後直接對回傳值呼叫 `len(rendered)`。然而，`CodeExecutorJinja2TemplateRenderer.render_template` 的實作中，若 `result.get("result")` 回傳 `None`，則該方法會直接回傳 `None`（因為型別檢查只處理非 None 且非 str 的情況）。這會導致 `len(None)` 拋出 `TypeError`，且此例外不在 `except TemplateRenderError` 的捕捉範圍內，最終可能使節點執行失敗並產生未處理的例外。

**失敗情境**：當模板渲染結果為空（例如模板內容為空或渲染後無輸出）時，`execute_workflow_code_template` 可能回傳 `{"result": None}`，此時 `render_template` 回傳 `None`，`len(None)` 拋出 `TypeError`。

**建議修法**：在 `render_template` 中明確處理 `None` 情況，例如拋出 `TemplateRenderError`，或在 `_run` 中檢查 `rendered is None` 並回傳失敗結果。

**判斷依據**：diff 中 `template_transform_node.py` 第 68 行新增 `rendered = ...` 與 `if len(rendered) > ...`，而 `template_renderer.py` 第 36-38 行顯示 `rendered = result.get("result")` 後僅檢查非 None 且非 str 才拋錯，未處理 None 回傳。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:37</code> render_template 未處理 result 為 None 的情況，可能導致下游錯誤</summary>

`render_template` 方法中，`rendered = result.get("result")` 可能為 `None`，但程式碼僅在 `rendered is not None and not isinstance(rendered, str)` 時拋出 `TemplateRenderError`，若 `rendered` 為 `None` 則直接回傳 `None`。這違反了回傳型別標註 `str`，且呼叫端未預期 `None`，可能導致後續 `len()` 或字串操作失敗。

**建議修法**：在 `render_template` 中明確檢查 `rendered is None` 並拋出 `TemplateRenderError`，或確保 `execute_workflow_code_template` 永遠回傳字串。

**判斷依據**：diff 中 `template_renderer.py` 第 36-38 行顯示此邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/core/workflow/nodes/template_transform/template_transform_node_spec.py:449</code> 測試中 mock 的 render_template 回傳值與實際協定不符</summary>

多個測試使用 `@patch("core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template")` 並設定 `mock_execute.return_value` 為字串，但實際的 `render_template` 方法應回傳字串，這部分正確。然而，部分測試（如 `test_run_with_boolean_values`）中 mock 的 `render_template` 回傳值為 `"Active"`，但未驗證輸入參數，可能無法捕捉到變數傳遞錯誤。此外，測試中大量重複的 mock 設定可能掩蓋真實 renderer 的行為。

**建議**：考慮使用真實的 `CodeExecutorJinja2TemplateRenderer` 搭配 mock 的 `CodeExecutor` 進行整合測試，以驗證實際渲染邏輯。

**判斷依據**：diff 中測試檔案第 430 行附近，多個測試均以字串作為 mock 回傳值，但未驗證呼叫參數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16908 (cache hit 16896) ｜ completion tokens 1317 ｜ PR #3</sub>