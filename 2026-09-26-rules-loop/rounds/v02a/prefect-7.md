<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 試圖修復複合觸發器在並行評估時的競態條件，透過新增 advisory lock 與 DELETE ... RETURNING 來確保只有一個 worker 能觸發父觸發器。主要風險在於 advisory lock 的實作：使用 Python 內建 hash() 來產生 lock key，但 hash() 對字串的輸出在每次程序啟動時會因 PYTHONHASHSEED 而不同，可能導致不同 worker 使用不同 lock key，使鎖失效。此外，logger 初始化方式違反專案規範 R03，且 acquire_composite_trigger_lock 在無法取得 bind 時靜默返回，可能讓鎖完全失效。測試部分新增了並行測試，但未涵蓋 lock key 不一致或鎖失效的情境。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | 使用 hash() 產生 advisory lock key 會因 PYTHONHASHSEED 而跨程序不一致 | 0.95 |
| ⚠️ | Major | `src/prefect/server/events/triggers.py:73` | [R03] Logger 初始化違反專案規範 | 0.90 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:30` | 無法取得 bind 時靜默返回，可能導致鎖完全失效 | 0.80 |
| 🔸 | Minor | `src/prefect/server/events/models/composite_trigger_child_firing.py:35` | 使用 type: ignore 可能隱藏型別問題 | 0.70 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:396` | 比較 deleted_ids 與 firing_ids 的長度可能不足以偵測競態 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> 使用 hash() 產生 advisory lock key 會因 PYTHONHASHSEED 而跨程序不一致</summary>

`lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建 hash()。對於字串，hash() 的輸出在每次 Python 程序啟動時會因 PYTHONHASHSEED 而不同（除非明確設定）。這表示不同的 worker 程序（或甚至同一程序重啟後）對同一個 trigger.id 會計算出不同的 lock key，導致 advisory lock 無法正確序列化，競態條件仍然存在。

建議改用穩定的雜湊函數，例如 `int.from_bytes(hashlib.sha256(str(trigger.id).encode()).digest()[:8], 'big')`，或直接使用 UUID 的整數表示（若資料庫支援）。

**判斷依據**：diff 中新增的 `acquire_composite_trigger_lock` 函式內，使用 `hash(str(trigger.id))` 來產生 lock key。Python 的 hash() 對 str 的輸出在每次程序啟動時會因 PYTHONHASHSEED 而不同，這是已知行為。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/triggers.py:73</code> [R03] Logger 初始化違反專案規範</summary>

專案規範 R03 要求 logger 使用 `logger: "logging.Logger" = get_logger("module_name")` 模式。此處改為 `logger = logging.getLogger(__name__)`，違反規範。

建議改回使用 `get_logger` 並加上型別註記。

**判斷依據**：diff 中將原本的 `logger: "logging.Logger" = get_logger(__name__)` 改為 `logger = logging.getLogger(__name__)`，違反 R03。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:30</code> 無法取得 bind 時靜默返回，可能導致鎖完全失效</summary>

`acquire_composite_trigger_lock` 在 `bind is None` 時直接 `return`，沒有記錄任何警告或錯誤。這可能發生在 session 尚未綁定 engine 的罕見情況下，此時鎖不會被取得，競態條件仍然存在。

建議至少記錄 warning，或考慮拋出例外，讓呼叫者知道鎖未取得。

**判斷依據**：diff 中新增的函式內，`if bind is None: return` 沒有 logging 或 raise。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:35</code> 使用 type: ignore 可能隱藏型別問題</summary>

`engine: sa.Engine = bind if isinstance(bind, sa.Engine) else bind.engine  # type: ignore[union-attr]` 使用了 type: ignore，這可能掩蓋了 bind 可能不是 Engine 或 Connection 的型別問題。建議更明確地處理型別，例如使用 isinstance 檢查或 cast。

**判斷依據**：diff 中該行有 `# type: ignore[union-attr]`，表示型別檢查器可能對 `bind.engine` 的存取發出警告。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:396</code> 比較 deleted_ids 與 firing_ids 的長度可能不足以偵測競態</summary>

`if len(deleted_ids) != len(firing_ids):` 僅比較數量，但若刪除的 ID 集合與預期的 firing_ids 不完全相同（例如刪除了不同的 ID 但數量相同），則不會被偵測到。雖然在正常情況下不太可能發生，但更嚴謹的做法是比較集合是否相等：`if deleted_ids != set(firing_ids):`。

**判斷依據**：diff 中新增的比較邏輯使用 len() 而非集合相等。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6579 (cache hit 1536) ｜ completion tokens 1405 ｜ PR #7</sub>