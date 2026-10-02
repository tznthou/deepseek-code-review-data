<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了 get_plan_bulk_with_cache 方法，透過 Redis 快取來減少批次作業中對 billing API 的呼叫，並在 get_plan_bulk 中加入了對無效資料的跳過處理。整體設計合理，但存在幾個需要修正的問題：最嚴重的是在快取寫入時使用了錯誤的變數 bulk_plans 而非 plans_to_cache，可能導致快取不一致；此外，SubscriptionPlan 是 TypedDict，json.dumps 可以正常序列化，但需注意型別相容性；測試中使用了 time.sleep 來模擬 TTL 過期，可能導致測試不穩定。建議修正這些問題後再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/billing_service.py:350` | 快取寫入時使用了錯誤的變數 bulk_plans 而非 plans_to_cache | 0.95 |
| ⚠️ | Major | `api/services/billing_service.py:376` | 快取寫入時可能將 None 序列化為 'null' 字串 | 0.85 |
| ⚠️ | Major | `api/services/billing_service.py:376` | 快取寫入時未處理 json.dumps 可能拋出的例外 | 0.80 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_billing_service.py:332` | 測試中使用 time.sleep 模擬 TTL 過期可能導致不穩定 | 0.70 |
| 🔸 | Minor | `api/services/billing_service.py:372` | 快取寫入時未使用 pipeline 的上下文管理器 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/billing_service.py:350</code> 快取寫入時使用了錯誤的變數 bulk_plans 而非 plans_to_cache</summary>

在 Step 3 的快取寫入迴圈中，程式碼遍歷的是 `bulk_plans.items()`，但 `bulk_plans` 是從 `get_plan_bulk` 回傳的完整字典，而 `plans_to_cache` 才是經過篩選、只包含需要快取的項目。這會導致即使某個 tenant 的 plan 驗證失敗（在 `get_plan_bulk` 中被設為 `None`），仍然會被寫入快取，造成快取中存有無效資料。

**失敗情境**：假設 `get_plan_bulk` 回傳 `{'tenant-1': valid_plan, 'tenant-2': None}`，則 `plans_to_cache` 只包含 `tenant-1`，但迴圈會將 `tenant-2` 也寫入快取，值為 `None`。下次讀取快取時，`json.loads('null')` 會得到 `None`，然後 `subscription_adapter.validate_python(None)` 會拋出例外，導致該 tenant 被視為 cache miss，但實際上快取中已有無效資料。

**建議修法**：將迴圈改為遍歷 `plans_to_cache.items()`。

**判斷依據**：diff 中第 350 行（新增側）顯示 `for tenant_id, subscription_plan in bulk_plans.items():`，而前一行是 `if plans_to_cache:`，且 `plans_to_cache` 是在前一個迴圈中只加入有效 plan 的字典。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/billing_service.py:376</code> 快取寫入時可能將 None 序列化為 'null' 字串</summary>

即使修正了變數名稱，如果 `plans_to_cache` 中包含值為 `None` 的項目（例如 `get_plan_bulk` 回傳的字典中某個 tenant 的值為 `None`），`json.dumps(None)` 會產生字串 `'null'`。之後讀取快取時，`json.loads('null')` 會得到 `None`，然後 `validate_python(None)` 會拋出例外，導致該 tenant 被視為 cache miss，但實際上快取中已有無效資料。

**失敗情境**：`get_plan_bulk` 回傳 `{'tenant-1': None}`，`plans_to_cache` 包含 `tenant-1`，寫入快取的值為 `'null'`。下次讀取時，`json.loads` 得到 `None`，驗證失敗，進入 cache miss，重新呼叫 API，但 API 可能再次回傳 `None`，形成無效快取。

**建議修法**：在寫入快取前，過濾掉值為 `None` 的項目，或確保 `get_plan_bulk` 不會回傳 `None` 值。

**判斷依據**：diff 中第 352 行（新增側）顯示 `json_str = json.dumps(subscription_plan)`，而 `subscription_plan` 的型別是 `SubscriptionPlan`，但 `get_plan_bulk` 可能回傳 `None`（在驗證失敗時）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/billing_service.py:376</code> 快取寫入時未處理 json.dumps 可能拋出的例外</summary>

`json.dumps(subscription_plan)` 可能因為 `subscription_plan` 包含不可序列化的物件而拋出 `TypeError`。雖然 `SubscriptionPlan` 是 `TypedDict`，但實際值可能包含其他型別（例如 `datetime` 物件），導致序列化失敗。此例外會中斷整個 pipeline 的執行，且不會被外層的 `try` 捕捉（因為 `try` 只包住 `pipe.execute()`）。

**失敗情境**：如果 `subscription_plan` 中包含一個 `datetime` 物件，`json.dumps` 會拋出 `TypeError`，導致整個快取寫入失敗，且沒有記錄任何錯誤。

**建議修法**：將 `json.dumps` 移入 `try` 區塊，或使用 `default=str` 參數來處理不可序列化的物件。

**判斷依據**：diff 中第 352 行（新增側）顯示 `json_str = json.dumps(subscription_plan)`，且該行不在 `try` 區塊內。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_billing_service.py:332</code> 測試中使用 time.sleep 模擬 TTL 過期可能導致不穩定</summary>

在 `test_get_plan_bulk_with_cache_ttl_expired` 測試中，使用 `time.sleep(2)` 來等待 TTL 過期。這會讓測試執行時間增加，且在某些環境下（例如 Redis 的 TTL 精度或系統負載）可能仍然無法保證 key 已過期，導致測試偶發性失敗。

**建議修法**：使用 `redis_client.delete` 直接刪除 key 來模擬過期，或使用 `unittest.mock.patch` 來模擬 `redis_client.exists` 回傳 0。

**判斷依據**：diff 中第 300 行（新增側）顯示 `time.sleep(2)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/services/billing_service.py:372</code> 快取寫入時未使用 pipeline 的上下文管理器</summary>

`redis_client.pipeline()` 通常建議使用 `with` 語句來確保資源正確釋放。雖然目前程式碼在 `try` 區塊中呼叫 `pipe.execute()`，但如果 `pipe.execute()` 拋出例外，pipeline 物件可能不會被正確關閉，導致連線洩漏。

**建議修法**：使用 `with redis_client.pipeline() as pipe:` 來管理 pipeline 的生命週期。

**判斷依據**：diff 中第 349 行（新增側）顯示 `pipe = redis_client.pipeline()`，且沒有使用 `with`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11650 (cache hit 11648) ｜ completion tokens 1861 ｜ PR #10</sub>