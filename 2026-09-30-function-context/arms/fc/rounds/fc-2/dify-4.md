<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 conversation variable 的持久化從 VariableAssignerNode 內部移至 GraphEngineLayer，並引入 ConversationVariablePersistenceLayer 與 ConversationVariableUpdaterImpl。主要風險在於 ConversationVariableUpdaterImpl.update 中 Session 未正確關閉，可能導致連線洩漏；此外，ConversationVariablePersistenceLayer 在處理多個更新時會多次 flush，且未處理 update 可能拋出的例外。整體架構方向合理，但需先修正資源管理問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:18` | Session 未關閉導致連線洩漏 | 0.95 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | 多個變數更新時重複 flush 且未處理例外 | 0.80 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:40` | selector 長度檢查可能不足 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:18</code> Session 未關閉導致連線洩漏</summary>

在 `ConversationVariableUpdaterImpl.update` 中，`session = Session(db.engine)` 建立的 Session 在方法結束後沒有呼叫 `close()`。若 `session.commit()` 拋出例外，Session 不會被關閉；即使正常執行，Session 也會殘留直到被垃圾回收，可能導致資料庫連線耗盡。建議使用 `with Session(db.engine) as session:` 或 `try/finally` 確保關閉。

**判斷依據**：diff 中新增的 `session = Session(db.engine)` 沒有對應的 `session.close()`，且方法內可能拋出例外。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> 多個變數更新時重複 flush 且未處理例外</summary>

在 `on_event` 中，對每個 updated variable 都呼叫 `self._conversation_variable_updater.update(...)` 後立即 `flush()`。若有多個變數，會造成多次資料庫 commit，降低效能且非原子性。此外，`update` 可能拋出例外（如 `ConversationVariableNotFoundError`），此處未捕捉，可能導致整個 workflow 失敗。建議收集所有更新後一次 flush，並考慮錯誤處理策略。

**判斷依據**：diff 中 for 迴圈內連續呼叫 update 和 flush，且無例外處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:40</code> selector 長度檢查可能不足</summary>

程式碼檢查 `len(selector) < 2` 後才使用 `selector[0]` 和 `selector[1]`，但未驗證 `selector[0]` 是否為 `CONVERSATION_VARIABLE_NODE_ID` 時就呼叫 `variable_pool.get(selector)`。若 selector 格式錯誤，可能導致非預期行為。建議先驗證 selector 結構再進行後續操作。

**判斷依據**：diff 中僅檢查長度，未檢查 selector 元素型別或內容。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15831 (cache hit 15744) ｜ completion tokens 936 ｜ PR #4</sub>