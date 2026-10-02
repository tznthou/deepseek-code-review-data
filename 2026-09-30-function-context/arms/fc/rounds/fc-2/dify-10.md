<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 get_plan_bulk_with_cache 方法，利用 Redis 快取批次取得租用戶方案，並修改 get_plan_bulk 以跳過無效資料。主要風險在於快取資料可能包含 None 值，導致後續使用時發生型別錯誤；此外，快取寫入使用 bulk_plans 而非 plans_to_cache，可能快取到無效資料。建議先修正 None 值處理與快取寫入邏輯。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/billing_service.py:292` | get_plan_bulk 可能回傳包含 None 的 dict，導致型別錯誤 | 0.95 |
| ⚠️ | Major | `api/services/billing_service.py:344` | 快取寫入使用 bulk_plans 而非 plans_to_cache，可能快取到無效資料 | 0.85 |
| 🔸 | Minor | `api/services/billing_service.py:326` | Redis mget 回傳長度不符時拋出例外，但未記錄 tenant_ids | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/billing_service.py:292</code> get_plan_bulk 可能回傳包含 None 的 dict，導致型別錯誤</summary>

在 get_plan_bulk 中，當 subscription_adapter.validate_python(plan) 失敗時，會將 results[tenant_id] 設為 None。這使得回傳的 dict 型別為 dict[str, Optional[SubscriptionPlan]]，但函式標註為 dict[str, SubscriptionPlan]。呼叫端（如 get_plan_bulk_with_cache）若直接使用這些值，可能遇到 None 而導致 AttributeError 或型別錯誤。建議在 get_plan_bulk 中跳過無效資料，或將回傳型別改為 dict[str, Optional[SubscriptionPlan]] 並在呼叫端處理 None。

**判斷依據**：diff 中新增的 except 區塊：`results[tenant_id] = None`，而函式回傳型別為 `dict[str, SubscriptionPlan]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/billing_service.py:344</code> 快取寫入使用 bulk_plans 而非 plans_to_cache，可能快取到無效資料</summary>

在 get_plan_bulk_with_cache 中，plans_to_cache 被建立但未使用，實際寫入快取時迭代的是 bulk_plans。若 bulk_plans 中包含 None 值（來自 get_plan_bulk 的錯誤處理），則會將 None 序列化為 'null' 寫入 Redis，後續讀取時 json.loads 會得到 None，導致 validate_python 失敗。建議改為迭代 plans_to_cache，或確保 bulk_plans 不包含 None。

**判斷依據**：diff 中建立 plans_to_cache 後，在 pipeline 迴圈中卻使用 bulk_plans。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/services/billing_service.py:326</code> Redis mget 回傳長度不符時拋出例外，但未記錄 tenant_ids</summary>

當 redis_client.mget 回傳的 list 長度與 tenant_ids 不符時，程式拋出例外並記錄錯誤，但未包含 tenant_ids 資訊，不利於除錯。建議在錯誤訊息中加入 tenant_ids 或相關上下文。

**判斷依據**：diff 中 raise Exception 的訊息未包含 tenant_ids。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9286 (cache hit 9216) ｜ completion tokens 831 ｜ PR #10</sub>