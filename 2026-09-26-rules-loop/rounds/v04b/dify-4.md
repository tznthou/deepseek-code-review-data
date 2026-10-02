<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 conversation variable 的持久化從 VariableAssignerNode 移至新的 GraphEngineLayer，並將 updater 移至 services 層。主要風險在於 ConversationVariableUpdaterImpl.update 未使用 context manager 管理 SQLAlchemy session，可能導致連線洩漏；且查詢未依 tenant_id 隔離，在多租戶環境下可能存取到其他租戶的資料。此外，layer 中 flush 在迴圈內呼叫，可能造成不必要的資料庫往返。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:18` | [R06] SQLAlchemy session 未使用 context manager | 0.95 |
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:15` | [R07] 查詢未包含 tenant_id 隔離 | 0.90 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | flush 在迴圈內呼叫，可能造成效能問題 | 0.80 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:40` | selector 長度檢查可能不足 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:18</code> [R06] SQLAlchemy session 未使用 context manager</summary>

`Session(db.engine)` 建立的 session 未使用 `with` 語句，若 `session.commit()` 拋出例外，session 不會被關閉，可能導致連線洩漏。建議改為 `with Session(db.engine) as session:`。

**判斷依據**：diff 中新增的 `session = Session(db.engine)` 沒有對應的 `with` 或 `close()`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:15</code> [R07] 查詢未包含 tenant_id 隔離</summary>

查詢 `ConversationVariable` 時僅以 `id` 和 `conversation_id` 過濾，未包含 `tenant_id`。在多租戶環境中，若 conversation_id 不唯一，可能更新到其他租戶的變數。建議加入 tenant_id 條件。

**判斷依據**：diff 中的查詢條件缺少 tenant_id。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> flush 在迴圈內呼叫，可能造成效能問題</summary>

`self._conversation_variable_updater.flush()` 在 for 迴圈內每次更新後呼叫，若有多個變數，會產生多次資料庫往返。建議將 flush 移至迴圈外。

**判斷依據**：diff 中 flush 位於 for 迴圈內。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:40</code> selector 長度檢查可能不足</summary>

檢查 `len(selector) < 2` 後直接使用 `selector[0]` 和 `selector[1]`，但未驗證 selector 的內容是否合法。若 selector 包含非預期值，可能導致錯誤。

**判斷依據**：diff 中僅檢查長度，未驗證內容。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12043 (cache hit 12032) ｜ completion tokens 959 ｜ PR #4</sub>