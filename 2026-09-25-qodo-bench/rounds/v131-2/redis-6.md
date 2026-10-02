<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Redis 版本從 8.2.0 更新至 8.2.1，並包含多項錯誤修正與測試變更。主要風險在於 `src/replication.c` 中 active defrag 的暫時停用與恢復邏輯，可能因未使用原始值而導致設定不一致；`src/t_stream.c` 的 null 檢查可能改變既有行為；測試程式碼的輔助函式 `discard_replies_every` 邏輯可能與原意不符。建議優先修正 replication.c 中的設定恢復問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/replication.c:1962` | active defrag 設定恢復錯誤 | 0.95 |
| ⚠️ | Major | `src/t_stream.c:2708` | streamEntryIsReferenced 的 null 檢查可能改變行為 | 0.80 |
| ⚠️ | Major | `tests/unit/memefficiency.tcl:70` | discard_replies_every 邏輯可能錯誤 | 0.70 |
| 🔸 | Minor | `tests/unit/memefficiency.tcl:982` | 測試中可能未正確處理 activedefrag 設定 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/replication.c:1962</code> active defrag 設定恢復錯誤</summary>

在 `rdbLoadEmptyDbFunc` 中，暫時停用 active defrag 後，恢復時直接將 `server.active_defrag_enabled` 設為 1，而非使用先前儲存的 `orig_active_defrag`。這會導致即使原本設定為停用，函式執行後仍會強制啟用 active defrag，可能造成非預期的記憶體整理行為或效能影響。

建議改為 `server.active_defrag_enabled = orig_active_defrag;`。

**判斷依據**：diff 中新增的程式碼：
```
+    int orig_active_defrag = server.active_defrag_enabled;
+    server.active_defrag_enabled = 0;
...
+    server.active_defrag_enabled = 1;
```
恢復時未使用 `orig_active_defrag`，而是硬編碼為 1。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2708</code> streamEntryIsReferenced 的 null 檢查可能改變行為</summary>

新增的 `if (!s->cgroups_ref) return 1;` 會在沒有 consumer groups 時直接回傳 1（表示被引用），這可能導致某些刪除或修剪邏輯誤判訊息仍被引用，進而無法正確釋放記憶體或刪除條目。需要確認此變更是否符合預期，並檢查所有呼叫此函式的情境。

**判斷依據**：diff 中新增的這一行。原本若 `s->cgroups_ref` 為 NULL，`raxFind` 可能處理 NULL 指標而 crash，但直接回傳 1 可能掩蓋了真實的引用狀態。

</details>

<details><summary>⚠️ <b>Major</b> — <code>tests/unit/memefficiency.tcl:70</code> discard_replies_every 邏輯可能錯誤</summary>

新增的輔助函式 `discard_replies_every` 在 `count % frequency == 0` 時不丟棄任何回覆，否則丟棄 `discard_num` 個回覆。這與原本的邏輯相反：原本是每 `frequency` 次丟棄 `discard_num` 個回覆。這可能導致測試中累積過多未讀回覆，造成記憶體問題或測試失敗。

建議修正條件，例如改為 `if {$count % $frequency == 0}` 才丟棄。

**判斷依據**：diff 中新增的函式，條件判斷為 `!= 0` 才丟棄，與原本的 `== 0` 相反。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/memefficiency.tcl:982</code> 測試中可能未正確處理 activedefrag 設定</summary>

在新增的測試中，使用 `catch {$replica config set activedefrag yes} e` 來嘗試啟用 active defrag，但未檢查錯誤內容。若設定失敗，後續的 `if` 條件可能無法正確判斷，導致測試跳過或誤判。建議明確處理錯誤或使用 `assert` 驗證設定成功。

**判斷依據**：diff 中新增的測試程式碼片段。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4782 (cache hit 4736) ｜ completion tokens 1178 ｜ PR #6</sub>