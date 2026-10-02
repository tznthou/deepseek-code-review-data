<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在修復複合觸發器（compound trigger）在並行評估時的競態條件，透過新增 advisory lock 與 DELETE ... RETURNING 來確保父觸發器只會觸發一次。整體方向正確，但 lock key 的產生方式使用 Python 內建 hash()，其值在不同程序間可能不一致，導致鎖失效；此外，lock 的取得僅限於 PostgreSQL，SQLite 的並行寫入仍可能造成競態。clear_child_firings 的回傳值型別變更可能影響其他呼叫者，需確認相容性。測試部分新增了並行測試，但未涵蓋 lock 失效或 SQLite 的情境。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | 使用 Python hash() 作為 advisory lock key 可能導致鎖失效 | 0.80 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:38` | SQLite 不支援 advisory lock，競態條件仍可能發生 | 0.70 |
| 🔸 | Minor | `src/prefect/server/events/models/composite_trigger_child_firing.py:134` | clear_child_firings 回傳型別變更可能影響其他呼叫者 | 0.60 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:396` | 刪除數量比較可能因重複 firing_ids 而誤判 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> 使用 Python hash() 作為 advisory lock key 可能導致鎖失效</summary>

`lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建 hash()，其值在每次程序啟動時可能不同（因 PYTHONHASHSEED 隨機化）。這會導致不同 worker 程序對同一個 trigger.id 計算出不同的 lock key，使得 advisory lock 無法正確序列化，競態條件仍然存在。建議改用 trigger.id 的整數表示（例如 `trigger.id.int`）或直接使用 UUID 的 bytes 轉換為整數，確保跨程序一致。

**判斷依據**：diff 中新增的 `acquire_composite_trigger_lock` 函式內，使用 `hash(str(trigger.id))` 來產生 lock key。Python 的 hash() 對字串會因 PYTHONHASHSEED 而隨機化，不同程序間不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:38</code> SQLite 不支援 advisory lock，競態條件仍可能發生</summary>

程式碼僅在 PostgreSQL 時取得 advisory lock，SQLite 則直接跳過。雖然 SQLite 的寫入序列化可能降低機率，但並不能完全避免競態：兩個交易可能同時讀取到相同的 child firings，然後各自嘗試刪除並觸發父觸發器。建議在 SQLite 上使用其他同步機制（例如樂觀鎖或應用層級的鎖），或明確接受此限制並在文件中說明。

**判斷依據**：diff 中 `acquire_composite_trigger_lock` 函式僅在 dialect 為 postgresql 時執行鎖定，SQLite 則無任何處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:134</code> clear_child_firings 回傳型別變更可能影響其他呼叫者</summary>

`clear_child_firings` 的回傳型別從 `None` 改為 `set[UUID]`，但此函式可能被其他模組呼叫。若其他呼叫者未預期回傳值，可能導致型別錯誤或行為不符。建議確認所有呼叫點都已更新，或保留原回傳型別並新增另一個函式。

**判斷依據**：diff 中 `clear_child_firings` 的簽名從 `-> None` 改為 `-> set[UUID]`，且函式內新增 `return set(result.scalars().all())`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:396</code> 刪除數量比較可能因重複 firing_ids 而誤判</summary>

在 `evaluate_composite_trigger` 中，比較 `len(deleted_ids) != len(firing_ids)` 來判斷是否成功刪除所有 firing。但 `firing_ids` 是 set，而 `deleted_ids` 也是 set，若 `firing_ids` 中有重複（雖然 set 不會重複），但若資料庫中因某些原因存在重複的 child_firing_id（例如先前未清理乾淨），刪除數量可能小於預期，導致誤判為競態而跳過觸發。建議使用集合比較（`deleted_ids == firing_ids`）或確認資料庫唯一性。

**判斷依據**：diff 中新增的比較邏輯，使用長度比較而非集合相等。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6227 (cache hit 1536) ｜ completion tokens 1366 ｜ PR #7</sub>