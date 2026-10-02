<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 `run_deployment` 改為非同步函式 `arun_deployment`，並以別名保留向後相容。主要風險在於同步呼叫路徑的移除：`run_deployment` 現在直接指向非同步函式，但測試中仍以 `_sync=True` 呼叫，這可能導致同步環境下無法正常運作。此外，`deployment_id` 在非 UUID 名稱路徑下可能為 `None`，傳入 `create_flow_run_from_deployment` 可能造成型別錯誤。建議優先確認同步呼叫的相容性與 `deployment_id` 的處理。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/deployments/flow_runs.py:241` | 同步呼叫路徑失效：`run_deployment` 不再支援同步執行 | 0.95 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:211` | `deployment_id` 可能為 `None`，傳入 `create_flow_run_from_deployment` 可能導致型別錯誤 | 0.80 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:149` | `collect_task_run_inputs` 改為同步呼叫，可能阻塞事件迴圈 | 0.70 |
| 🔸 | Minor | `src/prefect/deployments/flow_runs.py:231` | 輪詢邏輯變更：先 sleep 再檢查狀態，可能延遲最終結果 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/deployments/flow_runs.py:241</code> 同步呼叫路徑失效：`run_deployment` 不再支援同步執行</summary>

原本 `run_deployment` 使用 `@sync_compatible` 裝飾器，允許在同步環境中直接呼叫。此 PR 移除了該裝飾器，並將 `run_deployment` 設為 `arun_deployment` 的別名，但 `arun_deployment` 是純非同步函式。這導致所有現有的同步呼叫（例如 `run_deployment(...)` 在沒有事件迴圈的環境中）會拋出 `RuntimeError` 或回傳 coroutine 物件而非實際結果。測試中仍使用 `_sync=True` 參數呼叫，但該參數已不存在於函式簽名中，會引發 `TypeError`。

**失敗情境**：任何在同步 Python 腳本或測試中呼叫 `run_deployment` 的使用者，會遇到 `TypeError: run_deployment() got an unexpected keyword argument '_sync'` 或 `RuntimeError: no running event loop`。

**建議**：保留同步包裝器，例如使用 `asyncio.run` 或 `anyio.run` 在同步函式中執行非同步邏輯，或提供獨立的同步函式。

**判斷依據**：diff 中移除了 `@sync_compatible` 和 `@inject_client`，並在檔案末尾新增 `run_deployment = arun_deployment`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:211</code> `deployment_id` 可能為 `None`，傳入 `create_flow_run_from_deployment` 可能導致型別錯誤</summary>

在 `name` 不是 UUID 且無法解析為 UUID 時，`deployment_id` 保持為 `None`。後續呼叫 `client.create_flow_run_from_deployment(deployment_id, ...)` 時，若該函式預期 `deployment_id` 為 `UUID` 型別，則可能拋出 `TypeError` 或驗證錯誤。

**失敗情境**：使用者傳入非 UUID 且非合法 UUID 字串的部署名稱（例如 `"my-flow/my-deployment"`），且該名稱無法透過 `read_deployment_by_name` 解析時，`deployment_id` 為 `None`，導致 API 呼叫失敗。

**建議**：在呼叫前檢查 `deployment_id` 是否為 `None`，或改用 `deployment.id`（從 `read_deployment_by_name` 取得的物件）作為參數。

**判斷依據**：diff 中將原本的 `deployment.id` 改為 `deployment_id`，但 `deployment_id` 在名稱路徑下可能未被設定。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:149</code> `collect_task_run_inputs` 改為同步呼叫，可能阻塞事件迴圈</summary>

原本 `await collect_task_run_inputs(v)` 被改為 `collect_task_run_inputs(v)`，移除了 `await`。若 `collect_task_run_inputs` 是同步函式，此變更沒有問題；但若它內部包含非同步操作（例如資料庫查詢），則會導致 `RuntimeError` 或阻塞事件迴圈。

**失敗情境**：在非同步環境中呼叫 `arun_deployment` 且 `as_subflow=True` 時，若 `collect_task_run_inputs` 需要非同步執行，會拋出 `TypeError: object dict can't be used in 'await' expression` 或造成效能問題。

**建議**：確認 `collect_task_run_inputs` 的實作是否為同步；若非同步，應保留 `await`。

**判斷依據**：diff 中將 `await collect_task_run_inputs(v)` 改為 `collect_task_run_inputs(v)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/deployments/flow_runs.py:231</code> 輪詢邏輯變更：先 sleep 再檢查狀態，可能延遲最終結果</summary>

原本的輪詢迴圈先讀取 flow run 狀態，若未完成則 sleep；現在改為先 sleep 再讀取。這會導致即使 flow run 在第一次檢查前已完成，也會等待 `poll_interval` 秒後才回傳。

**失敗情境**：當 `timeout` 設定較小且 `poll_interval` 較大時，可能超過 timeout 才回傳，或延遲回傳已完成的结果。

**建議**：恢復先檢查再 sleep 的順序，或使用 `anyio.move_on_after` 搭配更精確的輪詢。

**判斷依據**：diff 中將 `await anyio.sleep(poll_interval)` 移至迴圈開頭。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8185 (cache hit 1536) ｜ completion tokens 1513 ｜ PR #6</sub>