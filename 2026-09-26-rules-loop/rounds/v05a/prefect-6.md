<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 `run_deployment` 改為 `arun_deployment`，並以 `run_deployment = arun_deployment` 提供向後相容。主要風險在於 `run_deployment` 的同步呼叫路徑：原本的 `@sync_compatible` 裝飾器被移除，但測試仍以 `_sync=True` 呼叫，且 `arun_deployment` 內部使用 `get_or_create_client` 取得 client，在同步情境下可能無法正確建立 client，導致同步呼叫失敗。此外，`collect_task_run_inputs` 的呼叫從 `await` 改為直接呼叫，若該函式為 async，將導致協程未被執行。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/deployments/flow_runs.py:241` | 移除 @sync_compatible 後，同步呼叫 run_deployment 將失敗 | 0.95 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:149` | collect_task_run_inputs 可能未被 await | 0.80 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:133` | 使用 get_or_create_client 可能無法在同步上下文中建立 client | 0.70 |
| 🔸 | Minor | `src/prefect/deployments/flow_runs.py:212` | 使用 deployment_id 而非 deployment.id 可能造成型別不一致 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/deployments/flow_runs.py:241</code> 移除 @sync_compatible 後，同步呼叫 run_deployment 將失敗</summary>

原本的 `run_deployment` 使用 `@sync_compatible` 裝飾器，允許在同步上下文中直接呼叫。此 PR 移除了該裝飾器，並將 `run_deployment` 設為 `arun_deployment` 的別名。然而，`arun_deployment` 是 async 函式，在同步上下文中呼叫會回傳 coroutine 物件，不會執行。測試中仍以 `_sync=True` 參數呼叫 `run_deployment`，但 `arun_deployment` 的簽名中沒有 `_sync` 參數，這會導致 `TypeError`。

建議：若需保留同步介面，應使用 `@sync_compatible` 裝飾器或提供明確的同步包裝函式。

**判斷依據**：diff 中移除了 `@sync_compatible` 裝飾器，並在檔案末尾新增 `run_deployment = arun_deployment`。測試檔案中仍以 `_sync=True` 呼叫 `run_deployment`，但 `arun_deployment` 的參數列表中沒有 `_sync`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:149</code> collect_task_run_inputs 可能未被 await</summary>

原本的程式碼為 `k: await collect_task_run_inputs(v) for k, v in parameters.items()`，此 PR 改為 `k: collect_task_run_inputs(v) for k, v in parameters.items()`，移除了 `await`。若 `collect_task_run_inputs` 是 async 函式，則會建立 coroutine 物件但未執行，導致 task inputs 未被正確收集。

建議：確認 `collect_task_run_inputs` 是否為 async，若是則應保留 `await`。

**判斷依據**：diff 中將 `await collect_task_run_inputs(v)` 改為 `collect_task_run_inputs(v)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:133</code> 使用 get_or_create_client 可能無法在同步上下文中建立 client</summary>

原本使用 `@inject_client` 裝飾器注入 client，此 PR 改為在函式內呼叫 `get_or_create_client(client)`。`get_or_create_client` 可能是 async 函式，但此處沒有 `await`，導致 client 可能未被正確建立。此外，在同步上下文中呼叫 `run_deployment` 時，`get_or_create_client` 可能無法取得 event loop，進而拋出例外。

建議：確認 `get_or_create_client` 的實作，並確保在同步與非同步情境下都能正確取得 client。

**判斷依據**：diff 中新增 `client, _ = get_or_create_client(client)`，且移除了 `@inject_client` 裝飾器。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/deployments/flow_runs.py:212</code> 使用 deployment_id 而非 deployment.id 可能造成型別不一致</summary>

原本的程式碼為 `deployment.id`，此 PR 改為 `deployment_id`。`deployment_id` 是從輸入參數解析出的 UUID 或名稱，而 `deployment.id` 是從 API 回應取得的 UUID。若輸入為名稱，`deployment_id` 會是字串，但 `create_flow_run_from_deployment` 可能預期 UUID 物件。

建議：確認 `create_flow_run_from_deployment` 接受的型別，並確保傳入正確的型別。

**判斷依據**：diff 中將 `deployment.id` 改為 `deployment_id`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8309 (cache hit 6016) ｜ completion tokens 1249 ｜ PR #6</sub>