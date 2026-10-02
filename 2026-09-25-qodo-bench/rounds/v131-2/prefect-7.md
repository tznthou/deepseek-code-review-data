<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 旨在修復複合觸發器在並行評估時的競態條件，透過新增 advisory lock 與 DELETE ... RETURNING 來確保只有一個 worker 能觸發父觸發器。整體方向正確，但 lock key 的產生方式有缺陷：使用 Python 內建 hash() 對 UUID 字串做雜湊，而 hash() 對字串會隨機化（PYTHONHASHSEED），導致不同 process 可能產生不同 key，使 lock 失效。此外，SQLite 不支援 advisory lock，但程式碼未處理此情況，可能造成行為不一致。建議改用 UUID 的整數表示或穩定雜湊，並明確處理 SQLite 的鎖定策略。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | 使用 hash() 產生 advisory lock key 會因 PYTHONHASHSEED 隨機化而失效 | 0.95 |
| ⚠️ | Major | `src/prefect/server/events/triggers.py:396` | clear_child_firings 回傳 deleted_ids 但未驗證是否包含所有 firing_ids | 0.85 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:46` | SQLite 不支援 advisory lock，但程式碼未提供替代方案 | 0.80 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:397` | logger.debug 使用 extra 參數但格式字串未包含對應佔位符 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> 使用 hash() 產生 advisory lock key 會因 PYTHONHASHSEED 隨機化而失效</summary>

`lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建 hash() 對字串做雜湊。在 CPython 中，字串的 hash 值會受到 PYTHONHASHSEED 環境變數影響，每個 process 可能不同。這會導致不同 worker process 對同一個 trigger.id 計算出不同的 lock key，使得 advisory lock 無法正確序列化，競態條件仍然存在。

建議改用 UUID 的整數表示（例如 `trigger.id.int`）或使用穩定雜湊（如 hashlib.sha256）來產生 lock key。

**判斷依據**：diff 中新增的 `acquire_composite_trigger_lock` 函式內，使用 `hash(str(trigger.id))` 來產生 lock key。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/triggers.py:396</code> clear_child_firings 回傳 deleted_ids 但未驗證是否包含所有 firing_ids</summary>

在 `evaluate_composite_trigger` 中，呼叫 `clear_child_firings` 後取得 `deleted_ids`，並比較 `len(deleted_ids) != len(firing_ids)` 來判斷是否贏得競賽。但此比較僅檢查數量，未檢查內容。若因某些原因（例如部分 firing_ids 已被其他 transaction 刪除，但同時又有新的 firing 加入）導致刪除的數量相同但 ID 不同，仍會誤判為贏得競賽而觸發父觸發器。

建議改為比較集合是否相等：`if deleted_ids != set(firing_ids):`。

**判斷依據**：diff 中新增的比較邏輯，僅比較長度。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:46</code> SQLite 不支援 advisory lock，但程式碼未提供替代方案</summary>

在 `acquire_composite_trigger_lock` 中，只有當 dialect 為 postgresql 時才執行 `pg_advisory_xact_lock`，但 SQLite 分支僅有註解說明「SQLite 也序列化寫入」，並未採取任何鎖定措施。然而，SQLite 的寫入序列化並不能完全防止此處的競態條件：兩個 transaction 可能同時讀取 child firings，然後各自嘗試刪除，但只有一個會成功（因為 DELETE ... RETURNING 會回傳實際刪除的列）。這可能導致其中一個 transaction 誤以為自己贏得競賽而觸發父觸發器，造成 double firing。

建議在 SQLite 上使用其他鎖定機制（例如 BEGIN IMMEDIATE 或應用層級的鎖），或明確處理此情況以避免 double firing。

**判斷依據**：diff 中新增的 `acquire_composite_trigger_lock` 函式，在 dialect 為 sqlite 時僅有註解，沒有實際鎖定。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:397</code> logger.debug 使用 extra 參數但格式字串未包含對應佔位符</summary>

在 `logger.debug` 呼叫中，格式字串包含 `%s` 佔位符，但同時傳入了 `extra` 參數。`extra` 參數用於提供額外的 context 欄位，但格式字串中的 `%s` 會嘗試從 `extra` 中取得對應的 key，若不存在則可能拋出 KeyError 或產生錯誤的 log 訊息。

建議移除 `extra` 參數，或將所有資訊直接放入格式字串中。

**判斷依據**：diff 中新增的 logger.debug 呼叫，格式字串有 %s 但同時使用 extra。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5048 (cache hit 4992) ｜ completion tokens 1381 ｜ PR #7</sub>