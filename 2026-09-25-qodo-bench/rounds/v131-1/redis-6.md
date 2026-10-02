<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Redis 版本從 8.2.0 更新至 8.2.1，並包含多項錯誤修正與測試變更。主要風險在於 `rdbLoadEmptyDbFunc` 中對 `active_defrag_enabled` 的處理：程式碼在函式結尾無條件將其設為 1，而非還原為原始值，可能導致原本停用 defrag 的伺服器意外啟用。此外，`streamEntryIsReferenced` 新增的 `if (!s->cgroups_ref) return 1;` 邏輯可能不正確，需確認其意圖。測試程式碼的重構大致安全，但新測試中的條件判斷可能因型別不符而永遠為真，需驗證。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/replication.c:1961` | active_defrag_enabled 未正確還原，可能意外啟用 defrag | 0.95 |
| ⚠️ | Major | `src/t_stream.c:2708` | streamEntryIsReferenced 中 cgroups_ref 為 NULL 時回傳 1 可能不正確 | 0.80 |
| ⚠️ | Major | `tests/unit/memefficiency.tcl:983` | 測試條件判斷可能因型別不符而永遠為真 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/replication.c:1961</code> active_defrag_enabled 未正確還原，可能意外啟用 defrag</summary>

在 `rdbLoadEmptyDbFunc` 中，程式碼先將 `server.active_defrag_enabled` 存入 `orig_active_defrag`，然後設為 0，但在函式結尾卻直接設為 1，而非還原為 `orig_active_defrag`。這會導致原本停用 active defrag 的伺服器在執行此函式後被強制啟用，可能造成非預期的記憶體整理行為，甚至影響效能或穩定性。

建議修正：
```c
server.active_defrag_enabled = orig_active_defrag;
```

**判斷依據**：diff 中新增的程式碼：
```c
+    int orig_active_defrag = server.active_defrag_enabled;
+    server.active_defrag_enabled = 0;
...
+    server.active_defrag_enabled = 1;
```
註解聲稱要還原，但實際值固定為 1。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_stream.c:2708</code> streamEntryIsReferenced 中 cgroups_ref 為 NULL 時回傳 1 可能不正確</summary>

新增的 `if (!s->cgroups_ref) return 1;` 表示當 stream 沒有 consumer groups 時，直接回傳 1（代表被引用）。這可能導致呼叫者誤判 entry 仍被引用，進而無法刪除或處理。需確認此邏輯是否符合預期：若沒有 cgroups，entry 應只被 stream 本身引用，回傳 1 可能造成記憶體無法釋放或錯誤行為。

建議：確認此處應回傳 0 或 1，並補充註解說明。

**判斷依據**：diff 中新增的一行，位於 `streamEntryIsReferenced` 函式內，在檢查 PEL 之前。

</details>

<details><summary>⚠️ <b>Major</b> — <code>tests/unit/memefficiency.tcl:983</code> 測試條件判斷可能因型別不符而永遠為真</summary>

在新增的測試中，`if {[$replica config get activedefrag] eq "activedefrag yes"}` 的寫法可能有誤。`config get activedefrag` 回傳的是一個 list，例如 `{activedefrag yes}`，直接與字串比較會永遠不相等，導致條件永遠為假，測試主體不會執行。應改為：
```tcl
if {[lindex [$replica config get activedefrag] 1] eq "yes"} {
```
或使用 `[dict get [$replica config get activedefrag] activedefrag]`。

**判斷依據**：diff 中新增的測試程式碼，該行用於判斷是否成功啟用 activedefrag。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4782 (cache hit 1408) ｜ completion tokens 1044 ｜ PR #6</sub>