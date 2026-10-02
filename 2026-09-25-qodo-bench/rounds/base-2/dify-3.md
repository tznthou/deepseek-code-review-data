<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 TemplateTransformNode 的 Jinja2 渲染邏輯抽象為 TemplateRenderer 介面，並引入 CodeExecutorJinja2TemplateRenderer 實作，同時在 NodeFactory 中注入依賴。整體設計合理，但存在一個關鍵缺陷：render_template 方法在渲染結果為 None 時未拋出例外，導致後續 len(rendered) 拋出 TypeError，使節點失敗但錯誤訊息不精確。此外，測試覆蓋了多種情境，但未包含此 None 結果的案例。建議修正 render_template 的型別檢查，並補充相應測試。

### Findings（1 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_renderer.py:37` | render_template 可能回傳 None，導致後續 len() 拋出 TypeError | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:37</code> render_template 可能回傳 None，導致後續 len() 拋出 TypeError</summary>

在 `CodeExecutorJinja2TemplateRenderer.render_template` 中，若 `execute_workflow_code_template` 回傳的 dict 中 `result` 鍵的值為 `None`，則方法會直接回傳 `None`。呼叫端 `TemplateTransformNode._run` 接著執行 `len(rendered)`，對 `None` 呼叫 `len()` 會拋出 `TypeError`，且此例外未被捕捉，導致節點以未處理例外失敗，而非回傳明確的錯誤訊息。

**失敗情境**：當模板渲染結果為空（例如模板僅包含註解或空白控制）時，`execute_workflow_code_template` 可能回傳 `{'result': None}`，觸發此問題。

**建議修法**：在 `render_template` 中，若 `rendered` 為 `None`，應拋出 `TemplateRenderError`，例如：
```python
if rendered is None:
    raise TemplateRenderError("Template render result is None.")
```
或將型別檢查改為：
```python
if not isinstance(rendered, str):
    raise TemplateRenderError("Template render result must be a string.")
```

**判斷依據**：diff 中新增的 `template_renderer.py` 第 36-39 行顯示：`rendered = result.get("result")`，接著僅在 `rendered is not None` 時檢查型別，否則直接回傳 `rendered`。而呼叫端 `template_transform_node.py` 第 68 行執行 `len(rendered)`，若 `rendered` 為 `None` 將拋出 `TypeError`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14240 (cache hit 14208) ｜ completion tokens 683 ｜ PR #3</sub>