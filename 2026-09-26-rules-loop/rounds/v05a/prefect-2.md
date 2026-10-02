<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 automation action 事件新增 automation.triggered/resolved 事件的關聯資源，並更新相關測試與文件。主要風險在於 `actions.py` 中 `fail()` 方法內 `action.triggered` 事件的 `related` 欄位被改為 `self._resulting_related_resources`，可能遺漏本次新增的關聯資源；此外 `triggers.py` 中 `primary_state_change_event_id` 的選取邏輯在同時存在 Triggered 與 Resolved 事件時可能選錯事件，導致關聯錯誤。建議優先修正這兩個問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/actions.py:202` | action.triggered 事件遺漏 automation-triggered-event 關聯資源 | 0.95 |
| ⚠️ | Major | `src/prefect/server/events/triggers.py:442` | primary_state_change_event 選取邏輯可能選錯事件 | 0.80 |
| 🔸 | Minor | `src/prefect/server/events/schemas/automations.py:772` | field_validator 使用 info.data 可能無法取得其他欄位值 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/actions.py:202</code> action.triggered 事件遺漏 automation-triggered-event 關聯資源</summary>

在 `fail()` 方法中，`action.triggered` 事件的 `related` 欄位被改為 `self._resulting_related_resources`，但此列表不包含本次新增的 `automation-triggered-event` 關聯資源。這會導致當 action 失敗時，`action.triggered` 事件無法連結回對應的 `automation.triggered` 事件，違反了 PR 的目標。

**失敗情境**：當 `triggered_action.automation_triggered_event_id` 有值且 action 執行失敗時，產生的 `action.triggered` 事件將缺少 `automation-triggered-event` 關聯資源，使用者無法從該事件追溯到 automation 狀態變更事件。

**建議修法**：將 `related` 改回 `related_resources`，該變數已包含 `automation-triggered-event` 關聯資源。

**判斷依據**：diff 中第 202 行將原本的 `related=related_resources` 改為 `related=self._resulting_related_resources`，而 `related_resources` 是基於 `self._resulting_related_resources` 並額外加入 `automation-triggered-event` 的列表。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/triggers.py:442</code> primary_state_change_event 選取邏輯可能選錯事件</summary>

當 automation 同時觸發 Triggered 和 Resolved 狀態時，`primary_state_change_event` 會優先選擇 Triggered 事件。然而，若 action 是針對 Resolved 狀態（例如 `actions_on_resolve`），則關聯的 `automation_triggered_event_id` 應指向 Resolved 事件，而非 Triggered 事件。目前的邏輯會導致所有 action 都關聯到 Triggered 事件，即使該 action 是由 Resolved 觸發。

**失敗情境**：一個 automation 同時定義了 `actions_on_trigger` 和 `actions_on_resolve`，且某次 firing 同時包含 Triggered 和 Resolved 狀態。此時，`actions_on_resolve` 中的 action 會錯誤地關聯到 Triggered 事件，而非 Resolved 事件。

**建議修法**：根據 action 的來源（`actions`、`actions_on_trigger`、`actions_on_resolve`）分別設定對應的 `automation_triggered_event_id`，而不是統一使用 `primary_state_change_event_id`。

**判斷依據**：diff 中新增的 `primary_state_change_event` 選取邏輯，以及後續將 `primary_state_change_event_id` 應用於所有 `source_actions` 的程式碼。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/schemas/automations.py:772</code> field_validator 使用 info.data 可能無法取得其他欄位值</summary>

在 Pydantic v2 中，`field_validator` 的 `info.data` 僅包含已驗證的欄位，若 `triggering_event` 在模型中的順序晚於 `automation_triggered_event_id`，則 `info.data.get("triggering_event")` 可能為 `None`，導致驗證錯誤。建議改用 `model_validator` 進行跨欄位驗證。

**失敗情境**：若 `TriggeredAction` 模型的欄位順序使得 `automation_triggered_event_id` 在 `triggering_event` 之前被驗證，則即使 `triggering_event` 有值，驗證器仍可能因 `info.data` 中尚無該欄位而拋出錯誤。

**建議修法**：使用 `@model_validator(mode='after')` 進行跨欄位驗證，或確保欄位順序正確。

**判斷依據**：diff 中新增的 `field_validator` 使用 `info.data.get("triggering_event")`，但未考慮欄位驗證順序。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12027 (cache hit 9728) ｜ completion tokens 1367 ｜ PR #2</sub>