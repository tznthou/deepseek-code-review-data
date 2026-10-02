<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 objectComputeSize 改名為 kvobjComputeSize，並調整記憶體計算方式：先以 malloc_usable_size(o) 取得 kvobj 整體大小，再累加內部結構。主要風險在於 malloc_usable_size 可能回傳大於實際配置的大小，導致高估；且對 OBJ_ENCODING_INT 的處理未將整數值本身計入，可能低估。此外，quicklist 的取樣平均計算改為除以 samples 而非 elecount，可能造成高估。測試新增了 MEMORY USAGE 的覆蓋，但未涵蓋所有編碼與邊界。建議修正計算邏輯並補充測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/object.c:1217` | malloc_usable_size 可能高估記憶體使用量 | 0.80 |
| ⚠️ | Major | `src/object.c:1221` | OBJ_ENCODING_INT 未計入整數值本身大小 | 0.70 |
| ⚠️ | Major | `src/object.c:1239` | quicklist 取樣平均計算可能高估 | 0.70 |
| 🔸 | Minor | `src/object.c:1330` | stream 最後一個 listpack 的處理可能重複計算 | 0.60 |
| 🔸 | Minor | `tests/unit/type/string.tcl:688` | 測試未涵蓋所有編碼與邊界 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1217</code> malloc_usable_size 可能高估記憶體使用量</summary>

使用 malloc_usable_size(o) 作為 kvobj 的基礎大小，但 malloc_usable_size 回傳的是分配器實際配置的區塊大小，可能大於 kvobj 結構體本身的大小（例如因對齊或分配器 overhead）。這會導致記憶體使用量被高估，尤其當 kvobj 是從較大的記憶體池分配時。建議改為 sizeof(kvobj) 或使用 zmalloc_size(o)（若該函式能回傳實際配置大小且符合需求）。

**判斷依據**：diff 中新增行 `size_t asize = malloc_usable_size((void *)o);`，取代原本的 `sizeof(*o)` 計算。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1221</code> OBJ_ENCODING_INT 未計入整數值本身大小</summary>

當字串編碼為 OBJ_ENCODING_INT 時，整數值直接存放在 robj 的 ptr 欄位中，但此處僅以 malloc_usable_size(o) 計算 kvobj 大小，未額外加上整數值佔用的空間。然而，malloc_usable_size(o) 可能已包含 ptr 欄位的空間，但若整數值大於指標大小（例如 64 位元整數），則可能低估。建議確認 kvobj 結構中 ptr 的型別與大小，必要時加上 sizeof(long long) 或實際整數大小。

**判斷依據**：diff 中對 OBJ_ENCODING_INT 的處理僅留下註解，未增加任何大小。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1239</code> quicklist 取樣平均計算可能高估</summary>

原本計算平均時除以 elecount（實際元素數），現在改為除以 samples（取樣節點數）。若每個節點包含多個元素，samples 會小於 elecount，導致平均每個元素的大小被高估，進而使整體估計值偏高。建議維持除以 elecount，或改為計算每個節點的平均元素數再換算。

**判斷依據**：diff 中將 `(double)elesize/elecount*ql->count` 改為 `(double)elesize/samples*ql->count`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/object.c:1330</code> stream 最後一個 listpack 的處理可能重複計算</summary>

在 stream 的計算中，原本使用 `s->rax->numele-1` 來估算非最後一個 listpack 的數量，現在改為 `s->rax->numele`。這可能導致最後一個 listpack 被重複計算，因為後續程式碼似乎有單獨處理最後一個 listpack。建議確認此處的邏輯是否正確。

**判斷依據**：diff 中將 `asize += lpsize * (s->rax->numele-1);` 改為 `asize += lpsize * s->rax->numele;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/string.tcl:688</code> 測試未涵蓋所有編碼與邊界</summary>

新增的 MEMORY USAGE 測試僅涵蓋 string 類型的部分大小，未測試其他資料型別（如 hash、list、set、zset、stream）的記憶體計算。建議擴充測試以覆蓋所有編碼路徑，特別是本次修改的 quicklist、stream 等。

**判斷依據**：diff 中新增的測試僅針對 string 型別。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5274 (cache hit 5248) ｜ completion tokens 1277 ｜ PR #5</sub>