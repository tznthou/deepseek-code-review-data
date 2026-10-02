<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 conversation variable 的持久化從 variable assigner node 移至新的 GraphEngineLayer，並將 updater 移至 services 層。主要風險在於 ConversationVariableUpdaterImpl.update 未使用 context manager 管理 SQLAlchemy session，可能造成連線洩漏；且查詢未依 tenant_id 過濾，在多租戶環境下可能導致資料外洩。此外，layer 中 flush 在迴圈內呼叫，可能造成不必要的資料庫往返。建議優先修正 session 管理與 tenant 隔離問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:18` | [R06] SQLAlchemy session 未使用 context manager，可能造成連線洩漏 | 0.95 |
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:15` | [R07] 查詢未依 tenant_id 過濾，可能造成跨租戶資料存取 | 0.90 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | flush 在迴圈內呼叫，可能造成不必要的資料庫往返 | 0.80 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:40` | selector 長度檢查可能不完整 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:18</code> [R06] SQLAlchemy session 未使用 context manager，可能造成連線洩漏</summary>

`ConversationVariableUpdaterImpl.update` 中直接建立 `Session(db.engine)` 並在方法結束時未關閉 session。若 `session.scalar` 或後續操作拋出例外，session 不會被關閉，導致資料庫連線洩漏。建議改用 `with Session(db.engine) as session:` 模式。

**判斷依據**：diff 中新增的 `session = Session(db.engine)` 未使用 context manager，且方法內無 `session.close()` 或 `finally` 清理。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:15</code> [R07] 查詢未依 tenant_id 過濾，可能造成跨租戶資料存取</summary>

`update` 方法中的查詢僅以 `ConversationVariable.id` 和 `conversation_id` 過濾，未加入 `tenant_id` 條件。若 `conversation_id` 在不同租戶間不唯一，攻擊者可能透過猜測 ID 修改其他租戶的變數。建議加入 tenant_id 條件，並從變數或上下文中取得 tenant_id。

**判斷依據**：diff 中查詢條件僅包含 id 和 conversation_id，未包含 tenant_id。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> flush 在迴圈內呼叫，可能造成不必要的資料庫往返</summary>

`on_event` 中對每個 updated variable 呼叫 `update` 後立即呼叫 `flush`。若一次事件包含多個變數，會產生多次資料庫寫入。建議將 `flush` 移至迴圈外，僅在所有變數更新後呼叫一次。

**判斷依據**：diff 中 `flush` 位於 for 迴圈內，且 `update` 本身已執行 commit。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:40</code> selector 長度檢查可能不完整</summary>

程式碼檢查 `len(selector) < 2` 後才使用 `selector[0]`，但未驗證 selector 的格式是否正確（例如是否為字串列表）。若 selector 包含非字串元素，可能導致後續比較或查詢異常。建議增加型別驗證或使用更嚴格的檢查。

**判斷依據**：diff 中僅檢查長度，未檢查元素型別。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13492 (cache hit 9984) ｜ completion tokens 1095 ｜ PR #4</sub>