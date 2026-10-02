<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正了 v1 Variable Assigner 節點在串流回應時，可能於對話變數更新前就輸出結果的問題。主要變更包括：新增 blocks_variable_output 方法以判斷節點是否阻擋特定變數輸出、調整 _run 方法中 result_input_value 的計算邏輯，並新增對應的測試。整體風險低，但需注意 blocks_variable_output 的型別標註與既有程式碼風格不一致，以及測試中對事件型別的斷言可能過於脆弱。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `api/core/workflow/nodes/variable_assigner/v1/node.py:36` | [R04] 型別標註使用舊式 typing 語法 | 0.80 |
| 🔸 | Minor | `api/tests/unit_tests/core/workflow/graph_engine/test_streaming_conversation_variables.py:75` | 測試斷言可能過於脆弱 | 0.60 |

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/nodes/variable_assigner/v1/node.py:36</code> [R04] 型別標註使用舊式 typing 語法</summary>

新增的 `blocks_variable_output` 方法使用了 `Set[Tuple[str, ...]]`，但專案規範 R04 要求使用 Python 3.12+ 的現代型別語法（`set[tuple[str, ...]]`）。建議改用現代語法以符合規範。

**判斷依據**：diff 中新增的方法簽名使用了 `Set` 和 `Tuple`，而檔案開頭已從 `typing` 匯入 `Set, Tuple`，但根據 R04 應使用內建泛型。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/core/workflow/graph_engine/test_streaming_conversation_variables.py:75</code> 測試斷言可能過於脆弱</summary>

測試中斷言所有 `NodeRunStreamChunkEvent` 的 `chunk` 都等於 `input_query`，但若未來串流事件包含其他內容（如中繼資料），此斷言將失敗。建議改為檢查事件是否存在且其值符合預期，而非要求所有事件完全相同。

**判斷依據**：diff 中新增的測試斷言使用 `all(event.chunk == input_query ...)`，對事件內容過於嚴格。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7287 (cache hit 7168) ｜ completion tokens 598 ｜ PR #1</sub>