<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 試圖解決複合觸發器在並行評估時的競態條件，透過加入 advisory lock 與 DELETE ... RETURNING 來確保只有一個 worker 能觸發父觸發器。整體方向合理，但實作中有幾個關鍵問題：advisory lock 的 key 使用 Python hash() 產生，跨程序不穩定，可能導致鎖失效；clear_child_firings 的 RETURNING 子句在 SQLite 上可能不支援，且未處理資料庫方言差異；logger 初始化方式違反專案規範 R03。建議先修正 lock key 的產生方式與資料庫相容性問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | advisory lock key 使用 Python hash() 導致跨程序不一致 | 0.95 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:154` | SQLite 不支援 RETURNING 子句，可能導致 clear_child_firings 失敗 | 0.85 |
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | advisory lock key 截斷可能導致碰撞 | 0.80 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:73` | [R03] Logger 初始化方式違反專案規範 | 0.90 |
| 🔸 | Minor | `src/prefect/server/events/triggers.py:406` | 日誌訊息中 extra 參數可能導致格式錯誤 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> advisory lock key 使用 Python hash() 導致跨程序不一致</summary>

`lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建的 `hash()` 函數。Python 的 `hash()` 對於字串會加入隨機的 salt（PYTHONHASHSEED），因此同一個 trigger.id 在不同程序（或不同次執行）中會產生不同的 hash 值。這會導致 advisory lock 的 key 不一致，使得鎖無法正確序列化跨程序的並行操作，競態條件仍然存在。

建議改用穩定的整數表示，例如直接使用 UUID 的 int 值（`trigger.id.int`）或將其轉換為 bytes 後取前 8 bytes 轉為整數。

**判斷依據**：diff 中新增的 `acquire_composite_trigger_lock` 函式內，使用 `hash(str(trigger.id))` 來產生 lock key。Python 的 `hash()` 對字串使用隨機 seed，跨程序不穩定。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:154</code> SQLite 不支援 RETURNING 子句，可能導致 clear_child_firings 失敗</summary>

`clear_child_firings` 使用 `sa.delete(...).returning(...)`，但 SQLite 在較舊版本（<3.35）不支援 DELETE ... RETURNING。Prefect 支援 SQLite 作為後端資料庫，這可能導致在 SQLite 上執行時拋出例外。

建議檢查資料庫方言，若不支援 RETURNING，則改用先 SELECT 再 DELETE 的方式，或使用其他方式取得被刪除的 ID。

**判斷依據**：diff 中 `clear_child_firings` 的修改加入了 `.returning(...)`，但未處理 SQLite 的相容性。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> advisory lock key 截斷可能導致碰撞</summary>

`lock_key = hash(str(trigger.id)) % (2**63)` 將 UUID 的 hash 值截斷為 63 位元，雖然註解說「collision is extremely unlikely and benign」，但實際上若發生碰撞，兩個不同的 trigger 會共用同一個 lock，可能導致不必要的序列化，甚至在某些情況下造成死鎖或效能問題。

建議使用完整的 UUID int 值（128 位元）或使用兩個 bigint 參數來避免截斷。

**判斷依據**：diff 中明確使用 `% (2**63)` 進行截斷。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:73</code> [R03] Logger 初始化方式違反專案規範</summary>

專案規範 R03 要求 logger 使用 `get_logger(__name__)` 並以型別註記方式初始化。此處將原本的 `logger: "logging.Logger" = get_logger(__name__)` 改為 `logger = logging.getLogger(__name__)`，違反了規範。

建議改回使用 `get_logger` 並保留型別註記。

**判斷依據**：diff 中將 logger 初始化從 `get_logger` 改為 `logging.getLogger`，且移除了型別註記。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/triggers.py:406</code> 日誌訊息中 extra 參數可能導致格式錯誤</summary>

在 `logger.debug` 的 `extra` 參數中，使用了 `sorted(str(f) for f in firing_ids)` 和 `sorted(str(f) for f in deleted_ids)`，但 `firing_ids` 和 `deleted_ids` 的型別可能不是可迭代的 UUID 集合？從上下文看，`firing_ids` 是 `list[UUID]`，`deleted_ids` 是 `set[UUID]`，應該沒問題。但若未來型別改變，可能導致錯誤。

建議確認型別，或直接使用 `list(map(str, ...))` 以確保可迭代。

**判斷依據**：diff 中新增的日誌程式碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5785 (cache hit 4224) ｜ completion tokens 1443 ｜ PR #7</sub>