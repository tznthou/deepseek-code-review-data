<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 TemplateTransformNode 的 Jinja2 渲染邏輯抽象為 Jinja2TemplateRenderer 協定，並新增 CodeExecutorJinja2TemplateRenderer 實作，同時在 NodeFactory 中注入 renderer。整體重構方向合理，但存在兩個主要風險：render_template 回傳型別未明確保證為 str，可能導致後續 len() 呼叫拋出 TypeError；以及 NodeFactory 在建構 renderer 時可能傳入 None 的 code_executor，造成執行時期錯誤。建議優先修正型別與空值處理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_renderer.py:37` | render_template 回傳型別未保證為 str，可能導致 len() 拋出 TypeError | 0.80 |
| ⚠️ | Major | `api/core/workflow/nodes/node_factory.py:63` | NodeFactory 可能傳入 None 的 code_executor 給 CodeExecutorJinja2TemplateRenderer | 0.70 |
| 🔸 | Minor | `api/core/workflow/nodes/template_transform/template_transform_node.py:41` | TemplateTransformNode 在建構時未傳入 code_executor，可能導致測試或特定環境下行為不一致 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:37</code> render_template 回傳型別未保證為 str，可能導致 len() 拋出 TypeError</summary>

`CodeExecutorJinja2TemplateRenderer.render_template` 的型別標註為 `-> str`，但實作中 `rendered = result.get("result")` 後僅檢查 `rendered is not None and not isinstance(rendered, str)`，若 `result` 為 `None` 或 `result.get("result")` 回傳 `None`，則函式會回傳 `None`，違反型別標註。呼叫端 `TemplateTransformNode._run` 直接對回傳值呼叫 `len(rendered)`，若為 `None` 將拋出 `TypeError`，且此例外未被捕捉，導致節點執行失敗且錯誤訊息不明確。建議在 renderer 中明確檢查 `rendered is None` 並拋出 `TemplateRenderError`，或確保 `execute_workflow_code_template` 一定回傳包含 `result` 鍵的字典。

**判斷依據**：diff 中 `render_template` 回傳 `rendered`，但未處理 `rendered` 為 `None` 的情況；呼叫端 `template_transform_node.py` 新增的 `len(rendered)` 直接假設為字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/node_factory.py:63</code> NodeFactory 可能傳入 None 的 code_executor 給 CodeExecutorJinja2TemplateRenderer</summary>

`NodeFactory.__init__` 新增參數 `template_renderer: Jinja2TemplateRenderer | None = None`，並在未提供時建立 `CodeExecutorJinja2TemplateRenderer(code_executor)`。但 `code_executor` 參數本身也是 `type[CodeExecutor] | None = None`，若呼叫端未提供 `code_executor` 且未提供 `template_renderer`，則會將 `None` 傳給 `CodeExecutorJinja2TemplateRenderer`，其建構子雖有 `code_executor or CodeExecutor` 的處理，但型別標註為 `type[CodeExecutor]`，可能導致型別檢查錯誤或執行時期問題。建議在建構 renderer 時明確處理 `code_executor` 為 `None` 的情況，或調整 `CodeExecutorJinja2TemplateRenderer` 的建構子接受 `None`。

**判斷依據**：diff 中 `code_executor` 參數可為 `None`，且直接傳入 `CodeExecutorJinja2TemplateRenderer`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/nodes/template_transform/template_transform_node.py:41</code> TemplateTransformNode 在建構時未傳入 code_executor，可能導致測試或特定環境下行為不一致</summary>

`TemplateTransformNode.__init__` 中若未提供 `template_renderer`，會建立 `CodeExecutorJinja2TemplateRenderer()`，但此建構子未接收 `code_executor`，因此使用預設的 `CodeExecutor`。然而在 `NodeFactory` 中建立的 renderer 會傳入 `code_executor`，兩者行為可能不同。若未來需要自訂 code executor，此處可能遺漏。建議統一 renderer 的建立方式，或明確說明此處使用預設 executor 的意圖。

**判斷依據**：diff 中 `TemplateTransformNode` 建立 renderer 時未傳入 `code_executor`，而 `NodeFactory` 有傳入。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16918 (cache hit 5376) ｜ completion tokens 1188 ｜ PR #3</sub>