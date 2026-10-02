<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 objectComputeSize 改名為 kvobjComputeSize，並調整記憶體計算方式，使其包含 kvobj header 與 embedded key 的大小。主要風險在於計算邏輯變更可能導致記憶體估算不準確，且新增測試的邊界條件可能過於寬鬆。建議先確認計算方式與實際記憶體配置一致，並補強測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/object.c:1217` | kvobjComputeSize 使用 malloc_usable_size 可能高估記憶體 | 0.80 |
| ⚠️ | Major | `src/object.c:1239` | 快速列表取樣平均計算可能低估記憶體 | 0.70 |
| ⚠️ | Major | `src/object.c:1330` | Stream 記憶體計算可能多算最後一個 listpack | 0.70 |
| 🔸 | Minor | `tests/unit/type/string.tcl:701` | 測試邊界條件可能過於寬鬆 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1217</code> kvobjComputeSize 使用 malloc_usable_size 可能高估記憶體</summary>

函式開頭使用 `malloc_usable_size((void *)o)` 來取得 kvobj 實際配置大小，但此函式回傳的是 malloc 分配區塊的可用大小，可能大於實際使用的記憶體（例如因對齊或分配器 overhead）。這會導致 MEMORY USAGE 回報的數值偏高。建議改用 `zmalloc_size(o)` 或確認 kvobj 的分配方式，以取得精確的配置大小。

**判斷依據**：diff 中新增行 `size_t asize = malloc_usable_size((void *)o);`，取代原本的 `sizeof(*o)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1239</code> 快速列表取樣平均計算可能低估記憶體</summary>

在 quicklist 分支中，原本使用 `elesize/elecount*ql->count` 計算平均每個元素的記憶體，現在改為 `elesize/samples*ql->count`。但 `samples` 是取樣節點數，而非元素數，若節點內元素數不一，此計算可能不準確。建議維持原本的 `elecount` 或改用更精確的加權平均。

**判斷依據**：diff 中將 `asize += (double)elesize/elecount*ql->count;` 改為 `asize += (double)elesize/samples*ql->count;`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1330</code> Stream 記憶體計算可能多算最後一個 listpack</summary>

在 stream 分支中，原本使用 `s->rax->numele-1` 來計算平均 listpack 大小乘以元素數，現在改為 `s->rax->numele`。若最後一個 listpack 未滿，可能導致高估。建議確認 stream 的結構與計算邏輯，或保留原本的 `-1`。

**判斷依據**：diff 中將 `asize += lpsize * (s->rax->numele-1);` 改為 `asize += lpsize * s->rax->numele;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/string.tcl:701</code> 測試邊界條件可能過於寬鬆</summary>

新增的測試中，`max` 的計算為 `32 > $min ? 64 : [expr $min * 2]`，這可能允許過大的記憶體使用量，無法有效偵測記憶體計算錯誤。建議根據實際記憶體配置特性設定更嚴格的上下界。

**判斷依據**：diff 中新增的測試程式碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5758 (cache hit 4736) ｜ completion tokens 969 ｜ PR #5</sub>