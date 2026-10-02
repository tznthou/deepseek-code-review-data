<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Redis 版本從 8.2.0 升級至 8.2.1，並包含三個主要變更：修正複製期間資料庫清空時可能觸發 active defrag 的問題、修正 stream 在沒有 consumer group 參考時 XADD ACKED 可能當機的問題，以及重構測試程式碼。主要風險在於 replication.c 中 active defrag 的停用/恢復邏輯可能不正確，以及 t_stream.c 中新增的 null 檢查可能改變既有行為。建議先修正 replication.c 的恢復邏輯，並確認 stream 變更的相容性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/replication.c:1961` | active defrag 恢復邏輯錯誤：無條件設為 1，忽略原始設定 | 0.95 |
| ⚠️ | Major | `src/t_stream.c:2707` | streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1 可能造成記憶體洩漏或錯誤保留 | 0.80 |
| 🔸 | Minor | `tests/unit/memefficiency.tcl:70` | discard_replies_every 函式參數名稱與用途不符 | 0.70 |
| 🔸 | Minor | `tests/unit/memefficiency.tcl:989` | 測試中直接使用 `s` 指令可能取得錯誤的 server 資訊 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/replication.c:1961</code> active defrag 恢復邏輯錯誤：無條件設為 1，忽略原始設定</summary>

在 `rdbLoadEmptyDbFunc` 中，程式碼先將 `server.active_defrag_enabled` 存入 `orig_active_defrag`，然後設為 0，但在 `emptyData` 呼叫後卻直接設為 1，而不是恢復為 `orig_active_defrag`。這會導致即使原本 active defrag 是停用的，此函式執行後也會被強制啟用，可能造成非預期的記憶體整理行為，甚至影響效能或穩定性。

**失敗情境**：若使用者在設定檔中明確停用 active defrag（`activedefrag no`），當 replica 進行同步並觸發此函式後，active defrag 會被意外啟用，直到下次設定變更。

**建議修法**：將 `server.active_defrag_enabled = 1;` 改為 `server.active_defrag_enabled = orig_active_defrag;`

**判斷依據**：diff 中新增的兩行：`int orig_active_defrag = server.active_defrag_enabled;` 和 `server.active_defrag_enabled = 1;`。變數 `orig_active_defrag` 被儲存但從未被使用，且恢復值硬編碼為 1。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2707</code> streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1 可能造成記憶體洩漏或錯誤保留</summary>

新增的 `if (!s->cgroups_ref) return 1;` 表示當 stream 沒有 consumer group 參考時，函式直接回傳 1（代表被參考）。這可能導致呼叫者認為該 entry 仍被參考，而無法刪除或釋放，造成記憶體洩漏或資料不一致。

**失敗情境**：在沒有 consumer group 的 stream 上執行 XADD with MAXLEN 或 XTRIM 時，舊的 entry 可能因為被誤判為「被參考」而無法被刪除，導致 stream 長度超過預期。

**建議修法**：確認此行為是否符合預期。若沒有 cgroups_ref 就應該視為未被參考，應回傳 0；若此處是為了避免後續 raxFind 對 NULL 的 dereference，則應在呼叫前檢查，而不是直接回傳 1。

**判斷依據**：diff 中新增的 `if (!s->cgroups_ref) return 1;` 行。此函式用於判斷 entry 是否被參考，回傳 1 表示被參考，但當 cgroups_ref 為 NULL 時，實際上沒有 consumer group 參考，回傳 1 可能不正確。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/memefficiency.tcl:70</code> discard_replies_every 函式參數名稱與用途不符</summary>

函式 `discard_replies_every` 的參數 `frequency` 和 `discard_num` 的命名容易混淆。`frequency` 實際上是檢查的間隔（例如每 10000 次），而 `discard_num` 是要丟棄的回覆數量。建議改名為 `interval` 和 `num_to_discard` 以提高可讀性。

**判斷依據**：diff 中新增的函式定義。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/memefficiency.tcl:989</code> 測試中直接使用 `s` 指令可能取得錯誤的 server 資訊</summary>

在新增的測試中，`wait_for_condition` 內使用 `[s total_active_defrag_time]`，但 `s` 是預設的 server client，可能指向 master 而非 replica。應使用 `$replica` 來取得 replica 的資訊。

**判斷依據**：diff 中新增的測試程式碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5829 (cache hit 5760) ｜ completion tokens 1327 ｜ PR #6</sub>