<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 conversation variable 的持久化從 VariableAssignerNode 內部移至 GraphEngineLayer，並將 updater 移至 services 層。主要風險在於 ConversationVariableUpdaterImpl.update 未使用 context manager 管理 SQLAlchemy session，可能導致連線洩漏；且查詢未依 tenant_id 過濾，在多租戶環境下可能造成資料外洩。此外，persistence layer 在迴圈內對每個變數呼叫 flush，可能造成不必要的資料庫往返。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:18` | [R06] SQLAlchemy session 未使用 context manager | 0.95 |
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:15` | [R07] 查詢未依 tenant_id 過濾 | 0.90 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | 在迴圈內呼叫 flush 可能造成效能問題 | 0.80 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | 未處理 updater 拋出的例外 | 0.75 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:40` | selector 長度檢查可能不完整 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:18</code> [R06] SQLAlchemy session 未使用 context manager</summary>

`Session(db.engine)` 建立的 session 沒有使用 `with` 語句，也未呼叫 `close()`。若 `session.scalar()` 或 `session.commit()` 拋出例外，session 不會被關閉，可能導致連線洩漏。建議改為 `with Session(db.engine) as session:` 並在區塊內完成查詢與提交。

**判斷依據**：diff 中新增的 `update` 方法直接建立 session 而未使用 context manager，違反 R06。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:15</code> [R07] 查詢未依 tenant_id 過濾</summary>

查詢 `ConversationVariable` 時僅以 `id` 和 `conversation_id` 過濾，未包含 `tenant_id`。在多租戶環境下，若 conversation_id 在不同租戶間重複，可能更新到其他租戶的變數。建議加入 tenant_id 條件，並從變數或上下文中取得 tenant_id。

**判斷依據**：diff 中新增的查詢未包含 tenant_id 過濾，違反 R07。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> 在迴圈內呼叫 flush 可能造成效能問題</summary>

`flush()` 在每個變數更新後立即呼叫，若一次更新多個變數，會產生多次資料庫往返。建議將 `flush()` 移至迴圈外，或讓 updater 自行管理批次提交。

**判斷依據**：diff 中 `flush()` 位於 for 迴圈內，且 `update` 本身已執行 commit，flush 可能為空操作，但若實作有緩衝，則會造成多次提交。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> 未處理 updater 拋出的例外</summary>

`update` 可能拋出 `ConversationVariableNotFoundError` 或其他資料庫例外，但此處未捕捉或記錄，可能導致整個 graph 執行失敗。建議捕捉例外並記錄錯誤，或根據業務需求決定是否中斷。

**判斷依據**：diff 中呼叫 `update` 未包在 try-except 中，且 updater 實作會拋出例外。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:40</code> selector 長度檢查可能不完整</summary>

僅檢查 `len(selector) < 2`，但後續使用 `selector[0]` 和 `selector[1]`，若 selector 長度為 2 但元素為 None 或空字串，可能導致非預期行為。建議驗證 selector 的內容。

**判斷依據**：diff 中僅檢查長度，未驗證元素有效性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13482 (cache hit 13440) ｜ completion tokens 1232 ｜ PR #4</sub>