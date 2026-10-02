<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — ✅ 未發現阻斷性問題

此 PR 修正 v1 Variable Assigner 節點在串流回應中，於對話變數更新前就開始輸出的問題。主要變更包括：新增 blocks_variable_output 方法、修正 CLEAR 模式下的輸入值處理，並加入對應的測試。整體風險低，但需注意 blocks_variable_output 的型別提示與潛在的效能影響，以及測試中對事件順序的假設。

_沒有 inline findings。_

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5240 (cache hit 5120) ｜ completion tokens 117 ｜ PR #1</sub>