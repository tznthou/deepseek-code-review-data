<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 conversation variable 的持久化從 VariableAssignerNode 移到 GraphEngineLayer，並引入 ConversationVariablePersistenceLayer。主要風險在於 ConversationVariableUpdaterImpl 的 session 管理不當，可能導致連線洩漏；此外，layer 在處理多個變數時會多次 flush，可能造成效能問題。整體架構方向合理，但需修正資源管理與錯誤處理。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:18` | Session 未關閉導致連線洩漏 | 0.95 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | 每個變數更新後都 flush，可能造成效能問題 | 0.80 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | 未處理 ConversationVariableNotFoundError | 0.75 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:43` | selector 長度檢查可能不足 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:18</code> Session 未關閉導致連線洩漏</summary>

`ConversationVariableUpdaterImpl.update` 中建立 `Session(db.engine)` 後，在方法結束時未呼叫 `session.close()`。若 `session.commit()` 拋出例外，session 不會被關閉，可能導致資料庫連線池耗盡。建議使用 `with Session(db.engine) as session:` 或 `try/finally` 確保 session 關閉。

**判斷依據**：diff 中新增的 `session = Session(db.engine)` 後沒有對應的 `session.close()`，且 `session.commit()` 可能拋出例外。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> 每個變數更新後都 flush，可能造成效能問題</summary>

在 `for item in updated_variables` 迴圈內，每次呼叫 `self._conversation_variable_updater.update(...)` 後都呼叫 `self._conversation_variable_updater.flush()`。如果一次更新多個 conversation variables，會造成多次資料庫寫入。建議將 flush 移到迴圈外，或讓 updater 內部累積變更後一次 flush。

**判斷依據**：diff 中 `flush()` 位於 for 迴圈內，且 `updated_variables` 可能包含多個元素。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> 未處理 ConversationVariableNotFoundError</summary>

`self._conversation_variable_updater.update(...)` 可能拋出 `ConversationVariableNotFoundError`，但此處未捕捉。若變數在資料庫中不存在，整個 workflow 會失敗。需確認此行為是否符合預期，或應記錄錯誤並繼續。

**判斷依據**：diff 中呼叫 `update` 未包在 try/except 中，且 `ConversationVariableUpdaterImpl.update` 會拋出 `ConversationVariableNotFoundError`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:43</code> selector 長度檢查可能不足</summary>

程式碼檢查 `len(selector) < 2` 後才使用 `selector[0]`，但未驗證 `selector[0]` 是否為 `CONVERSATION_VARIABLE_NODE_ID`。若 selector 長度大於等於 2 但第一個元素不是 conversation variable node id，後續 `variable_pool.get(selector)` 可能回傳非 conversation variable，但程式碼仍會嘗試更新。建議增加明確檢查。

**判斷依據**：diff 中僅檢查 `selector[0] != CONVERSATION_VARIABLE_NODE_ID`，但未檢查 selector 的其餘部分是否合法。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15831 (cache hit 1536) ｜ completion tokens 1087 ｜ PR #4</sub>