<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 旨在修復複合觸發器（compound trigger）在並行評估子觸發器時可能導致的雙重觸發（double-firing）競態條件。主要變更包括：新增 PostgreSQL advisory lock 以序列化同一複合觸發器的評估、修改 clear_child_firings 以回傳實際刪除的 ID 並在觸發前檢查、以及新增兩個並行測試。整體方向正確，但 lock 的實作存在潛在問題：使用 Python hash() 作為 lock key 可能因 hash randomization 導致不同程序取得不同 lock，且 SQLite 上完全沒有鎖保護，競態仍可能發生。此外，測試可能因共用全域 mock 而互相干擾。建議先修正 lock key 的產生方式，並考慮 SQLite 的替代方案。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | 使用 Python hash() 作為 advisory lock key 會因 hash randomization 而失效 | 0.90 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:46` | SQLite 上完全沒有鎖保護，競態條件仍可能發生 | 0.80 |
| ⚠️ | Major | `src/prefect/server/events/triggers.py:73` | logger 改為標準 logging 可能遺失 Prefect 的日誌上下文 | 0.75 |
| 🔸 | Minor | `tests/events/server/triggers/test_composite_triggers.py:1645` | 測試可能因共用全域 mock 而互相干擾 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> 使用 Python hash() 作為 advisory lock key 會因 hash randomization 而失效</summary>

`lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建的 `hash()`，其值在每次程序啟動時會因 hash randomization 而不同（除非設定 PYTHONHASHSEED）。這表示不同的 worker 程序（或甚至同一程序重啟後）對同一個 trigger.id 會計算出不同的 lock key，導致 advisory lock 無法跨程序互斥，競態條件依然存在。

建議改用 trigger.id 的整數表示（例如 `trigger.id.int`）並取模，或使用 `uuid.UUID.int` 屬性，確保跨程序一致。

**判斷依據**：diff 中新增的 `acquire_composite_trigger_lock` 函式內，使用 `hash(str(trigger.id))` 產生 lock key。Python 的 hash() 對字串預設使用隨機種子（PYTHONHASHSEED），不同程序間不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:46</code> SQLite 上完全沒有鎖保護，競態條件仍可能發生</summary>

在 SQLite 上，`acquire_composite_trigger_lock` 直接跳過（註解說明 SQLite 序列化寫入，但讀取與寫入之間仍可能有競態）。`clear_child_firings` 的 DELETE ... RETURNING 雖然能偵測到競爭，但若兩個交易都讀到相同的 child firings，其中一個會刪除成功，另一個刪除 0 筆並跳過觸發，這可能導致複合觸發器永遠不觸發（如果兩個子觸發器事件分別由不同交易處理，且每個交易都只看到自己的 firing）。

建議在 SQLite 上使用其他同步機制（例如 application-level lock 或樂觀鎖），或至少記錄警告。

**判斷依據**：diff 中 `acquire_composite_trigger_lock` 函式內，對非 PostgreSQL 方言直接跳過，沒有提供任何鎖定機制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/triggers.py:73</code> logger 改為標準 logging 可能遺失 Prefect 的日誌上下文</summary>

原本使用 `get_logger(__name__)` 取得 Prefect 的 logger，現在改為 `logging.getLogger(__name__)`。這可能導致日誌訊息失去 Prefect 的日誌格式、額外上下文（例如 flow run id）或日誌級別控制。如果這是無意的變更，建議恢復使用 `get_logger`。

**判斷依據**：diff 中將 `logger: "logging.Logger" = get_logger(__name__)` 改為 `logger = logging.getLogger(__name__)`，且移除了 `get_logger` 的 import。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/events/server/triggers/test_composite_triggers.py:1645</code> 測試可能因共用全域 mock 而互相干擾</summary>

兩個測試都使用 `act` fixture（可能是全域的 mock），且都執行 `act.assert_called_once()`。如果測試執行順序不固定，前一個測試的呼叫可能殘留，導致後一個測試誤判。建議在每個測試前重置 mock（例如 `act.reset_mock()`）。

**判斷依據**：diff 中兩個測試方法都使用 `act` 參數，但未見重置 mock 的程式碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5084 (cache hit 4992) ｜ completion tokens 1248 ｜ PR #7</sub>