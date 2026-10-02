<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 v1 Variable Assigner 節點在串流回應時，未等待對話變數更新即輸出結果的問題。主要變更在 `node.py` 新增 `blocks_variable_output` 方法，並調整 `_run` 中 `inputs` 的 `value` 欄位，使其在 `CLEAR` 模式下輸出更新後的值。整體風險低，但需注意 `blocks_variable_output` 的型別提示與實際使用的一致性，以及測試中對事件順序的假設。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `api/core/workflow/nodes/variable_assigner/v1/node.py:36` | 型別提示 `Set[Tuple[str, ...]]` 可能與實際傳入型別不符 | 0.60 |
| 🔸 | Minor | `api/tests/unit_tests/core/workflow/graph_engine/test_streaming_conversation_variables.py:75` | 測試假設所有 chunk 事件的值都等於輸入查詢，可能過於嚴格 | 0.50 |

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/nodes/variable_assigner/v1/node.py:36</code> 型別提示 `Set[Tuple[str, ...]]` 可能與實際傳入型別不符</summary>

`blocks_variable_output` 的參數 `variable_selectors` 標註為 `Set[Tuple[str, ...]]`，但呼叫端可能傳入其他可迭代型別（如 list）。若型別不符，可能導致執行期錯誤或型別檢查失敗。建議確認呼叫端型別，或放寬為 `Iterable[Tuple[str, ...]]`。

**判斷依據**：diff 中新增的方法簽名使用了 `Set[Tuple[str, ...]]`，但未提供呼叫端程式碼，無法確認實際傳入型別。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/core/workflow/graph_engine/test_streaming_conversation_variables.py:75</code> 測試假設所有 chunk 事件的值都等於輸入查詢，可能過於嚴格</summary>

測試中 `assert all(event.chunk == input_query for event in conv_var_chunk_events)` 假設每個 chunk 事件的值都完全等於輸入查詢。若串流過程中有分段或格式變化，此斷言可能失敗。建議改為檢查最終累積值或至少包含輸入查詢。

**判斷依據**：diff 中新增的測試斷言要求所有 chunk 事件的值都等於 `input_query`，但未考慮串流分段的可能性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4689 (cache hit 4608) ｜ completion tokens 625 ｜ PR #1</sub>