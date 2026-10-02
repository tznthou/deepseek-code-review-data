<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — ✅ 未發現阻斷性問題

此 PR 修正了 v1 Variable Assigner 節點在串流回應時，可能於對話變數更新前就輸出結果的問題。主要變更包括新增 blocks_variable_output 方法、調整 NodeRunResult 的輸入值，以及新增測試。整體風險低，但需注意 blocks_variable_output 的型別提示與實作一致性，以及測試中對事件順序的假設。

_沒有 inline findings。_

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4653 (cache hit 4608) ｜ completion tokens 111 ｜ PR #1</sub>