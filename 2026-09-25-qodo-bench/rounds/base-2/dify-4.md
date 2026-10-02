<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 conversation variable 的持久化從 variable assigner 節點內部移至 GraphEngineLayer，並將 updater 移至 services 層。整體架構更清晰，但存在幾個關鍵問題：ConversationVariableUpdaterImpl.update 中 session 未正確關閉，可能導致連線洩漏；ConversationVariablePersistenceLayer 在迴圈內呼叫 flush，可能造成不必要的資料庫往返；此外，移除 conversation_id 檢查後，在非 debugger 情境下若 conversation_id 缺失，將靜默跳過持久化，可能導致資料不一致。建議優先修復 session 管理與 flush 位置。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:18` | Session 未正確關閉，可能導致連線洩漏 | 0.95 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | 在迴圈內呼叫 flush，可能造成不必要的資料庫往返 | 0.85 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:34` | conversation_id 缺失時靜默跳過，可能導致資料不一致 | 0.80 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:40` | selector 長度檢查可能不完整 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:18</code> Session 未正確關閉，可能導致連線洩漏</summary>

在 `ConversationVariableUpdaterImpl.update` 中，`session = Session(db.engine)` 建立的 session 在方法結束後沒有被關閉。若 `session.commit()` 拋出例外，session 不會被釋放，可能導致資料庫連線池耗盡。建議使用 `with Session(db.engine) as session:` 或 `try/finally` 確保 session 關閉。

**判斷依據**：diff 中 `session = Session(db.engine)` 之後沒有 `session.close()` 或 `with` 語句。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> 在迴圈內呼叫 flush，可能造成不必要的資料庫往返</summary>

`self._conversation_variable_updater.flush()` 在 for 迴圈內被呼叫，若有多個 conversation variables 需要更新，會導致多次 flush。建議將 flush 移到迴圈外，在所有 update 完成後只呼叫一次。

**判斷依據**：diff 中 `flush()` 位於 for 迴圈內，且 `update` 方法內部已執行 commit。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:34</code> conversation_id 缺失時靜默跳過，可能導致資料不一致</summary>

在 `ConversationVariablePersistenceLayer.on_event` 中，若 `conversation_id` 為 `None`，則直接 `return`，沒有記錄任何警告或錯誤。在非 debugger 情境下，這可能導致 conversation variable 更新被靜默丟棄，造成資料不一致。建議至少記錄 warning log，或考慮拋出例外。

**判斷依據**：diff 中 `if conversation_id is None: return` 沒有 log 或錯誤處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:40</code> selector 長度檢查可能不完整</summary>

`if len(selector) < 2:` 只檢查 selector 至少有兩個元素，但未驗證 selector[0] 是否為合法的 conversation variable node ID。若 selector[0] 不是 `CONVERSATION_VARIABLE_NODE_ID`，後續 `continue` 會跳過，但這可能掩蓋其他問題。建議增加更明確的驗證或 log。

**判斷依據**：diff 中僅檢查長度，未檢查 selector[0] 的合法性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10804 (cache hit 10752) ｜ completion tokens 1109 ｜ PR #4</sub>