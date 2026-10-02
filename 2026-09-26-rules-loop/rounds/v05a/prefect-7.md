<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 試圖修復複合觸發器在並行評估時的競態條件，透過新增 advisory lock 與修改 clear_child_firings 回傳實際刪除的 ID 來避免重複觸發。主要風險在於 advisory lock 的實作：使用 Python 內建 hash() 來產生 lock key，但 hash() 對字串有隨機化（PYTHONHASHSEED），不同 process 會得到不同 key，導致 lock 失效；且 hash() 可能回傳負數，取模後仍可能為負，傳給 pg_advisory_xact_lock 會出錯。此外，logger 初始化方式違反專案規範 R03。整體而言，修復方向合理，但 lock 實作需修正才能確保正確性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | 使用 hash() 產生 advisory lock key 會因 PYTHONHASHSEED 隨機化而失效 | 0.95 |
| 🛑 | Blocker | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | lock_key 可能為負數，導致 pg_advisory_xact_lock 執行失敗 | 0.90 |
| ⚠️ | Major | `src/prefect/server/events/triggers.py:73` | [R03] Logger 初始化方式違反專案規範 | 0.85 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:46` | advisory lock 僅在 PostgreSQL 生效，SQLite 下仍存在競態 | 0.80 |
| 🔸 | Minor | `src/prefect/server/events/models/composite_trigger_child_firing.py:35` | 使用 `bind.engine` 可能無法正確取得 Engine 物件 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> 使用 hash() 產生 advisory lock key 會因 PYTHONHASHSEED 隨機化而失效</summary>

`lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建 hash()。對於字串，hash() 的值會受到 PYTHONHASHSEED 環境變數影響，在不同 process 之間會不同。這表示兩個不同的 worker process 在處理同一個 trigger 時，會計算出不同的 lock_key，導致 advisory lock 無法互斥，競態條件依然存在。

建議改用穩定且非負的整數表示，例如直接使用 UUID 的 int 值：`lock_key = trigger.id.int % (2**63)`。

**判斷依據**：diff 中新增的 `acquire_composite_trigger_lock` 函式內，使用 `hash(str(trigger.id))` 來產生 lock key。Python 的 hash() 對 str 型別會因 PYTHONHASHSEED 而變動，跨 process 不一致。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> lock_key 可能為負數，導致 pg_advisory_xact_lock 執行失敗</summary>

`hash(str(trigger.id))` 可能回傳負數，取模 `% (2**63)` 後仍可能為負。PostgreSQL 的 `pg_advisory_xact_lock(bigint)` 不接受負數，會拋出錯誤。

建議確保 key 為非負整數，例如使用 `trigger.id.int % (2**63)` 或先取絕對值。

**判斷依據**：Python 的 hash() 可以回傳負數，且取模運算在 Python 中會保留負號。PostgreSQL 文件指出 advisory lock 的 key 必須是非負的 bigint。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/triggers.py:73</code> [R03] Logger 初始化方式違反專案規範</summary>

專案規範 R03 要求 logger 使用 `logger: "logging.Logger" = get_logger("module_name")` 模式。此處改為 `logger = logging.getLogger(__name__)`，且移除了型別註記，違反規範。

建議改回使用 `get_logger` 並保留型別註記。

**判斷依據**：diff 中將原本的 `logger: "logging.Logger" = get_logger(__name__)` 改為 `logger = logging.getLogger(__name__)`，且移除了型別註記。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:46</code> advisory lock 僅在 PostgreSQL 生效，SQLite 下仍存在競態</summary>

程式碼在 SQLite 下不執行任何鎖定，註解聲稱 SQLite 會序列化寫入，但實際上 SQLite 的寫入鎖定並不能完全避免此處的競態條件。在 SQLite 下，兩個 transaction 仍可能同時讀取到相同的 child firings，並各自嘗試刪除，導致其中一個刪除 0 筆而跳過，但另一個可能已觸發 fire，造成雙重觸發。

如果專案支援 SQLite 作為生產資料庫，此修復不完整。建議評估是否需要針對 SQLite 提供替代方案，或明確限制此修復僅適用於 PostgreSQL。

**判斷依據**：diff 中在 `acquire_composite_trigger_lock` 內，僅在 dialect 為 postgresql 時執行 lock，SQLite 分支只有註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:35</code> 使用 `bind.engine` 可能無法正確取得 Engine 物件</summary>

`engine: sa.Engine = bind if isinstance(bind, sa.Engine) else bind.engine` 假設 bind 若不是 Engine 就是 Connection，但實際上 bind 也可能是其他型別（例如 `AsyncEngine` 或 `AsyncConnection`）。若 bind 是 `AsyncConnection`，其 `engine` 屬性可能不存在或型別不符。

建議使用 `session.get_bind()` 回傳的物件，並透過 SQLAlchemy 的 `inspect()` 或 `bind.dialect` 來取得 dialect，避免直接存取 `engine` 屬性。

**判斷依據**：diff 中新增的程式碼直接假設 bind 的型別，並使用 type: ignore 忽略可能的錯誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6533 (cache hit 4224) ｜ completion tokens 1568 ｜ PR #7</sub>