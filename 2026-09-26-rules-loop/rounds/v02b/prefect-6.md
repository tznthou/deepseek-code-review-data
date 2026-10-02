<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 `run_deployment` 改為 `arun_deployment`，並以 `run_deployment = arun_deployment` 提供向後相容。主要風險在於移除 `@sync_compatible` 後，同步呼叫路徑可能依賴未實作的 `_sync` 參數，且 `collect_task_run_inputs` 改為同步呼叫可能導致協程物件未被 await。另有 `deployment_id` 可能為 None 的型別問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/deployments/flow_runs.py:241` | 移除 @sync_compatible 後，同步呼叫路徑可能依賴未實作的 _sync 參數 | 0.90 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:149` | collect_task_run_inputs 改為同步呼叫可能導致協程未被 await | 0.80 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:212` | deployment_id 可能為 None 導致型別錯誤 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/deployments/flow_runs.py:241</code> 移除 @sync_compatible 後，同步呼叫路徑可能依賴未實作的 _sync 參數</summary>

原 `run_deployment` 使用 `@sync_compatible` 裝飾器，允許在同步上下文中呼叫。現在直接將 `run_deployment` 設為 `arun_deployment` 的別名，但 `arun_deployment` 是純 async 函式，不具備同步執行能力。測試中使用了 `_sync=True` 參數，但 `arun_deployment` 的簽名中沒有 `_sync` 參數，這會導致同步呼叫時拋出 `TypeError`。

具體失敗情境：使用者在同步函式中呼叫 `run_deployment(...)`，會得到一個 coroutine 物件，若未 await 則不會執行；若嘗試使用 `_sync=True` 則會因參數不存在而失敗。

建議：保留 `@sync_compatible` 裝飾器於 `arun_deployment` 上，或提供明確的同步包裝函式。

**判斷依據**：diff 中移除了 `@sync_compatible` 和 `@inject_client`，並在檔案末尾新增 `run_deployment = arun_deployment`。測試檔案中呼叫 `run_deployment(..., _sync=True)`，但 `arun_deployment` 簽名沒有 `_sync` 參數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:149</code> collect_task_run_inputs 改為同步呼叫可能導致協程未被 await</summary>

原本 `await collect_task_run_inputs(v)` 被改為 `collect_task_run_inputs(v)`。若 `collect_task_run_inputs` 是 async 函式，則現在會回傳 coroutine 物件而不執行，導致 `task_inputs` 中包含未完成的協程，後續使用時可能出錯。

具體失敗情境：在 flow 中呼叫 `arun_deployment` 且提供 parameters 時，`task_inputs` 會包含 coroutine 物件，傳遞給 `create_flow_run_from_deployment` 時可能無法序列化或執行。

建議：確認 `collect_task_run_inputs` 是否為 async；若是，應保留 `await`。

**判斷依據**：diff 中將 `await collect_task_run_inputs(v)` 改為 `collect_task_run_inputs(v)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:212</code> deployment_id 可能為 None 導致型別錯誤</summary>

在 `create_flow_run_from_deployment` 呼叫中，第一個參數從 `deployment.id` 改為 `deployment_id`。但 `deployment_id` 可能為 None（當使用者以名稱指定 deployment 時），而函式預期收到 UUID。

具體失敗情境：呼叫 `arun_deployment("my-flow/my-deployment")` 時，`deployment_id` 為 None，傳入後可能導致 API 錯誤或型別檢查失敗。

建議：使用 `deployment.id` 或確保 `deployment_id` 不為 None。

**判斷依據**：diff 中將 `deployment.id` 改為 `deployment_id`，但 `deployment_id` 在名稱解析路徑中可能保持 None。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8355 (cache hit 8320) ｜ completion tokens 1069 ｜ PR #6</sub>