<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 conversation variable 的持久化從 variable assigner node 移至新的 GraphEngineLayer，並調整相關介面。主要風險在於 ConversationVariableUpdaterImpl.update 的 session 管理不當，可能導致連線洩漏；此外，persistence layer 中 flush 在迴圈內重複呼叫，可能造成效能問題。整體架構方向合理，但需修正上述問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/conversation_variable_updater.py:18` | Session 未正確關閉，可能導致連線洩漏 | 0.95 |
| ⚠️ | Major | `api/core/app/layers/conversation_variable_persist_layer.py:52` | flush 在迴圈內重複呼叫，可能造成效能問題 | 0.80 |
| 🔸 | Minor | `api/core/workflow/runtime/graph_runtime_state_protocol.py:12` | Protocol 方法簽章變更可能影響其他實作 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/conversation_variable_updater.py:18</code> Session 未正確關閉，可能導致連線洩漏</summary>

在 `update` 方法中，`session = Session(db.engine)` 建立的 session 在方法結束後未呼叫 `close()` 或使用 context manager。若 `session.commit()` 拋出例外，session 不會被關閉，可能導致資料庫連線洩漏。建議使用 `with Session(db.engine) as session:` 或確保在 `finally` 中關閉。

**判斷依據**：diff 中新增的 `update` 方法直接建立 session 而未關閉。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/app/layers/conversation_variable_persist_layer.py:52</code> flush 在迴圈內重複呼叫，可能造成效能問題</summary>

在 `on_event` 中，對每個 updated variable 都呼叫 `self._conversation_variable_updater.flush()`。若有多個變數需要更新，flush 會被呼叫多次。雖然目前 `flush` 是空操作，但若未來實作實際的 flush（例如批次寫入），此處可能導致不必要的 I/O。建議將 flush 移到迴圈外。

**判斷依據**：diff 中 `flush()` 位於 for 迴圈內。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/workflow/runtime/graph_runtime_state_protocol.py:12</code> Protocol 方法簽章變更可能影響其他實作</summary>

`ReadOnlyVariablePool.get` 的簽章從 `(node_id: str, variable_key: str)` 改為 `(selector: Sequence[str], /)`。這是一個 breaking change，所有實作此 Protocol 的類別都必須更新。雖然 diff 中已更新相關實作，但若有其他未包含在此 PR 的實作，將導致型別檢查或執行時錯誤。建議確認所有實作均已更新。

**判斷依據**：diff 中修改了 Protocol 的方法簽章。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10768 (cache hit 10752) ｜ completion tokens 816 ｜ PR #4</sub>