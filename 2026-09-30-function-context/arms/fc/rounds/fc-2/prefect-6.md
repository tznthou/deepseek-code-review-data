<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 `run_deployment` 改為 `arun_deployment`，並以 `run_deployment = arun_deployment` 提供向後相容。主要風險在於：`run_deployment` 不再具備同步包裝，同步呼叫會直接失敗；`client` 參數在 `get_or_create_client` 後可能被覆寫為 None，導致後續 `client.read_deployment` 出錯；`deployment_id` 在名稱解析路徑中可能為 None，傳入 `create_flow_run_from_deployment` 會造成型別錯誤。測試新增了 `_sync` 參數，但該參數未在函式簽名中定義，測試會失敗。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/deployments/flow_runs.py:241` | `run_deployment` 不再支援同步呼叫，破壞向後相容性 | 0.95 |
| ⚠️ | Major | `tests/deployment/test_flow_runs.py:633` | 測試使用未定義的 `_sync` 參數 | 0.90 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:133` | `client` 參數可能被 `get_or_create_client` 覆寫為 None | 0.85 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:123` | `deployment_id` 可能為 None，傳入 `create_flow_run_from_deployment` 會出錯 | 0.80 |
| 🔸 | Minor | `src/prefect/deployments/flow_runs.py:149` | `collect_task_run_inputs` 改為同步呼叫，可能造成事件迴圈阻塞 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/deployments/flow_runs.py:241</code> `run_deployment` 不再支援同步呼叫，破壞向後相容性</summary>

原本的 `run_deployment` 使用 `@sync_compatible` 裝飾器，允許在同步與非同步環境中呼叫。現在 `run_deployment` 只是 `arun_deployment` 的別名，而 `arun_deployment` 是純 async 函式。任何現有同步呼叫 `run_deployment(...)` 的程式碼都會收到 coroutine 物件而非 FlowRun，導致執行錯誤。

失敗情境：
```python
flow_run = run_deployment("my-flow/my-deployment")  # 回傳 coroutine，未 await
print(flow_run.state)  # AttributeError: 'coroutine' object has no attribute 'state'
```

建議：保留同步包裝，例如使用 `sync_compatible` 裝飾器或提供獨立的同步函式。

**判斷依據**：diff 中 `run_deployment = arun_deployment` 取代了原本的 `@sync_compatible` 裝飾器。

</details>

<details><summary>⚠️ <b>Major</b> — <code>tests/deployment/test_flow_runs.py:633</code> 測試使用未定義的 `_sync` 參數</summary>

測試中呼叫 `run_deployment(..., _sync=True)`，但 `arun_deployment` 的簽名中沒有 `_sync` 參數。這會導致 TypeError: unexpected keyword argument '_sync'。

失敗情境：執行 `test_run_deployment_sync_basic` 時，會拋出 TypeError。

建議：移除 `_sync` 參數，或修改函式簽名以支援該參數。

**判斷依據**：diff 中測試新增的 `_sync=True` 參數，但函式簽名未包含。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:133</code> `client` 參數可能被 `get_or_create_client` 覆寫為 None</summary>

`get_or_create_client(client)` 若傳入的 `client` 為 None，會建立新的 client 並回傳；但若傳入的 client 不是 None，則會回傳該 client。然而，函式簽名中 `client` 的預設值為 None，且型別為 Optional。在 `client, _ = get_or_create_client(client)` 之後，`client` 變數被重新指派為回傳值，但若 `get_or_create_client` 內部因某些原因回傳 None（例如設定錯誤），後續 `client.read_deployment` 就會拋出 AttributeError。

失敗情境：當 `get_or_create_client` 無法建立 client 且未拋出例外時，`client` 為 None，下一行 `deployment = await client.read_deployment(...)` 會失敗。

建議：檢查回傳值是否為 None，或直接使用 `client = get_or_create_client(client)` 並確保其永不回傳 None。

**判斷依據**：diff 中新增的 `client, _ = get_or_create_client(client)` 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:123</code> `deployment_id` 可能為 None，傳入 `create_flow_run_from_deployment` 會出錯</summary>

在名稱解析路徑中，若 `name` 不是 UUID 且無法轉換為 UUID，`deployment_id` 保持為 None。之後呼叫 `client.create_flow_run_from_deployment(deployment_id, ...)` 時，若該函式預期 deployment_id 為 UUID 或字串，傳入 None 可能導致型別錯誤或 API 請求失敗。

失敗情境：`name` 為不合法的 UUID 字串且不是有效的 deployment 名稱時，`deployment_id` 為 None，`create_flow_run_from_deployment` 可能拋出 ValidationError 或伺服器端錯誤。

建議：在呼叫前檢查 `deployment_id` 是否為 None，或確保 `read_deployment_by_name` 失敗時會拋出例外。

**判斷依據**：diff 中 `deployment_id = None` 初始化，且後續 `create_flow_run_from_deployment(deployment_id, ...)` 使用該變數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/deployments/flow_runs.py:149</code> `collect_task_run_inputs` 改為同步呼叫，可能造成事件迴圈阻塞</summary>

原本 `await collect_task_run_inputs(v)` 是非同步呼叫，現在改為 `collect_task_run_inputs(v)` 同步呼叫。若該函式內部有 I/O 或耗時操作，會阻塞事件迴圈。

失敗情境：在高併發環境下，多個 subflow 建立時可能造成效能瓶頸。

建議：確認 `collect_task_run_inputs` 是否為純 CPU 操作，否則應保留 await。

**判斷依據**：diff 中將 `await collect_task_run_inputs(v)` 改為 `collect_task_run_inputs(v)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8185 (cache hit 8064) ｜ completion tokens 1648 ｜ PR #6</sub>