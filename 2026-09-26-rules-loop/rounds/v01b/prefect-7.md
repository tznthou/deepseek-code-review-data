<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 試圖修復複合觸發器在並行評估時的競態條件，透過新增 advisory lock 與 DELETE ... RETURNING 來確保只有一個 worker 能觸發父觸發器。主要風險在於 advisory lock 的實作使用 Python hash() 產生 lock key，其值在不同程序間不穩定，可能導致鎖失效；此外，clear_child_firings 的變更依賴 RETURNING 子句，但未驗證 SQLite 是否支援，可能造成測試或部署失敗。整體方向正確，但需先解決 lock key 的跨程序一致性與資料庫相容性問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | 使用 hash() 產生 advisory lock key 會因跨程序不一致而失效 | 0.95 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:154` | SQLite 不支援 RETURNING 子句，可能導致 clear_child_firings 失敗 | 0.80 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:73` | [R03] Logger 初始化違反專案規範 | 0.90 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:71` | import logging 位置不當，可能違反 PEP8 或專案慣例 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> 使用 hash() 產生 advisory lock key 會因跨程序不一致而失效</summary>

`lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建 hash()，其值在每次程序啟動時會因 PYTHONHASHSEED 而不同。這會導致不同 worker 程序對同一個 trigger.id 計算出不同的 lock key，使得 advisory lock 無法互斥，競態條件依然存在。

建議改用 trigger.id 的整數表示（例如 `trigger.id.int`）或直接使用 UUID 的 bytes 轉成整數，確保跨程序一致。

**判斷依據**：diff 中新增的 `lock_key = hash(str(trigger.id)) % (2**63)` 行，且 Python 的 hash() 對字串在預設情況下會使用隨機種子（PYTHONHASHSEED），導致跨程序不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:154</code> SQLite 不支援 RETURNING 子句，可能導致 clear_child_firings 失敗</summary>

`clear_child_firings` 新增了 `.returning(...)`，但 SQLite 在較舊版本（<3.35）不支援 DELETE ... RETURNING。若專案支援的 SQLite 版本低於此，此查詢會拋出例外，導致複合觸發器評估失敗。

建議確認支援的 SQLite 版本，或改用先 SELECT 再 DELETE 的方式，或針對不同 dialect 做條件處理。

**判斷依據**：diff 中新增的 `.returning(...)` 呼叫，且程式碼中未見對 SQLite 的相容處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:73</code> [R03] Logger 初始化違反專案規範</summary>

專案規範 R03 要求 logger 使用 `logger: "logging.Logger" = get_logger(__name__)` 模式，但此處改為 `logger = logging.getLogger(__name__)`，且移除了型別註記。

建議改回 `logger: "logging.Logger" = get_logger(__name__)`。

**判斷依據**：diff 中將原本的 `logger: "logging.Logger" = get_logger(__name__)` 改為 `logger = logging.getLogger(__name__)`，違反 R03。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:71</code> import logging 位置不當，可能違反 PEP8 或專案慣例</summary>

`import logging` 被放在 `if TYPE_CHECKING:` 區塊之後，且與其他 import 分離。通常 import 應集中在檔案頂部，除非有特殊原因。建議將 `import logging` 移到檔案頂部與其他 import 一起。

**判斷依據**：diff 中新增的 `import logging` 位於 `if TYPE_CHECKING:` 之後，且與其他 import 分離。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6578 (cache hit 6528) ｜ completion tokens 1079 ｜ PR #7</sub>