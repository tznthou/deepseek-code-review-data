<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 TemplateTransformNode 的 Jinja2 渲染邏輯抽象為 Jinja2TemplateRenderer 介面，並新增 CodeExecutorJinja2TemplateRenderer 實作。主要風險在於 render_template 回傳型別未嚴格驗證，可能導致下游 len() 或輸出處理出錯；此外，NodeFactory 在建構 renderer 時未傳入 code_executor，可能破壞依賴注入。整體架構合理，但需修正型別安全與依賴傳遞問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_renderer.py:37` | render_template 回傳值可能為 None，導致後續 len() 出錯 | 0.85 |
| ⚠️ | Major | `api/core/workflow/nodes/node_factory.py:63` | NodeFactory 建構 renderer 時未傳入 code_executor，可能破壞依賴注入 | 0.80 |
| 🔸 | Minor | `api/core/workflow/nodes/template_transform/template_transform_node.py:68` | 輸出長度檢查前未驗證 rendered 型別 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:37</code> render_template 回傳值可能為 None，導致後續 len() 出錯</summary>

`render_template` 在 `rendered` 為 `None` 時直接回傳 `None`，但呼叫端 `TemplateTransformNode._run` 會對回傳值執行 `len(rendered)`，若為 `None` 將拋出 `TypeError`。建議在回傳前檢查 `rendered is None` 並拋出 `TemplateRenderError`，或確保 `execute_workflow_code_template` 永遠回傳字串。

**判斷依據**：diff 中 `render_template` 方法回傳 `rendered`，但未處理 `rendered` 為 `None` 的情況；而 `template_transform_node.py` 中呼叫後直接 `len(rendered)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/node_factory.py:63</code> NodeFactory 建構 renderer 時未傳入 code_executor，可能破壞依賴注入</summary>

`self._template_renderer = template_renderer or CodeExecutorJinja2TemplateRenderer(code_executor)` 中，若 `template_renderer` 為 None，則使用傳入的 `code_executor` 建立 renderer；但若 `template_renderer` 已提供，則忽略 `code_executor`。這可能導致測試或自訂 renderer 無法使用預期的 executor。建議統一由 factory 傳入 `code_executor`，或明確文件說明。

**判斷依據**：diff 中 NodeFactory.__init__ 新增 `template_renderer` 參數，並在建構時使用 `or` 邏輯，可能忽略傳入的 `code_executor`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/nodes/template_transform/template_transform_node.py:68</code> 輸出長度檢查前未驗證 rendered 型別</summary>

`len(rendered)` 假設 `rendered` 為字串，但 `render_template` 可能回傳非字串（若實作未嚴格遵守 Protocol）。建議在呼叫後先檢查型別，或由 renderer 保證回傳字串。

**判斷依據**：diff 中直接對 `rendered` 呼叫 `len()`，未先確認其型別。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16918 (cache hit 16896) ｜ completion tokens 919 ｜ PR #3</sub>