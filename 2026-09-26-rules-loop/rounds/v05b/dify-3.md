<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 template transform 節點的 Jinja2 渲染邏輯抽象為 TemplateRenderer 介面，並引入 CodeExecutorJinja2TemplateRenderer 實作，同時在 NodeFactory 中注入 renderer。主要風險在於 render_template 回傳值可能為 None 時，後續 len() 會拋出未處理的 TypeError；此外，測試檔案新增大量測試，但部分測試的 mock 路徑可能因 renderer 實例化方式而失效。建議優先修正 None 處理，並確認測試覆蓋。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_transform_node.py:68` | render_template 回傳 None 時 len() 會拋出未處理的 TypeError | 0.80 |
| 🔸 | Minor | `api/core/workflow/nodes/template_transform/template_renderer.py:37` | render_template 回傳型別標示為 str，但可能回傳 None | 0.70 |
| 🔸 | Minor | `api/tests/unit_tests/core/workflow/nodes/template_transform/template_transform_node_spec.py:9` | 測試中 mock 路徑可能因 renderer 實例化方式而失效 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_transform_node.py:68</code> render_template 回傳 None 時 len() 會拋出未處理的 TypeError</summary>

在 `_run` 中，`rendered = self._template_renderer.render_template(...)` 後直接呼叫 `len(rendered)`。若 renderer 回傳 `None`（例如 `CodeExecutorJinja2TemplateRenderer` 在 `result.get("result")` 為 None 時會回傳 None），則 `len(None)` 會拋出 `TypeError`，且此例外未被捕捉，導致節點執行失敗但錯誤訊息不明確。建議在呼叫 `len` 前檢查 `rendered is None`，或讓 renderer 在結果為 None 時拋出 `TemplateRenderError`。

**判斷依據**：diff 中新增的 `len(rendered)` 呼叫，而 `CodeExecutorJinja2TemplateRenderer.render_template` 在 `result.get("result")` 為 None 時會回傳 None（見 template_renderer.py 第 36-38 行）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:37</code> render_template 回傳型別標示為 str，但可能回傳 None</summary>

`CodeExecutorJinja2TemplateRenderer.render_template` 的型別標示為 `-> str`，但當 `result.get("result")` 為 None 時，函式會回傳 None，與型別標示不符。這可能導致呼叫端在未檢查 None 的情況下發生錯誤（如本 PR 中的 `len(rendered)`）。建議在回傳前檢查並拋出 `TemplateRenderError`，或將回傳型別改為 `str | None` 並在呼叫端處理。

**判斷依據**：diff 中 `return rendered` 未處理 `rendered` 為 None 的情況，而函式標示回傳 `str`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/core/workflow/nodes/template_transform/template_transform_node_spec.py:9</code> 測試中 mock 路徑可能因 renderer 實例化方式而失效</summary>

測試使用 `@patch("core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template")` 來 mock renderer。但 `TemplateTransformNode.__init__` 中若未傳入 `template_renderer`，會建立 `CodeExecutorJinja2TemplateRenderer()` 實例，而 mock 是 patch 類別方法，可能無法攔截到實例方法呼叫。建議改為 patch `CodeExecutorJinja2TemplateRenderer` 類別本身，或直接傳入 mock renderer。

**判斷依據**：diff 中測試的 patch 目標為類別方法，但節點內部會建立實例並呼叫其方法，可能導致 mock 無效。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16838 (cache hit 16768) ｜ completion tokens 1084 ｜ PR #3</sub>