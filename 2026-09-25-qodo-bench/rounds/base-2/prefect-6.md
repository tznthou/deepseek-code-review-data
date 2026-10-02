<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 `run_deployment` 改為 `arun_deployment`，並以 `run_deployment = arun_deployment` 保留向後相容。主要風險在於 `run_deployment` 現在是 async 函式，同步呼叫時會回傳 coroutine 而非執行，可能導致既有同步程式碼失效。此外，`get_or_create_client` 的回傳值處理、`collect_task_run_inputs` 的 await 移除、以及 `deployment_id` 的使用方式都需要進一步確認。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:133` | `get_or_create_client` 回傳值未正確處理 | 0.80 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:241` | `run_deployment` 別名導致同步呼叫失效 | 0.80 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:149` | 移除 `await` 可能導致未完成的 coroutine | 0.70 |
| ⚠️ | Major | `src/prefect/deployments/flow_runs.py:212` | 使用 `deployment_id` 而非 `deployment.id` 可能導致錯誤 | 0.70 |
| 🔸 | Minor | `src/prefect/deployments/flow_runs.py:231` | 輪詢順序變更可能影響 timeout 行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:133</code> `get_or_create_client` 回傳值未正確處理</summary>

`get_or_create_client` 可能回傳一個 tuple `(client, context_manager)`，但程式碼只取第一個元素並指派給 `client`。如果回傳的 client 是透過 context manager 建立的，則在函式結束後可能無法正確關閉，導致資源洩漏。建議確認 `get_or_create_client` 的實作，並使用 `async with` 或確保 client 生命週期正確。

**判斷依據**：diff 中新增的這一行，將回傳值解包為 `client, _`，但未使用第二個元素。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:241</code> `run_deployment` 別名導致同步呼叫失效</summary>

`run_deployment = arun_deployment` 使得 `run_deployment` 成為 async 函式。原本使用 `@sync_compatible` 裝飾器時，同步呼叫會自動執行；現在同步呼叫會回傳 coroutine 而不會執行，導致既有同步程式碼失效。建議保留一個同步包裝函式，或使用 `@async_dispatch` 裝飾器來處理同步/非同步分派。

**判斷依據**：diff 中新增的別名指派，移除了原本的 `@sync_compatible` 裝飾器。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:149</code> 移除 `await` 可能導致未完成的 coroutine</summary>

原本 `await collect_task_run_inputs(v)` 被改為 `collect_task_run_inputs(v)`，如果該函式是 async，則會回傳 coroutine 物件而不會執行，導致 `task_inputs` 中包含未完成的 coroutine，後續使用時可能出錯。建議確認 `collect_task_run_inputs` 是否為 async，若是則應保留 `await`。

**判斷依據**：diff 中將 `await` 移除，但未提供 `collect_task_run_inputs` 的實作內容。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/deployments/flow_runs.py:212</code> 使用 `deployment_id` 而非 `deployment.id` 可能導致錯誤</summary>

原本使用 `deployment.id`，現在改為 `deployment_id`。如果 `deployment_id` 是從名稱解析而來，且解析失敗時可能為 `None`，則會傳遞 `None` 給 API，導致錯誤。建議確認 `deployment_id` 在此處一定有效。

**判斷依據**：diff 中將 `deployment.id` 改為 `deployment_id`，但未檢查 `deployment_id` 是否為 `None`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/deployments/flow_runs.py:231</code> 輪詢順序變更可能影響 timeout 行為</summary>

原本先讀取 flow run 再 sleep，現在改為先 sleep 再讀取。這會導致即使 timeout 為 0，也會先 sleep 一次，可能延遲回傳。建議確認此變更是否符合預期。

**判斷依據**：diff 中將 `await anyio.sleep(poll_interval)` 移到迴圈開頭。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6860 (cache hit 6784) ｜ completion tokens 1172 ｜ PR #6</sub>