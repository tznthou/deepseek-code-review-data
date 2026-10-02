<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 修正 HINCRBYFLOAT 在複本上會移除欄位過期時間的問題。主要變更為 hashTypeGetValue 增加 expiredAt 輸出參數，並在 hincrbyfloatCommand 中偵測過期時間，若有則手動傳播 HSET 與 HPEXPIREAT 指令。整體方向正確，但存在一個明確的陣列越界錯誤（argv 大小不足），可能導致記憶體損壞或崩潰，必須修正。另有測試涵蓋不足與程式碼可讀性問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/t_hash.c:2306` | argv 陣列大小不足，寫入 argv[5] 導致堆疊緩衝區溢位 | 0.95 |
| ⚠️ | Major | `src/t_hash.c:2309` | 手動傳播 HPEXPIREAT 時未處理 createStringObjectFromLongLong 可能失敗的情況 | 0.80 |
| ⚠️ | Major | `src/t_hash.c:2304` | 手動傳播指令時未處理 alsoPropagate 的失敗情況 | 0.70 |
| 🔸 | Minor | `src/t_hash.c:2310` | 使用 shared.fields 與 shared.integers[1] 作為 HPEXPIREAT 參數，但未確認其初始化狀態 | 0.60 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1290` | 測試未涵蓋 HINCRBYFLOAT 在欄位無過期時間時的正確性 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>src/t_hash.c:2306</code> argv 陣列大小不足，寫入 argv[5] 導致堆疊緩衝區溢位</summary>

在 hincrbyfloatCommand 中，宣告 `robj *argv[5];` 但後續指派 `argv[5] = c->argv[2];`，索引 5 超出陣列範圍（合法索引為 0-4）。這會造成堆疊緩衝區溢位，可能導致程式崩潰或任意程式碼執行。

失敗情境：當欄位有過期時間時，執行 HINCRBYFLOAT 即觸發此寫入。

建議修正：將陣列大小改為 6，例如 `robj *argv[6];`。

**判斷依據**：diff 中新增的程式碼片段顯示 `robj *argv[5];` 宣告大小為 5，但後續指派 `argv[5] = c->argv[2];` 使用索引 5，超出陣列邊界。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2309</code> 手動傳播 HPEXPIREAT 時未處理 createStringObjectFromLongLong 可能失敗的情況</summary>

`createStringObjectFromLongLong(expireat)` 可能因為記憶體不足而回傳 NULL，但程式碼未檢查就直接指派給 argv[2]，後續 alsoPropagate 可能對 NULL 物件進行操作，導致崩潰。

失敗情境：在記憶體極度不足時，執行 HINCRBYFLOAT 且欄位有過期時間。

建議修正：檢查回傳值，若為 NULL 則回傳錯誤或採取其他處理。

**判斷依據**：diff 中新增的程式碼直接呼叫 createStringObjectFromLongLong 而未檢查回傳值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2304</code> 手動傳播指令時未處理 alsoPropagate 的失敗情況</summary>

alsoPropagate 可能因為記憶體不足或其他原因失敗，但程式碼未檢查其回傳值。若傳播失敗，可能導致主從資料不一致。

失敗情境：在記憶體不足或網路異常時，HSET 或 HPEXPIREAT 未能正確傳播到 AOF 或複本。

建議修正：檢查 alsoPropagate 的回傳值，若失敗則進行適當處理（如記錄錯誤或回傳錯誤給客戶端）。

**判斷依據**：diff 中新增的 alsoPropagate 呼叫未檢查回傳值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/t_hash.c:2310</code> 使用 shared.fields 與 shared.integers[1] 作為 HPEXPIREAT 參數，但未確認其初始化狀態</summary>

shared.fields 在 createSharedObjects 中初始化，但 shared.integers[1] 是否已初始化需確認。若未初始化，可能導致傳播錯誤的指令。

失敗情境：若 shared.integers[1] 未正確初始化，傳播的 HPEXPIREAT 指令可能包含錯誤的參數。

建議修正：確認 shared.integers[1] 在 createSharedObjects 中已正確初始化，或改用其他方式建立整數物件。

**判斷依據**：diff 中新增的程式碼使用 shared.integers[1]，但未在 diff 中看到其初始化。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1290</code> 測試未涵蓋 HINCRBYFLOAT 在欄位無過期時間時的正確性</summary>

測試中對 f2 執行 HINCRBYFLOAT，但未驗證其值是否正確（僅驗證無過期時間）。建議增加對 f2 值的斷言，以確保 HINCRBYFLOAT 在無過期時間時仍正常運作。

失敗情境：若 HINCRBYFLOAT 在無過期時間時有錯誤，此測試無法發現。

建議修正：增加 `assert_equal [r -1 hget h1 f2] [r hget h1 f2]` 或類似斷言。

**判斷依據**：測試中對 f2 的驗證僅有 httl 和 hget，但未驗證 hget 的值是否正確。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5008 (cache hit 4992) ｜ completion tokens 1568 ｜ PR #8</sub>