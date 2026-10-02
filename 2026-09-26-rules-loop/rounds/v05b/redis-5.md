<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 objectComputeSize 改名為 kvobjComputeSize，並調整記憶體計算方式，使其包含 kvobj 標頭與嵌入的 key。主要風險在於計算邏輯變更可能導致記憶體估算不準確，尤其是 quicklist 與 stream 的取樣計算，以及新增測試的邊界條件。建議先修正 quicklist 的取樣分母與 stream 的 lpsize 計算，再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/object.c:1239` | quicklist 取樣計算使用 samples 而非 elecount 可能導致記憶體估算錯誤 | 0.90 |
| ⚠️ | Major | `src/object.c:1330` | stream 記憶體估算中 lpsize 乘以 numele 可能重複計算最後一個 listpack | 0.85 |
| 🔸 | Minor | `src/object.c:1205` | 函式註解與實際行為可能不符 | 0.70 |
| 🔸 | Minor | `tests/unit/type/string.tcl:701` | 測試中 max 計算可能過於寬鬆，無法有效驗證記憶體估算 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1239</code> quicklist 取樣計算使用 samples 而非 elecount 可能導致記憶體估算錯誤</summary>

在 quicklist 的記憶體估算中，原本使用 `elesize/elecount*ql->count` 來根據平均元素大小推算總大小，但修改後改為 `elesize/samples*ql->count`。當 quicklist 節點中的元素數量（elecount）與取樣節點數（samples）不一致時，會導致估算偏差。例如，若每個節點包含多個元素，samples 會小於 elecount，導致平均大小被高估，進而使總記憶體估算過高。建議改回使用 elecount 作為分母，或明確計算每個元素的平均大小。

**判斷依據**：diff 中將原本的 `asize += (double)elesize/elecount*ql->count;` 改為 `asize += (double)elesize/samples*ql->count;`，但 samples 是節點數，elecount 是元素數，兩者意義不同。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1330</code> stream 記憶體估算中 lpsize 乘以 numele 可能重複計算最後一個 listpack</summary>

在 stream 的記憶體估算中，原本使用 `lpsize * (s->rax->numele-1)` 來估算所有 listpack 的大小，但修改後改為 `lpsize * s->rax->numele`。這可能導致最後一個 listpack 被重複計算，因為在後續程式碼中，最後一個 listpack 的大小會單獨加入。建議確認 numele 的定義，若 numele 包含最後一個 listpack，則應維持減 1。

**判斷依據**：diff 中將 `asize += lpsize * (s->rax->numele-1);` 改為 `asize += lpsize * s->rax->numele;`，但後續程式碼有針對最後一個 listpack 的處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/object.c:1205</code> 函式註解與實際行為可能不符</summary>

函式註解改為「Returns the size in bytes consumed by the object header, key and value in RAM」，但函式參數中仍包含 `key`，且實際計算中並未明確包含 key 的大小（除了透過 `malloc_usable_size((void *)o)` 可能包含嵌入的 key）。建議確認註解是否準確反映實際計算內容，或調整註解以避免誤導。

**判斷依據**：diff 中修改了註解，但函式內部的計算邏輯是否真的包含 key 的大小需要進一步確認。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/string.tcl:701</code> 測試中 max 計算可能過於寬鬆，無法有效驗證記憶體估算</summary>

在新增的測試中，`max` 的計算方式為 `32 > $min ? 64 : [expr $min * 2]`，這可能導致測試過於寬鬆，無法有效驗證記憶體估算的準確性。建議根據實際記憶體配置設定更嚴格的界限，或使用更精確的預期值。

**判斷依據**：diff 中新增的測試程式碼，max 的計算方式可能無法有效捕捉記憶體估算的錯誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5758 (cache hit 5632) ｜ completion tokens 1131 ｜ PR #5</sub>