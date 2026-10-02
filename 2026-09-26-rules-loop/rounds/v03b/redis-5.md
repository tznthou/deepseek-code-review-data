<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 objectComputeSize 改名為 kvobjComputeSize，並調整記憶體計算方式，將物件標頭與鍵的記憶體納入計算。主要風險在於計算方式變更可能導致記憶體估算不準確，特別是 quicklist 與 stream 的取樣計算，以及測試中對記憶體上限的假設可能過於寬鬆。建議先修正 quicklist 的取樣計算，並確認 stream 的計算邏輯。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/object.c:1239` | quicklist 取樣計算使用 samples 而非 elecount 可能導致記憶體估算錯誤 | 0.80 |
| ⚠️ | Major | `src/object.c:1330` | stream 記憶體估算中 lpsize 乘以 numele 可能重複計算最後一個 listpack | 0.70 |
| 🔸 | Minor | `tests/unit/type/string.tcl:701` | 測試中記憶體上限的計算可能過於寬鬆，無法有效驗證記憶體估算 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1239</code> quicklist 取樣計算使用 samples 而非 elecount 可能導致記憶體估算錯誤</summary>

在 quicklist 的記憶體估算中，原本使用 `elesize/elecount*ql->count` 來估算總元素大小，現在改為 `elesize/samples*ql->count`。然而 `samples` 是取樣的節點數，而 `elesize` 是這些節點中元素的總大小，`elecount` 是這些節點中的元素總數。若每個節點的元素數量不同，使用 `samples` 作為分母會導致平均每個元素的估計值不準確。例如，若取樣了 5 個節點，但其中一個節點包含大量元素，則 `elesize/samples` 會高估每個元素的平均大小，進而高估總記憶體。建議改回使用 `elecount` 作為分母，或改為計算每個節點的平均元素大小再乘以節點數。

**判斷依據**：diff 中將 `asize += (double)elesize/elecount*ql->count;` 改為 `asize += (double)elesize/samples*ql->count;`，但 `samples` 是節點數而非元素數，可能導致計算錯誤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1330</code> stream 記憶體估算中 lpsize 乘以 numele 可能重複計算最後一個 listpack</summary>

在 stream 的記憶體估算中，原本使用 `lpsize * (s->rax->numele-1)` 來估算 listpack 的總大小，現在改為 `lpsize * s->rax->numele`。這可能導致最後一個 listpack 被重複計算，因為在後續的程式碼中，如果取樣未涵蓋所有元素，會另外加上最後一個 listpack 的大小。例如，若 `s->rax->numele` 為 10，取樣了 5 個 listpack，則 `lpsize` 是這 5 個的平均大小，乘以 10 會高估總大小，因為最後一個 listpack 可能尚未滿，且後續程式碼會再單獨加上它。建議確認此處的計算邏輯，避免重複計算。

**判斷依據**：diff 中將 `asize += lpsize * (s->rax->numele-1);` 改為 `asize += lpsize * s->rax->numele;`，但後續程式碼有針對最後一個 listpack 的單獨處理，可能導致重複計算。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/string.tcl:701</code> 測試中記憶體上限的計算可能過於寬鬆，無法有效驗證記憶體估算</summary>

在新增的測試中，`max` 的計算方式為 `32 > $min ? 64 : [expr $min * 2]`，這可能導致上限過於寬鬆，使得即使記憶體估算有較大誤差也能通過測試。例如，若 `min` 為 100，則 `max` 為 200，允許 100% 的誤差。建議根據實際記憶體配置設定更嚴格的上限，或使用更精確的估算方式。

**判斷依據**：測試中設定的上限可能無法有效捕捉記憶體估算的錯誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5792 (cache hit 5760) ｜ completion tokens 1076 ｜ PR #5</sub>