<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 conversation variable 的持久化從 VariableAssignerNode 移至新的 GraphEngineLayer，並將 updater 移至 services 層。主要風險在於 ConversationVariableUpdaterImpl 的 session 管理不當（未使用 context manager、未關閉 session），可能導致連線洩漏；此外，layer 中 flush 在迴圈內被呼叫，可能造成不必要的資料庫往返。整體架構方向合理，但需先修正資源管理問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:18` | [R06] SQLAlchemy session 未使用 context manager 且未關閉 | 0.95 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | flush 在迴圈內被呼叫，可能造成多次資料庫往返 | 0.80 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:40` | selector 長度檢查可能不完整 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:18</code> [R06] SQLAlchemy session 未使用 context manager 且未關閉</summary>

`Session(db.engine)` 建立的 session 沒有使用 `with` 語句，且在方法結束後沒有呼叫 `session.close()`。這會導致資料庫連線無法釋放，可能造成連線池耗盡。請改用 `with Session(db.engine) as session:` 模式，或確保在 `finally` 中關閉 session。

**判斷依據**：diff 中新增的 `session = Session(db.engine)` 沒有對應的 `session.close()`，且未使用 context manager。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> flush 在迴圈內被呼叫，可能造成多次資料庫往返</summary>

`self._conversation_variable_updater.flush()` 在 for 迴圈內每次迭代都被呼叫。如果有多個 conversation variables 需要更新，這會導致多次資料庫 commit。建議將 flush 移到迴圈外，在所有變數更新完成後只呼叫一次。

**判斷依據**：diff 中 `flush()` 位於 for 迴圈內，且 `update` 方法本身已執行 `session.commit()`，因此 flush 可能只是空操作，但若未來 flush 有實際邏輯，此處會造成效能問題。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:40</code> selector 長度檢查可能不完整</summary>

程式碼檢查 `len(selector) < 2` 後才使用 `selector[0]`，但未驗證 selector 的內容是否為預期的格式。如果 selector 的第一個元素不是字串，比較 `selector[0] != CONVERSATION_VARIABLE_NODE_ID` 可能不會如預期運作。建議增加型別檢查或使用更嚴格的驗證。

**判斷依據**：diff 中僅檢查長度，未檢查元素型別。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13483 (cache hit 1536) ｜ completion tokens 876 ｜ PR #4</sub>