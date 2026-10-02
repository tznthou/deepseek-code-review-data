<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這次 PR 新增了 `get_plan_bulk_with_cache` 方法，利用 Redis 快取來減少批次查詢 billing API 的負載，並在 `get_plan_bulk` 中加入了對無效資料的跳過處理。整體設計合理，但存在幾個需要修正的問題：最嚴重的是 `get_plan_bulk` 現在會將無效租戶的結果設為 `None`，這可能導致呼叫端出現 `NoneType` 錯誤；此外，快取方法中對 Redis 操作失敗的處理可能造成資料不一致，且測試中使用了 `time.sleep` 來等待 TTL 過期，這會拖慢測試並可能導致不穩定。建議優先修正 `None` 值的處理，並考慮在快取寫入失敗時記錄更明確的警告。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/services/billing_service.py:292` | get_plan_bulk 現在會將無效租戶的結果設為 None，可能導致呼叫端錯誤 | 0.95 |
| ⚠️ | Major | `api/services/billing_service.py:340` | Redis 快取寫入失敗時可能導致資料不一致 | 0.80 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_billing_service.py:332` | 測試中使用 time.sleep 等待 TTL 過期，可能導致測試不穩定 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/services/billing_service.py:292</code> get_plan_bulk 現在會將無效租戶的結果設為 None，可能導致呼叫端錯誤</summary>

在 `get_plan_bulk` 中，當 `validate_python` 拋出例外時，程式碼將 `results[tenant_id]` 設為 `None`。這改變了原有的行為：之前若驗證失敗，該租戶不會出現在結果中，而現在會以 `None` 值存在。呼叫端若未檢查 `None`，可能在後續處理時遇到 `AttributeError` 或 `TypeError`。建議改為跳過該租戶（不加入結果），或明確記錄並繼續，以維持向後相容。

**判斷依據**：diff 中新增的 `except Exception` 區塊內將 `results[tenant_id]` 設為 `None`，而原本的程式碼在驗證失敗時不會將該租戶加入結果。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/billing_service.py:340</code> Redis 快取寫入失敗時可能導致資料不一致</summary>

在 `get_plan_bulk_with_cache` 中，若 Redis pipeline 執行失敗（例如網路問題），程式碼僅記錄例外，但不會將失敗的租戶從結果中移除或標記。這可能導致呼叫端認為資料已成功快取，但實際上快取中沒有資料，下次查詢時又會再次呼叫 API。建議在 pipeline 失敗時，至少記錄警告，並考慮將這些租戶視為未快取（例如從 `tenant_plans` 中移除或標記），或提供重試機制。

**判斷依據**：diff 中 pipeline 執行失敗的 except 區塊僅記錄例外，沒有對 `tenant_plans` 做任何處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_billing_service.py:332</code> 測試中使用 time.sleep 等待 TTL 過期，可能導致測試不穩定</summary>

在 `test_get_plan_bulk_with_cache_ttl_expired` 中，使用 `time.sleep(2)` 來等待 Redis 鍵過期。這會拖慢測試執行，且在某些環境下（如 Redis 延遲）可能仍然存在鍵，導致測試失敗。建議使用 `redis_client.delete` 直接刪除鍵來模擬過期，或使用較短的 TTL 並輪詢檢查，避免固定等待。

**判斷依據**：diff 中新增的測試方法內包含 `time.sleep(2)`，用於等待 TTL 過期。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11687 (cache hit 11648) ｜ completion tokens 954 ｜ PR #10</sub>