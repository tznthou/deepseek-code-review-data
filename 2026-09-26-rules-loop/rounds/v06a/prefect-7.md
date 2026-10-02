<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 旨在修復複合觸發器在並行評估時可能重複觸發的競態條件。主要變更包括：新增 PostgreSQL advisory lock 以序列化相同觸發器的評估、修改 clear_child_firings 以回傳實際刪除的 ID 集合，並在觸發前檢查是否成功取得所有 firing。整體方向合理，但 lock 的實作存在重大缺陷：使用 Python 內建 hash() 產生 lock key，其值在程序間不穩定，可能導致 lock 失效；且未處理非 PostgreSQL 資料庫的並行問題。此外，日誌初始化違反專案規範 R03。測試部分新增了兩個並行測試，但未涵蓋 lock 失效或資料庫差異的情境。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | 使用 Python 內建 hash() 作為 advisory lock key 會導致跨程序 lock 失效 | 0.95 |
| ⚠️ | Major | `src/prefect/server/events/triggers.py:73` | [R03] Logger 初始化違反專案規範 | 0.90 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:38` | 非 PostgreSQL 資料庫未提供並行保護，競態條件仍可能發生 | 0.80 |
| ⚠️ | Major | `src/prefect/server/events/triggers.py:396` | 刪除數量不符時直接 return，可能遺漏觸發 | 0.75 |
| 🔸 | Minor | `tests/events/server/triggers/test_composite_triggers.py:1630` | 測試未涵蓋 lock 失效或非 PostgreSQL 情境 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> 使用 Python 內建 hash() 作為 advisory lock key 會導致跨程序 lock 失效</summary>

`hash(str(trigger.id))` 在 Python 中對字串的 hash 是隨機化的（受 PYTHONHASHSEED 影響），不同程序對相同字串會得到不同 hash 值。這會導致不同 worker 程序對同一個 trigger 取得不同的 lock key，advisory lock 完全失效，競態條件依然存在。

建議改用 trigger.id 的整數表示（例如 `trigger.id.int`）或直接使用 UUID 的 bytes 轉成整數，確保跨程序一致。

**判斷依據**：diff 中新增的 `acquire_composite_trigger_lock` 函式內，使用 `hash(str(trigger.id))` 產生 lock key。Python 的 hash() 對 str 型別預設使用隨機種子，不同程序間不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/triggers.py:73</code> [R03] Logger 初始化違反專案規範</summary>

專案規範 R03 要求 logger 使用 `logger: "logging.Logger" = get_logger("module_name")` 模式。此處改為 `logger = logging.getLogger(__name__)`，缺少型別註記且未使用專案的 `get_logger` 輔助函式，可能導致 logging 設定不一致。

建議改回 `logger: "logging.Logger" = get_logger(__name__)`。

**判斷依據**：diff 將原本的 `logger: "logging.Logger" = get_logger(__name__)` 改為 `logger = logging.getLogger(__name__)`，違反 R03。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:38</code> 非 PostgreSQL 資料庫未提供並行保護，競態條件仍可能發生</summary>

函式僅在 dialect 為 postgresql 時取得 advisory lock，其他資料庫（如 SQLite）則直接跳過。雖然 SQLite 寫入序列化，但讀取與寫入之間仍可能存在競態（例如兩個交易同時讀取 child firings，再各自刪除並觸發）。若專案支援多種資料庫，此修復不完整。

建議針對不支援 advisory lock 的資料庫，採用其他同步機制（如樂觀鎖、唯一約束或應用層級的分散式鎖）。

**判斷依據**：diff 中 `acquire_composite_trigger_lock` 的實作僅在 postgresql 分支取得 lock，其他 dialect 無任何處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/triggers.py:396</code> 刪除數量不符時直接 return，可能遺漏觸發</summary>

當 `len(deleted_ids) != len(firing_ids)` 時，程式直接 return，不觸發複合觸發器。這可能導致在某些情況下（例如部分 firing 已被其他程序刪除，但仍有足夠條件觸發）漏掉觸發。需要確認此行為是否符合預期，或應改為檢查是否滿足觸發條件而非僅比較數量。

**判斷依據**：diff 中新增的檢查，若刪除數量不符則直接 return，未觸發 fire。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/events/server/triggers/test_composite_triggers.py:1630</code> 測試未涵蓋 lock 失效或非 PostgreSQL 情境</summary>

新增的測試僅驗證在 PostgreSQL 下 lock 有效時的行為，未測試 lock key 不一致或非 PostgreSQL 資料庫的並行情況。建議增加測試以確保修復的完整性。

**判斷依據**：測試類別中僅有兩個測試，均假設 lock 正常運作。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6568 (cache hit 4224) ｜ completion tokens 1619 ｜ PR #7</sub>