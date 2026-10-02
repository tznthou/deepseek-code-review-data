<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 `run_deployment` 改為 `arun_deployment`，並以 `run_deployment = arun_deployment` 提供向後相容。主要風險在於 `run_deployment` 不再有 `@sync_compatible` 裝飾器，導致同步呼叫時行為改變（回傳 coroutine 而非執行），且 `_sync` 參數未在函式簽名中定義，可能造成 TypeError。此外，`collect_task_run_inputs` 的呼叫從 `await` 改為同步，若該函式為 async 將導致錯誤。測試涵蓋了基本情境，但未驗證同步呼叫的相容性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/deployments/flow_runs.py:241` | 移除 @sync_compatible 導致同步呼叫行為中斷 | 0.95 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:48` | 未定義的 `_sync` 參數可能導致 TypeError | 0.90 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:149` | `collect_task_run_inputs` 可能為 async 函式，移除 await 導致錯誤 | 0.85 |
| 🔸 | Minor | `src/prefect/deployments/flow_runs.py:211` | 使用 `deployment_id` 而非 `deployment.id` 可能造成型別不一致 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/deployments/flow_runs.py:241</code> 移除 @sync_compatible 導致同步呼叫行為中斷</summary>

原本 `run_deployment` 有 `@sync_compatible` 裝飾器，允許在同步環境中直接呼叫並等待結果。現在 `run_deployment` 只是 `arun_deployment` 的別名，而 `arun_deployment` 是 async 函式，因此在同步環境中呼叫 `run_deployment(...)` 會回傳 coroutine 物件，不會執行流程，除非呼叫者自行處理事件迴圈。這破壞了向後相容性，且違反規範 R07（Async Functions Must Have Sync Compatibility Wrappers Where Public）。

建議：保留一個同步包裝函式，例如使用 `@sync_compatible` 裝飾 `arun_deployment` 並指派給 `run_deployment`，或提供明確的同步版本。

**判斷依據**：diff 中移除了 `@sync_compatible` 和 `@inject_client`，並在檔案末尾新增 `run_deployment = arun_deployment`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:48</code> 未定義的 `_sync` 參數可能導致 TypeError</summary>

測試中呼叫 `run_deployment(..., _sync=True)`，但 `arun_deployment` 的簽名中沒有 `_sync` 參數。如果 `run_deployment` 只是 `arun_deployment` 的別名，傳入 `_sync=True` 會導致 `TypeError: unexpected keyword argument '_sync'`。這表示同步包裝器必須處理 `_sync` 參數，或者測試本身有誤。

建議：若需支援同步呼叫，應在同步包裝器中接受 `_sync` 參數並忽略或使用；否則應移除測試中的 `_sync` 參數。

**判斷依據**：函式簽名中沒有 `_sync` 參數，但測試中使用了 `_sync=True`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:149</code> `collect_task_run_inputs` 可能為 async 函式，移除 await 導致錯誤</summary>

原本程式碼為 `k: await collect_task_run_inputs(v) for k, v in parameters.items()`，現在改為 `k: collect_task_run_inputs(v) for k, v in parameters.items()`。如果 `collect_task_run_inputs` 是 async 函式，移除 `await` 會導致回傳 coroutine 物件而非實際值，造成後續使用錯誤。需要確認該函式的定義。

**判斷依據**：diff 中將 `await collect_task_run_inputs(v)` 改為 `collect_task_run_inputs(v)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/deployments/flow_runs.py:211</code> 使用 `deployment_id` 而非 `deployment.id` 可能造成型別不一致</summary>

原本 `create_flow_run_from_deployment` 使用 `deployment.id`，現在改為 `deployment_id`。若 `deployment_id` 是 UUID 物件，而 API 預期字串，可能導致型別錯誤。需確認 `deployment_id` 的型別與 API 要求。

**判斷依據**：diff 中將 `deployment.id` 改為 `deployment_id`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8354 (cache hit 1536) ｜ completion tokens 1336 ｜ PR #6</sub>