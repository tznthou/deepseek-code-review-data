<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 objectComputeSize 改名為 kvobjComputeSize，並調整記憶體計算方式，使其包含 kvobj 標頭與嵌入的 key。主要風險在於計算方式變更可能導致記憶體估算不準確，且新增測試的邊界條件可能過於寬鬆。最需優先確認的是 quicklist 與 stream 的取樣計算是否正確，以及測試是否足以捕捉回歸。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/object.c:1239` | quicklist 取樣計算可能低估記憶體使用量 | 0.80 |
| ⚠️ | Major | `src/object.c:1330` | stream 記憶體估算可能重複計算最後一個 listpack | 0.70 |
| 🔸 | Minor | `src/object.c:1210` | 函式名稱變更可能影響外部模組或測試 | 0.60 |
| 🔸 | Minor | `tests/unit/type/string.tcl:701` | 測試邊界條件可能過於寬鬆 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1239</code> quicklist 取樣計算可能低估記憶體使用量</summary>

在 quicklist 分支中，原本使用 `elesize/elecount*ql->count` 來估算總元素大小，現在改為 `elesize/samples*ql->count`。當 `samples` 小於 `elecount` 時（例如 quicklist 節點包含多個元素），此計算會低估實際記憶體使用量。

**失敗情境**：假設 quicklist 有 10 個節點，每個節點包含 10 個元素，`sample_size` 為 5。原本會取樣 5 個節點，累計 `elecount` 為 50，`elesize` 為 50 個元素的總大小，然後乘以 `ql->count`（100）除以 50，得到正確的平均值。修改後，`samples` 為 5（節點數），`elesize` 為 5 個節點的總大小，乘以 `ql->count`（100）除以 5，會將每個節點的大小乘以 20，嚴重高估。

**建議**：保留原本的 `elecount` 變數，並使用 `elesize/elecount*ql->count` 進行估算。

**判斷依據**：diff 中將 `asize += (double)elesize/elecount*ql->count;` 改為 `asize += (double)elesize/samples*ql->count;`，但 `samples` 是節點數而非元素數，可能導致計算錯誤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1330</code> stream 記憶體估算可能重複計算最後一個 listpack</summary>

在 stream 分支中，原本使用 `lpsize * (s->rax->numele-1)` 來估算 listpack 總大小，現在改為 `lpsize * s->rax->numele`。這可能導致最後一個 listpack 被重複計算，因為在後續的 `raxSeek(&ri,"$",NULL,0);` 中會再次處理最後一個 listpack。

**失敗情境**：假設 stream 有 10 個 listpack，`sample_size` 為 5。原本會取樣前 5 個 listpack，計算平均大小後乘以 9（numele-1），然後再加上最後一個 listpack 的實際大小。修改後，乘以 10（numele），再加上最後一個 listpack 的實際大小，導致最後一個 listpack 被計算兩次。

**建議**：確認此處的意圖，若最後一個 listpack 確實需要單獨計算，則應保持 `numele-1`；否則應移除後續的單獨處理。

**判斷依據**：diff 中將 `asize += lpsize * (s->rax->numele-1);` 改為 `asize += lpsize * s->rax->numele;`，但後續仍有 `raxSeek(&ri,"$",NULL,0);` 處理最後一個 listpack。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/object.c:1210</code> 函式名稱變更可能影響外部模組或測試</summary>

函式 `objectComputeSize` 被改名為 `kvobjComputeSize`，但此函式可能被其他模組或測試程式碼引用。若未同步更新所有引用，可能導致編譯錯誤或連結錯誤。

**失敗情境**：若有外部模組或測試程式碼直接呼叫 `objectComputeSize`，在編譯時會出現未定義符號錯誤。

**建議**：確認所有引用均已更新，或保留舊函式作為別名以維持相容性。

**判斷依據**：diff 中函式名稱從 `objectComputeSize` 改為 `kvobjComputeSize`，但未提供相容性別名。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/string.tcl:701</code> 測試邊界條件可能過於寬鬆</summary>

新增的測試中，使用 `assert_lessthan_equal $min $memory_used` 和 `assert_morethan_equal $max $memory_used` 來驗證記憶體使用量，但 `max` 的計算方式可能過於寬鬆，無法有效捕捉記憶體計算錯誤。

**失敗情境**：若記憶體計算錯誤導致使用量略高於預期，但仍在寬鬆的 `max` 範圍內，測試將無法發現問題。

**建議**：考慮使用更嚴格的邊界，或增加對特定編碼的針對性測試。

**判斷依據**：測試中 `max` 的計算方式為 `min * 2` 或固定 64，可能無法有效偵測記憶體計算的細微錯誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5772 (cache hit 4736) ｜ completion tokens 1471 ｜ PR #5</sub>