<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 TemplateTransformNode 的 Jinja2 渲染邏輯抽象為 Jinja2TemplateRenderer 協定，並新增 CodeExecutorJinja2TemplateRenderer 實作，同時在 NodeFactory 中注入 renderer。主要風險在於 render_template 回傳值可能為 None，導致後續 len() 呼叫拋出 TypeError；此外，CodeExecutorJinja2TemplateRenderer 在建構時可能因 code_executor 為 None 而使用預設 CodeExecutor，但型別標示為 type[CodeExecutor] 可能造成混淆。整體重構方向合理，但需修正 None 處理與型別一致性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_transform_node.py:68` | render_template 可能回傳 None，導致 len() 拋出 TypeError | 0.90 |
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_renderer.py:37` | render_template 回傳型別與協定不符，可能回傳 None | 0.85 |
| 🔸 | Minor | `api/core/workflow/nodes/template_transform/template_renderer.py:26` | CodeExecutorJinja2TemplateRenderer 建構子參數型別可能造成混淆 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_transform_node.py:68</code> render_template 可能回傳 None，導致 len() 拋出 TypeError</summary>

在 `_run` 中，`rendered = self._template_renderer.render_template(...)` 的結果直接傳給 `len(rendered)`。但 `CodeExecutorJinja2TemplateRenderer.render_template` 在 `result.get("result")` 為 None 時會回傳 None（見 template_renderer.py 第 36 行），此時 `len(None)` 會拋出 `TypeError`，且此例外未被捕捉，導致節點執行失敗且無明確錯誤訊息。建議在 renderer 中確保回傳值為字串，或在呼叫端檢查 None 並回傳失敗結果。

**判斷依據**：diff 中新增的 `rendered = self._template_renderer.render_template(...)` 與 `if len(rendered) > ...`，以及 template_renderer.py 中 `return rendered` 可能為 None。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:37</code> render_template 回傳型別與協定不符，可能回傳 None</summary>

`Jinja2TemplateRenderer` 協定宣告 `render_template` 回傳 `str`，但 `CodeExecutorJinja2TemplateRenderer.render_template` 在 `result.get("result")` 為 None 時會回傳 None，違反協定。這會導致呼叫端在未檢查的情況下使用 None 而發生錯誤。建議在 renderer 中檢查並拋出 `TemplateRenderError`，或確保回傳值為字串。

**判斷依據**：diff 中 `return rendered` 且 `rendered` 可能為 None，與協定回傳 `str` 不符。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:26</code> CodeExecutorJinja2TemplateRenderer 建構子參數型別可能造成混淆</summary>

`__init__` 的參數 `code_executor` 型別標示為 `type[CodeExecutor] | None`，但若傳入 None，則使用 `CodeExecutor` 類別本身。然而 `CodeExecutor` 可能不是可呼叫的類別，而是抽象基底類別或具有不同介面，導致後續呼叫 `execute_workflow_code_template` 時出錯。建議確認 `CodeExecutor` 的實際型別，或改為接受實例而非類別。

**判斷依據**：diff 中 `self._code_executor = code_executor or CodeExecutor`，若 `CodeExecutor` 為抽象類別，則無法直接呼叫其方法。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16908 (cache hit 13440) ｜ completion tokens 1050 ｜ PR #3</sub>