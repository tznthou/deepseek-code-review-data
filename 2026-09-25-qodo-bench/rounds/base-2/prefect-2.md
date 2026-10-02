<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 automation action 事件新增 `automation_triggered_event_id` 欄位，並在 action 事件中建立與 automation.triggered/resolved 事件的關聯資源，以利追蹤。主要風險在於 `actions.py` 中 `related_resources` 的建構順序與 `related` 參數的指派，可能導致事件關聯不正確或重複。此外，`triggers.py` 中 `primary_state_change_event` 的選擇邏輯在同時觸發 Triggered 與 Resolved 時可能選錯事件，且 `state_change_events` 可能缺少對應鍵。建議優先修正 `actions.py` 中的關聯資源指派邏輯。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/prefect/server/events/actions.py:202` | action.triggered 事件使用了錯誤的 related 參數 | 0.80 |
| ⚠️ | Major | `src/prefect/server/events/actions.py:213` | action.failed 事件使用了錯誤的 related 參數 | 0.80 |
| ⚠️ | Major | `src/prefect/server/events/actions.py:290` | action.triggered 事件使用了錯誤的 related 參數 | 0.80 |
| ⚠️ | Major | `src/prefect/server/events/actions.py:301` | action.executed 事件使用了錯誤的 related 參數 | 0.80 |
| ⚠️ | Major | `src/prefect/server/events/triggers.py:442` | primary_state_change_event 選擇邏輯可能選錯事件 | 0.70 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:442` | state_change_events 可能缺少對應鍵 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/actions.py:202</code> action.triggered 事件使用了錯誤的 related 參數</summary>

在 `fail` 方法中，`action.triggered` 事件的 `related` 參數被指派為 `self._resulting_related_resources`，而非建構好的 `related_resources`。這會導致該事件缺少 `automation-triggered-event` 和 `triggering-event` 關聯資源，違反此 PR 的目標。

失敗情境：當 action 失敗時，`action.triggered` 事件將無法連結回 automation.triggered 事件，使用者無法追蹤觸發來源。

建議：將 `related` 改為 `related_resources`。

**判斷依據**：diff 中第 202 行（新增側）顯示 `related=self._resulting_related_resources`，而上方已建構 `related_resources` 並加入 automation-triggered-event 與 triggering-event。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/actions.py:213</code> action.failed 事件使用了錯誤的 related 參數</summary>

在 `fail` 方法中，`action.failed` 事件的 `related` 參數被指派為 `related_resources`，但此變數是從 `self._resulting_related_resources` 複製後再加入 automation-triggered-event 與 triggering-event。然而，`self._resulting_related_resources` 可能已包含 triggering-event（若先前已加入），導致重複。

失敗情境：當 action 失敗時，`action.failed` 事件可能包含重複的 triggering-event 關聯資源，造成資料不一致。

建議：確認 `self._resulting_related_resources` 的內容，避免重複加入 triggering-event。

**判斷依據**：diff 中第 213 行（新增側）顯示 `related=related_resources`，而 `related_resources` 是基於 `self._resulting_related_resources` 建構，可能已包含 triggering-event。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/actions.py:290</code> action.triggered 事件使用了錯誤的 related 參數</summary>

在 `succeed` 方法中，`action.triggered` 事件的 `related` 參數被指派為 `related_resources`，但此變數是從 `self._resulting_related_resources` 複製後再加入 automation-triggered-event 與 triggering-event。然而，`self._resulting_related_resources` 可能已包含 triggering-event（若先前已加入），導致重複。

失敗情境：當 action 成功時，`action.triggered` 事件可能包含重複的 triggering-event 關聯資源。

建議：確認 `self._resulting_related_resources` 的內容，避免重複加入 triggering-event。

**判斷依據**：diff 中第 290 行（新增側）顯示 `related=related_resources`，而 `related_resources` 是基於 `self._resulting_related_resources` 建構，可能已包含 triggering-event。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/actions.py:301</code> action.executed 事件使用了錯誤的 related 參數</summary>

在 `succeed` 方法中，`action.executed` 事件的 `related` 參數被指派為 `related_resources`，但此變數是從 `self._resulting_related_resources` 複製後再加入 automation-triggered-event 與 triggering-event。然而，`self._resulting_related_resources` 可能已包含 triggering-event（若先前已加入），導致重複。

失敗情境：當 action 成功時，`action.executed` 事件可能包含重複的 triggering-event 關聯資源。

建議：確認 `self._resulting_related_resources` 的內容，避免重複加入 triggering-event。

**判斷依據**：diff 中第 301 行（新增側）顯示 `related=related_resources`，而 `related_resources` 是基於 `self._resulting_related_resources` 建構，可能已包含 triggering-event。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/triggers.py:442</code> primary_state_change_event 選擇邏輯可能選錯事件</summary>

當 automation 同時觸發 Triggered 和 Resolved 狀態時，`primary_state_change_event` 會優先選擇 Triggered 事件。但若 Triggered 事件不存在（例如僅 Resolved），則會選擇 Resolved 事件。然而，若兩者皆存在，但實際觸發 action 的是 Resolved 事件（例如 `actions_on_resolve`），則 action 事件會錯誤地連結到 Triggered 事件。

失敗情境：當 automation 同時觸發 Triggered 和 Resolved，且 action 是定義在 `actions_on_resolve` 中時，action 事件會連結到錯誤的 automation.triggered 事件。

建議：根據 action 的來源（`actions`、`actions_on_trigger`、`actions_on_resolve`）選擇對應的 state change event，而非統一使用 primary。

**判斷依據**：diff 中第 441-443 行（新增側）顯示優先選擇 Triggered，但未考慮 action 的來源。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:442</code> state_change_events 可能缺少對應鍵</summary>

在 `act` 函式中，`state_change_events` 是根據 `firing.trigger_states` 建立的字典。若 `firing.trigger_states` 不包含 `TriggerState.Triggered` 或 `TriggerState.Resolved`，則 `state_change_events.get(TriggerState.Triggered)` 或 `state_change_events.get(TriggerState.Resolved)` 可能回傳 `None`。雖然程式碼使用 `or` 來處理，但若兩者皆為 `None`，則 `primary_state_change_event_id` 會是 `None`，這可能導致後續 action 事件缺少 automation-triggered-event 關聯。

失敗情境：當 automation 觸發條件不包含 Triggered 或 Resolved 狀態時，action 事件將無法連結到 automation.triggered 事件。

建議：確認 `firing.trigger_states` 是否保證包含至少一個狀態，或明確處理兩者皆無的情況。

**判斷依據**：diff 中第 441-443 行（新增側）顯示使用 `or` 處理，但未檢查兩者皆為 None 的情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10578 (cache hit 10496) ｜ completion tokens 2055 ｜ PR #2</sub>