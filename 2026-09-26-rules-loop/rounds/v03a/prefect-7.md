<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 旨在修復複合觸發器在並行評估子觸發器時可能重複觸發父觸發器的競態條件。主要變更包括：新增 advisory lock 以序列化同一複合觸發器的評估、修改 clear_child_firings 以回傳實際刪除的 ID 集合，並在觸發前檢查刪除數量以避免重複觸發。整體方向合理，但 lock 的實作存在潛在問題：使用 Python hash() 產生 lock key 可能因 hash 隨機化導致不同程序間 key 不一致，使 lock 失效；且 SQLite 上未實作 lock，但註解宣稱 SQLite 序列化寫入，此假設在 WAL 模式下可能不成立。此外，日誌記錄器初始化違反專案規範 R03。建議修正 lock key 的產生方式，並考慮 SQLite 的替代方案。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | 使用 hash() 產生 advisory lock key 可能因 hash 隨機化而失效 | 0.90 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:46` | SQLite 上未實作 advisory lock，但註解假設可能不成立 | 0.80 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:73` | [R03] 日誌記錄器初始化違反專案規範 | 0.95 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> 使用 hash() 產生 advisory lock key 可能因 hash 隨機化而失效</summary>

`lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建 hash()，其值在每次程序啟動時可能因 hash 隨機化而不同（取決於 PYTHONHASHSEED）。這會導致不同 worker 程序對同一 trigger.id 計算出不同的 lock key，使 advisory lock 無法序列化跨程序的並行評估，競態條件仍然存在。

建議改用 trigger.id 的穩定整數表示，例如 `int.from_bytes(trigger.id.bytes, byteorder='big') % (2**63)`，或直接使用 UUID 的前 8 bytes 轉為整數。

**判斷依據**：diff 中新增的 `lock_key = hash(str(trigger.id)) % (2**63)` 行。Python 的 hash() 對字串使用隨機種子，不同程序間不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:46</code> SQLite 上未實作 advisory lock，但註解假設可能不成立</summary>

程式碼在 SQLite 上未取得任何 lock，僅依賴註解宣稱「SQLite serializes writes at the database level」。然而，SQLite 在 WAL 模式下允許並行讀寫，且此處的競態涉及多個交易各自讀取後寫入，可能仍會發生。若 SQLite 是支援的後端，應考慮使用其他機制（如樂觀鎖或應用層鎖）來確保正確性。

**判斷依據**：diff 中新增的註解行，以及函式僅在 postgresql 時執行 lock。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:73</code> [R03] 日誌記錄器初始化違反專案規範</summary>

專案規範 R03 要求 logger 使用 `logger: "logging.Logger" = get_logger("module_name")` 模式。此處改為 `logger = logging.getLogger(__name__)`，缺少型別註解且未使用專案的 get_logger 輔助函式。

**判斷依據**：diff 中將原本的 `logger: "logging.Logger" = get_logger(__name__)` 改為 `logger = logging.getLogger(__name__)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6588 (cache hit 4224) ｜ completion tokens 974 ｜ PR #7</sub>