<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正了 v1 Variable Assigner 節點在串流回應中，於對話變數更新前就輸出結果的問題。主要變更包括新增 blocks_variable_output 方法、調整 _run 的輸入值處理，並新增測試與 fixture。整體風險低，但需注意 blocks_variable_output 的型別相容性與測試斷言的正確性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `api/core/workflow/nodes/variable_assigner/v1/node.py:36` | blocks_variable_output 的參數型別可能與呼叫端不一致 | 0.60 |
| 🔸 | Minor | `api/tests/unit_tests/core/workflow/graph_engine/test_streaming_conversation_variables.py:75` | 測試斷言可能未涵蓋串流延遲的核心行為 | 0.50 |

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/nodes/variable_assigner/v1/node.py:36</code> blocks_variable_output 的參數型別可能與呼叫端不一致</summary>

新增的 `blocks_variable_output` 方法參數型別為 `Set[Tuple[str, ...]]`，但呼叫端可能傳入其他集合型別（如 `list` 或 `set` 的變體）。若型別不符，可能導致執行時期錯誤或型別檢查失敗。建議確認呼叫端的實際型別，或放寬為 `Collection[Tuple[str, ...]]`。

**判斷依據**：diff 中新增的方法簽名使用 `Set[Tuple[str, ...]]`，但未提供呼叫端程式碼，無法確認實際傳入型別。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/core/workflow/graph_engine/test_streaming_conversation_variables.py:75</code> 測試斷言可能未涵蓋串流延遲的核心行為</summary>

測試僅檢查最終輸出與 chunk 事件內容，未驗證串流事件是否在變數更新後才發出。若實作未正確延遲，此測試仍可能通過。建議增加事件順序的斷言，例如確認 assigner 節點完成後才出現 answer 的 chunk。

**判斷依據**：測試中僅檢查 chunk 值，未檢查事件順序或時間戳。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7377 (cache hit 3840) ｜ completion tokens 567 ｜ PR #1</sub>