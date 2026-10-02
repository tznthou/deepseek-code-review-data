<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 旨在修復複合觸發器在並行評估時的競態條件，透過新增 advisory lock 與 DELETE ... RETURNING 來確保只有一個 worker 能觸發父觸發器。整體方向正確，但 lock key 的產生方式（使用 Python hash）在跨程序間不穩定，可能導致鎖失效；此外，SQLite 上完全沒有鎖保護，仍可能發生競態。建議改用 UUID 的穩定整數表示，並考慮對 SQLite 提供替代方案。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | 使用 Python hash 作為 advisory lock key 不穩定 | 0.90 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:46` | SQLite 上完全沒有鎖保護，競態仍可能發生 | 0.80 |
| ⚠️ | Major | `src/prefect/server/events/triggers.py:396` | 刪除數量檢查可能因重複 firing_ids 而誤判 | 0.75 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> 使用 Python hash 作為 advisory lock key 不穩定</summary>

`hash(str(trigger.id))` 的結果在每次 Python 程序啟動時都可能不同（因為 hash 隨機化），這會導致不同 worker 對同一個 trigger 計算出不同的 lock key，使得 advisory lock 無法正確序列化，競態條件仍然存在。建議改用 UUID 的整數表示（例如 `trigger.id.int`）並截斷至 63 位元，以確保跨程序一致。

**判斷依據**：diff 中新增的 `acquire_composite_trigger_lock` 函式使用 `hash(str(trigger.id))` 來產生 lock key。Python 的 hash 函式對字串使用隨機種子（PYTHONHASHSEED），因此不同程序會得到不同結果。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:46</code> SQLite 上完全沒有鎖保護，競態仍可能發生</summary>

在 SQLite 上，`acquire_composite_trigger_lock` 直接返回，沒有取得任何鎖。雖然 SQLite 的寫入序列化可能降低機率，但讀取與寫入之間仍可能交錯，導致兩個 worker 都讀到相同的 child firings 並各自嘗試刪除，最終只有一個成功，但另一個可能已經通過檢查並觸發父觸發器。建議對 SQLite 使用其他機制（例如樂觀鎖或應用層級的鎖）。

**判斷依據**：diff 中 `acquire_composite_trigger_lock` 函式僅在 PostgreSQL 時執行鎖定，SQLite 分支只有註解，沒有實際鎖定。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/triggers.py:396</code> 刪除數量檢查可能因重複 firing_ids 而誤判</summary>

`firing_ids` 可能包含重複的 ID（例如同一個 child firing 被多次加入），但 `clear_child_firings` 回傳的是實際刪除的 ID 集合，其長度可能小於 `firing_ids` 的長度，導致誤判為競態而跳過觸發。建議先對 `firing_ids` 去重，或比較集合而非長度。

**判斷依據**：diff 中 `evaluate_composite_trigger` 使用 `len(deleted_ids) != len(firing_ids)` 來判斷是否全部刪除，但未考慮 `firing_ids` 可能包含重複項。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5084 (cache hit 1536) ｜ completion tokens 913 ｜ PR #7</sub>