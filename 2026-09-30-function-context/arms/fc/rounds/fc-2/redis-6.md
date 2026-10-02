<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Redis 版本從 8.2.0 更新至 8.2.1，並包含三個主要修正：在複製資料庫清空期間停用主動碎片整理、修復 stream 在 RDB 載入後因缺少 cgroups_ref 而可能發生的崩潰，以及新增對應的測試。整體風險中等，主要疑慮在於 replication.c 中恢復 active_defrag_enabled 的方式可能不正確，以及 stream.c 的修正可能改變既有行為。建議優先修正 replication.c 的設定恢復邏輯，並確認 stream.c 的變更是否會影響其他依賴 cgroups_ref 為 NULL 的程式碼路徑。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/replication.c:1961` | active_defrag_enabled 恢復方式錯誤，可能永久停用主動碎片整理 | 0.95 |
| ⚠️ | Major | `src/t_stream.c:2707` | streamEntryIsReferenced 在 cgroups_ref 為 NULL 時直接回傳 1，可能導致記憶體洩漏或錯誤保留 | 0.80 |
| 🔸 | Minor | `tests/unit/memefficiency.tcl:100` | 測試中 discard_replies_every 的 discard_num 參數可能與實際回覆數不符 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/replication.c:1961</code> active_defrag_enabled 恢復方式錯誤，可能永久停用主動碎片整理</summary>

在 `rdbLoadEmptyDbFunc()` 中，程式碼先將 `server.active_defrag_enabled` 儲存至 `orig_active_defrag`，然後設為 0，但在 `emptyData()` 呼叫後卻直接設回 1，而非恢復為 `orig_active_defrag`。

**失敗情境**：若使用者在執行 replicaof 同步前已將 `activedefrag` 設為 `no`（即 `server.active_defrag_enabled` 原本為 0），則此函式執行後會將該值強制設為 1，導致主動碎片整理被意外啟用，可能造成不必要的延遲或資源消耗。

**建議修法**：將 `server.active_defrag_enabled = 1;` 改為 `server.active_defrag_enabled = orig_active_defrag;`。

**判斷依據**：diff 中新增的兩行：`int orig_active_defrag = server.active_defrag_enabled;` 與 `server.active_defrag_enabled = 1;`。前者儲存原始值，後者卻忽略該值直接設為 1，明顯違反註解所述「Restore the original active defragmentation setting」。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2707</code> streamEntryIsReferenced 在 cgroups_ref 為 NULL 時直接回傳 1，可能導致記憶體洩漏或錯誤保留</summary>

新增的 `if (!s->cgroups_ref) return 1;` 會在 `cgroups_ref` 為 NULL 時直接回傳 1，表示該 entry 被引用。這可能發生在 RDB 載入後，若 stream 有 consumer groups 但尚未建立 `cgroups_ref`（例如所有 PEL 皆為空）。

**失敗情境**：當 `cgroups_ref` 為 NULL 且 `min_cgroup_last_id` 小於 entry ID 時，原本應回傳 0（未被引用），但現在會回傳 1，導致 `XADD` 或 `XTRIM` 無法刪除實際上已無引用的 entry，造成記憶體無法釋放。

**建議修法**：確認 `cgroups_ref` 為 NULL 時的預期行為。若 NULL 代表沒有 PEL 引用，應回傳 0；若代表未知，則應先建立 `cgroups_ref` 或採用其他方式判斷。

**判斷依據**：diff 新增的 `if (!s->cgroups_ref) return 1;` 位於原本的 `raxFind` 呼叫之前。原本若 `cgroups_ref` 為 NULL，`raxFind` 可能無法處理，但直接回傳 1 可能過度保守，影響記憶體回收。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/memefficiency.tcl:100</code> 測試中 discard_replies_every 的 discard_num 參數可能與實際回覆數不符</summary>

在 `discard_replies_every` 的呼叫中，部分傳入的 `discard_num` 可能與該迴圈每次迭代產生的回覆數不一致。例如在 `Active defrag big list` 測試中，每次迭代會產生兩個回覆（`lpush` 兩次），但呼叫時傳入的 `discard_num` 為 20000，而 `frequency` 為 10000，這表示每 10000 次迭代會丟棄 20000 個回覆，但實際上每 10000 次迭代會產生 20000 個回覆，因此正確。然而在其他地方（如 `Active defrag big keys` 的 `hset` 迴圈）每次迭代只產生一個回覆，但傳入的 `discard_num` 為 10000，頻率為 10000，這也正確。需要逐一檢查所有呼叫點，確保 `discard_num` 等於 `frequency` 乘以每次迭代的回覆數。

**建議**：在程式碼審查中確認所有呼叫點的參數正確性，或考慮改為自動計算回覆數。

**判斷依據**：diff 中多處將原本的 `if {$count % 10000 == 0} { for {set k 0} {$k < 10000} {incr k} { $rd read } }` 替換為 `discard_replies_every $rd $count 10000 10000`。此重構本身合理，但需確保參數與實際回覆數匹配。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 23032 (cache hit 22912) ｜ completion tokens 1420 ｜ PR #6</sub>