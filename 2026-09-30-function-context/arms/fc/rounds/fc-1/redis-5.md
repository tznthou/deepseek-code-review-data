<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 MEMORY USAGE 的計算從 robj 改為 kvobj，並調整了相關函式與測試。主要風險在於 stream 的 listpack 估算邏輯變更可能導致記憶體高估，以及測試中對記憶體數值的斷言可能因配置或架構而脆弱。建議先確認 stream 估算的正確性，並評估測試斷言的穩定性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/object.c:1330` | Stream listpack 估算邏輯變更可能導致記憶體高估 | 0.80 |
| 🔸 | Minor | `tests/unit/type/string.tcl:700` | 測試中記憶體斷言可能因配置或架構而不穩定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1330</code> Stream listpack 估算邏輯變更可能導致記憶體高估</summary>

在 `kvobjComputeSize` 中，原本的估算方式是 `lpsize * (s->rax->numele-1)` 再加上最後一個 listpack 的實際大小，現在改為 `lpsize * s->rax->numele` 後又加上最後一個 listpack 的大小。這會導致最後一個 listpack 被重複計算，造成記憶體使用量高估。

具體情境：當 stream 中的元素數量超過 sample_size 時，程式會先計算前 N 個 listpack 的平均大小，然後乘以總數 `numele`，接著又加上最後一個 listpack 的實際大小。但平均大小已經包含了最後一個 listpack 的貢獻，因此最後一個 listpack 被算了兩次。

建議改回 `lpsize * (s->rax->numele-1)`，或調整邏輯以避免重複計算。

**判斷依據**：diff 中將 `asize += lpsize * (s->rax->numele-1);` 改為 `asize += lpsize * s->rax->numele;`，且後續仍執行 `asize += zmalloc_size(ri.data);` 來加入最後一個 listpack 的大小。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/string.tcl:700</code> 測試中記憶體斷言可能因配置或架構而不穩定</summary>

新增的測試 `MEMORY USAGE - STRINGS` 使用 `assert_lessthan_equal` 和 `assert_morethan_equal` 來驗證記憶體使用量落在一個範圍內。但記憶體使用量會受到 allocator、架構（32/64 位元）以及 Redis 內部配置的影響，這些斷言可能在特定環境下失敗。

例如，`hdrsize` 的計算假設了固定的 header 大小，但實際大小可能因版本或編譯選項而異。建議放寬斷言範圍，或使用更精確的預期值（如參考現有的 jemalloc 測試）。

**判斷依據**：測試中使用了 `assert_lessthan_equal` 和 `assert_morethan_equal`，並依賴 `hdrsize` 的計算，但未考慮 allocator 的 overhead 差異。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 24489 (cache hit 1536) ｜ completion tokens 809 ｜ PR #5</sub>