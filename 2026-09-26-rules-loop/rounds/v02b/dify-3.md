<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 TemplateTransformNode 的 Jinja2 渲染邏輯抽象為 Jinja2TemplateRenderer 協定，並新增 CodeExecutorJinja2TemplateRenderer 實作，同時在 NodeFactory 中注入 renderer。主要風險在於 render_template 回傳型別未嚴格驗證，可能導致 None 或非字串值進入後續邏輯；此外，測試中大量使用 MagicMock 模擬 renderer，但未驗證實際渲染行為，且部分測試的 mock 設定可能與實際變數解析不符。建議優先修正 renderer 的回傳型別處理，並補強測試的真實性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_renderer.py:37` | render_template 可能回傳 None，導致後續 len() 出錯 | 0.80 |
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_transform_node.py:68` | 未處理 render_template 回傳 None 的情況 | 0.75 |
| 🔸 | Minor | `api/core/workflow/nodes/template_transform/template_renderer.py:24` | CodeExecutorJinja2TemplateRenderer 的型別標註可能不精確 | 0.60 |
| 🔸 | Minor | `api/tests/unit_tests/core/workflow/nodes/template_transform/template_transform_node_spec.py:430` | 測試中大量使用 MagicMock 模擬 renderer，未驗證實際渲染邏輯 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:37</code> render_template 可能回傳 None，導致後續 len() 出錯</summary>

在 `CodeExecutorJinja2TemplateRenderer.render_template` 中，`result.get("result")` 可能回傳 `None`，但函式僅在 `rendered is not None and not isinstance(rendered, str)` 時拋出錯誤，若 `rendered` 為 `None` 則直接回傳 `None`。呼叫端 `TemplateTransformNode._run` 會對回傳值執行 `len(rendered)`，若為 `None` 將拋出 `TypeError`，且未被捕捉，導致節點執行失敗但錯誤訊息不明確。建議在 renderer 中明確檢查 `rendered is None` 並拋出 `TemplateRenderError`，或確保回傳型別為 `str`。

**判斷依據**：diff 中新增的 template_renderer.py 第 36-38 行顯示，當 `rendered` 為 `None` 時，條件判斷不成立，直接回傳 `None`。而 template_transform_node.py 第 68 行呼叫 `len(rendered)`，若 `rendered` 為 `None` 會拋出 `TypeError`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_transform_node.py:68</code> 未處理 render_template 回傳 None 的情況</summary>

`_run` 方法中，`rendered = self._template_renderer.render_template(...)` 後直接執行 `len(rendered)`，但 renderer 可能回傳 `None`（如上述 finding），導致 `TypeError`。此例外未被捕捉，會使節點執行失敗且錯誤訊息不明確。建議在 renderer 中保證回傳 `str`，或在此處增加型別檢查。

**判斷依據**：diff 中 template_transform_node.py 第 68-69 行顯示直接對 `rendered` 呼叫 `len()`，而 renderer 的實作可能回傳 `None`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:24</code> CodeExecutorJinja2TemplateRenderer 的型別標註可能不精確</summary>

`_code_executor` 被標註為 `type[CodeExecutor]`，但 `execute_workflow_code_template` 可能是實例方法或靜態方法，若為實例方法，則傳入類別而非實例可能導致呼叫錯誤。建議確認 `CodeExecutor` 的設計，並考慮使用 `CodeExecutor` 的實例或調整型別標註。

**判斷依據**：diff 中 template_renderer.py 第 31-33 行顯示 `_code_executor` 被標註為 `type[CodeExecutor]`，但實際使用 `self._code_executor.execute_workflow_code_template(...)`，若該方法為實例方法，則會出錯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/core/workflow/nodes/template_transform/template_transform_node_spec.py:430</code> 測試中大量使用 MagicMock 模擬 renderer，未驗證實際渲染邏輯</summary>

新增的測試均以 `@patch` 模擬 `CodeExecutorJinja2TemplateRenderer.render_template`，僅驗證節點對回傳值的處理，未測試實際的 Jinja2 渲染行為。這可能導致渲染邏輯的錯誤未被發現。建議增加針對 `CodeExecutorJinja2TemplateRenderer` 的單元測試，或使用真實的 renderer 進行整合測試。

**判斷依據**：diff 中測試檔案從第 430 行開始新增多個測試，均使用 `@patch` 模擬 renderer，未實際執行渲染。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16919 (cache hit 16896) ｜ completion tokens 1415 ｜ PR #3</sub>