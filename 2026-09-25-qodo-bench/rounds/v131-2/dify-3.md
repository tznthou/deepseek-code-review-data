<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 TemplateTransformNode 的 Jinja2 渲染邏輯抽象為 TemplateRenderer 介面，並提供基於 CodeExecutor 的實作。整體重構方向合理，但存在一個關鍵問題：render_template 方法可能回傳 None，而呼叫端未處理，導致後續 len() 呼叫拋出 TypeError。此外，CodeExecutorJinja2TemplateRenderer 的型別標註與實際使用不一致，可能造成混淆。建議先修正 None 處理再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/workflow/nodes/template_transform/template_renderer.py:37` | render_template 可能回傳 None，導致呼叫端 TypeError | 0.95 |
| 🔸 | Minor | `api/core/workflow/nodes/template_transform/template_renderer.py:24` | 型別標註不一致：_code_executor 標為 type[CodeExecutor] 但實際為實例 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:37</code> render_template 可能回傳 None，導致呼叫端 TypeError</summary>

在 `CodeExecutorJinja2TemplateRenderer.render_template` 中，`result.get("result")` 可能回傳 `None`（例如執行器回傳的 dict 缺少 `result` 鍵）。方法回傳型別標註為 `str`，但實際上可能回傳 `None`。呼叫端 `TemplateTransformNode._run` 直接對回傳值呼叫 `len(rendered)`，若為 `None` 將拋出 `TypeError`，且未被 `TemplateRenderError` 捕捉，導致節點執行失敗且錯誤訊息不明確。

建議在 `render_template` 中檢查 `rendered is None` 並拋出 `TemplateRenderError`，或確保回傳值不為 `None`。

**判斷依據**：diff 中 `rendered = result.get("result")` 可能回傳 `None`，且後續 `return rendered` 未處理 `None`。呼叫端 `template_transform_node.py` 第 68 行 `if len(rendered) > MAX_TEMPLATE_TRANSFORM_OUTPUT_LENGTH:` 直接使用 `rendered`，若為 `None` 將拋出 `TypeError`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:24</code> 型別標註不一致：_code_executor 標為 type[CodeExecutor] 但實際為實例</summary>

`_code_executor` 被標註為 `type[CodeExecutor]`，但在 `__init__` 中賦值為 `code_executor or CodeExecutor`，其中 `code_executor` 參數型別為 `type[CodeExecutor] | None`，因此 `_code_executor` 實際上是類別而非實例。然而，在 `render_template` 中呼叫 `self._code_executor.execute_workflow_code_template(...)`，這暗示 `_code_executor` 應該是實例。若 `execute_workflow_code_template` 是實例方法，此處會因缺少 `self` 參數而失敗；若是類別方法或靜態方法則可運作。建議釐清並修正型別標註或呼叫方式。

**判斷依據**：diff 中 `_code_executor` 標註為 `type[CodeExecutor]`，但 `render_template` 中呼叫 `self._code_executor.execute_workflow_code_template(...)`，若該方法為實例方法，則此呼叫會因缺少 `self` 參數而失敗。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14204 (cache hit 14080) ｜ completion tokens 930 ｜ PR #3</sub>