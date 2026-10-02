<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 試圖修復複合觸發器在並行評估時的競態條件，透過新增 PostgreSQL advisory lock 與將 clear_child_firings 改為 DELETE ... RETURNING 來確保只有一個 worker 能觸發父觸發器。主要風險在於 advisory lock 的實作：使用 Python 內建 hash() 來產生 lock key，但 hash() 對字串的輸出在每次程序啟動時會因 PYTHONHASHSEED 而不同，可能導致不同 worker 取得不同的 lock key，使鎖失效。此外，logger 初始化違反專案規範 R03，且 acquire_composite_trigger_lock 在非 PostgreSQL 資料庫上完全沒有鎖定機制，若未來支援其他資料庫仍可能發生競態。整體而言，修復方向正確，但 lock key 的產生方式需要改為穩定且跨程序一致的演算法。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | 使用 hash() 產生 advisory lock key 會因 PYTHONHASHSEED 導致跨程序不一致 | 0.95 |
| ⚠️ | Major | `src/prefect/server/events/triggers.py:73` | [R03] Logger 初始化違反專案規範，未使用 get_logger 且型別註記不一致 | 0.90 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:38` | 非 PostgreSQL 資料庫完全沒有鎖定機制，競態條件仍可能存在 | 0.80 |
| 🔸 | Minor | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | 使用 hash() 可能導致 lock key 碰撞，雖然機率低但可避免 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> 使用 hash() 產生 advisory lock key 會因 PYTHONHASHSEED 導致跨程序不一致</summary>

`lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建 `hash()`。對於字串，`hash()` 的輸出會受到環境變數 `PYTHONHASHSEED` 的影響，每次啟動程序時可能不同。這表示不同的 worker 程序（或不同的服務實例）在處理同一個 trigger 時，會計算出不同的 lock key，導致 advisory lock 無法正確序列化，競態條件仍然存在。

建議改用穩定且跨程序一致的演算法，例如直接使用 UUID 的整數表示（`trigger.id.int`）並取模，或使用 `hashlib.sha256` 等加密雜湊後再轉為整數。

**判斷依據**：diff 中新增的 `acquire_composite_trigger_lock` 函式內，使用 `hash(str(trigger.id))` 來產生 lock key。Python 的 `hash()` 對字串的輸出依賴於 `PYTHONHASHSEED`，預設為隨機，因此不同程序間不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/triggers.py:73</code> [R03] Logger 初始化違反專案規範，未使用 get_logger 且型別註記不一致</summary>

此處將原本符合規範的 `logger: "logging.Logger" = get_logger(__name__)` 改為 `logger = logging.getLogger(__name__)`，違反了專案規範 R03（Logger Instances Must Follow Standard Initialization Pattern）。規範要求使用 `get_logger("module_name")` 並加上型別註記。此外，原本的 `import logging` 被移出 `TYPE_CHECKING` 區塊，但 `logging` 僅用於型別註記，應保留在 `TYPE_CHECKING` 中。

建議改回 `logger: "logging.Logger" = get_logger(__name__)`，並將 `import logging` 移回 `TYPE_CHECKING` 區塊。

**判斷依據**：diff 中將 `logger: "logging.Logger" = get_logger(__name__)` 改為 `logger = logging.getLogger(__name__)`，且將 `import logging` 從 `TYPE_CHECKING` 區塊移至模組層級。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:38</code> 非 PostgreSQL 資料庫完全沒有鎖定機制，競態條件仍可能存在</summary>

`acquire_composite_trigger_lock` 僅在 `dialect.name == "postgresql"` 時取得 advisory lock，對於其他資料庫（如 SQLite）則直接跳過。雖然註解提到 SQLite 會序列化寫入，但這並不能完全防止競態條件，特別是在多程序或多執行緒環境下。如果專案支援其他資料庫，此修復將無法涵蓋所有情況。

建議至少記錄警告，或考慮使用其他跨資料庫的鎖定機制（例如樂觀鎖定或基於資料表的鎖）。

**判斷依據**：diff 中 `acquire_composite_trigger_lock` 函式僅在 PostgreSQL 時執行鎖定，其他資料庫無任何處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> 使用 hash() 可能導致 lock key 碰撞，雖然機率低但可避免</summary>

即使 `hash()` 的輸出是穩定的，將 UUID 雜湊後取模 2^63 仍有可能發生碰撞。雖然註解提到「collision is extremely unlikely and benign」，但碰撞會導致兩個不同的 trigger 意外地互相阻塞，可能造成不必要的延遲。

建議直接使用 UUID 的整數表示（`trigger.id.int`）並取模，這樣可以保證唯一性（在 2^63 範圍內）。

**判斷依據**：diff 中 `lock_key` 的計算方式。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6579 (cache hit 6528) ｜ completion tokens 1513 ｜ PR #7</sub>