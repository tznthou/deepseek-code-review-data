<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 objectComputeSize 改名為 kvobjComputeSize，並調整記憶體計算方式，使其包含 kvobj header 與 key 的記憶體。主要風險在於計算方式變更可能導致記憶體估算不準確，尤其是 quicklist 的取樣平均計算、stream 的 listpack 數量計算，以及 module 類型的記憶體計算。建議先修正 quicklist 的取樣平均計算，並確認 stream 與 module 的計算邏輯。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/object.c:1239` | quicklist 取樣平均計算可能不準確 | 0.80 |
| ⚠️ | Major | `src/object.c:1330` | stream 的 listpack 數量計算可能多算一個 | 0.70 |
| 🔸 | Minor | `src/object.c:1371` | module 類型的記憶體計算可能重複計算 header | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1239</code> quicklist 取樣平均計算可能不準確</summary>

在 quicklist 的記憶體估算中，原本使用 `elesize/elecount*ql->count` 計算平均元素大小，現在改為 `elesize/samples*ql->count`。但 `samples` 是取樣的節點數，而 `elesize` 是這些節點中所有元素的總大小，`elecount` 是這些節點中的元素總數。若每個節點的元素數量不同，使用 `samples` 作為分母會導致平均元素大小計算錯誤。例如，若取樣了 5 個節點，但其中一個節點包含 100 個元素，其他節點各包含 1 個元素，則 `elesize` 會包含 104 個元素的大小，但除以 `samples`（5）會高估平均元素大小。建議改回使用 `elecount` 作為分母，或改為計算每個節點的平均元素大小再乘以節點數。

**判斷依據**：diff 中此行由 `asize += (double)elesize/elecount*ql->count;` 改為 `asize += (double)elesize/samples*ql->count;`，但 `samples` 是節點數，`elesize` 是所有取樣節點的元素總大小，兩者單位不同。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1330</code> stream 的 listpack 數量計算可能多算一個</summary>

在 stream 的記憶體估算中，原本使用 `lpsize * (s->rax->numele-1)` 計算 listpack 的總大小，現在改為 `lpsize * s->rax->numele`。但 `s->rax->numele` 是 radix tree 中的元素數量，而 listpack 的數量可能與元素數量不同。若 radix tree 中的每個元素對應一個 listpack，則 listpack 數量應為 `numele`，但若最後一個 listpack 是部分填充的，則可能不應計入平均。此變更可能導致記憶體估算偏高。建議確認 stream 的資料結構，並根據實際 listpack 數量計算。

**判斷依據**：diff 中此行由 `asize += lpsize * (s->rax->numele-1);` 改為 `asize += lpsize * s->rax->numele;`，但未提供為何移除 `-1` 的說明。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/object.c:1371</code> module 類型的記憶體計算可能重複計算 header</summary>

在 module 類型的記憶體計算中，原本直接使用 `moduleGetMemUsage` 的回傳值，現在改為 `asize += moduleGetMemUsage(...)`。但 `asize` 已經包含了 `malloc_usable_size((void *)o)`，即 kvobj header 的大小。若 `moduleGetMemUsage` 的回傳值也包含 header 的大小，則會重複計算。建議確認 `moduleGetMemUsage` 的實作，並避免重複計算。

**判斷依據**：diff 中此行由 `asize = moduleGetMemUsage(key, o, sample_size, dbid);` 改為 `asize += moduleGetMemUsage(key, o, sample_size, dbid);`，但 `asize` 已初始化為 `malloc_usable_size((void *)o)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4781 (cache hit 4736) ｜ completion tokens 1093 ｜ PR #5</sub>