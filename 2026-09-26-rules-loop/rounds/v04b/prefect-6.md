<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 `run_deployment` 改為 `arun_deployment` 並以別名保留向後相容，同時引入 `@async_dispatch` 機制。主要風險在於 `run_deployment` 別名在同步上下文中可能無法正確運作，因為 `arun_deployment` 是純 async 函式，且 `_sync` 參數未在函式簽名中定義。此外，`collect_task_run_inputs` 的呼叫被改為同步，可能導致協程物件未 await 而產生錯誤。建議先確認同步相容性與參數傳遞的正確性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/deployments/flow_runs.py:241` | `run_deployment` 別名在同步上下文中無法運作 | 0.95 |
| 🛑 | Blocker | `src/prefect/deployments/flow_runs.py:149` | `collect_task_run_inputs` 呼叫未 await，可能產生未執行的協程 | 0.90 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:133` | `get_or_create_client` 回傳的 client 可能為 None 未處理 | 0.80 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:212` | 使用 `deployment_id` 而非 `deployment.id` 可能導致型別錯誤 | 0.75 |
| 🔸 | Minor | `src/prefect/deployments/flow_runs.py:231` | 輪詢迴圈中先 sleep 再檢查狀態，可能延遲最終結果 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/deployments/flow_runs.py:241</code> `run_deployment` 別名在同步上下文中無法運作</summary>

`run_deployment` 被直接指派為 `arun_deployment`，但 `arun_deployment` 是 async 函式，沒有同步包裝。在同步上下文中呼叫 `run_deployment(...)` 會回傳 coroutine 物件，不會執行流程，導致呼叫者誤以為已建立 flow run。此外，測試中使用了 `_sync=True` 參數，但函式簽名中沒有此參數，會引發 `TypeError`。建議使用 `@sync_compatible` 裝飾器或提供明確的同步包裝函式。

**判斷依據**：diff 中新增 `run_deployment = arun_deployment`，且 `arun_deployment` 定義為 `async def`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/deployments/flow_runs.py:149</code> `collect_task_run_inputs` 呼叫未 await，可能產生未執行的協程</summary>

原本 `await collect_task_run_inputs(v)` 被改為 `collect_task_run_inputs(v)`，若該函式為 async，則會建立 coroutine 物件但未執行，導致 `task_inputs` 中包含未 await 的協程，後續使用時可能引發錯誤或產生不正確的輸入。請確認 `collect_task_run_inputs` 是否為 async，若是則必須保留 `await`。

**判斷依據**：diff 中將 `await collect_task_run_inputs(v)` 改為 `collect_task_run_inputs(v)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:133</code> `get_or_create_client` 回傳的 client 可能為 None 未處理</summary>

`client, _ = get_or_create_client(client)` 若 `client` 參數為 None 且無法建立 client，可能回傳 None，後續 `client.read_deployment` 會拋出 `AttributeError`。建議檢查回傳值或確保 `get_or_create_client` 總會回傳有效 client。

**判斷依據**：diff 中新增此行，且後續使用 `client.read_deployment`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:212</code> 使用 `deployment_id` 而非 `deployment.id` 可能導致型別錯誤</summary>

`client.create_flow_run_from_deployment` 的第一個參數原本是 `deployment.id`，現在改為 `deployment_id`。若 `deployment_id` 是字串（例如 deployment 名稱），而 API 預期 UUID，可能導致錯誤。請確認 `deployment_id` 的型別與 API 要求一致。

**判斷依據**：diff 中將 `deployment.id` 改為 `deployment_id`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/deployments/flow_runs.py:231</code> 輪詢迴圈中先 sleep 再檢查狀態，可能延遲最終結果</summary>

原本先檢查狀態再 sleep，現在改為先 sleep 再檢查。若 flow run 在 sleep 期間完成，會多等待一個 `poll_interval` 才回傳。雖然影響不大，但可能增加不必要的延遲。建議恢復原本順序。

**判斷依據**：diff 中將 `await anyio.sleep(poll_interval)` 移到迴圈開頭。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7561 (cache hit 7552) ｜ completion tokens 1230 ｜ PR #6</sub>