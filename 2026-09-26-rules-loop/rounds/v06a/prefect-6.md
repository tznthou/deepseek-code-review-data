<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 `run_deployment` 改為非同步函式 `arun_deployment`，並以 `run_deployment = arun_deployment` 保留向後相容性，同時新增測試。主要風險在於 `run_deployment` 不再具有同步包裝，可能破壞既有同步呼叫；此外，`get_or_create_client` 的回傳值處理、`deployment_id` 的使用以及 `collect_task_run_inputs` 的呼叫方式需要進一步確認。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:241` | `run_deployment` 不再提供同步包裝，可能破壞既有同步呼叫 | 0.80 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:133` | `get_or_create_client` 的回傳值可能為 `None`，但未檢查 | 0.75 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:212` | 使用 `deployment_id` 而非 `deployment.id` 可能導致型別錯誤 | 0.70 |
| 🔸 | Minor | `src/prefect/deployments/flow_runs.py:149` | `collect_task_run_inputs` 改為同步呼叫可能導致效能問題 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:241</code> `run_deployment` 不再提供同步包裝，可能破壞既有同步呼叫</summary>

原本的 `run_deployment` 使用 `@sync_compatible` 裝飾器，允許在同步環境中直接呼叫。此 PR 移除了該裝飾器，並將 `run_deployment` 設為 `arun_deployment` 的別名，這使得 `run_deployment` 變成一個非同步函式。任何在同步程式碼中呼叫 `run_deployment` 的使用者都會遇到 `RuntimeError` 或需要自行處理事件迴圈，這是一個破壞性變更。建議保留一個同步包裝函式，或使用 `@sync_compatible` 裝飾器來維持向後相容性。

**判斷依據**：diff 中移除了 `@sync_compatible` 裝飾器，並在檔案末尾新增 `run_deployment = arun_deployment`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:133</code> `get_or_create_client` 的回傳值可能為 `None`，但未檢查</summary>

`get_or_create_client` 可能回傳 `(None, None)` 或類似的空值，但程式碼直接將第一個元素指派給 `client` 並使用。如果 `client` 為 `None`，後續的 `client.read_deployment` 等呼叫會拋出 `AttributeError`。建議檢查回傳值，或使用 `assert client is not None` 來確保型別安全。

**判斷依據**：diff 中新增了 `client, _ = get_or_create_client(client)`，但未檢查 `client` 是否為 `None`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:212</code> 使用 `deployment_id` 而非 `deployment.id` 可能導致型別錯誤</summary>

原本的程式碼使用 `deployment.id`，但此 PR 改為 `deployment_id`。`deployment_id` 可能是字串或 UUID，而 `create_flow_run_from_deployment` 可能預期 UUID 型別。如果 `deployment_id` 是字串，可能會導致型別錯誤或 API 呼叫失敗。建議確認 `deployment_id` 的型別，或使用 `deployment.id` 來確保正確性。

**判斷依據**：diff 中將 `deployment.id` 改為 `deployment_id`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/deployments/flow_runs.py:149</code> `collect_task_run_inputs` 改為同步呼叫可能導致效能問題</summary>

原本的程式碼使用 `await collect_task_run_inputs(v)`，但此 PR 移除了 `await`，改為同步呼叫。如果 `collect_task_run_inputs` 是一個非同步函式，這會導致 `TypeError`；如果它是一個同步函式，則可能阻塞事件迴圈。建議確認該函式的性質，並保留適當的呼叫方式。

**判斷依據**：diff 中將 `await collect_task_run_inputs(v)` 改為 `collect_task_run_inputs(v)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8344 (cache hit 6016) ｜ completion tokens 1063 ｜ PR #6</sub>