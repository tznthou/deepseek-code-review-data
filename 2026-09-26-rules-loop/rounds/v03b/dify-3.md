<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 TemplateTransformNode 的 Jinja2 渲染邏輯抽象為 Jinja2TemplateRenderer 介面，並提供 CodeExecutorJinja2TemplateRenderer 實作，同時在 NodeFactory 中注入。整體重構方向合理，但存在一個關鍵問題：render_template 的型別標示為回傳 str，但實際可能回傳 None，導致後續 len(rendered) 在渲染結果為 None 時拋出 TypeError，造成節點執行失敗。此外，測試檔新增大量測試案例，但部分測試的 mock 設定可能與實際渲染器行為不一致。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/workflow/nodes/template_transform/template_renderer.py:37` | render_template 可能回傳 None，導致後續 len() 拋出 TypeError | 0.95 |
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_transform_node.py:68` | 未處理 rendered 為 None 的情況 | 0.85 |
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_renderer.py:37` | render_template 回傳型別與 Protocol 不一致 | 0.80 |
| 🔸 | Minor | `api/tests/unit_tests/core/workflow/nodes/template_transform/template_transform_node_spec.py:449` | 測試中 mock 的 render_template 回傳值與實際可能不符 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:37</code> render_template 可能回傳 None，導致後續 len() 拋出 TypeError</summary>

`CodeExecutorJinja2TemplateRenderer.render_template` 的型別標示為回傳 `str`，但實作中若 `result.get("result")` 為 `None`，則直接回傳 `None`。呼叫端 `TemplateTransformNode._run` 在取得 `rendered` 後立即執行 `len(rendered)`，若 `rendered` 為 `None` 將拋出 `TypeError: object of type 'NoneType' has no len()`，且此例外未被捕捉，導致節點執行失敗。

**失敗情境**：當模板渲染結果為空（例如模板僅包含註解或空白控制）時，`execute_workflow_code_template` 可能回傳 `{"result": None}`，此時 `rendered` 為 `None`，`len(rendered)` 拋出例外。

**建議修法**：在 `render_template` 中明確檢查 `rendered is None` 並拋出 `TemplateRenderError`，或將回傳型別改為 `str | None` 並在呼叫端處理 `None` 情況。

**判斷依據**：diff 中 `template_renderer.py` 第 36-39 行：`rendered = result.get("result")`，若 `result` 中沒有 `"result"` 鍵或值為 `None`，則 `rendered` 為 `None`，函式直接回傳 `None`。而 `template_transform_node.py` 第 68 行：`if len(rendered) > MAX_TEMPLATE_TRANSFORM_OUTPUT_LENGTH:` 對 `rendered` 呼叫 `len()`，若為 `None` 則拋出 `TypeError`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_transform_node.py:68</code> 未處理 rendered 為 None 的情況</summary>

`_run` 方法中，`rendered = self._template_renderer.render_template(...)` 後直接呼叫 `len(rendered)`，但 `render_template` 可能回傳 `None`（見 `template_renderer.py` 的實作）。若渲染結果為 `None`，此處將拋出 `TypeError`，且未被 `except TemplateRenderError` 捕捉，導致節點執行失敗。

**建議修法**：在呼叫 `len` 前檢查 `rendered is not None`，或修改 `render_template` 使其在結果為 `None` 時拋出 `TemplateRenderError`。

**判斷依據**：diff 中 `template_transform_node.py` 第 68-69 行，直接對 `rendered` 呼叫 `len()`，而 `render_template` 可能回傳 `None`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:37</code> render_template 回傳型別與 Protocol 不一致</summary>

`Jinja2TemplateRenderer` Protocol 定義 `render_template` 回傳 `str`，但 `CodeExecutorJinja2TemplateRenderer` 的實作可能回傳 `None`（如上述）。這違反了 Protocol 的契約，可能導致靜態型別檢查錯誤，且呼叫端若未處理 `None` 將有 runtime 風險。

**建議修法**：在 `render_template` 中確保回傳值為 `str`，若 `result.get("result")` 為 `None` 則拋出 `TemplateRenderError`，或將 Protocol 的回傳型別改為 `str | None` 並在呼叫端處理。

**判斷依據**：diff 中 `template_renderer.py` 第 36-39 行，函式可能回傳 `None`，但 Protocol 定義回傳 `str`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/core/workflow/nodes/template_transform/template_transform_node_spec.py:449</code> 測試中 mock 的 render_template 回傳值與實際可能不符</summary>

多個測試案例中，`mock_execute.return_value` 被設定為字串（例如 `"Active"`），但實際的 `CodeExecutorJinja2TemplateRenderer.render_template` 可能回傳 `None` 或非字串型別。這些測試僅驗證了成功路徑，未涵蓋渲染結果為 `None` 或型別錯誤的情況，可能掩蓋了上述 blocker 問題。

**建議修法**：新增測試案例，模擬 `render_template` 回傳 `None` 或非字串，驗證節點能正確處理並回傳失敗狀態。

**判斷依據**：diff 中測試檔案第 430 行附近，多處 `mock_execute.return_value` 設定為字串，但未測試 `None` 或型別錯誤的情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16928 (cache hit 16896) ｜ completion tokens 1626 ｜ PR #3</sub>