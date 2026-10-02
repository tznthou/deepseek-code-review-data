<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 objectComputeSize 改名為 kvobjComputeSize，並調整記憶體計算方式：先以 malloc_usable_size 取得物件頭部大小，再累加各資料結構的配置大小。主要風險在於 stream 的取樣計算從 (numele-1) 改為 numele，可能造成高估；此外，新增的測試僅在 jemalloc 下執行，且未涵蓋所有編碼。整體方向合理，但需確認 stream 計算的正確性與測試覆蓋。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/object.c:1330` | Stream 記憶體計算可能高估：取樣平均乘以 numele 而非 (numele-1) | 0.80 |
| 🔸 | Minor | `src/object.c:1217` | 使用 malloc_usable_size 可能包含未初始化的 padding，導致記憶體估算不精確 | 0.70 |
| 🔸 | Minor | `tests/unit/type/string.tcl:714` | 新增的 MEMORY USAGE 測試僅在 jemalloc 下執行，可能遺漏其他 allocator 的覆蓋 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1330</code> Stream 記憶體計算可能高估：取樣平均乘以 numele 而非 (numele-1)</summary>

在 stream 的記憶體計算中，原本使用 `s->rax->numele-1` 來估算 listpack 總大小，此 PR 改為 `s->rax->numele`。由於 radix tree 中每個元素對應一個 listpack，但最後一個 listpack 可能未滿，若直接乘以總元素數，可能將最後一個 listpack 的實際大小高估為平均大小。建議確認此變更的意圖，或保留 `-1` 以避免高估。

**判斷依據**：diff 中將 `asize += lpsize * (s->rax->numele-1);` 改為 `asize += lpsize * s->rax->numele;`，但未提供理由。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/object.c:1217</code> 使用 malloc_usable_size 可能包含未初始化的 padding，導致記憶體估算不精確</summary>

`malloc_usable_size` 回傳的可用大小可能包含對齊用的 padding，實際配置大小可能小於此值。此處直接將其作為物件頭部大小，可能高估記憶體使用量。建議改用 `zmalloc_size` 或確認此處使用 `malloc_usable_size` 的合理性。

**判斷依據**：新增的 `malloc_usable_size` 呼叫，與其他使用 `zmalloc_size` 的程式碼不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/string.tcl:714</code> 新增的 MEMORY USAGE 測試僅在 jemalloc 下執行，可能遺漏其他 allocator 的覆蓋</summary>

此測試區塊被包在 `if {[string match {*jemalloc*} [s mem_allocator]]}` 中，因此僅在 jemalloc 環境下執行。若 CI 使用其他 allocator（如 libc），此測試將被跳過，無法驗證 kvobjComputeSize 的正確性。建議考慮將測試移至不受 allocator 限制的區塊，或增加條件判斷。

**判斷依據**：diff 顯示新增的測試位於 jemalloc 條件區塊內。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5782 (cache hit 1536) ｜ completion tokens 836 ｜ PR #5</sub>