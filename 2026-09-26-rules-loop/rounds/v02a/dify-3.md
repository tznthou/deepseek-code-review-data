<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 TemplateTransformNode 的 Jinja2 渲染邏輯抽象為 Jinja2TemplateRenderer 協定，並新增 CodeExecutorJinja2TemplateRenderer 實作，同時在 NodeFactory 中注入 renderer。主要風險在於 render_template 回傳型別未嚴格驗證，可能導致 None 或非字串值流入後續邏輯；此外，測試中大量使用 MagicMock 模擬 renderer，未驗證實際渲染行為。建議優先修正 renderer 回傳型別驗證，並考慮增加整合測試。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_renderer.py:37` | render_template 可能回傳 None，導致後續 len() 或輸出錯誤 | 0.80 |
| 🔸 | Minor | `api/core/workflow/nodes/template_transform/template_transform_node.py:68` | render_template 回傳非字串時，錯誤訊息可能不明確 | 0.60 |
| 🔸 | Minor | `api/tests/unit_tests/core/workflow/nodes/template_transform/template_transform_node_spec.py:430` | 測試大量使用 MagicMock 模擬 renderer，未驗證實際渲染行為 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:37</code> render_template 可能回傳 None，導致後續 len() 或輸出錯誤</summary>

在 `CodeExecutorJinja2TemplateRenderer.render_template` 中，`result.get("result")` 可能回傳 `None`，但函式回傳型別標註為 `str`。若 `execute_workflow_code_template` 回傳的 dict 缺少 `result` 鍵或值為 `None`，則 `rendered` 為 `None`，函式會直接回傳 `None`。呼叫端 `TemplateTransformNode._run` 接著執行 `len(rendered)`，將拋出 `TypeError`，導致節點失敗且錯誤訊息不明確。建議在 renderer 中明確檢查 `rendered is None` 並拋出 `TemplateRenderError`，或確保回傳型別為 `str`。

**判斷依據**：diff 中新增的 `template_renderer.py` 第 36-38 行顯示 `rendered` 可能為 `None`，且函式回傳型別為 `str`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/nodes/template_transform/template_transform_node.py:68</code> render_template 回傳非字串時，錯誤訊息可能不明確</summary>

在 `TemplateTransformNode._run` 中，呼叫 `self._template_renderer.render_template` 後直接使用 `len(rendered)`。若 renderer 因實作錯誤回傳非字串（例如 `None` 或數字），會拋出 `TypeError`，但此例外未被捕捉，導致節點以未處理例外失敗，而非回傳結構化的 `NodeRunResult`。建議在 renderer 中嚴格驗證回傳型別，或在節點中捕捉 `TypeError` 並轉換為 `TemplateRenderError`。

**判斷依據**：diff 中 `template_transform_node.py` 第 68-69 行顯示直接對 `rendered` 呼叫 `len()`，未檢查型別。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/core/workflow/nodes/template_transform/template_transform_node_spec.py:430</code> 測試大量使用 MagicMock 模擬 renderer，未驗證實際渲染行為</summary>

新增的測試案例均使用 `@patch` 模擬 `CodeExecutorJinja2TemplateRenderer.render_template`，僅驗證節點邏輯對模擬回傳值的處理，未測試實際的 Jinja2 渲染功能。這可能導致渲染器本身的錯誤（如模板語法錯誤、變數處理不當）未被測試覆蓋。建議增加針對 `CodeExecutorJinja2TemplateRenderer` 的單元測試，或使用真實的 CodeExecutor 進行整合測試。

**判斷依據**：diff 中測試檔案新增的多個測試函式均使用 `@patch` 模擬 renderer，未呼叫真實渲染邏輯。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16919 (cache hit 1536) ｜ completion tokens 1103 ｜ PR #3</sub>