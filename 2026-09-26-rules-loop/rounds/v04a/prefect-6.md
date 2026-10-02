<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 `run_deployment` 改為 `arun_deployment`，並以 `run_deployment = arun_deployment` 提供向後相容。主要風險在於移除 `@sync_compatible` 後，同步呼叫路徑可能失效，且 `run_deployment` 的型別與行為可能與預期不符。此外，`client` 參數的取得方式變更可能影響相依性注入。建議先確認同步呼叫的相容性與型別正確性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:241` | 移除 @sync_compatible 可能導致同步呼叫失敗 | 0.80 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:133` | client 參數取得方式變更可能破壞相依性注入 | 0.70 |
| 🔸 | Minor | `src/prefect/deployments/flow_runs.py:149` | collect_task_run_inputs 改為同步呼叫可能造成效能問題 | 0.60 |
| 🔸 | Minor | `src/prefect/deployments/flow_runs.py:212` | 使用 deployment_id 而非 deployment.id 可能造成不一致 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:241</code> 移除 @sync_compatible 可能導致同步呼叫失敗</summary>

原本 `run_deployment` 有 `@sync_compatible` 裝飾器，允許在同步環境中直接呼叫。現在改為 `run_deployment = arun_deployment`，但 `arun_deployment` 是 async 函式，同步呼叫會回傳 coroutine 而非執行結果。若使用者原本在同步程式碼中呼叫 `run_deployment(...)`，現在會得到 coroutine 物件，可能導致未預期的行為。建議保留同步包裝或提供明確的同步版本。

**判斷依據**：diff 中移除 `@sync_compatible` 並在檔案末尾新增 `run_deployment = arun_deployment`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:133</code> client 參數取得方式變更可能破壞相依性注入</summary>

原本使用 `@inject_client` 裝飾器，會自動注入 client 並處理相依性。現在改為手動呼叫 `get_or_create_client(client)`，可能遺漏某些情境（例如在沒有傳入 client 且不在 flow run context 中時，原本的 inject_client 可能提供不同的預設行為）。建議確認 `get_or_create_client` 與原本 `inject_client` 的行為完全一致。

**判斷依據**：diff 中移除 `@inject_client` 並新增 `client, _ = get_or_create_client(client)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/deployments/flow_runs.py:149</code> collect_task_run_inputs 改為同步呼叫可能造成效能問題</summary>

原本 `await collect_task_run_inputs(v)` 改為 `collect_task_run_inputs(v)`，若該函式是 async，則會回傳 coroutine 而未 await，可能導致錯誤。若該函式是同步，則無影響。建議確認 `collect_task_run_inputs` 的型別。

**判斷依據**：diff 中將 `await collect_task_run_inputs(v)` 改為 `collect_task_run_inputs(v)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/deployments/flow_runs.py:212</code> 使用 deployment_id 而非 deployment.id 可能造成不一致</summary>

原本 `deployment.id` 改為 `deployment_id`，但 `deployment_id` 可能為 None（若使用者以名稱呼叫且解析失敗），而 `deployment.id` 是從解析後的 deployment 物件取得，較為可靠。建議確認此變更不會在 deployment_id 為 None 時造成錯誤。

**判斷依據**：diff 中將 `deployment.id` 改為 `deployment_id`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7561 (cache hit 6016) ｜ completion tokens 966 ｜ PR #6</sub>