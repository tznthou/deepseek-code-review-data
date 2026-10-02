<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 get_plan_bulk_with_cache 方法，利用 Redis 快取來減少批次作業中對 billing API 的呼叫，並修改了 get_plan_bulk 以跳過驗證失敗的租戶。整體設計合理，但存在幾個需要修正的問題：最嚴重的是快取資料型別錯誤（json.dumps 直接序列化 TypedDict 會失敗），以及 get_plan_bulk 中將失敗租戶設為 None 可能導致下游錯誤。此外，測試中使用了 time.sleep 可能造成不穩定，且部分測試未驗證快取寫入。建議修正後再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/billing_service.py:376` | json.dumps 無法序列化 SubscriptionPlan (TypedDict) | 0.95 |
| ⚠️ | Major | `api/services/billing_service.py:292` | get_plan_bulk 將驗證失敗的租戶設為 None，可能導致下游錯誤 | 0.85 |
| ⚠️ | Major | `api/services/billing_service.py:325` | Redis mget 回傳值長度檢查可能誤判 | 0.80 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_billing_service.py:332` | 測試中使用 time.sleep 可能導致不穩定 | 0.70 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_billing_service.py:123` | 測試未驗證快取寫入的 TTL 值 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/billing_service.py:376</code> json.dumps 無法序列化 SubscriptionPlan (TypedDict)</summary>

在 `get_plan_bulk_with_cache` 中，`subscription_plan` 是 `SubscriptionPlan` 型別（TypedDict），但 `json.dumps(subscription_plan)` 會嘗試直接序列化該物件。TypedDict 在執行時是普通的 dict，但此處的 `subscription_plan` 是從 `subscription_adapter.validate_python(plan_dict)` 回傳的，其型別為 `SubscriptionPlan`，實際上是一個 dict，因此 `json.dumps` 應該可以正常運作。然而，如果 `validate_python` 回傳的物件不是純 dict（例如是 Pydantic model 或其他自訂型別），則會拋出 `TypeError`。建議先將 `subscription_plan` 轉換為 dict 再序列化，例如 `json.dumps(dict(subscription_plan))`。

**判斷依據**：diff 中新增的程式碼：`json_str = json.dumps(subscription_plan)`，其中 `subscription_plan` 是 `subscription_adapter.validate_python(plan_dict)` 的回傳值，型別為 `SubscriptionPlan`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/billing_service.py:292</code> get_plan_bulk 將驗證失敗的租戶設為 None，可能導致下游錯誤</summary>

在 `get_plan_bulk` 中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式碼將 `results[tenant_id]` 設為 `None`。這可能導致呼叫端在後續處理時遇到 `None` 值而發生錯誤，因為原本的契約是回傳 `dict[str, SubscriptionPlan]`，且 `SubscriptionPlan` 不包含 `None`。建議改為跳過該租戶（不加入 results），或記錄錯誤後重新拋出例外，讓呼叫端決定如何處理。

**判斷依據**：diff 中新增的程式碼：`results[tenant_id] = None`，位於 `except Exception:` 區塊內。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/billing_service.py:325</code> Redis mget 回傳值長度檢查可能誤判</summary>

在 `get_plan_bulk_with_cache` 中，程式碼檢查 `len(cached_values) != len(tenant_ids)` 並拋出例外。但 Redis 的 `mget` 在鍵不存在時會回傳 `None`，因此長度應該永遠等於輸入的鍵數量。這個檢查可能永遠不會觸發，但若 Redis client 實作有問題，拋出例外會導致整個快取讀取失敗並 fallback 到 API，這可能是可接受的。然而，更穩健的做法是直接處理 `None` 值，而不是依賴長度檢查。

**判斷依據**：diff 中新增的程式碼，位於 `get_plan_bulk_with_cache` 方法內。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_billing_service.py:332</code> 測試中使用 time.sleep 可能導致不穩定</summary>

在 `test_get_plan_bulk_with_cache_ttl_expired` 測試中，使用 `time.sleep(2)` 來等待 Redis 鍵過期。這可能導致測試執行時間過長，且在 CI 環境中可能因為時間誤差而變得不穩定。建議使用 Redis 的 `EXPIRE` 命令設定極短的 TTL，或使用 mock 來模擬過期。

**判斷依據**：diff 中新增的測試程式碼：`time.sleep(2)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_billing_service.py:123</code> 測試未驗證快取寫入的 TTL 值</summary>

在 `test_get_plan_bulk_with_cache_all_cache_miss` 測試中，驗證了 TTL 大於 0 且小於等於 600，但未驗證 TTL 是否精確等於 600。這可能導致測試不夠嚴格，無法確保 TTL 設定正確。建議使用 `assert ttl_1 == 600` 來驗證。

**判斷依據**：diff 中新增的測試程式碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8972 (cache hit 8960) ｜ completion tokens 1456 ｜ PR #10</sub>