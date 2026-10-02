<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 conversation variable 的持久化從 VariableAssignerNode 內部移出，改由新的 GraphEngineLayer（ConversationVariablePersistenceLayer）在節點成功後統一處理。整體架構方向合理，但實作中有幾個關鍵問題：ConversationVariableUpdaterImpl.update 的 session 未正確關閉，可能造成連線洩漏；ConversationVariablePersistenceLayer 在迴圈內呼叫 flush，且 flush 為空實作，可能導致效能問題或誤解；此外，移除 v1 節點中 conversation_id 不存在時的錯誤處理，可能導致靜默失敗。建議優先修正 session 管理與 flush 邏輯。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:18` | Session 未關閉，可能造成連線洩漏 | 0.95 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | 在迴圈內呼叫 flush，且 flush 為空實作 | 0.85 |
| ⚠️ | Major | `api/core/workflow/nodes/variable_assigner/v1/node.py:11` | 移除 conversation_id 不存在時的錯誤處理，可能導致靜默失敗 | 0.80 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:40` | selector 長度檢查可能不完整 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:18</code> Session 未關閉，可能造成連線洩漏</summary>

`update` 方法中建立了 `Session(db.engine)`，但在方法結束時沒有呼叫 `session.close()`。若 `session.commit()` 拋出例外，session 不會被關閉；即使正常執行，session 也會殘留直到被垃圾回收，可能導致資料庫連線池耗盡。建議使用 `with Session(db.engine) as session:` 或 `try/finally` 確保關閉。

**判斷依據**：diff 中新增的 `session = Session(db.engine)` 後沒有對應的 `session.close()` 或 context manager。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> 在迴圈內呼叫 flush，且 flush 為空實作</summary>

`on_event` 中對每個 updated variable 呼叫 `update` 後立即呼叫 `flush`。但 `ConversationVariableUpdaterImpl.flush` 目前是空實作（pass），因此 flush 沒有實際效果。若未來 flush 實作批次提交，此處在迴圈內呼叫會導致多次提交，降低效能。建議將 flush 移到迴圈外，或明確 flush 的語義。

**判斷依據**：diff 中 `flush()` 在 for 迴圈內，且 `ConversationVariableUpdaterImpl.flush` 的實作為 `pass`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/workflow/nodes/variable_assigner/v1/node.py:11</code> 移除 conversation_id 不存在時的錯誤處理，可能導致靜默失敗</summary>

原本 v1 節點在 `conversation_id` 不存在時會拋出 `VariableOperatorNodeError`，現在此檢查被移除。若 `conversation_id` 缺失，新的 persistence layer 會直接跳過更新（因為 `conversation_id is None` 時 return），導致 conversation variable 未持久化且無任何錯誤提示。建議在 layer 中記錄警告或保留錯誤處理。

**判斷依據**：diff 中刪除了上述檢查，而新 layer 中僅有 `if conversation_id is None: return`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:40</code> selector 長度檢查可能不完整</summary>

程式碼檢查 `len(selector) < 2` 後才使用 `selector[0]`，但未驗證 selector 的第二個元素是否為有效的 variable name。若 selector 為 `[CONVERSATION_VARIABLE_NODE_ID]`（長度 1），會被跳過；但若 selector 為 `[CONVERSATION_VARIABLE_NODE_ID, None]` 或類似，可能導致後續 `variable_pool.get` 行為異常。建議增加更嚴格的驗證。

**判斷依據**：diff 中僅檢查長度，未檢查元素型別或值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10804 (cache hit 1536) ｜ completion tokens 1250 ｜ PR #4</sub>