<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 objectComputeSize 改名為 kvobjComputeSize，並調整記憶體計算方式，使其包含 kvobj 標頭與嵌入的 key。主要風險在於計算方式變更可能導致記憶體估算不準確，且新增測試的斷言可能過於寬鬆或錯誤。建議先修正測試中的變數名稱錯誤，並確認記憶體計算邏輯的正確性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `tests/unit/type/string.tcl:708` | 測試中變數名稱錯誤：使用未定義的 min 變數 | 0.90 |
| ⚠️ | Major | `src/object.c:1217` | 記憶體計算可能重複計算 key 的大小 | 0.80 |
| 🔸 | Minor | `src/object.c:1239` | 取樣計算中除以 samples 可能導致高估 | 0.70 |
| 🔸 | Minor | `src/object.c:1330` | Stream 記憶體計算中乘以 numele 可能包含未取樣的最後一個元素 | 0.70 |
| 🔸 | Minor | `tests/unit/type/string.tcl:702` | 測試斷言可能過於寬鬆 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>tests/unit/type/string.tcl:708</code> 測試中變數名稱錯誤：使用未定義的 min 變數</summary>

在測試中，`set min [expr $hdrsize + $ksize]` 使用了未定義的變數 `min`，應為 `min` 但實際上變數名為 `min`，但此處可能為筆誤，應為 `min` 或 `min_size`。這會導致 Tcl 錯誤，使測試失敗。

**判斷依據**：diff 中新增的測試程式碼包含此行，且未定義 `min` 變數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1217</code> 記憶體計算可能重複計算 key 的大小</summary>

在 `kvobjComputeSize` 中，`asize` 初始化為 `malloc_usable_size((void *)o)`，這包含了 kvobj 結構體本身以及可能嵌入的 key。但後續在處理不同類型時，並未明確排除 key 的大小，可能導致 key 被重複計算。例如，對於 OBJ_STRING 的 RAW 編碼，`asize += sdsZmallocSize(o->ptr)` 只計算 value 的大小，但 key 可能已包含在 `malloc_usable_size` 中，若 key 是單獨分配則可能重複計算。需要確認 kvobj 的記憶體佈局。

**判斷依據**：diff 中新增此行，且後續計算未扣除 key 大小。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/object.c:1239</code> 取樣計算中除以 samples 可能導致高估</summary>

在 quicklist 的計算中，原本使用 `elesize/elecount*ql->count`，現在改為 `elesize/samples*ql->count`。若 samples 小於 elecount，則平均每個元素的大小會被高估，導致整體估算偏大。建議確認此變更的意圖。

**判斷依據**：diff 中此行由 `elesize/elecount` 改為 `elesize/samples`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/object.c:1330</code> Stream 記憶體計算中乘以 numele 可能包含未取樣的最後一個元素</summary>

在 stream 的計算中，原本使用 `lpsize * (s->rax->numele-1)`，現在改為 `lpsize * s->rax->numele`。這可能導致最後一個 listpack 被重複計算，因為後續有單獨處理最後一個 listpack 的程式碼。需要確認是否會造成高估。

**判斷依據**：diff 中此行由 `numele-1` 改為 `numele`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/string.tcl:702</code> 測試斷言可能過於寬鬆</summary>

測試中 `assert_morethan_equal $max $memory_used` 使用 `max` 為 `min * 2` 或 64，可能無法有效驗證記憶體計算的準確性。建議使用更嚴格的範圍或與預期值比較。

**判斷依據**：diff 中新增的測試斷言。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5782 (cache hit 4736) ｜ completion tokens 1120 ｜ PR #5</sub>