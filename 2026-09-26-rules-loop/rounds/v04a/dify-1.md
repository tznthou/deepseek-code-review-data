<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正了 v1 Variable Assigner 節點在串流回應時，未等待對話變數更新即輸出結果的問題。主要變更包括：新增 blocks_variable_output 方法、調整 NodeRunResult 的輸入值處理，以及新增對應的測試。整體風險低，但需注意 blocks_variable_output 的型別提示與既有程式碼一致性，以及測試中對事件順序的假設。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `api/core/workflow/nodes/variable_assigner/v1/node.py:36` | 型別提示使用 Set 而非 set，與既有程式碼風格不一致 | 0.60 |
| 🔸 | Minor | `api/tests/unit_tests/core/workflow/graph_engine/test_streaming_conversation_variables.py:75` | 測試假設事件順序，可能導致不穩定 | 0.50 |

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/nodes/variable_assigner/v1/node.py:36</code> 型別提示使用 Set 而非 set，與既有程式碼風格不一致</summary>

此方法使用 `Set[Tuple[str, ...]]` 作為參數型別，但 Python 3.9+ 建議使用內建泛型 `set[tuple[str, ...]]`。檢查同檔案其他方法，如 `_run` 的參數型別，均使用內建泛型（例如 `Mapping`、`Sequence`）。為保持一致性，建議改為 `set[tuple[str, ...]]`。

**判斷依據**：diff 中新增的型別提示使用 `Set` 和 `Tuple`，而檔案頂部已從 `typing` 匯入 `Set, Tuple`，但同檔案其他方法（如 `_run`）使用 `Mapping`、`Sequence` 等內建泛型。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/core/workflow/graph_engine/test_streaming_conversation_variables.py:75</code> 測試假設事件順序，可能導致不穩定</summary>

測試中透過 `result.events` 收集所有 `NodeRunStreamChunkEvent` 並檢查其 `chunk` 值，但未驗證事件順序。若未來事件順序改變，此測試可能誤報。建議明確檢查事件順序或改為驗證最終狀態。

**判斷依據**：測試僅檢查所有 chunk 事件的值是否等於 input_query，未檢查事件順序。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5928 (cache hit 3840) ｜ completion tokens 617 ｜ PR #1</sub>