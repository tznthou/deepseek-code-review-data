<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 conversation variable 的持久化從 variable assigner node 移至 graph engine layer，並重構相關程式碼。主要風險在於 ConversationVariableUpdaterImpl.update 的 session 管理不當（未使用 context manager，可能造成連線洩漏），以及 layer 中 flush 呼叫位置可能導致多次資料庫寫入。此外，移除 conversation_id 檢查可能使 debugger 情境下的行為改變。建議優先修正 session 管理與 flush 邏輯。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:18` | [R06] SQLAlchemy session 未使用 context manager，可能造成連線洩漏 | 0.95 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | flush 在迴圈內呼叫，可能造成多次資料庫寫入 | 0.85 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:34` | 移除 conversation_id 檢查可能導致 debugger 情境下行為不一致 | 0.80 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:40` | selector 長度檢查可能遺漏合法變數 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:18</code> [R06] SQLAlchemy session 未使用 context manager，可能造成連線洩漏</summary>

`ConversationVariableUpdaterImpl.update` 中直接建立 `Session(db.engine)` 而未使用 `with` 語句，若後續操作拋出例外，session 將不會被關閉，導致資料庫連線洩漏。建議改為 `with Session(db.engine) as session:` 並在區塊內完成查詢與 commit。

**判斷依據**：diff 中新增的 `session = Session(db.engine)` 未搭配 context manager，且後續有 `raise` 可能中斷執行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> flush 在迴圈內呼叫，可能造成多次資料庫寫入</summary>

`self._conversation_variable_updater.flush()` 在 for 迴圈內每次 update 後立即呼叫，若有多個 conversation variables 被更新，將產生多次 flush。建議將 flush 移到迴圈外，在所有 update 完成後呼叫一次。

**判斷依據**：diff 中 `flush()` 位於 for 迴圈內，且 `update` 本身已執行 commit。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:34</code> 移除 conversation_id 檢查可能導致 debugger 情境下行為不一致</summary>

原 v2 node 在 `invoke_from != InvokeFrom.DEBUGGER` 且 conversation_id 缺失時會拋出 `ConversationIDNotFoundError`。新 layer 僅在 conversation_id 為 None 時直接 return，不再區分 debugger 情境，可能使非 debugger 情境下錯誤被靜默忽略。建議保留對 invoke_from 的判斷或記錄警告。

**判斷依據**：diff 中移除了原本的 `if self.invoke_from != InvokeFrom.DEBUGGER: raise ConversationIDNotFoundError` 邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:40</code> selector 長度檢查可能遺漏合法變數</summary>

`if len(selector) < 2` 假設 conversation variable 的 selector 至少為兩段，但若未來支援更複雜的 selector 結構，此檢查可能誤擋。目前程式碼中 conversation variable 的 selector 固定為 `[CONVERSATION_VARIABLE_NODE_ID, name]`，因此影響有限。

**判斷依據**：diff 中新增的 selector 長度檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13402 (cache hit 9984) ｜ completion tokens 1066 ｜ PR #4</sub>