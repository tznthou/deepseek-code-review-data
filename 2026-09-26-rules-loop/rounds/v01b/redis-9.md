<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在複製到 replica 時會移除欄位過期時間的問題，做法是將複製指令從 HSET 改為 HSETEX 並加上 KEEPTTL 旗標。主要風險在於新增的 rewriteClientCommandVector 呼叫參數是否正確，以及測試中對過期時間的斷言可能因時間誤差而不穩定。整體而言，變更範圍小且方向正確，但需確認參數順序與測試可靠性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2571` | rewriteClientCommandVector 參數順序可能錯誤 | 0.80 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1988` | 測試中對過期時間的斷言可能因時間誤差而不穩定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> rewriteClientCommandVector 參數順序可能錯誤</summary>

在 `rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj)` 中，參數順序可能不符合 HSETEX 命令的語法。HSETEX 的語法為 `HSETEX key [EX seconds | PX milliseconds | EXAT unix-time-seconds | PXAT unix-time-milliseconds | KEEPTTL] [NX | XX] [FIELDS numfields field value [field value ...]]`。目前傳入的參數順序是 `key, KEEPTTL, FIELDS, 1, field, value`，但正確順序應為 `key, KEEPTTL, FIELDS, 1, field, value`，看起來是正確的。然而，`shared.integers[1]` 是共享整數物件，其值為 1，但在此處作為 `numfields` 參數，可能與預期相符。不過，需確認 `rewriteClientCommandVector` 的參數數量是否正確：目前傳入 6 個參數（包含命令本身），但實際參數數量為 7（命令 + key + KEEPTTL + FIELDS + 1 + field + value），因此可能導致參數數量不符，進而產生錯誤的複製指令。

**判斷依據**：diff 中新增的 rewriteClientCommandVector 呼叫，參數數量為 6，但實際需要的參數數量為 7（命令 + key + KEEPTTL + FIELDS + 1 + field + value），可能導致複製指令不完整或錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1988</code> 測試中對過期時間的斷言可能因時間誤差而不穩定</summary>

在測試中，使用 `assert_range [r httl h1 FIELDS 1 f1] 90 100` 來斷言過期時間在 90 到 100 秒之間。然而，由於測試執行時間的延遲，實際的 TTL 可能略低於 90 秒，導致測試偶發性失敗。建議放寬範圍或使用更精確的同步機制。

**判斷依據**：測試中對 TTL 的斷言範圍較窄，且未考慮測試執行時間的延遲，可能導致 flaky test。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4604 (cache hit 4480) ｜ completion tokens 869 ｜ PR #9</sub>