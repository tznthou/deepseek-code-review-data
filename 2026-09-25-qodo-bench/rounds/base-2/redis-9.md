<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在複本上錯誤移除欄位過期時間的問題，將複寫指令從 HSET 改為 HSETEX 並加上 KEEPTTL 旗標。主要風險在於新增的共享物件與指令向量改寫的正確性，以及測試中對過期時間的斷言可能因時間誤差而不穩定。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2571` | rewriteClientCommandVector 參數數量與格式可能不正確 | 0.80 |
| ⚠️ | Major | `src/t_hash.c:2571` | HSETEX 指令格式可能不正確 | 0.70 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1965` | 測試中對過期時間的斷言可能因時間誤差而不穩定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> rewriteClientCommandVector 參數數量與格式可能不正確</summary>

`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj)` 中，第一個參數 `6` 表示新 argv 的元素數量，但實際傳入的參數有 7 個（hsetex, key, keepttl, fields, 1, field, value）。這可能導致指令向量建構錯誤，進而影響複寫內容。請確認 `rewriteClientCommandVector` 的實作，並修正參數數量。

**判斷依據**：diff 中新增的這一行，第一個參數為 6，但後續有 7 個參數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> HSETEX 指令格式可能不正確</summary>

HSETEX 的語法為 `HSETEX key [EX seconds|PX milliseconds|EXAT unix-time|PXAT unix-time|KEEPTTL] [FIELDS numfields field value [field value ...]]`。此處使用 `shared.integers[1]` 作為 FIELDS 的數量，但未確認 `shared.integers[1]` 是否為字串 "1"。若該共享整數物件不是 "1"，將導致複寫指令格式錯誤。

**判斷依據**：使用 shared.integers[1] 作為 FIELDS 數量，但未驗證其值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1965</code> 測試中對過期時間的斷言可能因時間誤差而不穩定</summary>

在測試中，使用 `assert_range [r httl h1 FIELDS 1 f1] 90 100` 斷言剩餘 TTL 在 90 到 100 秒之間。由於測試執行時間可能超過 10 秒（例如在慢速 CI 環境），TTL 可能低於 90 秒，導致測試偶發性失敗。建議放寬範圍或使用更精確的同步機制。

**判斷依據**：測試中新增的斷言，範圍固定為 90-100，未考慮執行時間。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3603 (cache hit 3584) ｜ completion tokens 896 ｜ PR #9</sub>