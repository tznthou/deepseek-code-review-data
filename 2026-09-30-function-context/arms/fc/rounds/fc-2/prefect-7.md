<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在修復複合觸發器在並行評估時的競態條件，透過新增 advisory lock 與 DELETE ... RETURNING 來確保只有一個 worker 能觸發父觸發器。整體方向正確，但 lock key 的產生方式存在碰撞風險，且 lock 的取得時機可能不足以完全序列化評估。此外，測試僅驗證了 PostgreSQL 路徑，未涵蓋 SQLite 的 fallback 行為。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/prefect/server/events/models/composite_trigger_child_firing.py:42` | advisory lock key 使用 hash() 可能導致碰撞 | 0.80 |
| ⚠️ | Major | `src/prefect/server/events/triggers.py:349` | advisory lock 取得時機可能不足以完全序列化 | 0.70 |
| 🔸 | Minor | `src/prefect/server/events/models/composite_trigger_child_firing.py:46` | SQLite 不支援 advisory lock，但未提供替代方案 | 0.60 |
| 🔸 | Minor | `tests/events/server/triggers/test_composite_triggers.py:1674` | 測試未涵蓋 SQLite 路徑 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:42</code> advisory lock key 使用 hash() 可能導致碰撞</summary>

使用 `hash(str(trigger.id)) % (2**63)` 作為 advisory lock 的 key，但 Python 的 `hash()` 對字串會隨機化（PYTHONHASHSEED），且可能產生碰撞。碰撞會導致不同的 trigger 共用同一把鎖，造成不必要的序列化，甚至可能讓不相關的 trigger 互相阻塞。建議改用 UUID 的整數表示（例如 `trigger.id.int`）或直接使用 UUID 的 bytes 轉成整數，以確保唯一性。

**判斷依據**：diff 中新增的 `acquire_composite_trigger_lock` 函式內，使用 `hash(str(trigger.id))` 來產生 lock key。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/events/triggers.py:349</code> advisory lock 取得時機可能不足以完全序列化</summary>

在 `evaluate_composite_trigger` 中，lock 是在 `trigger.num_expected_firings != 1` 且執行 `clear_old_child_firings` 之前取得。但 `clear_old_child_firings` 會刪除過期的 child firings，若兩個 worker 同時執行，其中一個可能在另一個取得 lock 前就刪除了資料，導致後續的 `get_child_firings` 結果不一致。建議將 lock 的取得移至函式最開頭，涵蓋整個評估流程。

**判斷依據**：diff 中 `evaluate_composite_trigger` 的修改，lock 在 `clear_old_child_firings` 之前取得，但 `clear_old_child_firings` 本身可能影響後續的判斷。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/events/models/composite_trigger_child_firing.py:46</code> SQLite 不支援 advisory lock，但未提供替代方案</summary>

程式碼中註解提到 SQLite 不支援 advisory lock，且 SQLite 會序列化寫入，因此 race condition 較不易發生。但 SQLite 的寫入序列化僅在單一程序內有效，若有多個 worker 程序（例如多個 Prefect server instance）同時存取同一個 SQLite 資料庫，仍可能發生競態。建議在 SQLite 情況下考慮使用其他機制（例如樂觀鎖或應用層級的鎖）來確保一致性。

**判斷依據**：diff 中 `acquire_composite_trigger_lock` 的註解，僅說明 SQLite 不支援，但未提供替代方案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/events/server/triggers/test_composite_triggers.py:1674</code> 測試未涵蓋 SQLite 路徑</summary>

新增的測試僅在 PostgreSQL 環境下執行（因為使用了 advisory lock），但未測試 SQLite 下的行為。若專案支援 SQLite，應增加對應的測試，確保在 SQLite 下不會因為缺少 lock 而導致錯誤。

**判斷依據**：diff 中新增的測試類別 `TestCompoundTriggerConcurrency`，未見針對 SQLite 的測試。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6227 (cache hit 6144) ｜ completion tokens 1248 ｜ PR #7</sub>