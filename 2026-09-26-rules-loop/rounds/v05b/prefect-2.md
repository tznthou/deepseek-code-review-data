<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 為 automation action 事件加入與 automation.triggered/resolved 事件的關聯，並更新文件與測試。主要風險在於 `actions.py` 中 `fail()` 方法內 `action.triggered` 事件的 `related` 欄位被改為 `self._resulting_related_resources`，可能遺漏 `triggering-event` 與 `automation-triggered-event` 關聯，造成 traceability 中斷。建議優先修正此處，並確認 `automation_triggered_event_id` 的驗證邏輯與既有測試相容。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/actions.py:202` | action.triggered 事件遺漏 triggering-event 與 automation-triggered-event 關聯 | 0.95 |
| ⚠️ | Major | `src/prefect/server/events/schemas/automations.py:774` | automation_triggered_event_id 驗證器可能無法正確取得 triggering_event | 0.80 |
| ⚠️ | Major | `src/prefect/server/events/triggers.py:442` | primary_state_change_event 選擇邏輯可能導致錯誤關聯 | 0.75 |
| 🔸 | Minor | `src/prefect/server/events/actions.py:177` | automation_triggered_event_id 可能為 None 時仍建立 RelatedResource | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/actions.py:202</code> action.triggered 事件遺漏 triggering-event 與 automation-triggered-event 關聯</summary>

在 `fail()` 方法中，`action.triggered` 事件的 `related` 欄位被改為 `self._resulting_related_resources`，而不是包含 `triggering-event` 與 `automation-triggered-event` 的 `related_resources`。這會導致當 action 失敗時，`action.triggered` 事件無法連結回原始的觸發事件與 automation 狀態變更事件，破壞 traceability。

**失敗情境**：當 automation 觸發且 action 執行失敗時，使用者查詢 `action.triggered` 事件將看不到 `triggering-event` 與 `automation-triggered-event` 關聯，無法追溯觸發來源。

**建議修法**：將該行改回 `related=related_resources`，與 `succeed()` 方法保持一致。

**判斷依據**：diff 中第 202 行（NEW）將原本的 `related=related_resources` 改為 `related=self._resulting_related_resources`，而 `related_resources` 已包含 `triggering-event` 與 `automation-triggered-event`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/schemas/automations.py:774</code> automation_triggered_event_id 驗證器可能無法正確取得 triggering_event</summary>

使用 `@field_validator` 驗證 `automation_triggered_event_id` 時，透過 `info.data.get("triggering_event")` 檢查 `triggering_event` 是否存在。但 Pydantic 的欄位驗證順序不保證 `triggering_event` 已先被驗證並放入 `info.data`，可能導致驗證器無法正確判斷，或在不同 Pydantic 版本中行為不一致。

**失敗情境**：當 `triggering_event` 欄位在 `automation_triggered_event_id` 之後才被驗證時，`info.data` 中可能沒有 `triggering_event`，導致即使提供了 `triggering_event` 仍會拋出驗證錯誤。

**建議修法**：改用 `@model_validator(mode="after")` 進行跨欄位驗證，或使用 `info.data.get("triggering_event")` 前先確認欄位順序。

**判斷依據**：diff 中新增的驗證器使用 `info.data.get("triggering_event")`，但未考慮欄位驗證順序。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/triggers.py:442</code> primary_state_change_event 選擇邏輯可能導致錯誤關聯</summary>

當 automation 同時觸發 `Triggered` 與 `Resolved` 狀態時，程式碼優先選擇 `Triggered` 事件作為 `primary_state_change_event`。但若 `Triggered` 事件不存在（例如僅觸發 `Resolved`），則會回退到 `Resolved`。然而，若兩者皆存在，但實際觸發 action 的是 `Resolved` 事件（例如 `actions_on_resolve`），則 action 事件仍會連結到 `Triggered` 事件，而非實際觸發的 `Resolved` 事件，造成關聯錯誤。

**失敗情境**：automation 同時定義了 `actions_on_trigger` 與 `actions_on_resolve`，且某次觸發僅滿足 `Resolved` 條件，但 `Triggered` 事件因某些原因仍存在（例如先前觸發過），則 `actions_on_resolve` 的 action 事件會錯誤地連結到 `Triggered` 事件。

**建議修法**：應根據每個 action 的觸發來源（`triggering_event`）來決定對應的 `automation_triggered_event_id`，而非統一使用 `primary_state_change_event_id`。

**判斷依據**：diff 中新增的邏輯優先選擇 `Triggered`，但未考慮 action 實際觸發來源。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/actions.py:177</code> automation_triggered_event_id 可能為 None 時仍建立 RelatedResource</summary>

在 `fail()` 與 `succeed()` 方法中，程式碼檢查 `if triggered_action.automation_triggered_event_id:` 後才建立 `RelatedResource`，但若該值為 `None`，則不會加入關聯。這可能導致在某些情況下（例如舊版 TriggeredAction 沒有此欄位）缺少 `automation-triggered-event` 關聯，但這是預期行為。然而，若未來需要強制此關聯，應考慮在 schema 層級設定為必填。

**失敗情境**：當 `automation_triggered_event_id` 為 `None` 時，action 事件不會包含 `automation-triggered-event` 關聯，可能影響 traceability。

**建議修法**：確認此欄位是否應為必填，或保留條件式加入。

**判斷依據**：diff 中條件式加入關聯，但未處理欄位為 None 的情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12027 (cache hit 11904) ｜ completion tokens 1777 ｜ PR #2</sub>