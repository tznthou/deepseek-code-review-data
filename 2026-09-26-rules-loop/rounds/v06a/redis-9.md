<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在複製到 replica 時會移除欄位過期時間的問題，做法是將複製指令從 HSET 改為 HSETEX 並加上 KEEPTTL 旗標。主要風險在於新增的 shared 物件（hsetex、fields）與 rewriteClientCommandVector 的使用是否正確，以及測試中對 TTL 的斷言可能因時間誤差而不穩定。整體邏輯合理，但需確認指令重寫的參數順序與測試的時序假設。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2571` | rewriteClientCommandVector 參數順序可能錯誤 | 0.75 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1984` | 測試中 TTL 斷言範圍可能因時間誤差而不穩定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> rewriteClientCommandVector 參數順序可能錯誤</summary>

在 `rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj)` 中，參數順序疑似有誤。HSETEX 的語法為 `HSETEX key [EX seconds|PX milliseconds|KEEPTTL] FIELDS num field value [field value ...]`，但此處傳入的順序是 `hsetex, key, keepttl, fields, 1, field, value`，缺少了 EX/PX 或 KEEPTTL 之前的時間參數位置。若 KEEPTTL 被當作時間參數，可能導致命令解析失敗或行為錯誤。建議核對 Redis 命令解析邏輯，確認此處參數順序是否正確。

**判斷依據**：diff 中新增的 rewriteClientCommandVector 呼叫，參數順序與 HSETEX 命令語法不符。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1984</code> 測試中 TTL 斷言範圍可能因時間誤差而不穩定</summary>

測試使用 `assert_range [r httl h1 FIELDS 1 f1] 90 100` 來驗證 TTL 在 90 到 100 秒之間，但實際 TTL 可能因測試執行時間、複製延遲或時鐘誤差而超出此範圍，導致測試偶發性失敗。建議放寬範圍或使用更精確的同步機制。

**判斷依據**：測試中對 TTL 的斷言範圍較窄，且未考慮時間誤差。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4594 (cache hit 3584) ｜ completion tokens 712 ｜ PR #9</sub>