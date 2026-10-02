<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 conversation variable 的持久化從 VariableAssignerNode 內部移至 GraphEngineLayer，並將 updater 移至 services 層。主要風險在於 ConversationVariableUpdaterImpl.update 中 SQLAlchemy session 未使用 context manager，可能導致連線洩漏；且查詢未包含 tenant_id，在多租戶環境下可能造成跨租戶資料存取。此外，新 layer 的 on_event 中 flush 在迴圈內呼叫，可能造成不必要的資料庫往返。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:18` | [R06] SQLAlchemy session 未使用 context manager | 0.95 |
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:15` | [R07] 查詢未包含 tenant_id 條件 | 0.90 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | flush 在迴圈內呼叫，可能造成多次資料庫往返 | 0.80 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:40` | selector 長度檢查後仍可能索引越界 | 0.70 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:45` | 變數池中找不到變數時僅記錄警告，可能導致資料不一致 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:18</code> [R06] SQLAlchemy session 未使用 context manager</summary>

在 `ConversationVariableUpdaterImpl.update` 中，`Session(db.engine)` 被直接賦值給 `session`，沒有使用 `with` 語句。如果 `session.scalar` 或後續操作拋出例外，session 不會被正確關閉，可能導致資料庫連線洩漏。建議改為 `with Session(db.engine) as session:`。

**判斷依據**：diff 中 `session = Session(db.engine)` 沒有 `with` 包覆，且後續有 `session.commit()`，若 `scalar` 拋出例外則 session 不會關閉。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:15</code> [R07] 查詢未包含 tenant_id 條件</summary>

`select(ConversationVariable).where(ConversationVariable.id == variable.id, ConversationVariable.conversation_id == conversation_id)` 未包含 tenant_id 條件。在多租戶架構下，若 conversation_id 在不同租戶間重複，可能更新到其他租戶的變數。建議加入 tenant_id 條件，例如從 conversation 或 variable 中取得 tenant_id 並加入 where。

**判斷依據**：diff 中查詢條件僅有 id 和 conversation_id，未見 tenant_id。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> flush 在迴圈內呼叫，可能造成多次資料庫往返</summary>

在 `for item in updated_variables:` 迴圈內，每次 `update` 後都呼叫 `flush()`。雖然目前 `flush()` 是空操作，但若未來實作實際 flush，將導致每個變數更新都觸發一次資料庫寫入，影響效能。建議將 `flush()` 移到迴圈外，在所有更新完成後呼叫一次。

**判斷依據**：diff 中 `flush()` 位於 for 迴圈內，且 `update` 每次都會執行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:40</code> selector 長度檢查後仍可能索引越界</summary>

程式碼檢查 `len(selector) < 2` 後才使用 `selector[0]`，但後續 `self.graph_runtime_state.variable_pool.get(selector)` 可能接受任意長度的 selector，若 selector 長度為 1 且未通過前面的檢查，則不會執行到這裡。但若 selector 長度為 0，前面的檢查會攔截。此處邏輯正確，但可考慮更嚴謹的型別檢查。

**判斷依據**：diff 中先檢查長度再取 selector[0]，但後續 get 可能接受任意長度。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:45</code> 變數池中找不到變數時僅記錄警告，可能導致資料不一致</summary>

當 `variable_pool.get(selector)` 回傳非 `Variable` 時，程式碼記錄警告並跳過，但該變數可能已在 assigner 中更新，導致記憶體與資料庫不一致。建議考慮拋出例外或採取其他補救措施。

**判斷依據**：diff 中僅記錄警告並 continue，未處理不一致。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12043 (cache hit 9984) ｜ completion tokens 1381 ｜ PR #4</sub>