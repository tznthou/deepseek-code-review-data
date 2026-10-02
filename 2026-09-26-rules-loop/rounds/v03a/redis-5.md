<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 `objectComputeSize` 改名為 `kvobjComputeSize`，並調整記憶體計算方式：現在會先以 `malloc_usable_size(o)` 取得物件實際配置大小，再依型別累加內部結構。主要風險在於 `malloc_usable_size` 可能回傳大於 `sizeof(kvobj)` 的值，導致高估；且 quicklist 取樣平均的計算從除以 `elecount` 改為除以 `samples`，可能因取樣不足而低估。此外，stream 的 listpack 估算將乘數從 `numele-1` 改為 `numele`，可能修正了先前低估，但需確認是否會高估。整體而言，變更合理但需驗證記憶體估算的準確性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/object.c:1217` | 使用 malloc_usable_size 可能高估記憶體用量 | 0.80 |
| ⚠️ | Major | `src/object.c:1239` | quicklist 取樣平均計算可能低估記憶體 | 0.75 |
| 🔸 | Minor | `src/object.c:1330` | stream listpack 估算乘數變更可能高估 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1217</code> 使用 malloc_usable_size 可能高估記憶體用量</summary>

`malloc_usable_size(o)` 回傳的實際配置大小可能大於 `sizeof(kvobj)`，因為記憶體配置器常會配置比請求更大的區塊。這會導致所有型別的記憶體估算都偏高，尤其當物件數量多時誤差累積。建議改用 `zmalloc_size(o)` 或 `sizeof(*o)` 來取得物件本身大小，以維持一致性。

**判斷依據**：diff 中新增行 `size_t asize = malloc_usable_size((void *)o);`，取代原先在每個分支中明確計算 `sizeof(*o)` 的方式。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1239</code> quicklist 取樣平均計算可能低估記憶體</summary>

原先 `asize += (double)elesize/elecount*ql->count;` 使用實際走訪的節點數 `elecount` 作為平均分母，現在改為 `samples`。但 `samples` 是取樣節點數，可能小於 `elecount`（例如最後一個節點未滿時），導致平均每個元素的記憶體被高估，進而高估整體用量。建議維持使用 `elecount` 或確認 `samples` 與 `elecount` 的關係。

**判斷依據**：diff 中此行由 `asize += (double)elesize/elecount*ql->count;` 改為 `asize += (double)elesize/samples*ql->count;`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/object.c:1330</code> stream listpack 估算乘數變更可能高估</summary>

將 `asize += lpsize * (s->rax->numele-1);` 改為 `asize += lpsize * s->rax->numele;`。若 `numele` 包含最後一個不完整的 listpack，則此變更可能修正低估；但若 `numele` 已排除最後一個，則可能高估。需確認 `numele` 的定義。

**判斷依據**：diff 中此行由 `asize += lpsize * (s->rax->numele-1);` 改為 `asize += lpsize * s->rax->numele;`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5792 (cache hit 4736) ｜ completion tokens 914 ｜ PR #5</sub>