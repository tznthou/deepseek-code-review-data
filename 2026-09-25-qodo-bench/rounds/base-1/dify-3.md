<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 TemplateTransformNode 的 Jinja2 渲染邏輯抽象為 Jinja2TemplateRenderer 協定，並新增 CodeExecutorJinja2TemplateRenderer 實作。主要風險在於 render_template 回傳值可能為 None，導致後續 len() 呼叫拋出 TypeError；此外，CodeExecutorJinja2TemplateRenderer 在建構時未檢查傳入的 code_executor 是否為類別，可能造成執行期錯誤。整體重構方向合理，但需先修正上述問題。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/workflow/nodes/template_transform/template_renderer.py:37` | render_template 可能回傳 None，導致後續 len() 拋出 TypeError | 0.95 |
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_renderer.py:26` | 建構子未驗證 code_executor 是否為類別，可能導致執行期錯誤 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:37</code> render_template 可能回傳 None，導致後續 len() 拋出 TypeError</summary>

在 `CodeExecutorJinja2TemplateRenderer.render_template` 中，若 `execute_workflow_code_template` 回傳的 dict 缺少 `'result'` 鍵，`rendered` 會是 `None`，函式直接回傳 `None`。呼叫端 `TemplateTransformNode._run` 接著執行 `len(rendered)`，會拋出 `TypeError: object of type 'NoneType' has no len()`，且此例外未被捕捉，導致節點執行失敗且無明確錯誤訊息。建議在回傳前檢查 `rendered` 是否為 `None`，若為 `None` 則拋出 `TemplateRenderError`。

**判斷依據**：diff 中新增的 `template_renderer.py` 第 34-36 行：`rendered = result.get("result")` 可能得到 `None`，且未處理；`template_transform_node.py` 第 68 行呼叫 `len(rendered)` 會因此失敗。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:26</code> 建構子未驗證 code_executor 是否為類別，可能導致執行期錯誤</summary>

`CodeExecutorJinja2TemplateRenderer.__init__` 接受 `code_executor` 參數，但未檢查其是否為 `CodeExecutor` 的子類別。若傳入實例而非類別，後續呼叫 `self._code_executor.execute_workflow_code_template(...)` 會因缺少 `self` 參數而拋出 `TypeError`。建議在建構時驗證型別，或明確標註參數型別為 `type[CodeExecutor]` 並在執行前檢查。

**判斷依據**：diff 中 `template_renderer.py` 第 26-27 行：建構子直接指派 `self._code_executor`，未驗證傳入值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14240 (cache hit 1536) ｜ completion tokens 795 ｜ PR #3</sub>