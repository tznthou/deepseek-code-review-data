<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 試圖修復複合觸發器在並行評估時的競態條件，透過新增 advisory lock 與 DELETE ... RETURNING 來確保只有一個 worker 能觸發父觸發器。整體方向合理，但實作中有幾個關鍵問題：advisory lock 的 key 使用 Python hash() 產生，其值在不同 process 間不保證一致，可能導致鎖失效；clear_child_firings 的 RETURNING 子句在 SQLite 上可能不被支援，且回傳的欄位與預期不符；此外，日誌初始化方式違反專案規範 R03。建議先修正 lock key 的產生方式與資料庫相容性問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | advisory lock key 使用 hash() 導致跨 process 不一致 | 0.90 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:154` | SQLite 不支援 RETURNING 子句，可能導致 clear_child_firings 失敗 | 0.80 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:154` | RETURNING 回傳欄位與預期不符，可能導致 deleted_ids 永遠為空 | 0.80 |
| ⚠️ | Major | `src/prefect/server/events/triggers.py:352` | 競態條件可能仍存在：advisory lock 與 DELETE 之間缺乏交易隔離 | 0.70 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:73` | [R03] Logger 初始化方式違反專案規範 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> advisory lock key 使用 hash() 導致跨 process 不一致</summary>

`lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建 hash()，其值在同一個 process 內穩定，但不同 process 間可能不同（因為 hash 隨機化）。這會導致不同 worker 對同一個 trigger 計算出不同的 lock key，advisory lock 無法序列化，競態條件仍然存在。

建議改用 trigger.id 的整數表示（例如 `trigger.id.int`）或直接使用 UUID 的 bytes 轉成整數，確保跨 process 一致。

**判斷依據**：diff 中新增的 `acquire_composite_trigger_lock` 函式內，使用 `hash()` 產生 lock key。Python 的 hash() 對 str 型別預設會加入隨機 salt，不同 process 的 hash 值不同。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:154</code> SQLite 不支援 RETURNING 子句，可能導致 clear_child_firings 失敗</summary>

`clear_child_firings` 使用 `sa.delete(...).returning(...)`，但 SQLite 在較舊版本（<3.35）不支援 RETURNING，而專案可能支援多種資料庫。若在 SQLite 上執行，會拋出語法錯誤。

建議檢查資料庫 dialect，若不支援 RETURNING，則改用先 SELECT 再 DELETE 的方式，或使用其他相容做法。

**判斷依據**：diff 中 `clear_child_firings` 新增了 `.returning(...)`，但未見針對 SQLite 的處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:154</code> RETURNING 回傳欄位與預期不符，可能導致 deleted_ids 永遠為空</summary>

`clear_child_firings` 回傳的是 `child_trigger_id`，但函式名稱與呼叫端預期的是被刪除的 `child_firing_id`。在 `evaluate_composite_trigger` 中，`deleted_ids` 被拿來與 `firing_ids` 比較，但 `firing_ids` 是 `child_firing_id` 的集合，型別不符，可能導致比較永遠不相等，進而跳過觸發。

建議確認 RETURNING 的欄位應為 `child_firing_id`，或調整比較邏輯。

**判斷依據**：diff 中 `clear_child_firings` 回傳 `child_trigger_id`，但呼叫端在 `triggers.py` 中比較 `deleted_ids` 與 `firing_ids`，而 `firing_ids` 是 `child_firing_id` 的集合。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/triggers.py:352</code> 競態條件可能仍存在：advisory lock 與 DELETE 之間缺乏交易隔離</summary>

雖然加入了 advisory lock，但 lock 的取得與後續的 DELETE 操作可能不在同一個交易中，或者交易的 isolation level 不足以防止其他 worker 在 lock 釋放後插入新的 child firing。此外，若 lock 取得失敗（例如資料庫不支援），程式碼會直接跳過鎖定，競態條件依然存在。

建議確認交易邊界，並在 lock 取得失敗時採取保守策略（例如直接 return 或重試）。

**判斷依據**：diff 中在 `evaluate_composite_trigger` 呼叫 `acquire_composite_trigger_lock`，但該函式在 bind 為 None 或 dialect 不支援時直接 return，沒有鎖定效果。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:73</code> [R03] Logger 初始化方式違反專案規範</summary>

專案規範 R03 要求 logger 使用 `logger: "logging.Logger" = get_logger(__name__)` 模式，但此處改為 `logger = logging.getLogger(__name__)`，且移除了型別註記。

建議改回使用 `get_logger` 並加上型別註記。

**判斷依據**：diff 中將原本的 `logger: "logging.Logger" = get_logger(__name__)` 改為 `logger = logging.getLogger(__name__)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6533 (cache hit 6528) ｜ completion tokens 1470 ｜ PR #7</sub>