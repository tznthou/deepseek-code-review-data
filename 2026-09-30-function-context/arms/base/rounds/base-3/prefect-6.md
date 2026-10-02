<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 `run_deployment` 改為 `arun_deployment`，並以 `run_deployment = arun_deployment` 保留向後相容。主要風險在於 `run_deployment` 現在是純 async 函式，同步呼叫時會回傳 coroutine 而非執行，可能破壞現有同步使用者的行為。此外，`client` 參數的取得方式改變，需確認 `get_or_create_client` 在無 client 時能正確建立。測試涵蓋了 async 與 sync 情境，但 sync 測試依賴 `_sync` 參數，而該參數在函式簽名中不存在，可能導致測試失敗。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/deployments/flow_runs.py:241` | `run_deployment` 失去同步執行能力，破壞向後相容性 | 0.95 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:133` | `get_or_create_client` 可能無法正確處理未提供的 client | 0.80 |
| ⚠️ | Major | `tests/deployment/test_flow_runs.py:762` | 測試中使用未定義的 `_sync` 參數 | 0.80 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:149` | `collect_task_run_inputs` 改為同步呼叫，可能導致效能問題 | 0.75 |
| 🔸 | Minor | `src/prefect/deployments/flow_runs.py:212` | 使用 `deployment_id` 而非 `deployment.id` 可能導致型別不一致 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/deployments/flow_runs.py:241</code> `run_deployment` 失去同步執行能力，破壞向後相容性</summary>

原本 `run_deployment` 使用 `@sync_compatible` 裝飾器，允許在同步與非同步環境中呼叫。現在改為 `run_deployment = arun_deployment`，而 `arun_deployment` 是純 async 函式，因此在同步環境中呼叫 `run_deployment(...)` 會回傳 coroutine 物件，而不會實際執行流程。這會導致所有現有同步呼叫者的程式碼靜默失敗（例如在腳本或同步函式中呼叫）。

建議：保留一個同步包裝函式，例如使用 `asyncio.run` 或 `anyio.from_thread.run` 來執行 async 版本，或使用 `@sync_compatible` 裝飾器來維持原有行為。

**判斷依據**：diff 中新增 `run_deployment = arun_deployment`，且移除了 `@sync_compatible` 裝飾器。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:133</code> `get_or_create_client` 可能無法正確處理未提供的 client</summary>

原本使用 `@inject_client` 裝飾器，會自動注入 client 或建立新的 client。現在改為手動呼叫 `get_or_create_client(client)`，但未檢查回傳的 client 是否有效。如果 `client` 為 `None`，`get_or_create_client` 應建立新的 client，但需確認其行為與原本一致，特別是在沒有活動 event loop 的同步環境中。

建議：確認 `get_or_create_client` 的實作，並在必要時處理例外或提供明確的錯誤訊息。

**判斷依據**：diff 中新增 `client, _ = get_or_create_client(client)`，取代了 `@inject_client` 裝飾器。

</details>

<details><summary>⚠️ <b>Major</b> — <code>tests/deployment/test_flow_runs.py:762</code> 測試中使用未定義的 `_sync` 參數</summary>

在 `TestRunDeploymentSyncContext` 類別中的測試方法呼叫 `run_deployment(..., _sync=True)`，但 `run_deployment` 的簽名中沒有 `_sync` 參數。這會導致測試失敗，因為函式不接受該參數。

建議：移除 `_sync=True`，或修改函式簽名以支援該參數。

**判斷依據**：diff 中多處出現 `_sync=True`，但 `run_deployment` 的定義中沒有此參數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:149</code> `collect_task_run_inputs` 改為同步呼叫，可能導致效能問題</summary>

原本 `await collect_task_run_inputs(v)` 是非同步呼叫，現在改為 `collect_task_run_inputs(v)` 同步呼叫。如果 `collect_task_run_inputs` 內部有 I/O 或需要非同步操作，這會阻塞事件迴圈。需確認該函式是否為純同步函式，否則應保留 `await`。

**判斷依據**：diff 中將 `await collect_task_run_inputs(v)` 改為 `collect_task_run_inputs(v)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/deployments/flow_runs.py:212</code> 使用 `deployment_id` 而非 `deployment.id` 可能導致型別不一致</summary>

原本傳遞 `deployment.id`，現在改為 `deployment_id`。需確認 `deployment_id` 的型別與 `create_flow_run_from_deployment` 預期的參數型別一致。如果 `deployment_id` 是字串而函式預期 UUID 物件，可能導致型別錯誤。

**判斷依據**：diff 中將 `deployment.id` 改為 `deployment_id`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6860 (cache hit 6784) ｜ completion tokens 1324 ｜ PR #6</sub>