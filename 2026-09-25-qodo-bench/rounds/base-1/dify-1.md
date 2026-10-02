<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正了 v1 Variable Assigner 節點在串流回應時，可能於對話變數更新前就輸出結果的問題。新增 `blocks_variable_output` 方法讓圖引擎能正確等待變數更新，並調整 `_run` 中 `result_input_value` 的計算以反映寫入模式。整體變更範圍小且聚焦，但需注意 `blocks_variable_output` 的型別提示與實際使用的一致性，以及測試中對事件順序的假設。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `api/core/workflow/nodes/variable_assigner/v1/node.py:36` | 型別提示 `Set[Tuple[str, ...]]` 可能與實際傳入型別不符 | 0.60 |
| 🔸 | Minor | `api/tests/unit_tests/core/workflow/graph_engine/test_streaming_conversation_variables.py:75` | 測試假設所有 chunk 事件的值都等於輸入值，可能過於嚴格 | 0.50 |

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/nodes/variable_assigner/v1/node.py:36</code> 型別提示 `Set[Tuple[str, ...]]` 可能與實際傳入型別不符</summary>

`blocks_variable_output` 的參數 `variable_selectors` 標註為 `Set[Tuple[str, ...]]`，但呼叫端可能傳入其他可迭代型別（如 list）。若型別不符，可能導致執行時期錯誤或型別檢查警告。建議確認呼叫端傳入的型別，或放寬為 `Iterable[Tuple[str, ...]]`。

**判斷依據**：diff 中新增的方法簽名使用了 `Set[Tuple[str, ...]]`，但未提供呼叫端程式碼，無法確認實際傳入型別。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/core/workflow/graph_engine/test_streaming_conversation_variables.py:75</code> 測試假設所有 chunk 事件的值都等於輸入值，可能過於嚴格</summary>

測試中 `assert all(event.chunk == input_query for event in conv_var_chunk_events)` 假設每個 chunk 事件的值都完全等於輸入字串。若串流實作將輸入拆分成多個 chunk（例如逐字元），此斷言將失敗。建議改為驗證串接後的值等於輸入值，或放寬為檢查事件存在且值非空。

**判斷依據**：diff 中新增的測試斷言要求每個 chunk 事件的值都等於 `input_query`，但未考慮串流可能分段。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4689 (cache hit 1536) ｜ completion tokens 638 ｜ PR #1</sub>