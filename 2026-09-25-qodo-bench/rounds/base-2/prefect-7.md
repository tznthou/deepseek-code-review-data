<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 旨在修復複合觸發器在並行評估時可能重複觸發的競態條件。主要變更包括：新增 PostgreSQL advisory lock 以序列化評估、修改 clear_child_firings 使用 DELETE ... RETURNING 並回傳實際刪除的 ID 集合、以及在 evaluate_composite_trigger 中檢查刪除數量以決定是否觸發。整體方向合理，但 lock 的實作存在重大缺陷：使用 Python hash() 產生 lock key 在跨行程間不穩定，可能導致鎖失效；且 SQLite 未實作鎖，仍可能發生競態。此外，logger 的變更可能破壞既有日誌配置。建議修正 lock key 的產生方式，並考慮 SQLite 的替代方案。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | 使用 hash() 產生 advisory lock key 在跨行程間不穩定 | 0.95 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:38` | SQLite 未實作 advisory lock，競態仍可能發生 | 0.80 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:73` | logger 取得方式變更可能破壞既有日誌配置 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> 使用 hash() 產生 advisory lock key 在跨行程間不穩定</summary>

`hash(str(trigger.id))` 在 Python 中對字串的 hash 值會因行程而異（除非設定 PYTHONHASHSEED=0）。這會導致不同 worker 行程對同一個 trigger 計算出不同的 lock key，使得 advisory lock 無法序列化，競態條件仍然存在。

建議改用 trigger.id 的整數表示（例如 `trigger.id.int`）或直接使用 UUID 的 bytes 轉換為整數，確保跨行程一致。

**判斷依據**：diff 中新增的 `lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建 hash，其對字串的 hash 值在預設情況下會因行程而異（PYTHONHASHSEED 隨機化）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:38</code> SQLite 未實作 advisory lock，競態仍可能發生</summary>

函式僅在 dialect 為 postgresql 時取得 advisory lock，SQLite 則直接跳過。雖然 SQLite 的寫入序列化可能降低機率，但無法完全避免競態（例如兩個交易都先讀取再寫入）。若系統支援 SQLite，此修復不完整。

建議在 SQLite 上使用其他機制（如樂觀鎖或應用層級的分散式鎖），或明確限制此修復僅適用於 PostgreSQL。

**判斷依據**：diff 中新增的 `if dialect.name == "postgresql":` 區塊，以及註解說明 SQLite 不支援 advisory lock。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:73</code> logger 取得方式變更可能破壞既有日誌配置</summary>

原本使用 `get_logger(__name__)` 取得 logger，現在改為 `logging.getLogger(__name__)`。若專案中 `get_logger` 有特殊設定（例如設定 propagate、handler 或 level），此變更可能導致日誌行為不一致。

建議確認 `get_logger` 的實作，若無特殊需求則可接受，但需注意一致性。

**判斷依據**：diff 中將 `logger: "logging.Logger" = get_logger(__name__)` 改為 `logger = logging.getLogger(__name__)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5084 (cache hit 4992) ｜ completion tokens 1060 ｜ PR #7</sub>