<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 `get_plan_bulk_with_cache` 方法，透過 Redis 快取來減少批次作業中對 billing API 的呼叫，並在 `get_plan_bulk` 中加入了對無效資料的容錯處理。整體設計合理，但存在一個關鍵的型別不一致問題：`get_plan_bulk` 在驗證失敗時會將結果設為 `None`，但型別標註仍為 `SubscriptionPlan`，這可能導致下游程式碼在未檢查 `None` 的情況下發生錯誤。此外，快取方法在 Redis 操作失敗時會回退到 API，但回退後仍嘗試寫入快取，若 Redis 持續故障，每次呼叫都會重複此流程，可能造成不必要的延遲。建議優先修正型別不一致問題，並考慮在 Redis 故障時跳過快取寫入。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/services/billing_service.py:292` | 型別不一致：`get_plan_bulk` 可能回傳 `None` 值，但型別標註為 `SubscriptionPlan` | 0.90 |
| 🔸 | Minor | `api/services/billing_service.py:370` | Redis 故障時仍嘗試寫入快取，可能造成不必要的延遲 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>api/services/billing_service.py:292</code> 型別不一致：`get_plan_bulk` 可能回傳 `None` 值，但型別標註為 `SubscriptionPlan`</summary>

在 `get_plan_bulk` 方法中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式碼會將 `results[tenant_id]` 設為 `None`。然而，方法的回傳型別標註為 `dict[str, SubscriptionPlan]`，這表示每個值都應該是 `SubscriptionPlan` 物件，而不是 `None`。這會導致下游呼叫者在未檢查 `None` 的情況下直接存取屬性（例如 `plan['plan']`）時發生 `AttributeError` 或 `TypeError`。

**具體失敗情境**：
1. 某個 tenant 的 billing API 回傳了格式錯誤的資料（例如缺少 `expiration_date` 欄位）。
2. `get_plan_bulk` 將該 tenant 對應的值設為 `None`。
3. 呼叫者（例如 `get_plan_bulk_with_cache` 或其它程式碼）遍歷回傳的字典，並直接使用 `subscription_plan['plan']`，此時會因為 `None` 沒有 `__getitem__` 方法而拋出例外。

**建議修法**：
- 將回傳型別改為 `dict[str, Optional[SubscriptionPlan]]`，並確保所有呼叫者都處理 `None` 的情況。
- 或者，在驗證失敗時直接跳過該 tenant（不加入 `results`），而不是設為 `None`。這樣可以保持型別一致性，但需要確認呼叫者是否依賴於鍵的存在性。

**判斷依據**：diff 中新增的 `except` 區塊內有 `results[tenant_id] = None`，而方法簽章仍為 `def get_plan_bulk(cls, tenant_ids: Sequence[str]) -> dict[str, SubscriptionPlan]`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/services/billing_service.py:370</code> Redis 故障時仍嘗試寫入快取，可能造成不必要的延遲</summary>

在 `get_plan_bulk_with_cache` 方法中，當 Redis `mget` 失敗時，程式碼會回退到呼叫 `get_plan_bulk` 取得資料，然後仍然嘗試使用 pipeline 將結果寫入 Redis。如果 Redis 持續故障（例如連線中斷），每次呼叫都會執行這個寫入嘗試，而寫入操作本身可能會因為連線問題而阻塞或拋出例外，增加不必要的延遲。

**具體失敗情境**：
1. Redis 服務暫時不可用。
2. 呼叫 `get_plan_bulk_with_cache`，`mget` 拋出例外，進入回退流程。
3. 從 API 取得資料後，嘗試建立 pipeline 並執行 `setex`，但由於 Redis 仍不可用，pipeline 執行失敗，記錄例外。
4. 這個流程在每次呼叫時都會重複，即使 Redis 一直不可用，也會不斷嘗試寫入，浪費資源。

**建議修法**：
- 在 `mget` 失敗時，設定一個標誌（例如 `redis_available = False`），並在後續的寫入步驟中檢查此標誌，若為 `False` 則跳過寫入。
- 或者，將寫入操作包裹在單獨的 `try-except` 中，但考慮到效能，最好在已知 Redis 不可用時完全跳過。

**判斷依據**：在 `except` 區塊中記錄了 `redis mget failed, falling back to API`，但之後的程式碼沒有檢查 Redis 是否可用，直接進入寫入流程。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8972 (cache hit 1536) ｜ completion tokens 1273 ｜ PR #10</sub>