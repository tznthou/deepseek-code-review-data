<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 conversation variable 的持久化從 VariableAssigner node 移至 GraphEngineLayer，並將 updater 移至 services 層。主要風險在於 ConversationVariableUpdaterImpl.update 的 session 管理違反 R06，可能造成連線洩漏；此外，persistence layer 在迴圈內呼叫 flush 可能造成不必要的資料庫往返。整體架構方向合理，但需先修正 session 管理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:18` | [R06] SQLAlchemy session 未使用 context manager | 0.95 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | 在迴圈內呼叫 flush 可能造成多次資料庫往返 | 0.80 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:40` | selector 長度檢查可能不完整 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:18</code> [R06] SQLAlchemy session 未使用 context manager</summary>

`Session(db.engine)` 沒有使用 `with` 語句，違反 R06。若 `session.scalar` 或後續操作拋出例外，session 不會被關閉，可能導致連線洩漏。建議改為 `with Session(db.engine) as session:`。

**判斷依據**：diff 中新增的 `session = Session(db.engine)` 沒有對應的 `with` 或 `session.close()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> 在迴圈內呼叫 flush 可能造成多次資料庫往返</summary>

`self._conversation_variable_updater.flush()` 在 for 迴圈內被呼叫，若有多個 conversation variables 需要更新，會造成多次 flush。建議將 flush 移到迴圈外，或確認 updater 的 flush 是 no-op（目前實作是 pass）。

**判斷依據**：diff 中 for 迴圈內連續呼叫 update 和 flush。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:40</code> selector 長度檢查可能不完整</summary>

`if len(selector) < 2` 只檢查長度，但未驗證 selector 的內容是否合法。若 selector 為 `[CONVERSATION_VARIABLE_NODE_ID, '']` 或包含空字串，可能導致後續查詢異常。建議增加更嚴格的驗證。

**判斷依據**：diff 中僅檢查長度，未檢查元素內容。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13472 (cache hit 13440) ｜ completion tokens 779 ｜ PR #4</sub>