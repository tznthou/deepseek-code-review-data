<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 get_plan_bulk_with_cache 方法，利用 Redis 快取來減少批次作業中對 billing API 的呼叫，並修改了 get_plan_bulk 以跳過無效的租戶資料。整體設計合理，但存在一些正確性與可維護性問題：快取寫入時序列化 SubscriptionPlan 可能失敗、快取資料驗證失敗時未清除無效快取、以及 get_plan_bulk 中將無效租戶設為 None 可能導致下游型別錯誤。建議優先修正序列化與型別問題，並考慮清除無效快取。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/services/billing_service.py:376` | json.dumps(subscription_plan) 可能失敗，導致快取寫入中斷 | 0.80 |
| ⚠️ | Major | `api/services/billing_service.py:292` | get_plan_bulk 將無效租戶設為 None，可能導致下游型別錯誤 | 0.75 |
| 🔸 | Minor | `api/services/billing_service.py:330` | 快取資料驗證失敗時未清除無效快取，可能導致重複失敗 | 0.70 |
| 🔸 | Minor | `api/services/billing_service.py:28` | [R21] 新增 __str__ 方法可能違反不必要的 dunder 覆寫規範 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/services/billing_service.py:376</code> json.dumps(subscription_plan) 可能失敗，導致快取寫入中斷</summary>

在 `get_plan_bulk_with_cache` 中，從 `get_plan_bulk` 取得的 `subscription_plan` 是 `SubscriptionPlan` 型別（TypedDict），但 `json.dumps` 預期可序列化的物件。若 `SubscriptionPlan` 包含非 JSON 相容的型別（例如 datetime、Decimal 等），`json.dumps` 會拋出 `TypeError`，導致整個 pipeline 執行失敗，且該例外被外層 `except` 捕捉後僅記錄日誌，不會寫入任何快取。

**失敗情境**：當 billing API 回傳的 `expiration_date` 是 ISO 格式字串而非整數時，`validate_python` 可能將其轉為 datetime 物件，此時 `json.dumps` 會失敗。

**建議**：在序列化前先將 `subscription_plan` 轉為純 dict（例如 `dict(subscription_plan)`），或使用 Pydantic 的 `model_dump()` 方法（若改用 BaseModel）。

**判斷依據**：diff 中新增的 `json.dumps(subscription_plan)` 行，其中 `subscription_plan` 來自 `bulk_plans`，而 `bulk_plans` 是 `get_plan_bulk` 的回傳值，型別為 `dict[str, SubscriptionPlan]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/billing_service.py:292</code> get_plan_bulk 將無效租戶設為 None，可能導致下游型別錯誤</summary>

在 `get_plan_bulk` 中，當 `validate_python` 失敗時，程式碼將 `results[tenant_id]` 設為 `None`。但函式的回傳型別標註為 `dict[str, SubscriptionPlan]`，且呼叫端（例如 `get_plan_bulk_with_cache`）預期每個值都是 `SubscriptionPlan`。若下游程式碼直接存取 `result[tenant_id]['plan']`，會遇到 `TypeError: 'NoneType' object is not subscriptable`。

**失敗情境**：當某個租戶的 billing API 回傳格式錯誤時，該租戶在結果中為 `None`，而呼叫端未檢查 `None` 就使用，導致執行時期錯誤。

**建議**：不要將無效租戶放入結果字典，或將回傳型別改為 `dict[str, SubscriptionPlan | None]` 並要求呼叫端處理 `None`。

**判斷依據**：diff 中新增的 `results[tenant_id] = None` 行，位於 `except Exception` 區塊內。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/services/billing_service.py:330</code> 快取資料驗證失敗時未清除無效快取，可能導致重複失敗</summary>

在 `get_plan_bulk_with_cache` 中，當從 Redis 讀取的快取資料無法通過 `validate_python` 驗證時，程式碼將該租戶加入 `cache_misses`，但未刪除 Redis 中的無效鍵。這會導致每次呼叫都重複嘗試解析無效資料，並在日誌中產生大量錯誤。

**失敗情境**：若某租戶的快取因版本變更而格式不符，每次批次作業都會嘗試解析並失敗，直到 TTL 過期。

**建議**：在驗證失敗時，主動刪除該租戶的 Redis 鍵（例如 `redis_client.delete(redis_key)`），或使用較短的 TTL 來加速失效。

**判斷依據**：diff 中新增的例外處理區塊，僅記錄日誌並加入 `cache_misses`，未刪除無效鍵。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/services/billing_service.py:28</code> [R21] 新增 __str__ 方法可能違反不必要的 dunder 覆寫規範</summary>

在 `SubscriptionPlan` TypedDict 中新增了 `__str__` 方法，用於除錯。但 TypedDict 通常不應定義方法，且此方法僅用於日誌輸出，可能違反專案規範 R21（避免不必要的 dunder 方法覆寫）。

**建議**：若僅為除錯，可考慮使用 `repr()` 或直接在日誌中格式化 dict，而不覆寫 `__str__`。

**判斷依據**：diff 中新增的 `__str__` 方法定義。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11650 (cache hit 1536) ｜ completion tokens 1489 ｜ PR #10</sub>