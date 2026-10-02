<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — ✅ 未發現阻斷性問題

此 PR 修正了 v1 Variable Assigner 節點在串流回應時，可能於變數更新前就開始輸出的問題。主要變更包括：新增 `blocks_variable_output` 方法、調整 `_run` 中 `inputs` 的 `value` 欄位以反映寫入模式，並新增測試。整體風險低，但需注意 `blocks_variable_output` 的型別提示與實際使用的一致性，以及測試中對事件順序的假設。

_沒有 inline findings。_

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4653 (cache hit 1408) ｜ completion tokens 131 ｜ PR #1</sub>