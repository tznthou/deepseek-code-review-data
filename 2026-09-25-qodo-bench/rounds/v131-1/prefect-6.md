<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 `run_deployment` 改為 `arun_deployment`，並以 `run_deployment = arun_deployment` 保留向後相容。主要風險在於 `run_deployment` 不再具有同步包裝，同步呼叫會失敗；此外，`get_or_create_client` 的回傳值未檢查，可能導致 `client` 為 `None` 而後續操作失敗。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/deployments/flow_runs.py:133` | `get_or_create_client` 可能回傳 `None`，導致後續 `client` 為 `None` 而拋出例外 | 0.95 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:241` | `run_deployment` 別名失去同步包裝，同步呼叫會失敗 | 0.90 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:149` | 在非同步上下文中，`collect_task_run_inputs` 未使用 `await`，可能導致未預期的行為 | 0.80 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:212` | 使用 `deployment_id` 而非 `deployment.id` 可能導致型別錯誤 | 0.80 |
| 🔸 | Minor | `src/prefect/deployments/flow_runs.py:231` | 輪詢迴圈中先 sleep 再檢查狀態，可能延遲回傳 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/deployments/flow_runs.py:133</code> `get_or_create_client` 可能回傳 `None`，導致後續 `client` 為 `None` 而拋出例外</summary>

`get_or_create_client` 在無法建立 client 時可能回傳 `None`，但程式碼未檢查回傳值，直接使用 `client` 呼叫方法，可能導致 `AttributeError`。建議檢查回傳值，若為 `None` 則拋出明確的例外。

**判斷依據**：diff 中新增的這一行，未檢查回傳值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:241</code> `run_deployment` 別名失去同步包裝，同步呼叫會失敗</summary>

原本 `run_deployment` 有 `@sync_compatible` 裝飾器，可在同步上下文中呼叫。現在 `run_deployment = arun_deployment` 只是 async 函式的別名，同步呼叫會回傳 coroutine 而非執行結果，導致既有同步程式碼失效。建議保留同步包裝或提供明確的同步版本。

**判斷依據**：diff 中新增的別名指派，移除了原本的裝飾器。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:149</code> 在非同步上下文中，`collect_task_run_inputs` 未使用 `await`，可能導致未預期的行為</summary>

原本的程式碼使用 `await collect_task_run_inputs(v)`，但修改後移除了 `await`。若 `collect_task_run_inputs` 是 async 函式，這會導致回傳 coroutine 而非實際值，造成後續錯誤。請確認該函式是否為同步函式，若不是，應保留 `await`。

**判斷依據**：diff 中將 `await collect_task_run_inputs(v)` 改為 `collect_task_run_inputs(v)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:212</code> 使用 `deployment_id` 而非 `deployment.id` 可能導致型別錯誤</summary>

原本使用 `deployment.id`，修改後改為 `deployment_id`。若 `deployment_id` 是字串而 API 預期 UUID，可能導致型別錯誤。請確認 `deployment_id` 的型別與 API 要求一致。

**判斷依據**：diff 中將 `deployment.id` 改為 `deployment_id`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/deployments/flow_runs.py:231</code> 輪詢迴圈中先 sleep 再檢查狀態，可能延遲回傳</summary>

原本先檢查狀態再 sleep，修改後先 sleep 再檢查。這會導致即使 flow run 已完成，仍會等待一個 `poll_interval` 才回傳。若 `poll_interval` 較大，可能造成不必要的延遲。建議先檢查狀態再 sleep。

**判斷依據**：diff 中將 `await anyio.sleep(poll_interval)` 移到迴圈開頭。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6824 (cache hit 1408) ｜ completion tokens 1086 ｜ PR #6</sub>