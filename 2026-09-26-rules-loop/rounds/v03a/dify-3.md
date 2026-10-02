<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 template transform 節點的 Jinja2 渲染邏輯抽象成 Jinja2TemplateRenderer 協定，並新增 CodeExecutorJinja2TemplateRenderer 實作，同時在 NodeFactory 中注入渲染器。整體設計合理，但存在兩個主要風險：render_template 可能回傳 None 導致後續 len() 呼叫拋出 TypeError；NodeFactory 在建構子中建立渲染器時，若傳入的 code_executor 為 None，會建立一個未初始化的 CodeExecutor 實例，可能導致後續執行失敗。此外，測試檔案新增大量測試案例，但部分測試的 mock 設定可能與實際行為不符。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_transform_node.py:68` | render_template 可能回傳 None，導致 len() 拋出 TypeError | 0.90 |
| ⚠️ | Major | `api/core/workflow/nodes/node_factory.py:63` | NodeFactory 在建構子中建立 CodeExecutorJinja2TemplateRenderer 時可能傳入 None 的 code_executor | 0.80 |
| 🔸 | Minor | `api/core/workflow/nodes/template_transform/template_renderer.py:37` | render_template 未處理 result 為 None 或非 dict 的情況 | 0.70 |
| 🔸 | Minor | `api/tests/unit_tests/core/workflow/nodes/template_transform/template_transform_node_spec.py:449` | 測試中 mock 的 render_template 回傳值與實際行為可能不符 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_transform_node.py:68</code> render_template 可能回傳 None，導致 len() 拋出 TypeError</summary>

在 `_run` 方法中，呼叫 `self._template_renderer.render_template(...)` 後直接對回傳值呼叫 `len(rendered)`。然而，`CodeExecutorJinja2TemplateRenderer.render_template` 的實作中，若 `result.get("result")` 回傳 `None`，則該方法會回傳 `None`（因為沒有對 `None` 進行處理）。這會導致 `len(None)` 拋出 `TypeError`，且此例外不會被 `except TemplateRenderError` 捕捉，造成節點執行失敗且錯誤訊息不明確。

**失敗情境**：當模板渲染結果為空（例如模板內容為空或渲染後輸出為空字串）時，`execute_workflow_code_template` 可能回傳 `{"result": None}`，此時 `render_template` 回傳 `None`，`len(None)` 拋出 `TypeError`。

**建議修法**：在 `CodeExecutorJinja2TemplateRenderer.render_template` 中，若 `rendered` 為 `None`，應拋出 `TemplateRenderError` 或回傳空字串；或在 `_run` 中先檢查 `rendered` 是否為 `None`。

**判斷依據**：diff 中 `template_transform_node.py` 第 68 行新增 `len(rendered)` 呼叫，而 `template_renderer.py` 第 37-39 行顯示 `rendered` 可能為 `None`（`result.get("result")` 且未檢查 `None`）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/node_factory.py:63</code> NodeFactory 在建構子中建立 CodeExecutorJinja2TemplateRenderer 時可能傳入 None 的 code_executor</summary>

在 `NodeFactory.__init__` 中，新增了 `self._template_renderer = template_renderer or CodeExecutorJinja2TemplateRenderer(code_executor)`。若 `code_executor` 參數為 `None`（預設值），則 `CodeExecutorJinja2TemplateRenderer` 的建構子會收到 `None`，並在內部執行 `self._code_executor = code_executor or CodeExecutor`，這會將 `_code_executor` 設為 `CodeExecutor` 類別本身，而非實例。後續呼叫 `execute_workflow_code_template` 時，若該方法為實例方法，則會因為缺少 `self` 參數而拋出 `TypeError`。

**失敗情境**：當 `NodeFactory` 以預設參數建立（未傳入 `code_executor`）時，任何使用 template transform 節點的工作流程在執行時都會失敗。

**建議修法**：在 `NodeFactory.__init__` 中，若 `code_executor` 為 `None`，應傳入 `CodeExecutor` 類別（而非實例）給 `CodeExecutorJinja2TemplateRenderer`，或修改 `CodeExecutorJinja2TemplateRenderer` 使其接受類別或實例。

**判斷依據**：diff 中 `node_factory.py` 第 63 行新增此行程式碼，而 `template_renderer.py` 第 25-26 行顯示 `CodeExecutorJinja2TemplateRenderer.__init__` 接受 `code_executor` 參數並賦值給 `self._code_executor`，但未檢查是否為 `None`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:37</code> render_template 未處理 result 為 None 或非 dict 的情況</summary>

`execute_workflow_code_template` 的回傳值型別未在程式碼中明確，但根據使用方式，它應該是一個 dict。然而，若該方法因某些原因回傳 `None` 或非 dict 物件，則 `result.get("result")` 會拋出 `AttributeError`。雖然這種情況可能不常見，但為了穩健性，建議先檢查 `result` 是否為 dict。

**判斷依據**：diff 中 `template_renderer.py` 第 37-39 行，直接呼叫 `result.get`，未檢查 `result` 是否為 dict。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/core/workflow/nodes/template_transform/template_transform_node_spec.py:449</code> 測試中 mock 的 render_template 回傳值與實際行為可能不符</summary>

在新增的測試中，多處將 `mock_execute.return_value` 設為字串（例如 `"Active"`），但實際的 `CodeExecutorJinja2TemplateRenderer.render_template` 會回傳 `result.get("result")`，而 `execute_workflow_code_template` 的回傳值為 dict。雖然測試是針對 `TemplateTransformNode._run` 的行為，但若未來修改 `render_template` 的實作，這些測試可能無法捕捉到型別不符的問題。建議測試中 mock 的回傳值應與實際協定一致（即回傳 dict 或直接 mock `render_template` 方法）。

**判斷依據**：diff 中測試檔案第 430 行附近，多個測試將 `mock_execute.return_value` 設為字串，而實際 `render_template` 應回傳字串（但內部是從 dict 取得），此處 mock 的層級可能造成測試與實作脫節。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16928 (cache hit 13440) ｜ completion tokens 1755 ｜ PR #3</sub>