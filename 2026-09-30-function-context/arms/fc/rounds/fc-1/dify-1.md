<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 v1 Variable Assigner 節點在串流回應時，可能於 conversation variable 更新前就輸出結果的問題。主要變更包括：新增 blocks_variable_output 方法、調整 CLEAR 模式的輸入值處理，以及新增測試。整體風險低，但需注意 income_value 在 CLEAR 模式下的未定義問題，以及 blocks_variable_output 的型別與效能疑慮。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/workflow/nodes/variable_assigner/v1/node.py:93` | CLEAR 模式下 income_value 可能未定義 | 0.80 |
| 🔸 | Minor | `api/core/workflow/nodes/variable_assigner/v1/node.py:36` | blocks_variable_output 的型別與效能疑慮 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/variable_assigner/v1/node.py:93</code> CLEAR 模式下 income_value 可能未定義</summary>

在 WriteMode.CLEAR 分支中，程式碼未設定 income_value 變數。若 write_mode 為 CLEAR，則後續的 `result_input_value = income_value.to_object()` 會拋出 UnboundLocalError。建議在 CLEAR 分支中明確設定 income_value 或調整邏輯。

**判斷依據**：diff 中 CLEAR 分支未指派 income_value，但後續程式碼使用 income_value.to_object()。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/nodes/variable_assigner/v1/node.py:36</code> blocks_variable_output 的型別與效能疑慮</summary>

方法參數使用 Set[Tuple[str, ...]]，但呼叫端可能傳入其他可迭代型別。此外，每次呼叫都進行集合查找，若頻繁呼叫可能影響效能。建議確認呼叫端型別，並考慮使用 frozenset 或快取。

**判斷依據**：方法簽名使用 Set，但未見呼叫端，無法確認型別一致性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5240 (cache hit 1536) ｜ completion tokens 539 ｜ PR #1</sub>