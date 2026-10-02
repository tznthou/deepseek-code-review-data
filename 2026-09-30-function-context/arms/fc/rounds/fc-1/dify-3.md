<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 TemplateTransformNode 的 Jinja2 渲染邏輯抽象為 Jinja2TemplateRenderer 介面，並提供 CodeExecutorJinja2TemplateRenderer 實作，同時在 DifyNodeFactory 中注入 renderer。主要風險在於 render_template 回傳值可能為 None，導致後續 len() 呼叫拋出 TypeError；此外，CodeExecutorJinja2TemplateRenderer 在建構時未傳入 code_executor，可能與 factory 注入的 executor 不一致。整體重構方向合理，但需修正上述問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_transform_node.py:68` | render_template 回傳 None 時 len() 會拋出 TypeError | 0.90 |
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_renderer.py:37` | render_template 可能回傳 None，違反回傳型別標註 | 0.85 |
| 🔸 | Minor | `api/core/workflow/nodes/template_transform/template_transform_node.py:41` | 預設 renderer 未使用 factory 注入的 code_executor | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_transform_node.py:68</code> render_template 回傳 None 時 len() 會拋出 TypeError</summary>

在 `_run` 中，`rendered = self._template_renderer.render_template(...)` 後直接呼叫 `len(rendered)`。但 `CodeExecutorJinja2TemplateRenderer.render_template` 在 `result.get("result")` 為 None 時會回傳 None（見 template_renderer.py 第 36 行），此時 `len(None)` 會拋出 `TypeError`，且未被 `except TemplateRenderError` 捕捉，導致節點執行崩潰。建議在 renderer 中對 None 結果拋出 `TemplateRenderError`，或在 `_run` 中檢查 `rendered is None` 並回傳失敗。

**判斷依據**：template_renderer.py 第 36 行 `return rendered` 可能回傳 None；template_transform_node.py 第 75 行 `len(rendered)` 未處理 None。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:37</code> render_template 可能回傳 None，違反回傳型別標註</summary>

`render_template` 的型別標註為 `-> str`，但當 `result.get("result")` 為 None 時會回傳 None。這會導致呼叫端在未檢查的情況下發生型別錯誤。建議在 None 時拋出 `TemplateRenderError`，確保回傳值永遠是 str。

**判斷依據**：第 34-36 行：rendered 可能為 None，直接回傳。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/nodes/template_transform/template_transform_node.py:41</code> 預設 renderer 未使用 factory 注入的 code_executor</summary>

`TemplateTransformNode.__init__` 中，若未提供 `template_renderer`，會建立 `CodeExecutorJinja2TemplateRenderer()`，其內部使用預設的 `CodeExecutor`。但 `DifyNodeFactory` 在建構時可能注入了自訂的 `code_executor`（例如用於測試或沙箱），此時節點使用的 executor 與 factory 不一致。建議將 factory 的 `_code_executor` 傳入 renderer，或由 factory 統一建立 renderer 並注入。

**判斷依據**：node_factory.py 第 57 行 `self._template_renderer = template_renderer or CodeExecutorJinja2TemplateRenderer(code_executor)` 有傳入 code_executor，但此處未傳。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15946 (cache hit 1536) ｜ completion tokens 991 ｜ PR #3</sub>