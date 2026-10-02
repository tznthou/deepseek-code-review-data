<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 試圖修復複合觸發器在並行評估時的競態條件，透過新增 advisory lock 與 DELETE ... RETURNING 來序列化並行評估並防止重複觸發。主要風險在於 advisory lock 的實作：使用 Python 內建 hash() 來產生 lock key，但 hash() 對字串會隨機化（PYTHONHASHSEED），可能導致不同程序取得不同 lock key，使鎖失效。此外，lock 的取得時機在讀取 child firings 之後，可能無法完全序列化。DELETE ... RETURNING 的用法在 SQLite 上可能不受支援，需要驗證。測試部分新增了兩個並行測試，但未涵蓋 lock 失效的情境。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | 使用 hash() 產生 advisory lock key 會因 PYTHONHASHSEED 隨機化而失效 | 0.95 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:17` | advisory lock 取得時機太晚，無法完全序列化 | 0.80 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:154` | SQLite 不支援 DELETE ... RETURNING，可能導致錯誤 | 0.70 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:73` | [R03] Logger 初始化方式與專案慣例不一致 | 0.90 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:396` | 比較 deleted_ids 與 firing_ids 的長度可能不足以偵測競態 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> 使用 hash() 產生 advisory lock key 會因 PYTHONHASHSEED 隨機化而失效</summary>

`lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建 hash()，但 hash() 對字串的結果會受到 PYTHONHASHSEED 環境變數影響，在不同程序間可能不同。這會導致不同 worker 對同一個 trigger 取得不同的 lock key，使 advisory lock 無法序列化，競態條件依然存在。

建議改用穩定的整數表示，例如直接使用 UUID 的 int 值（`trigger.id.int`）或將其轉換為 64 位元整數（例如取前 8 bytes）。

**判斷依據**：diff 中新增的這一行使用 hash()，而 Python 文件明確指出 hash() 對 str、bytes 和 datetime 物件會使用隨機的 salt，且該 salt 在每次 Python 啟動時可能不同。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:17</code> advisory lock 取得時機太晚，無法完全序列化</summary>

`acquire_composite_trigger_lock` 在 `evaluate_composite_trigger` 中於讀取 child firings 之後才呼叫。這表示兩個並行交易可能都先讀取了相同的 child firings，然後才嘗試取得 lock。雖然 lock 會序列化後續的刪除與觸發，但讀取階段仍可能看到不一致的狀態。

建議在讀取 child firings 之前就取得 lock，以確保整個評估過程的序列化。

**判斷依據**：在 triggers.py 的 diff 中，lock 的取得位於 `get_child_firings` 呼叫之後（從上下文可看出）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:154</code> SQLite 不支援 DELETE ... RETURNING，可能導致錯誤</summary>

`clear_child_firings` 使用 `sa.delete(...).returning(...)`，但 SQLite 在較舊版本（<3.35）不支援 RETURNING 子句。如果專案支援的 SQLite 版本較舊，這會導致執行時期錯誤。

建議檢查專案支援的 SQLite 版本，或改用其他方式取得刪除的 ID（例如先 SELECT 再 DELETE）。

**判斷依據**：diff 中新增了 `.returning(...)`，而 SQLite 的 RETURNING 支援是 3.35.0 才加入。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:73</code> [R03] Logger 初始化方式與專案慣例不一致</summary>

原本使用 `get_logger(__name__)`，但被改為 `logging.getLogger(__name__)`。這可能違反專案規範 R03（Logger Instances Must Follow Standard Initialization Pattern），且可能失去 Prefect 自訂的 logging 設定。

建議改回 `get_logger(__name__)`。

**判斷依據**：diff 中將 `logger: "logging.Logger" = get_logger(__name__)` 改為 `logger = logging.getLogger(__name__)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:396</code> 比較 deleted_ids 與 firing_ids 的長度可能不足以偵測競態</summary>

`if len(deleted_ids) != len(firing_ids)` 假設每個 firing_id 都是唯一的，且刪除的數量差異就代表競態。但如果 firing_ids 中有重複的 ID，或者刪除條件可能刪除多個相同 child_trigger_id 的記錄，這個比較可能誤判。

建議改為比較集合是否相等，或使用更精確的條件。

**判斷依據**：diff 中新增的這一行使用長度比較，但 firing_ids 的來源可能包含重複。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5785 (cache hit 5760) ｜ completion tokens 1404 ｜ PR #7</sub>