<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 旨在修復複合觸發器在並行評估時可能重複觸發的競態條件。主要變更包括：新增 advisory lock 以序列化評估、修改 clear_child_firings 以回傳實際刪除的 ID 並據此判斷是否觸發、以及新增並行測試。整體方向正確，但 lock 的實作存在重大缺陷（使用 Python hash 作為 lock key 不穩定且可能碰撞），且 logger 初始化違反專案規範。建議修正 lock key 的產生方式並調整 logger 初始化。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | 使用 Python hash() 作為 advisory lock key 不穩定且可能碰撞 | 0.95 |
| ⚠️ | Major | `src/prefect/server/events/triggers.py:73` | [R03] Logger 初始化違反專案規範 | 0.90 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:38` | advisory lock 僅在 PostgreSQL 上生效，SQLite 上無保護 | 0.80 |
| 🔸 | Minor | `src/prefect/server/events/models/composite_trigger_child_firing.py:35` | 取得 engine 的方式可能不正確 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> 使用 Python hash() 作為 advisory lock key 不穩定且可能碰撞</summary>

`lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建 hash，其值在每次執行時可能不同（因 hash randomization），且可能產生負數（取模後仍可能為負），導致 lock 失效或非預期行為。此外，hash 碰撞可能導致不同 trigger 共用同一 lock，雖然註解聲稱「collision is extremely unlikely and benign」，但實際上可能造成不必要的序列化或錯誤的互斥。建議使用 trigger.id 的整數表示（例如 `trigger.id.int`）或直接使用 UUID 的 bytes 轉換為整數，並確保為正數。

**判斷依據**：diff 中新增的 `acquire_composite_trigger_lock` 函式內，使用 `hash(str(trigger.id)) % (2**63)` 作為 lock key。Python 的 hash 對字串有隨機化（PYTHONHASHSEED），且可能回傳負數，取模後仍可能為負，導致 SQL 查詢失敗或 lock 行為不正確。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/triggers.py:73</code> [R03] Logger 初始化違反專案規範</summary>

專案規範 R03 要求 logger 使用 `logger: "logging.Logger" = get_logger(__name__)` 模式，但此處改為 `logger = logging.getLogger(__name__)`，且移除了型別註記。這可能導致 logging 配置不一致，且違反程式碼風格。建議改回使用 `get_logger` 並保留型別註記。

**判斷依據**：diff 中將原本的 `logger: "logging.Logger" = get_logger(__name__)` 改為 `logger = logging.getLogger(__name__)`，違反 R03。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:38</code> advisory lock 僅在 PostgreSQL 上生效，SQLite 上無保護</summary>

函式僅在 dialect 為 postgresql 時執行 lock，SQLite 則直接跳過。雖然註解聲稱 SQLite 會序列化寫入，但實際上 SQLite 的寫入鎖定可能無法完全避免此處的競態條件（例如兩個 transaction 同時讀取後再寫入）。若專案支援 SQLite 作為生產資料庫，此修復可能不完整。建議評估 SQLite 下的行為，或至少在 SQLite 上採用其他同步機制（如 application-level lock）。

**判斷依據**：diff 中新增的 lock 邏輯僅在 PostgreSQL 上執行，SQLite 上無任何保護。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:35</code> 取得 engine 的方式可能不正確</summary>

`engine: sa.Engine = bind if isinstance(bind, sa.Engine) else bind.engine` 假設 bind 若不是 Engine 就一定是 Connection，但實際上 bind 也可能是其他型別（例如 `AsyncEngine` 或 `AsyncConnection`）。若 bind 是 `AsyncConnection`，其 `engine` 屬性可能不存在或型別不符。建議使用更穩健的方式取得 dialect，例如 `session.get_bind().dialect`。

**判斷依據**：diff 中新增的程式碼直接假設 bind 的型別，並使用 type: ignore 忽略可能的型別錯誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6578 (cache hit 1536) ｜ completion tokens 1332 ｜ PR #7</sub>