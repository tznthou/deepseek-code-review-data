<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 conversation variable 的持久化從 variable assigner node 移至 GraphEngineLayer，並重構相關 factory 與 updater。主要風險在於 ConversationVariableUpdaterImpl.update 的 session 管理違反 R06，可能造成連線洩漏；此外 layer 中 flush 在迴圈內呼叫可能導致多次提交，以及缺少 tenant_id 過濾（R07）等問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:18` | [R06] SQLAlchemy session 未使用 context manager | 0.95 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | flush 在迴圈內呼叫，可能造成多次提交 | 0.85 |
| ⚠️ | Major | `api/services/conversation_variable_updater.py:15` | [R07] 查詢未包含 tenant_id 過濾 | 0.80 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:39` | selector 長度檢查不足，可能導致 IndexError | 0.75 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:45` | 變數池查詢可能回傳 None，未處理 | 0.70 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:52` | update 可能拋出例外，導致 layer 中斷 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:18</code> [R06] SQLAlchemy session 未使用 context manager</summary>

`Session(db.engine)` 未使用 `with` 語句，若 `session.scalar` 或後續操作拋出例外，session 不會被關閉，可能導致連線洩漏。建議改為 `with Session(db.engine) as session:` 並在區塊內完成查詢與 commit。

**判斷依據**：diff 中新增的 `session = Session(db.engine)` 沒有對應的 `with` 或 `session.close()`，違反 R06。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> flush 在迴圈內呼叫，可能造成多次提交</summary>

`self._conversation_variable_updater.flush()` 在 for 迴圈內每次 update 後呼叫，若 updater 實作有實際 flush 行為（例如 commit），會導致多次資料庫提交，降低效能且可能造成部分更新。建議將 flush 移到迴圈外，在所有 update 完成後呼叫一次。

**判斷依據**：diff 中 `flush()` 位於 for 迴圈內，且 `update` 可能累積變更，應批次處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/conversation_variable_updater.py:15</code> [R07] 查詢未包含 tenant_id 過濾</summary>

`select(ConversationVariable).where(ConversationVariable.id == variable.id, ConversationVariable.conversation_id == conversation_id)` 未加入 tenant_id 條件，可能導致跨租戶資料存取。若 `variable.id` 或 `conversation_id` 可被操縱，可能讀取或修改其他租戶的變數。建議加入 tenant_id 過濾。

**判斷依據**：diff 中查詢條件僅有 id 和 conversation_id，未見 tenant_id，違反 R07。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:39</code> selector 長度檢查不足，可能導致 IndexError</summary>

`if len(selector) < 2:` 僅檢查長度至少為 2，但後續 `selector[0]` 和 `selector[1]` 的使用假設 selector 至少有兩個元素。若 selector 為空或只有一個元素，此檢查會攔截，但若 selector 為 None 則會拋出 TypeError。建議增加 `if not selector or len(selector) < 2:` 或明確處理 None。

**判斷依據**：diff 中 `item.selector` 可能為 None，直接呼叫 `len()` 會拋出例外。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:45</code> 變數池查詢可能回傳 None，未處理</summary>

`variable = self.graph_runtime_state.variable_pool.get(selector)` 可能回傳 None，但後續 `isinstance(variable, Variable)` 檢查會攔截 None，因此不會造成錯誤。但若 `variable_pool.get` 拋出例外（例如 selector 格式錯誤），則未處理。建議確認 `get` 的契約，必要時捕捉例外。

**判斷依據**：diff 中未對 `get` 可能拋出的例外進行處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> update 可能拋出例外，導致 layer 中斷</summary>

`self._conversation_variable_updater.update(...)` 可能拋出 `ConversationVariableNotFoundError` 或其他例外，若未捕捉，整個 graph 執行可能失敗。建議考慮是否應記錄錯誤並繼續處理其他變數，或讓例外向上傳播。

**判斷依據**：diff 中未對 update 呼叫進行例外處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13472 (cache hit 9984) ｜ completion tokens 1490 ｜ PR #4</sub>