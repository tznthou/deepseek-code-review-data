<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在修復複合觸發器（compound trigger）在並行評估子觸發器時可能導致的雙重觸發（double-firing）競態條件。主要變更包括：新增 PostgreSQL 的 advisory lock 來序列化同一複合觸發器的評估、修改 clear_child_firings 以回傳實際刪除的 ID 並在觸發前檢查數量、以及新增兩個並行測試。整體方向正確，但 lock 的實作存在潛在問題：使用 Python 內建 hash() 來產生 lock key 在跨程序間不穩定（PYTHONHASHSEED），可能導致 lock 失效；此外，在 SQLite 上沒有 lock 機制，但測試卻在 SQLite 上執行，可能無法真正驗證競態修復。另有 logging 初始化方式違反專案規範 R03。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | 使用 Python 內建 hash() 產生 advisory lock key 可能導致跨程序 lock 失效 | 0.80 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:38` | SQLite 上沒有 lock 機制，但測試可能在 SQLite 上執行，無法驗證競態修復 | 0.70 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:73` | [R03] Logger 初始化方式違反專案規範 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> 使用 Python 內建 hash() 產生 advisory lock key 可能導致跨程序 lock 失效</summary>

`lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建 `hash()`，其值在每次啟動時可能因 `PYTHONHASHSEED` 而不同（尤其對字串）。如果多個 worker 程序各自有不同的 hash seed，它們會對同一個 trigger 計算出不同的 lock key，導致 advisory lock 無法互斥，競態條件仍然存在。建議改用穩定且確定性的方式從 UUID 產生整數，例如 `int.from_bytes(trigger.id.bytes, byteorder='big') % (2**63)` 或直接使用 UUID 的前 8 bytes 轉為整數。

**判斷依據**：diff 中新增的 `acquire_composite_trigger_lock` 函式內使用 `hash(str(trigger.id))` 來產生 lock key。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:38</code> SQLite 上沒有 lock 機制，但測試可能在 SQLite 上執行，無法驗證競態修復</summary>

程式碼中僅在 PostgreSQL 上取得 advisory lock，SQLite 則依賴其序列化寫入的特性。然而，測試環境可能使用 SQLite（從測試檔案中未指定資料庫可推測），因此測試可能無法真正模擬並行寫入的競態，導致測試通過但實際在 PostgreSQL 上仍可能有問題。建議在測試中明確使用 PostgreSQL 或模擬 lock 行為，以確保測試有效性。

**判斷依據**：diff 中 `acquire_composite_trigger_lock` 函式僅在 PostgreSQL 分支取得 lock，SQLite 分支無作為。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:73</code> [R03] Logger 初始化方式違反專案規範</summary>

專案規範 R03 要求 logger 使用 `logger: "logging.Logger" = get_logger("module_name")` 模式。此處將原本的 `logger: "logging.Logger" = get_logger(__name__)` 改為 `logger = logging.getLogger(__name__)`，違反規範。建議改回使用 `get_logger` 並保留型別註解。

**判斷依據**：diff 中將 logger 初始化從 `get_logger` 改為 `logging.getLogger`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6568 (cache hit 6528) ｜ completion tokens 1081 ｜ PR #7</sub>