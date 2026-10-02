<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 `run_deployment` 改為 `arun_deployment` 並以 `run_deployment = arun_deployment` 提供向後相容，同時引入 `@async_dispatch` 裝飾器（推測）以支援同步/非同步呼叫。主要風險在於 `get_or_create_client` 的回傳值處理、`deployment_id` 可能為 `None` 時傳入 `create_flow_run_from_deployment`、以及 `collect_task_run_inputs` 改為同步呼叫可能造成事件迴圈阻塞。測試新增完整，但部分測試可能依賴未顯示的 `@async_dispatch` 實作。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:133` | `get_or_create_client` 回傳值未檢查，可能導致 `client` 為 `None` | 0.80 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:211` | `deployment_id` 可能為 `None` 時傳入 `create_flow_run_from_deployment` | 0.75 |
| 🔸 | Minor | `src/prefect/deployments/flow_runs.py:149` | `collect_task_run_inputs` 改為同步呼叫可能阻塞事件迴圈 | 0.60 |
| 🔸 | Minor | `src/prefect/deployments/flow_runs.py:230` | 輪詢迴圈中 `await anyio.sleep(poll_interval)` 移至開頭可能延遲首次檢查 | 0.50 |
| 🔸 | Minor | `tests/deployment/test_flow_runs.py:930` | 測試中 `run_deployment` 使用 `_sync=True` 參數，但函式簽名未顯示該參數 | 0.40 |

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:133</code> `get_or_create_client` 回傳值未檢查，可能導致 `client` 為 `None`</summary>

`get_or_create_client` 可能回傳 `None`（例如無法建立 client 時），但後續直接使用 `client.read_deployment` 等，會導致 `AttributeError`。建議檢查回傳值或確保該函式必定回傳有效 client。

**判斷依據**：diff 中新增 `client, _ = get_or_create_client(client)`，但未檢查 `client` 是否為 `None`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:211</code> `deployment_id` 可能為 `None` 時傳入 `create_flow_run_from_deployment`</summary>

若 `name` 不是 UUID 且找不到對應 deployment，`deployment_id` 會是 `None`，但此處直接傳入 `create_flow_run_from_deployment`，可能導致 API 錯誤或未定義行為。建議在呼叫前檢查 `deployment_id` 是否存在。

**判斷依據**：diff 中將 `deployment.id` 改為 `deployment_id`，但 `deployment_id` 可能為 `None`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/deployments/flow_runs.py:149</code> `collect_task_run_inputs` 改為同步呼叫可能阻塞事件迴圈</summary>

原本 `await collect_task_run_inputs(v)` 改為 `collect_task_run_inputs(v)`，若該函式內部有非同步操作，可能導致事件迴圈阻塞或錯誤。需確認 `collect_task_run_inputs` 是否為同步函式。

**判斷依據**：diff 中移除 `await`，但未確認函式同步性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/deployments/flow_runs.py:230</code> 輪詢迴圈中 `await anyio.sleep(poll_interval)` 移至開頭可能延遲首次檢查</summary>

原本先檢查狀態再 sleep，現在先 sleep 再檢查，若 `poll_interval` 較大，會延遲首次狀態檢查。若 `timeout` 小於 `poll_interval`，可能直接超時而無法取得最終狀態。

**判斷依據**：diff 中將 `await anyio.sleep(poll_interval)` 移到迴圈開頭。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/deployment/test_flow_runs.py:930</code> 測試中 `run_deployment` 使用 `_sync=True` 參數，但函式簽名未顯示該參數</summary>

測試呼叫 `run_deployment(..., _sync=True)`，但 `arun_deployment` 的簽名中沒有 `_sync` 參數。若 `@async_dispatch` 未正確處理，測試可能失敗。需確認裝飾器實作。

**判斷依據**：diff 中測試使用 `_sync=True`，但函式定義未見該參數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8354 (cache hit 8320) ｜ completion tokens 1202 ｜ PR #6</sub>