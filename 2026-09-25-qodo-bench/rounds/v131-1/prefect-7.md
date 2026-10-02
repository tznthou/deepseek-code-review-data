<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 旨在修復複合觸發器在並行評估時的競態條件，透過新增 advisory lock 與 DELETE ... RETURNING 來確保只有一個 worker 能觸發父觸發器。整體方向正確，但 lock key 的產生方式有缺陷：使用 Python 內建 hash() 對 UUID 字串做雜湊，而 hash() 對字串會隨機化（PYTHONHASHSEED），導致不同 process 產生不同 lock key，使 lock 失效。此外，SQLite 不支援 advisory lock，但程式碼未處理此情況，可能造成行為不一致。建議改用 UUID 的整數表示或穩定雜湊，並明確處理 SQLite 的鎖定策略。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | 使用 hash() 產生 advisory lock key 會因 PYTHONHASHSEED 而失效 | 0.95 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:46` | SQLite 不支援 advisory lock，但程式碼未處理此情況 | 0.80 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:73` | logger 取得方式不一致，可能導致日誌層級設定失效 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> 使用 hash() 產生 advisory lock key 會因 PYTHONHASHSEED 而失效</summary>

`lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建 hash() 對字串做雜湊。在 CPython 中，字串的 hash 會受到 PYTHONHASHSEED 環境變數影響，每個 process 的 seed 可能不同，導致不同 worker process 對同一個 trigger.id 計算出不同的 lock key。這會使 advisory lock 無法跨 process 互斥，競態條件仍然存在。

建議改用 UUID 的整數表示（例如 `trigger.id.int`）或使用穩定的雜湊函式（如 hashlib.sha256）來產生 lock key。

**判斷依據**：diff 中新增的 `acquire_composite_trigger_lock` 函式內，使用 `hash(str(trigger.id))` 來產生 lock key。Python 的 hash() 對字串會隨機化，不同 process 可能得到不同結果。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:46</code> SQLite 不支援 advisory lock，但程式碼未處理此情況</summary>

程式碼僅在 dialect 為 postgresql 時執行 advisory lock，但對於 SQLite 等其他資料庫，函式直接返回，沒有提供任何替代的鎖定機制。雖然註解提到 SQLite 會序列化寫入，但這並不能完全防止競態條件，特別是在多程序或多執行緒環境下。建議明確處理 SQLite 的情況，例如使用檔案鎖或依賴資料庫的交易隔離級別，並在文件中說明。

**判斷依據**：diff 中新增的 `acquire_composite_trigger_lock` 函式，在 dialect 不是 postgresql 時直接跳過鎖定，僅留下註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:73</code> logger 取得方式不一致，可能導致日誌層級設定失效</summary>

原本使用 `get_logger(__name__)` 取得 logger，現在改為 `logging.getLogger(__name__)`。這可能導致日誌層級設定不一致，因為 `get_logger` 可能套用了自訂的 logging 設定。建議維持使用 `get_logger` 以保持一致性。

**判斷依據**：diff 中將 `logger: "logging.Logger" = get_logger(__name__)` 改為 `logger = logging.getLogger(__name__)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5048 (cache hit 1408) ｜ completion tokens 963 ｜ PR #7</sub>