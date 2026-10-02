<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 conversation variable 的持久化從 variable assigner node 移至 graph engine layer，並重構相關介面。主要風險在於 ConversationVariableUpdaterImpl.update 的 session 管理不當，可能導致連線洩漏；此外，layer 在處理多個變數時會多次 flush，且對 conversation_id 的取得方式與既有邏輯不同，可能造成行為差異。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:18` | Session 未關閉，可能導致連線洩漏 | 0.95 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | 多個變數時重複 flush，可能造成效能問題 | 0.85 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:34` | conversation_id 取得方式與既有邏輯不同，可能導致行為差異 | 0.80 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:40` | selector 長度檢查可能不完整 | 0.70 |
| 🔸 | Minor | `api/core/app/layers/conversation_variable_persist_layer.py:46` | 變數不存在時僅記錄警告，可能隱藏錯誤 | 0.70 |
| 🔸 | Minor | `api/core/workflow/runtime/graph_runtime_state_protocol.py:12` | Protocol 方法簽名變更可能影響其他實作 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:18</code> Session 未關閉，可能導致連線洩漏</summary>

`update` 方法中建立了 `Session(db.engine)`，但沒有呼叫 `close()` 或使用 context manager。每次呼叫都會建立新的 session，若未正確關閉，可能耗盡資料庫連線池。建議使用 `with Session(db.engine) as session:` 或確保在 finally 中關閉。

**判斷依據**：diff 中新增的 `session = Session(db.engine)` 沒有對應的 `session.close()` 或 context manager。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> 多個變數時重複 flush，可能造成效能問題</summary>

在 `for item in updated_variables:` 迴圈內，每次 `update` 後都呼叫 `flush()`。若有多個 conversation variable 被更新，會造成多次資料庫操作。建議將 `flush()` 移到迴圈外，或讓 `update` 累積變更後一次 flush。

**判斷依據**：diff 中 `flush()` 位於 for 迴圈內，且 `update` 本身已執行 commit。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:34</code> conversation_id 取得方式與既有邏輯不同，可能導致行為差異</summary>

此處使用 `self.graph_runtime_state.system_variable.conversation_id`，而舊邏輯是從 variable pool 取得 `["sys", "conversation_id"]`。若 system_variable 的 conversation_id 與 variable pool 中的不一致，可能造成更新到錯誤的 conversation。需確認兩者來源是否一致。

**判斷依據**：diff 中新增的 conversation_id 取得方式，與被移除的舊程式碼（`self.graph_runtime_state.variable_pool.get(["sys", "conversation_id"])`）不同。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:40</code> selector 長度檢查可能不完整</summary>

檢查 `len(selector) < 2` 後，只使用 `selector[0]` 判斷是否為 conversation variable。但後續 `variable_pool.get(selector)` 可能預期 selector 長度為 2，若長度大於 2 可能導致錯誤。建議確認 selector 的合法長度。

**判斷依據**：diff 中僅檢查長度下限，未檢查上限。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:46</code> 變數不存在時僅記錄警告，可能隱藏錯誤</summary>

當 `variable_pool.get(selector)` 回傳非 `Variable` 時，僅記錄警告並繼續。若預期該變數一定存在，此情況可能代表上游邏輯錯誤，建議考慮拋出例外或提高日誌等級。

**判斷依據**：diff 中新增的警告處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/runtime/graph_runtime_state_protocol.py:12</code> Protocol 方法簽名變更可能影響其他實作</summary>

`ReadOnlyVariablePool.get` 的簽名從 `(node_id, variable_key)` 改為 `(selector, /)`，這會影響所有實作此 Protocol 的類別。需確認所有實作都已更新，否則可能導致執行時錯誤。

**判斷依據**：diff 中修改了 Protocol 的方法簽名。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10804 (cache hit 10752) ｜ completion tokens 1426 ｜ PR #4</sub>