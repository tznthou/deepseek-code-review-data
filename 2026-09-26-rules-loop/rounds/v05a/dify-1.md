<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正了 v1 Variable Assigner 節點在串流回應時，可能於對話變數更新前就輸出結果的問題。主要變更包括：新增 blocks_variable_output 方法、調整 _run 中 result_input_value 的計算，並加入對應的測試與 fixture。整體風險低，但需注意 blocks_variable_output 的型別標註與既有程式碼風格不一致，以及測試中對事件順序的假設可能過於嚴格。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `api/core/workflow/nodes/variable_assigner/v1/node.py:36` | [R04] 使用舊式 typing 語法 Set 與 Tuple | 0.80 |
| 🔸 | Minor | `api/tests/unit_tests/core/workflow/graph_engine/test_streaming_conversation_variables.py:75` | 測試假設所有 chunk 事件的值都等於 input_query | 0.60 |

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/nodes/variable_assigner/v1/node.py:36</code> [R04] 使用舊式 typing 語法 Set 與 Tuple</summary>

此方法使用了 `Set[Tuple[str, ...]]`，但專案規範 R04 要求使用 Python 3.12+ 的現代型別語法，例如 `set[tuple[str, ...]]`。建議改用內建泛型以符合規範。

**判斷依據**：diff 中新增的這一行使用了 `Set` 和 `Tuple`，而檔案頂部已從 `typing` 匯入 `Set, Tuple`，但根據 R04，應使用 `set` 和 `tuple`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/core/workflow/graph_engine/test_streaming_conversation_variables.py:75</code> 測試假設所有 chunk 事件的值都等於 input_query</summary>

此測試斷言所有 `conv_var_chunk_events` 的 `chunk` 都等於 `input_query`。但若串流過程中有多個 chunk，且其中包含部分內容或後續更新，此斷言可能過於嚴格。建議改為驗證最終值或至少包含 input_query。

**判斷依據**：diff 中新增的測試程式碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7287 (cache hit 3840) ｜ completion tokens 574 ｜ PR #1</sub>