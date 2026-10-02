<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 修正 HINCRBYFLOAT 在複製到 replica 時會移除欄位過期時間的問題。主要變更包括：hashTypeGetValue 新增 expiredAt 輸出參數、hincrbyfloatCommand 在欄位有過期時間時手動傳播 HSET 與 HPEXPIREAT 指令、新增 shared.fields 共用物件，以及新增測試。整體方向正確，但存在一個明確的陣列越界錯誤（argv 大小為 5 但寫入 6 個元素），可能導致記憶體損毀，必須修正。此外，測試中對複製流的斷言可能過於嚴格，且部分程式碼風格可改善。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/t_hash.c:2306` | argv 陣列大小不足，寫入 6 個元素導致堆疊緩衝區溢位 | 0.99 |
| ⚠️ | Major | `src/t_hash.c:2309` | createStringObjectFromLongLong 建立的物件未釋放，造成記憶體洩漏 | 0.85 |
| 🔸 | Minor | `src/t_hash.c:2244` | 變數 unused_flag 宣告後未使用 | 0.70 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1288` | 測試中對複製流的斷言可能過於嚴格 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/t_hash.c:2306</code> argv 陣列大小不足，寫入 6 個元素導致堆疊緩衝區溢位</summary>

在 hincrbyfloatCommand 中，宣告 `robj *argv[5];` 但隨後寫入 `argv[0]` 到 `argv[5]` 共 6 個元素，造成陣列越界寫入。這會破壞堆疊上的其他變數，可能導致程式崩潰或任意程式碼執行。

建議將陣列大小改為 6：
```c
robj *argv[6];
```

**判斷依據**：diff 中新增的程式碼片段顯示 `robj *argv[5];` 但後續指派了 6 個元素（索引 0 到 5）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2309</code> createStringObjectFromLongLong 建立的物件未釋放，造成記憶體洩漏</summary>

`argv[2] = createStringObjectFromLongLong(expireat);` 建立了一個新的 robj，但在 alsoPropagate 之後沒有對其呼叫 decrRefCount。雖然 alsoPropagate 可能會複製參照，但此處建立的物件在函式結束後不再使用，應釋放以避免記憶體洩漏。

建議在 alsoPropagate 呼叫後加入 `decrRefCount(argv[2]);`。

**判斷依據**：diff 中新增的程式碼建立物件後未見對應的釋放操作。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/t_hash.c:2244</code> 變數 unused_flag 宣告後未使用</summary>

在 hincrbyfloatCommand 中宣告了 `int unused_flag = 0;` 但從未使用。這可能是開發過程中的殘留，應移除。

**判斷依據**：diff 中新增的變數宣告，但後續程式碼未引用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1288</code> 測試中對複製流的斷言可能過於嚴格</summary>

測試使用 `assert_replication_stream` 檢查複製流的精確內容，包括 `{hset h1 f1 *}` 和 `{hpexpireat h1 * FIELDS 1 f1}`。但 `hset` 的值和 `hpexpireat` 的過期時間是動態的，使用 `*` 萬用字元可能無法匹配所有情況，且未來實作變更可能導致測試脆弱。建議改為驗證關鍵指令的存在而非完整序列。

**判斷依據**：測試中對複製流的精確匹配可能因動態值而失敗。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5008 (cache hit 1536) ｜ completion tokens 1126 ｜ PR #8</sub>