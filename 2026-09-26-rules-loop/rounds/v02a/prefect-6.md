<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 `run_deployment` 改為非同步函式 `arun_deployment`，並以 `run_deployment = arun_deployment` 提供向後相容別名。主要風險在於移除 `@sync_compatible` 後，同步呼叫路徑可能失效，且 `run_deployment` 在同步環境中不再自動包裝。此外，`get_or_create_client` 的回傳值處理、`collect_task_run_inputs` 的 await 移除、以及 `deployment_id` 的使用方式都需要進一步確認。測試涵蓋了非同步與同步情境，但同步測試依賴 `_sync` 參數，可能掩蓋實際問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/deployments/flow_runs.py:241` | 移除 @sync_compatible 後，同步呼叫 run_deployment 將失敗 | 0.95 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:133` | client 可能為 None，但未處理 get_or_create_client 的回傳 | 0.80 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:149` | 移除 await 可能導致 collect_task_run_inputs 回傳未完成的 coroutine | 0.75 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:212` | 使用 deployment_id 而非 deployment.id 可能導致型別錯誤 | 0.70 |
| 🔸 | Minor | `tests/deployment/test_flow_runs.py:604` | 測試使用 _sync 參數可能掩蓋同步包裝問題 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/deployments/flow_runs.py:241</code> 移除 @sync_compatible 後，同步呼叫 run_deployment 將失敗</summary>

原本 `run_deployment` 使用 `@sync_compatible` 裝飾器，允許在同步環境中直接呼叫並自動執行非同步函式。此 PR 移除裝飾器，並將 `run_deployment` 設為 `arun_deployment` 的別名，導致在同步環境中呼叫 `run_deployment` 會回傳 coroutine 物件，而非執行結果。這破壞了既有 API 的同步相容性，違反規範 R07。

建議：保留 `@sync_compatible` 裝飾器於 `arun_deployment` 上，或提供明確的同步包裝函式。

**判斷依據**：diff 中移除 `@sync_compatible` 裝飾器，並在檔案結尾新增 `run_deployment = arun_deployment`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:133</code> client 可能為 None，但未處理 get_or_create_client 的回傳</summary>

`get_or_create_client` 可能回傳 `(None, None)` 或拋出例外，但程式碼直接解包並使用 `client`，未檢查是否為 None。若 client 建立失敗，後續 `client.read_deployment` 會拋出 `AttributeError`，錯誤訊息不明確。

建議：檢查回傳值，若為 None 則拋出明確的例外。

**判斷依據**：diff 中新增 `client, _ = get_or_create_client(client)`，但未檢查 client 是否為 None。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:149</code> 移除 await 可能導致 collect_task_run_inputs 回傳未完成的 coroutine</summary>

原本 `await collect_task_run_inputs(v)` 會等待結果，現在改為 `collect_task_run_inputs(v)` 直接放入 dict。若 `collect_task_run_inputs` 是非同步函式，則會將 coroutine 物件存入 `task_inputs`，後續使用時可能出錯。

建議：確認 `collect_task_run_inputs` 是否為同步函式；若非同步，應保留 await。

**判斷依據**：diff 中將 `await collect_task_run_inputs(v)` 改為 `collect_task_run_inputs(v)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:212</code> 使用 deployment_id 而非 deployment.id 可能導致型別錯誤</summary>

原本使用 `deployment.id`，現在改為 `deployment_id`。若 `deployment_id` 是字串而 `deployment.id` 是 UUID，則傳入 `create_flow_run_from_deployment` 可能導致型別不符或查詢錯誤。

建議：確認 `deployment_id` 的型別與 API 預期一致，或使用 `deployment.id`。

**判斷依據**：diff 中將 `deployment.id` 改為 `deployment_id`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/deployment/test_flow_runs.py:604</code> 測試使用 _sync 參數可能掩蓋同步包裝問題</summary>

同步測試中呼叫 `run_deployment(..., _sync=True)`，但 `_sync` 參數並非公開 API，且可能觸發內部同步執行路徑。這無法驗證移除 `@sync_compatible` 後，一般使用者在同步環境中呼叫 `run_deployment` 的行為。

建議：移除 `_sync` 參數，直接測試同步呼叫是否正常運作。

**判斷依據**：測試中多處使用 `_sync=True` 參數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8355 (cache hit 1536) ｜ completion tokens 1334 ｜ PR #6</sub>