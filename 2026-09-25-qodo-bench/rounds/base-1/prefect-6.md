<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 `run_deployment` 改為非同步函式 `arun_deployment`，並以 `run_deployment = arun_deployment` 保留向後相容。主要風險在於移除 `@sync_compatible` 裝飾器後，同步呼叫路徑的相容性可能受損，且 `client` 參數的取得方式改為 `get_or_create_client` 可能引入非預期的行為差異。此外，測試中使用了未定義的 `_sync` 參數，可能導致測試失敗。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/deployments/flow_runs.py:48` | 移除 `@sync_compatible` 導致同步呼叫失敗 | 0.95 |
| ⚠️ | Major | `tests/deployment/test_flow_runs.py:626` | 測試中使用未定義的 `_sync` 參數 | 0.90 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:133` | `get_or_create_client` 可能建立非預期的 client | 0.80 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:149` | `collect_task_run_inputs` 改為同步呼叫可能阻塞事件迴圈 | 0.75 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:212` | 使用 `deployment_id` 而非 `deployment.id` 可能導致型別錯誤 | 0.70 |
| 🔸 | Minor | `tests/deployment/test_flow_runs.py:930` | 測試中斷言 `run_deployment.aio is arun_deployment` 可能不成立 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/deployments/flow_runs.py:48</code> 移除 `@sync_compatible` 導致同步呼叫失敗</summary>

原本 `run_deployment` 使用 `@sync_compatible` 裝飾器，允許在同步環境中直接呼叫。現在改為 `arun_deployment` 且僅以 `run_deployment = arun_deployment` 別名，未提供同步包裝。若使用者原本在同步程式碼中呼叫 `run_deployment(...)`，現在會得到一個 coroutine 物件而非 FlowRun，導致程式錯誤。

建議：保留一個同步包裝函式，例如使用 `asyncio.run` 或 `anyio.run` 來呼叫 `arun_deployment`，或繼續使用 `@sync_compatible` 裝飾器。

**判斷依據**：diff 中移除了 `@sync_compatible` 裝飾器，且新增 `run_deployment = arun_deployment` 別名，未提供同步執行路徑。

</details>

<details><summary>⚠️ <b>Major</b> — <code>tests/deployment/test_flow_runs.py:626</code> 測試中使用未定義的 `_sync` 參數</summary>

在 `TestRunDeploymentSyncContext` 的測試中，呼叫 `run_deployment(..., _sync=True)`，但 `arun_deployment` 的簽名中沒有 `_sync` 參數。這會導致測試拋出 `TypeError`。

建議：移除 `_sync` 參數，或修改函式簽名以支援同步呼叫。

**判斷依據**：diff 中多次出現 `_sync=True`，但函式定義中無此參數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:133</code> `get_or_create_client` 可能建立非預期的 client</summary>

原本使用 `@inject_client` 裝飾器，會根據上下文注入 client，若未提供則建立新的 client。現在改為 `get_or_create_client(client)`，其行為可能不同：若 `client` 為 None，它會建立一個新的 client，但可能未正確處理與目前執行中 flow run 的關聯（例如使用相同的 API URL 或認證）。這可能導致在 flow 內呼叫時無法正確連結父子關係。

建議：確認 `get_or_create_client` 的實作是否符合預期，或保留原本的 `@inject_client` 機制。

**判斷依據**：diff 中將 `@inject_client` 移除，改為在函式內呼叫 `get_or_create_client`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:149</code> `collect_task_run_inputs` 改為同步呼叫可能阻塞事件迴圈</summary>

原本 `await collect_task_run_inputs(v)` 是非同步呼叫，現在改為 `collect_task_run_inputs(v)` 同步呼叫。若該函式內部有 I/O 或耗時操作，會阻塞事件迴圈，影響效能。

建議：確認 `collect_task_run_inputs` 是否為非同步函式，若是則應保留 `await`。

**判斷依據**：diff 中移除了 `await`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:212</code> 使用 `deployment_id` 而非 `deployment.id` 可能導致型別錯誤</summary>

原本 `client.create_flow_run_from_deployment(deployment.id, ...)` 使用 `deployment.id`，現在改為 `deployment_id`。若 `deployment_id` 是字串（例如從名稱解析而來），而 API 期望 UUID，可能導致型別錯誤。

建議：確認 `deployment_id` 的型別，必要時轉換為 UUID。

**判斷依據**：diff 中將 `deployment.id` 改為 `deployment_id`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/deployment/test_flow_runs.py:930</code> 測試中斷言 `run_deployment.aio is arun_deployment` 可能不成立</summary>

若 `run_deployment` 是 `arun_deployment` 的別名，則 `run_deployment.aio` 屬性可能不存在，除非 `arun_deployment` 有定義 `aio` 屬性。此測試可能失敗。

建議：確認 `arun_deployment` 是否有 `aio` 屬性，或調整測試。

**判斷依據**：diff 中新增此斷言。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6860 (cache hit 1536) ｜ completion tokens 1473 ｜ PR #6</sub>