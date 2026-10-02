<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 旨在將 automation.action.* 事件連結回 automation.triggered/resolved 事件，以改善可追溯性。主要變更包括在 TriggeredAction 中新增 automation_triggered_event_id 欄位、在 actions.py 中建構相關資源、以及在 triggers.py 中傳遞該 ID。整體方向合理，但存在一個關鍵缺陷：在 actions.py 的 fail() 方法中，action.triggered 事件的 related 參數誤用了 self._resulting_related_resources，導致該事件缺少 triggering-event 與 automation-triggered-event 連結，破壞了因果鏈。此外，測試覆蓋不足，未驗證 fail() 中 action.triggered 事件的相關資源，也未涵蓋 automation_triggered_event_id 為 None 時的 fail() 情境。建議修正該缺陷並補強測試。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/actions.py:202` | fail() 中 action.triggered 事件使用了錯誤的 related 資源 | 0.95 |
| ⚠️ | Major | `src/prefect/server/events/actions.py:177` | fail() 中 action.triggered 事件缺少 triggering-event 連結 | 0.80 |
| 🔸 | Minor | `src/prefect/server/events/schemas/automations.py:776` | field_validator 可能無法正確取得 triggering_event | 0.70 |
| 🔸 | Minor | `tests/events/server/actions/test_actions_service.py:306` | 測試未涵蓋 fail() 中 action.triggered 事件的 related 資源 | 0.70 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:445` | primary_state_change_event 可能為 None 但未處理 | 0.60 |
| 🔸 | Minor | `tests/events/server/actions/test_actions_service.py:505` | 缺少 automation_triggered_event_id 為 None 時的 fail() 測試 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/actions.py:202</code> fail() 中 action.triggered 事件使用了錯誤的 related 資源</summary>

在 `fail()` 方法中，`prefect.automation.action.triggered` 事件的 `related` 參數被設為 `self._resulting_related_resources`，而不是包含 triggering-event 和 automation-triggered-event 的 `related_resources`。這會導致該事件缺少與觸發事件及 automation 狀態變更事件的連結，破壞了此 PR 旨在建立的因果鏈。

**失敗情境**：當 action 失敗時，`action.triggered` 事件將不包含 `triggering-event` 或 `automation-triggered-event` 相關資源，使用者無法從該事件追溯到觸發來源。

**建議修法**：將 `related=self._resulting_related_resources` 改為 `related=related_resources`。

**判斷依據**：diff 中 `fail()` 方法內，`await events.emit(Event(... event="prefect.automation.action.triggered" ... related=self._resulting_related_resources ...))`，而 `related_resources` 已正確建構但未被使用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/actions.py:177</code> fail() 中 action.triggered 事件缺少 triggering-event 連結</summary>

即使修正了上述 blocker，`fail()` 中的 `action.triggered` 事件仍可能缺少 `triggering-event` 連結。目前 `related_resources` 僅在 `triggered_action.triggering_event` 存在時才加入該連結，但 `triggering_event` 可能為 None（例如 proactive trigger 且無最近事件）。這會導致事件缺少關鍵上下文。

**失敗情境**：當 `triggering_event` 為 None 時，`action.triggered` 事件將沒有 `triggering-event` 相關資源，使用者無法追溯觸發來源。

**建議修法**：確認此情境下是否應包含 `triggering-event` 連結，或至少確保 `automation-triggered-event` 連結存在。

**判斷依據**：diff 中 `related_resources` 的建構邏輯：僅在 `triggered_action.triggering_event` 為真時才加入 `triggering-event` 相關資源。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/schemas/automations.py:776</code> field_validator 可能無法正確取得 triggering_event</summary>

`validate_automation_triggered_event_id` 使用 `info.data.get("triggering_event")` 來檢查 `triggering_event` 是否存在。在 Pydantic v2 中，`info.data` 包含已驗證的欄位，但若 `triggering_event` 在 `automation_triggered_event_id` 之後才被驗證，則可能尚未存在於 `info.data` 中，導致驗證失敗或誤判。

**失敗情境**：若欄位驗證順序導致 `triggering_event` 尚未被處理，則即使 `triggering_event` 實際存在，驗證器也可能拋出錯誤。

**建議修法**：改用 `info.data.get("triggering_event")` 或使用 `model_fields_set` 來檢查欄位是否已設定。

**判斷依據**：diff 中新增的 validator 依賴 `info.data`，但未考慮欄位驗證順序。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/events/server/actions/test_actions_service.py:306</code> 測試未涵蓋 fail() 中 action.triggered 事件的 related 資源</summary>

新增的測試 `test_failure_events_include_automation_triggered_event_link` 驗證了 `action.failed` 事件的相關資源，但未驗證 `action.triggered` 事件的相關資源。由於 `fail()` 中 `action.triggered` 事件的 `related` 參數存在 blocker，此測試未能捕捉該缺陷。

**建議修法**：在測試中增加對 `triggered_event.related` 的斷言，確保包含 `automation-triggered-event` 和 `triggering-event`。

**判斷依據**：測試中僅檢查了 `failed_event` 的相關資源，未檢查 `triggered_event`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:445</code> primary_state_change_event 可能為 None 但未處理</summary>

`primary_state_change_event` 可能為 None（當 `state_change_events` 中沒有 Triggered 或 Resolved 狀態時），但後續直接使用 `primary_state_change_event.id`，可能導致 AttributeError。

**失敗情境**：若 `firing.trigger_states` 不包含 Triggered 或 Resolved（例如僅有其他狀態），則 `primary_state_change_event` 為 None，存取 `.id` 會拋出例外。

**建議修法**：在使用前檢查 `primary_state_change_event` 是否為 None，或確保 `state_change_events` 至少包含一個狀態。

**判斷依據**：diff 中 `primary_state_change_event` 的取得方式，以及後續直接使用 `.id`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/events/server/actions/test_actions_service.py:505</code> 缺少 automation_triggered_event_id 為 None 時的 fail() 測試</summary>

現有測試 `test_action_events_without_automation_triggered_event_id` 僅涵蓋成功情境，未涵蓋失敗情境。當 `automation_triggered_event_id` 為 None 且 action 失敗時，`action.triggered` 和 `action.failed` 事件的相關資源應僅包含 `triggering-event`，但此行為未經測試。

**建議修法**：新增一個測試，模擬 action 失敗且 `automation_triggered_event_id` 為 None，驗證相關資源。

**判斷依據**：測試僅涵蓋成功路徑，未涵蓋失敗路徑。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 19582 (cache hit 1536) ｜ completion tokens 1952 ｜ PR #2</sub>