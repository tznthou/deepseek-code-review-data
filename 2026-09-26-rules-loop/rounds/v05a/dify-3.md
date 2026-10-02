<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 TemplateTransformNode 的 Jinja2 渲染邏輯抽象為 Jinja2TemplateRenderer 介面，並提供 CodeExecutorJinja2TemplateRenderer 實作，同時在 NodeFactory 中注入 renderer。整體重構方向合理，但存在一個關鍵的型別錯誤：render_template 的回傳型別標示為 str，但實際可能回傳 None，導致後續 len() 呼叫在特定條件下拋出 TypeError。此外，測試檔案新增大量測試案例，但部分測試的 mock 設定與實際行為不符，可能掩蓋問題。建議先修正 render_template 的型別與 None 處理，再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/workflow/nodes/template_transform/template_renderer.py:37` | render_template 可能回傳 None，導致後續 len() 呼叫拋出 TypeError | 0.95 |
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_renderer.py:39` | render_template 回傳型別標示為 str，但可能回傳 None，違反型別安全 | 0.85 |
| ⚠️ | Major | `api/tests/unit_tests/core/workflow/nodes/template_transform/template_transform_node_spec.py:150` | 測試中 mock 的 render_template 回傳值與實際行為不符，可能掩蓋 None 處理問題 | 0.80 |
| ⚠️ | Major | `api/core/workflow/nodes/template_transform/template_transform_node.py:68` | 未處理 render_template 回傳 None 的情況，可能導致 TypeError | 0.80 |
| 🔸 | Minor | `api/core/workflow/nodes/template_transform/template_renderer.py:39` | render_template 回傳型別標示為 str，但可能回傳 None，違反型別安全 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:37</code> render_template 可能回傳 None，導致後續 len() 呼叫拋出 TypeError</summary>

在 `CodeExecutorJinja2TemplateRenderer.render_template` 中，`result.get("result")` 可能回傳 `None`。雖然有檢查 `rendered is not None`，但若 `rendered` 為 `None`，函式會直接回傳 `None`，而函式簽名標示回傳 `str`。呼叫端 `TemplateTransformNode._run` 會直接對回傳值呼叫 `len(rendered)`，若為 `None` 將拋出 `TypeError`，且此例外未被捕捉，導致節點執行失敗且錯誤訊息不明確。

**失敗情境**：當 CodeExecutor 回傳的 result 字典中缺少 "result" 鍵或該鍵值為 None 時，`render_template` 回傳 None，`_run` 中的 `len(rendered)` 拋出 TypeError。

**建議**：在 `render_template` 中，若 `rendered` 為 None，應拋出 `TemplateRenderError`，或將回傳型別改為 `str | None` 並在呼叫端處理 None 情況。

**判斷依據**：diff 中第 39 行 `return rendered`，而 `rendered` 可能為 None；呼叫端 `template_transform_node.py` 第 68 行 `if len(rendered) > MAX_TEMPLATE_TRANSFORM_OUTPUT_LENGTH:` 直接使用 len()。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:39</code> render_template 回傳型別標示為 str，但可能回傳 None，違反型別安全</summary>

函式 `render_template` 的簽名標示回傳 `str`，但實作中可能回傳 `None`（當 `result.get("result")` 為 None 時）。這違反了型別安全，可能導致靜態型別檢查工具（如 basedpyright）發出警告，且呼叫端若未處理 None 會造成執行時期錯誤。

**建議**：將回傳型別改為 `str | None`，並在呼叫端明確處理 None 情況，或確保函式在 None 時拋出例外。

**判斷依據**：diff 中第 39 行 `return rendered`，而 `rendered` 可能為 None；函式簽名標示回傳 `str`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/tests/unit_tests/core/workflow/nodes/template_transform/template_transform_node_spec.py:150</code> 測試中 mock 的 render_template 回傳值與實際行為不符，可能掩蓋 None 處理問題</summary>

在 `test_run_simple_template` 等測試中，mock 的 `render_template` 回傳值為字串，但實際 `CodeExecutorJinja2TemplateRenderer.render_template` 可能回傳 None。這使得測試無法涵蓋 None 回傳值的情況，導致潛在的 TypeError 未被發現。

**建議**：新增測試案例，模擬 `render_template` 回傳 None，驗證節點能正確處理並回傳失敗狀態。

**判斷依據**：diff 中第 130 行，測試 mock 回傳字串，未涵蓋 None 情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/template_transform/template_transform_node.py:68</code> 未處理 render_template 回傳 None 的情況，可能導致 TypeError</summary>

在 `_run` 方法中，直接對 `rendered` 呼叫 `len()`，但 `rendered` 可能為 None（若 renderer 回傳 None）。這會拋出 `TypeError`，且未被 `except TemplateRenderError` 捕捉，導致節點執行失敗且錯誤訊息不明確。

**建議**：在呼叫 `len()` 前檢查 `rendered` 是否為 None，或確保 renderer 在 None 時拋出 `TemplateRenderError`。

**判斷依據**：diff 中第 68 行，直接使用 len(rendered)，未檢查 None。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/nodes/template_transform/template_renderer.py:39</code> render_template 回傳型別標示為 str，但可能回傳 None，違反型別安全</summary>

函式 `render_template` 的簽名標示回傳 `str`，但實作中可能回傳 `None`。這違反了型別安全，可能導致靜態型別檢查工具發出警告。

**建議**：將回傳型別改為 `str | None`，並在呼叫端明確處理 None 情況。

**判斷依據**：diff 中第 39 行 `return rendered`，而 `rendered` 可能為 None。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16838 (cache hit 13440) ｜ completion tokens 1667 ｜ PR #3</sub>