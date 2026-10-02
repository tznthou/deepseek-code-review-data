<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 `run_deployment` 改為 `arun_deployment`，並以 `run_deployment = arun_deployment` 提供向後相容。主要風險在於 `run_deployment` 不再有 `@sync_compatible` 裝飾器，同步呼叫時會回傳 coroutine 而非執行結果，可能破壞現有同步使用者的程式碼。此外，`client` 參數在 `get_or_create_client` 後未更新，導致後續使用可能出錯。測試涵蓋了 async 與 sync 情境，但 sync 測試依賴 `_sync` 參數，而該參數在函式簽名中不存在，可能導致測試失敗或誤導。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/deployments/flow_runs.py:241` | 移除 @sync_compatible 導致同步呼叫行為破壞 | 0.95 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:133` | client 參數未更新，可能使用 None 或舊客戶端 | 0.85 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:149` | 移除 await 可能導致未完成的 coroutine 被傳遞 | 0.80 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:212` | deployment_id 可能未定義 | 0.80 |
| ⚠️ | Major | `tests/deployment/test_flow_runs.py:760` | 測試使用不存在的 _sync 參數 | 0.75 |
| 🔸 | Minor | `src/prefect/deployments/flow_runs.py:241` | 缺少型別註記 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/deployments/flow_runs.py:241</code> 移除 @sync_compatible 導致同步呼叫行為破壞</summary>

原本 `run_deployment` 有 `@sync_compatible` 裝飾器，允許在同步上下文中直接呼叫並等待結果。現在 `run_deployment` 只是 `arun_deployment` 的別名，而 `arun_deployment` 是 async 函式，因此同步呼叫 `run_deployment(...)` 會回傳 coroutine 物件，不會執行任何邏輯，也不會等待 flow run 完成。這會破壞所有現有同步使用者的程式碼。

建議：保留一個同步包裝函式，例如使用 `sync_compatible` 裝飾器或提供明確的同步版本，確保向後相容。

**判斷依據**：diff 中移除了 `@sync_compatible` 和 `@inject_client`，並在檔案末尾新增 `run_deployment = arun_deployment`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:133</code> client 參數未更新，可能使用 None 或舊客戶端</summary>

`get_or_create_client(client)` 會回傳一個客戶端實例，但程式碼沒有將回傳值指派回 `client` 變數。後續程式碼（如 `client.read_deployment`）仍使用原始的 `client` 參數，若呼叫者未提供 client，則 `client` 為 None，導致 `AttributeError`。

建議：改為 `client, _ = get_or_create_client(client)` 或直接使用回傳值。

**判斷依據**：diff 中新增了 `client, _ = get_or_create_client(client)`，但後續程式碼仍使用 `client` 變數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:149</code> 移除 await 可能導致未完成的 coroutine 被傳遞</summary>

原本 `collect_task_run_inputs(v)` 前面有 `await`，現在被移除。若 `collect_task_run_inputs` 是 async 函式，則會回傳 coroutine 物件，而不是實際的輸入值，可能導致後續處理錯誤。

建議：確認 `collect_task_run_inputs` 是否為 async，若是則保留 `await`。

**判斷依據**：diff 中將 `await collect_task_run_inputs(v)` 改為 `collect_task_run_inputs(v)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:212</code> deployment_id 可能未定義</summary>

在 `create_flow_run_from_deployment` 呼叫中，第一個參數從 `deployment.id` 改為 `deployment_id`。但 `deployment_id` 變數只在前面解析名稱時有條件賦值，若名稱解析失敗或走其他路徑，`deployment_id` 可能未定義，導致 `NameError`。

建議：確保 `deployment_id` 在所有路徑下都有賦值，或改用 `deployment.id`。

**判斷依據**：diff 中將 `deployment.id` 改為 `deployment_id`，但未看到 `deployment_id` 的賦值邏輯有相應調整。

</details>

<details><summary>⚠️ <b>Major</b> — <code>tests/deployment/test_flow_runs.py:760</code> 測試使用不存在的 _sync 參數</summary>

在 `TestRunDeploymentSyncContext` 類別中，多個測試呼叫 `run_deployment(..., _sync=True)`。但 `run_deployment` 的簽名中沒有 `_sync` 參數，這會導致 `TypeError`。

建議：移除 `_sync` 參數，或提供實際的同步包裝函式。

**判斷依據**：diff 中新增的測試程式碼包含 `_sync=True`，但函式簽名未定義此參數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/deployments/flow_runs.py:241</code> 缺少型別註記</summary>

`run_deployment = arun_deployment` 沒有型別註記，可能影響型別檢查和 IDE 支援。

建議：加上型別註記，例如 `run_deployment: Callable[..., Awaitable[FlowRun]] = arun_deployment`。

**判斷依據**：diff 中新增的別名沒有型別註記。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8309 (cache hit 8192) ｜ completion tokens 1496 ｜ PR #6</sub>