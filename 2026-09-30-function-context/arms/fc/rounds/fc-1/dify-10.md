<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 get_plan_bulk_with_cache 方法，透過 Redis 快取減少 billing API 呼叫，並修改 get_plan_bulk 以跳過無效資料。整體設計合理，但存在一個 blocker：當 Redis mget 回傳長度不符時，會拋出例外並將所有 tenant 視為 cache miss，導致快取完全失效，且該例外被吞掉，可能隱藏 Redis 問題。另有兩個 major：get_plan_bulk 將無效 tenant 設為 None 可能造成下游型別錯誤；快取寫入使用 bulk_plans 而非 plans_to_cache，可能快取到無效資料。建議先修正 blocker，再處理 major。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/billing_service.py:325` | Redis mget 長度不符時快取完全失效且例外被吞掉 | 0.90 |
| ⚠️ | Major | `api/services/billing_service.py:286` | get_plan_bulk 將無效 tenant 設為 None，可能造成下游型別錯誤 | 0.80 |
| ⚠️ | Major | `api/services/billing_service.py:342` | 快取寫入使用 bulk_plans 而非 plans_to_cache，可能快取到無效資料 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/billing_service.py:325</code> Redis mget 長度不符時快取完全失效且例外被吞掉</summary>

在 `get_plan_bulk_with_cache` 中，若 `redis_client.mget(redis_keys)` 回傳的 list 長度與 `tenant_ids` 不符，程式會拋出例外，但該例外被外層的 `except Exception` 捕捉，僅記錄錯誤並將所有 tenant 設為 cache miss。這導致即使 Redis 正常運作，只要 mget 因任何原因回傳長度不符（例如 Redis 叢集節點變更），快取就會完全失效，且開發者難以察覺。

**失敗情境**：Redis 叢集在 mget 期間發生 failover，導致部分 key 遺失，回傳長度小於請求數量。此時所有 tenant 都會被視為 cache miss，直接呼叫 billing API，失去快取效益。

**建議**：不要將長度不符視為致命錯誤。可改為逐 key 檢查，或僅記錄警告並將缺失的 key 視為 miss。若必須拋出例外，應使用更精確的例外型別，並考慮重試機制。

**判斷依據**：diff 中新增的 `get_plan_bulk_with_cache` 方法內，第 316 行（NEW）的 `raise Exception` 被外層 `except Exception` 捕捉，導致快取失效。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/billing_service.py:286</code> get_plan_bulk 將無效 tenant 設為 None，可能造成下游型別錯誤</summary>

在 `get_plan_bulk` 中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式會將 `results[tenant_id]` 設為 `None`。但函式回傳型別標註為 `dict[str, SubscriptionPlan]`，且呼叫端可能預期每個值都是有效的 `SubscriptionPlan`。這可能導致下游在存取 `plan` 或 `expiration_date` 時發生 `AttributeError` 或 `TypeError`。

**失敗情境**：某 tenant 的 billing API 回傳格式錯誤，`get_plan_bulk` 回傳包含 `None` 的 dict，呼叫端若直接使用 `result[tenant_id]['plan']` 就會崩潰。

**建議**：跳過無效 tenant（不要加入 dict），或回傳一個明確的錯誤物件。若必須保留 `None`，應更新型別標註並在文件說明。

**判斷依據**：diff 中 `get_plan_bulk` 的修改，將無效 tenant 設為 `None`，但回傳型別為 `dict[str, SubscriptionPlan]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/billing_service.py:342</code> 快取寫入使用 bulk_plans 而非 plans_to_cache，可能快取到無效資料</summary>

在 `get_plan_bulk_with_cache` 的 Step 3 中，程式使用 `for tenant_id, subscription_plan in bulk_plans.items()` 來寫入快取，但 `bulk_plans` 是 `get_plan_bulk` 的回傳值，其中可能包含 `None`（若 `get_plan_bulk` 將無效 tenant 設為 `None`）。這會導致將 `None` 序列化為 JSON 字串 `"null"` 存入 Redis，之後讀取時會因驗證失敗而再次視為 cache miss，但已污染快取。

**失敗情境**：`get_plan_bulk` 回傳 `{'tenant-1': None}`，程式將 `None` 寫入 Redis，下次讀取時 `json.loads` 得到 `None`，`validate_python` 失敗，該 tenant 永遠無法命中快取。

**建議**：改為迭代 `plans_to_cache`，或先過濾掉 `None` 值。

**判斷依據**：diff 中 `get_plan_bulk_with_cache` 的 Step 3，使用 `bulk_plans` 而非 `plans_to_cache`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9286 (cache hit 1536) ｜ completion tokens 1422 ｜ PR #10</sub>