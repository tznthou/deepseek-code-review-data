<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 `get_plan_bulk_with_cache` 方法，透過 Redis 快取來減少批次作業中對 billing API 的呼叫，並修改了 `get_plan_bulk` 以跳過驗證失敗的 tenant。整體設計合理，但存在幾個需要修正的問題：最嚴重的是 `get_plan_bulk` 中將失敗 tenant 設為 `None` 可能導致下游型別錯誤；快取方法中 pipeline 寫入失敗時會遺失資料；以及測試中使用了 `time.sleep` 可能導致不穩定。建議先修正型別不一致與 pipeline 失敗處理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/billing_service.py:292` | get_plan_bulk 回傳值型別不一致：失敗時設為 None | 0.95 |
| ⚠️ | Major | `api/services/billing_service.py:342` | Redis pipeline 寫入失敗時，快取資料遺失且無重試機制 | 0.85 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_billing_service.py:332` | 測試中使用 time.sleep 可能導致不穩定 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/billing_service.py:292</code> get_plan_bulk 回傳值型別不一致：失敗時設為 None</summary>

在 `get_plan_bulk` 中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式將 `results[tenant_id]` 設為 `None`。但函式回傳型別標註為 `dict[str, SubscriptionPlan]`，且呼叫端（包括新的 `get_plan_bulk_with_cache`）預期每個值都是 `SubscriptionPlan`（TypedDict）。這會導致下游在存取 `plan` 或 `expiration_date` 時發生 `AttributeError` 或 `TypeError`。

**失敗情境**：如果 billing API 回傳的某個 tenant 資料格式錯誤，`get_plan_bulk` 會將該 tenant 對應的值設為 `None`。之後 `get_plan_bulk_with_cache` 將此結果合併到 `tenant_plans` 並回傳，呼叫端若嘗試讀取 `result[tenant_id]['plan']` 就會崩潰。

**建議**：不要將失敗的 tenant 設為 `None`，而是直接跳過（不加入 `results`），或記錄錯誤後繼續。這樣可以保持回傳值型別一致。

**判斷依據**：diff 中新增的 except 區塊內有 `results[tenant_id] = None`，而函式回傳型別為 `dict[str, SubscriptionPlan]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/billing_service.py:342</code> Redis pipeline 寫入失敗時，快取資料遺失且無重試機制</summary>

在 `get_plan_bulk_with_cache` 的 Step 3 中，使用 pipeline 批次寫入 Redis。如果 `pipe.execute()` 拋出例外，程式只記錄錯誤，但不會將資料寫入快取，也不會影響回傳值。這會導致下次查詢時仍然 cache miss，增加 API 負載。雖然不影響正確性，但降低了快取效益。

**失敗情境**：Redis 暫時不可用或 pipeline 執行失敗時，所有從 API 取得的資料都不會被快取，下次相同查詢仍會打到 API。

**建議**：考慮加入簡單的重試機制，或在 pipeline 失敗時降級為逐筆寫入（或至少記錄警告）。

**判斷依據**：diff 中 pipeline 執行被包在 try-except 中，except 區塊僅記錄錯誤，沒有重試或補償措施。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_billing_service.py:332</code> 測試中使用 time.sleep 可能導致不穩定</summary>

在 `test_get_plan_bulk_with_cache_ttl_expired` 測試中，使用 `time.sleep(2)` 等待 Redis key 過期。這會讓測試執行時間增加，且在 CI 環境中可能因為時間誤差而變得不穩定（例如 Redis 的過期機制可能延遲）。

**建議**：改用更可靠的方式模擬過期，例如直接刪除 key，或使用 `redis_client.delete` 來模擬過期。

**判斷依據**：diff 中新增的測試包含 `time.sleep(2)`，且測試名稱暗示依賴時間。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8936 (cache hit 1408) ｜ completion tokens 1084 ｜ PR #10</sub>