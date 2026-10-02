<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在修復複合觸發器在並行評估時的競態條件，透過新增 advisory lock 與修改 clear_child_firings 回傳刪除 ID 來避免重複觸發。主要風險在於 advisory lock 的實作使用 Python 內建 hash()，其值在不同程序間可能不一致，導致鎖失效；此外，lock key 的碰撞雖被認為良性，但可能造成不必要的序列化。測試部分新增了兩個並行測試，但未涵蓋 lock 取得失敗或刪除數量不符的情境。整體而言，修復方向正確，但 lock 實作需改用穩定 hash 以確保跨程序一致性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | advisory lock 使用 Python hash() 可能導致跨程序不一致 | 0.80 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:73` | [R03] Logger 初始化不符合專案規範 | 0.70 |
| 🔸 | Minor | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | advisory lock key 碰撞可能導致不必要的序列化 | 0.60 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:396` | 刪除數量不符時僅記錄 debug 並 return，可能隱藏錯誤 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> advisory lock 使用 Python hash() 可能導致跨程序不一致</summary>

`hash(str(trigger.id))` 在 Python 中對字串的 hash 會因 PYTHONHASHSEED 不同而在不同程序間產生不同值。這會導致多個 worker 程序對同一個 trigger 取得不同的 lock key，使 advisory lock 無法跨程序互斥，競態條件仍然存在。建議改用穩定的 hash 演算法（例如 SHA-256）並取前 8 bytes 轉為整數，或直接使用 UUID 的 int 表示（若資料庫支援 128-bit lock）。

**判斷依據**：diff 中新增的 `acquire_composite_trigger_lock` 函式使用 `hash(str(trigger.id))` 作為 lock key。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:73</code> [R03] Logger 初始化不符合專案規範</summary>

專案規範 R03 要求 logger 使用 `logger: "logging.Logger" = get_logger(__name__)` 模式，但此處改為 `logger = logging.getLogger(__name__)`，且移除了型別註解。這可能導致型別檢查不一致，並偏離專案慣例。建議改回使用 `get_logger` 並保留型別註解。

**判斷依據**：diff 中 `logger` 的初始化從 `logger: "logging.Logger" = get_logger(__name__)` 改為 `logger = logging.getLogger(__name__)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> advisory lock key 碰撞可能導致不必要的序列化</summary>

使用 `% (2**63)` 將 UUID 的 hash 截斷為 63-bit，雖然碰撞機率極低，但一旦碰撞，兩個不同的 trigger 會共用同一個 lock，導致不必要的序列化，可能影響效能。若使用完整 128-bit lock（例如 PostgreSQL 的 `pg_advisory_xact_lock` 支援兩個 32-bit 整數），可完全避免碰撞。

**判斷依據**：diff 中 `lock_key` 的計算方式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:396</code> 刪除數量不符時僅記錄 debug 並 return，可能隱藏錯誤</summary>

當 `deleted_ids` 數量與 `firing_ids` 不符時，程式僅記錄 debug 訊息並返回，沒有拋出例外或進行其他處理。這可能導致在某些情況下（例如資料庫錯誤）複合觸發器被靜默跳過，且 debug 層級的 log 在生產環境通常不會被記錄，使得問題難以追蹤。建議至少使用 warning 層級，或考慮拋出例外以觸發重試機制。

**判斷依據**：diff 中 `evaluate_composite_trigger` 函式新增的刪除數量檢查與處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6588 (cache hit 6528) ｜ completion tokens 1204 ｜ PR #7</sub>