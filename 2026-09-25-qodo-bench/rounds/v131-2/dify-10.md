<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 `get_plan_bulk_with_cache` 方法，透過 Redis 快取來減少批次作業中對 billing API 的呼叫，並修改了 `get_plan_bulk` 以跳過驗證失敗的 tenant。整體設計合理，但存在一些錯誤處理與型別安全問題，可能導致資料不一致或意外行為。最需要注意的是 `get_plan_bulk` 中將驗證失敗的 tenant 設為 `None` 可能違反型別契約，以及快取寫入時未過濾 `None` 值。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/services/billing_service.py:292` | 驗證失敗時將結果設為 None 可能違反型別契約 | 0.80 |
| ⚠️ | Major | `api/services/billing_service.py:342` | 快取寫入時未過濾 None 值 | 0.75 |
| 🔸 | Minor | `api/services/billing_service.py:325` | Redis mget 回傳長度檢查可能誤判 | 0.70 |
| 🔸 | Minor | `api/services/billing_service.py:337` | 快取值解碼時未處理非 bytes 型別 | 0.65 |
| 🔸 | Minor | `api/services/billing_service.py:352` | 快取寫入 pipeline 失敗時未記錄詳細資訊 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/services/billing_service.py:292</code> 驗證失敗時將結果設為 None 可能違反型別契約</summary>

在 `get_plan_bulk` 中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式碼將 `results[tenant_id]` 設為 `None`。但函式回傳型別標註為 `dict[str, SubscriptionPlan]`，且呼叫端（如 `get_plan_bulk_with_cache`）預期每個值都是有效的 `SubscriptionPlan`。這可能導致後續程式碼在存取 `plan` 或 `expiration_date` 時拋出 `AttributeError` 或 `TypeError`。

建議：跳過該 tenant（不要加入 `results`），或記錄錯誤後重新拋出例外，讓呼叫端決定如何處理。

**判斷依據**：diff 中新增的 `except` 區塊內將 `results[tenant_id]` 設為 `None`，而函式回傳型別為 `dict[str, SubscriptionPlan]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/billing_service.py:342</code> 快取寫入時未過濾 None 值</summary>

在 `get_plan_bulk_with_cache` 中，從 `get_plan_bulk` 取得的 `bulk_plans` 可能包含值為 `None` 的項目（因為 `get_plan_bulk` 在驗證失敗時會將該 tenant 設為 `None`）。程式碼直接將這些項目加入 `plans_to_cache` 並序列化為 JSON 寫入 Redis。這會導致快取中存有 `null` 值，之後讀取時 `json.loads` 會得到 `None`，再傳給 `validate_python` 會拋出例外，造成不必要的 cache miss 和 API 呼叫。

建議：在寫入快取前過濾掉值為 `None` 的項目，或修改 `get_plan_bulk` 不要回傳 `None`。

**判斷依據**：diff 中 `get_plan_bulk_with_cache` 的 Step 2 直接將 `bulk_plans` 的所有項目加入 `plans_to_cache`，未檢查 `subscription_plan` 是否為 `None`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/services/billing_service.py:325</code> Redis mget 回傳長度檢查可能誤判</summary>

程式碼檢查 `len(cached_values) != len(tenant_ids)` 來判斷 mget 是否失敗，但 Redis 的 `mget` 在 key 不存在時會回傳 `None`，長度仍然等於輸入的 key 數量。因此這個檢查無法偵測到 key 不存在的情況，但這並非錯誤，因為後續會將 `None` 視為 cache miss。然而，如果 Redis 發生其他錯誤（如連線中斷），`mget` 可能拋出例外，此處的長度檢查就沒有意義。建議移除這個檢查，直接依賴例外處理。

**判斷依據**：diff 中新增的長度檢查，但 Redis mget 在正常情況下長度一定等於輸入 key 數量，即使 key 不存在。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/services/billing_service.py:337</code> 快取值解碼時未處理非 bytes 型別</summary>

程式碼使用 `cached_value.decode("utf-8") if isinstance(cached_value, bytes) else cached_value` 來處理 Redis 回傳值。但 Redis 客戶端可能回傳 `str` 或其他型別（例如 `bytearray`），若回傳 `bytearray`，`isinstance` 檢查會失敗，導致 `json.loads` 收到非字串型別而拋出例外。雖然目前常見的 Redis 客戶端回傳 `bytes` 或 `str`，但為了穩健性，建議明確處理所有可能的型別。

**判斷依據**：diff 中對 `cached_value` 的型別判斷僅限於 `bytes`，未涵蓋其他可能的型別。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/services/billing_service.py:352</code> 快取寫入 pipeline 失敗時未記錄詳細資訊</summary>

在 `pipe.execute()` 失敗時，程式碼僅記錄 `logger.exception("get_plan_bulk_with_cache: redis pipeline failed")`，未包含 tenant_ids 或錯誤詳情。這可能導致除錯困難。建議在日誌中加入更多上下文，例如失敗的 key 或例外訊息。

**判斷依據**：diff 中 pipeline 失敗的例外處理僅記錄固定訊息，未包含變數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8936 (cache hit 8832) ｜ completion tokens 1556 ｜ PR #10</sub>