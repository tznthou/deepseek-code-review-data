<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 conversation variable 的持久化從 variable assigner node 移至新的 GraphEngineLayer，並將 updater 移至 services 層。主要風險在於 ConversationVariableUpdaterImpl.update 的 session 未使用 context manager，可能導致連線洩漏；且查詢未依 tenant_id 過濾，可能造成跨租戶資料存取。此外，新 layer 在 on_event 中對每個變數呼叫 flush，可能造成不必要的資料庫往返。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:18` | [R06] SQLAlchemy session 未使用 context manager | 0.95 |
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:15` | [R07] 查詢未依 tenant_id 過濾 | 0.90 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | 每個變數更新後都呼叫 flush，可能造成效能問題 | 0.80 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | 未處理 updater 可能拋出的例外 | 0.75 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:40` | selector 長度檢查可能不完整 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:18</code> [R06] SQLAlchemy session 未使用 context manager</summary>

在 `ConversationVariableUpdaterImpl.update` 中，`session = Session(db.engine)` 沒有使用 `with` 語句，且未在方法結束時關閉 session。若 `session.scalar` 或 `session.commit` 拋出例外，session 不會被關閉，可能導致連線洩漏。建議改為 `with Session(db.engine) as session:` 並在區塊內完成查詢與提交。

**判斷依據**：diff 中新增的 `session = Session(db.engine)` 未使用 context manager，且無 `session.close()`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:15</code> [R07] 查詢未依 tenant_id 過濾</summary>

`update` 方法中的查詢僅以 `ConversationVariable.id` 和 `conversation_id` 過濾，未包含 `tenant_id`。在多租戶環境中，若攻擊者知道其他租戶的 conversation variable id，可能跨租戶修改資料。建議在查詢中加入 `tenant_id` 條件，並從上下文取得當前租戶 ID。

**判斷依據**：diff 中查詢條件缺少 tenant_id。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> 每個變數更新後都呼叫 flush，可能造成效能問題</summary>

在 `on_event` 的迴圈中，每次 `update` 後都呼叫 `flush()`。若一次事件包含多個 conversation variables，會造成多次資料庫往返。建議在迴圈外只呼叫一次 `flush()`。

**判斷依據**：diff 中 `flush()` 位於 for 迴圈內。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> 未處理 updater 可能拋出的例外</summary>

`self._conversation_variable_updater.update` 可能拋出 `ConversationVariableNotFoundError` 或其他資料庫例外，但 `on_event` 未捕捉或記錄。這可能導致整個 graph 執行失敗，且沒有足夠的錯誤上下文。建議捕捉例外並記錄，或讓例外向上傳播並由框架處理。

**判斷依據**：diff 中呼叫 `update` 未包在 try/except 中。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:40</code> selector 長度檢查可能不完整</summary>

程式碼檢查 `len(selector) < 2` 後才使用 `selector[0]`，但未驗證 `selector[0]` 是否為預期的 conversation variable node ID。若 selector 格式錯誤，可能導致後續邏輯錯誤。建議增加更明確的驗證。

**判斷依據**：diff 中僅檢查長度，未驗證第一個元素。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13482 (cache hit 1920) ｜ completion tokens 1239 ｜ PR #4</sub>