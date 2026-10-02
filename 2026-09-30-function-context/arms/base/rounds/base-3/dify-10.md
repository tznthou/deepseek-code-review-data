<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 get_plan_bulk_with_cache 方法，利用 Redis 快取來減少批次作業中對 billing API 的呼叫，並修改了 get_plan_bulk 以跳過無效的租戶資料。整體設計合理，但存在幾個問題：快取資料可能包含 None 值，導致 json.dumps 序列化失敗；快取鍵未使用 namespace 隔離，可能與其他服務衝突；測試中使用了 time.sleep 可能導致不穩定；以及 get_plan_bulk 的變更可能影響既有呼叫者。建議優先處理 None 值序列化問題，並考慮加入 namespace 前綴。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/services/billing_service.py:376` | 快取資料可能包含 None 值，導致 json.dumps 序列化失敗 | 0.80 |
| 🔸 | Minor | `api/services/billing_service.py:40` | 快取鍵缺少 namespace 前綴，可能與其他服務衝突 | 0.70 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_billing_service.py:332` | 測試中使用 time.sleep 可能導致不穩定 | 0.60 |
| 🔸 | Minor | `api/services/billing_service.py:292` | get_plan_bulk 的變更可能影響既有呼叫者 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>api/services/billing_service.py:376</code> 快取資料可能包含 None 值，導致 json.dumps 序列化失敗</summary>

在 get_plan_bulk_with_cache 中，從 get_plan_bulk 取得的 bulk_plans 可能包含值為 None 的項目（因為 get_plan_bulk 現在會將無效租戶設為 None）。在寫入快取時，程式碼直接對 subscription_plan 呼叫 json.dumps，但 None 不是有效的 JSON 序列化對象，會拋出 TypeError。這會導致整個 pipeline 失敗，且該例外被捕獲後僅記錄日誌，但快取寫入全部失敗。

建議在寫入快取前過濾掉 None 值，或將 None 轉換為其他表示（例如空字典或特殊標記）。

**判斷依據**：diff 中新增的程式碼：`json_str = json.dumps(subscription_plan)`，而 `subscription_plan` 可能為 None（來自 `get_plan_bulk` 的結果）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/services/billing_service.py:40</code> 快取鍵缺少 namespace 前綴，可能與其他服務衝突</summary>

快取鍵使用 `tenant_plan:` 前綴，但未包含服務或環境 namespace。如果其他服務也使用相同的鍵格式，可能會發生衝突。建議加入服務名稱或環境變數作為前綴，例如 `billing:tenant_plan:`。

**判斷依據**：diff 中新增的常數：`_PLAN_CACHE_KEY_PREFIX = "tenant_plan:"`

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_billing_service.py:332</code> 測試中使用 time.sleep 可能導致不穩定</summary>

在 test_get_plan_bulk_with_cache_ttl_expired 中，使用 time.sleep(2) 等待 TTL 過期。這可能導致測試執行時間增加，且在 CI 環境中可能因為時間誤差而變得不穩定。建議使用 mock 來模擬 TTL 過期，或使用更短的 TTL 並配合輪詢。

**判斷依據**：diff 中新增的測試程式碼：`time.sleep(2)`

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/services/billing_service.py:292</code> get_plan_bulk 的變更可能影響既有呼叫者</summary>

get_plan_bulk 現在會將無效租戶設為 None 而不是拋出例外。這可能導致既有呼叫者（如果有）在處理結果時遇到 None 值而發生錯誤。建議確認所有呼叫者都能處理 None 值，或提供一個參數來控制行為。

**判斷依據**：diff 中修改的程式碼：`results[tenant_id] = None`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8972 (cache hit 8960) ｜ completion tokens 1005 ｜ PR #10</sub>