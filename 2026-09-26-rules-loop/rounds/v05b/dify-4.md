<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 conversation variable 的持久化從 variable assigner node 移至 GraphEngineLayer，並將 updater 移至 services 層。主要風險在於 ConversationVariableUpdaterImpl.update 未使用 context manager 管理 SQLAlchemy session，可能導致連線洩漏；且查詢未依 tenant_id 過濾，在多租戶環境下可能造成資料外洩。此外，新 layer 在處理多個變數時會多次 flush，效能較差。建議先修正 session 管理與 tenant 隔離問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:18` | [R06] SQLAlchemy session 未使用 context manager | 0.95 |
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:15` | [R07] 查詢未依 tenant_id 過濾 | 0.90 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | 多個變數更新時多次 flush，效能不佳 | 0.80 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:40` | selector 長度檢查可能不足 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:18</code> [R06] SQLAlchemy session 未使用 context manager</summary>

`ConversationVariableUpdaterImpl.update` 中直接建立 `Session(db.engine)` 並在方法結束前呼叫 `session.commit()`，但未使用 `with` 語句或 `try/finally` 確保 session 關閉。若 `session.scalar(stmt)` 或 `session.commit()` 拋出例外，session 將不會被關閉，造成連線洩漏。建議改為 `with Session(db.engine) as session:` 模式。

**判斷依據**：diff 中新增的 `session = Session(db.engine)` 與 `session.commit()` 沒有對應的 `session.close()` 或 context manager。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:15</code> [R07] 查詢未依 tenant_id 過濾</summary>

`update` 方法中的查詢僅以 `ConversationVariable.id` 和 `conversation_id` 過濾，未加入 `tenant_id` 條件。若 `conversation_id` 在不同 tenant 間可能重複，則可能更新到其他 tenant 的資料。建議在查詢中加入 tenant_id 條件，或確認 conversation_id 全域唯一。

**判斷依據**：diff 中查詢條件僅有 id 和 conversation_id，未見 tenant_id。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> 多個變數更新時多次 flush，效能不佳</summary>

在 `on_event` 中，對每個 conversation variable 呼叫 `update` 後立即呼叫 `flush`。若一次 assigner 更新多個變數，將產生多次資料庫 commit。建議將 `flush` 移到迴圈外，僅在所有變數更新後呼叫一次。

**判斷依據**：diff 中 `flush()` 位於 for 迴圈內。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:40</code> selector 長度檢查可能不足</summary>

程式碼檢查 `len(selector) < 2` 後才使用 `selector[0]`，但未驗證 `selector[0]` 是否為預期的 conversation variable node ID。若 selector 格式異常，可能導致後續邏輯錯誤。建議增加更明確的驗證。

**判斷依據**：diff 中僅檢查長度，未檢查 selector[0] 的型別或內容。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13402 (cache hit 13312) ｜ completion tokens 1089 ｜ PR #4</sub>