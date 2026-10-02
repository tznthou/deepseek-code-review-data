<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 `run_deployment` 改為 `arun_deployment`，並以 `run_deployment = arun_deployment` 保留向後相容。主要風險在於 `run_deployment` 現在是 async 函式，同步呼叫時會回傳 coroutine 而非 FlowRun，可能破壞既有同步使用者的程式碼。此外，`client` 參數的取得方式改為 `get_or_create_client`，需確認其行為與原本的 `inject_client` 一致。測試涵蓋了 async 與 sync 情境，但 sync 測試依賴 `_sync` 參數，需確認該參數是否為公開 API。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:241` | `run_deployment` 現在是 async 函式，同步呼叫會回傳 coroutine | 0.90 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:133` | `get_or_create_client` 可能無法正確處理 `client` 參數為 `None` 的情況 | 0.80 |
| 🔸 | Minor | `src/prefect/deployments/flow_runs.py:149` | `collect_task_run_inputs` 改為同步呼叫，可能造成效能問題 | 0.70 |
| 🔸 | Minor | `src/prefect/deployments/flow_runs.py:212` | 使用 `deployment_id` 而非 `deployment.id` 可能造成型別不一致 | 0.70 |
| 🔸 | Minor | `src/prefect/deployments/flow_runs.py:231` | 輪詢迴圈中先 sleep 再讀取，可能延遲首次狀態檢查 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:241</code> `run_deployment` 現在是 async 函式，同步呼叫會回傳 coroutine</summary>

原本 `run_deployment` 有 `@sync_compatible` 裝飾器，可同時支援同步與非同步呼叫。現在改成 `run_deployment = arun_deployment`，而 `arun_deployment` 是 async 函式，因此同步呼叫 `run_deployment(...)` 會回傳 coroutine 物件而非 FlowRun。這會破壞既有同步使用者的程式碼，且與專案規範 R07（Async Functions Must Have Sync Compatibility Wrappers Where Public）衝突。

建議：保留一個同步包裝函式，例如使用 `@sync_compatible` 裝飾 `arun_deployment`，或提供獨立的同步版本。

**判斷依據**：diff 中 `run_deployment = arun_deployment` 取代了原本的 `@sync_compatible` 裝飾器。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:133</code> `get_or_create_client` 可能無法正確處理 `client` 參數為 `None` 的情況</summary>

原本使用 `@inject_client` 裝飾器，會自動注入 client 並處理生命週期。現在改為手動呼叫 `get_or_create_client(client)`，但未檢查回傳的 client 是否有效，也未處理可能的例外。此外，`get_or_create_client` 的實作可能與 `inject_client` 不同，例如是否會自動關閉 client。

建議：確認 `get_or_create_client` 的行為，並考慮保留 `@inject_client` 或使用類似的生命週期管理。

**判斷依據**：diff 中新增 `client, _ = get_or_create_client(client)`，取代了原本的 `@inject_client`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/deployments/flow_runs.py:149</code> `collect_task_run_inputs` 改為同步呼叫，可能造成效能問題</summary>

原本 `collect_task_run_inputs` 是 `await` 呼叫，現在改成直接呼叫。如果該函式是 async，這會導致 coroutine 未被 await，可能造成錯誤或效能問題。需要確認 `collect_task_run_inputs` 的實作。

**判斷依據**：diff 中 `k: await collect_task_run_inputs(v)` 改為 `k: collect_task_run_inputs(v)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/deployments/flow_runs.py:212</code> 使用 `deployment_id` 而非 `deployment.id` 可能造成型別不一致</summary>

原本傳入 `deployment.id`，現在改為 `deployment_id`。如果 `deployment_id` 是 UUID 物件，而 API 預期字串，可能造成錯誤。需要確認型別。

**判斷依據**：diff 中 `deployment.id` 改為 `deployment_id`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/deployments/flow_runs.py:231</code> 輪詢迴圈中先 sleep 再讀取，可能延遲首次狀態檢查</summary>

原本先讀取 flow run 狀態，再 sleep。現在改成先 sleep 再讀取，這會導致即使 flow run 已經完成，也要等待一個 poll_interval 才能回傳。如果 poll_interval 較大，會增加不必要的延遲。

**判斷依據**：diff 中 `await anyio.sleep(poll_interval)` 移到 `flow_run = await client.read_flow_run(flow_run_id)` 之前。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8364 (cache hit 8320) ｜ completion tokens 1274 ｜ PR #6</sub>