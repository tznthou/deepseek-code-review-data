<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 MEMORY USAGE 的計算從 robj 改為 kvobj，並調整了各資料結構的記憶體估算方式。主要風險在於 stream 的 listpack 估算邏輯變更可能導致重複計算或低估，以及 quicklist 的取樣平均計算可能因樣本數為 0 而除零。整體方向合理，但需修正上述問題後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/object.c:1330` | Stream listpack 估算可能重複計算最後一個 listpack | 0.90 |
| ⚠️ | Major | `src/object.c:1239` | Quicklist 取樣平均計算可能除零 | 0.80 |
| 🔸 | Minor | `src/object.c:1217` | kvobjComputeSize 中 asize 初始化可能包含未初始化記憶體 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/object.c:1330</code> Stream listpack 估算可能重複計算最後一個 listpack</summary>

在 stream 的記憶體估算中，當 `s->rax->numele > samples` 時，程式碼先以平均大小乘以 `s->rax->numele`（而非原本的 `numele-1`），然後又加上最後一個 listpack 的實際大小。這會導致最後一個 listpack 被計算兩次（一次在平均估算中，一次在實際大小中），造成記憶體高估。

建議改回 `asize += lpsize * (s->rax->numele-1);` 或調整後續的實際大小加法邏輯。

**判斷依據**：diff 中將 `asize += lpsize * (s->rax->numele-1);` 改為 `asize += lpsize * s->rax->numele;`，但下方仍保留 `asize += zmalloc_size(ri.data);` 來加上最後一個 listpack 的實際大小。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1239</code> Quicklist 取樣平均計算可能除零</summary>

在 quicklist 的估算中，原本使用 `elecount` 作為分母，但 `elecount` 可能為 0（例如 quicklist 為空或所有節點均為空），導致除以零。修改後改用 `samples` 作為分母，但 `samples` 也可能為 0（例如 quicklist 為空或 `sample_size` 為 0）。

建議在計算前檢查 `samples` 是否為 0，若為 0 則跳過平均計算。

**判斷依據**：diff 中將 `asize += (double)elesize/elecount*ql->count;` 改為 `asize += (double)elesize/samples*ql->count;`，但未對 `samples` 進行零值檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/object.c:1217</code> kvobjComputeSize 中 asize 初始化可能包含未初始化記憶體</summary>

`asize` 初始化為 `malloc_usable_size((void *)o)`，但 `malloc_usable_size` 可能回傳大於實際配置的大小，且未初始化的部分可能包含垃圾資料。雖然這只是估算，但可能導致不穩定的結果。

建議改用 `zmalloc_size(o)` 或確保 `o` 的記憶體已初始化。

**判斷依據**：diff 中新增 `size_t asize = malloc_usable_size((void *)o);`，但未見對 `o` 的記憶體初始化保證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 24489 (cache hit 24448) ｜ completion tokens 907 ｜ PR #5</sub>