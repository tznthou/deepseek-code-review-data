<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在複製到 replica 時會移除欄位過期時間的問題，改為使用 HSETEX 搭配 KEEPTTL 旗標來保留 TTL。主要風險在於新增的 rewriteClientCommandVector 呼叫參數數量與型別是否正確，以及測試中對 TTL 範圍的斷言可能因時間誤差而不穩定。整體邏輯合理，但需確認命令重寫的正確性與測試的可靠性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2571` | rewriteClientCommandVector 參數數量可能不正確 | 0.75 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1987` | TTL 範圍斷言可能因時間誤差而不穩定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> rewriteClientCommandVector 參數數量可能不正確</summary>

呼叫 `rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj)` 時，第一個參數 `6` 表示新的 argv 長度，但實際傳入的參數有 8 個（hsetex, key, keepttl, fields, 1, field, value）。這可能導致命令重寫後參數數量錯誤，進而影響複製或 AOF 重寫。請確認 `rewriteClientCommandVector` 的實作，並修正參數數量。

**判斷依據**：diff 中新增的這行呼叫，第一個參數為 6，但後續傳入 8 個參數，數量不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1987</code> TTL 範圍斷言可能因時間誤差而不穩定</summary>

測試中使用 `assert_range [r httl h1 FIELDS 1 f1] 90 100` 來驗證 TTL 在 90 到 100 秒之間。由於測試執行時間可能超過 10 秒，TTL 可能低於 90，導致測試偶發性失敗。建議放寬範圍或使用更精確的驗證方式。

**判斷依據**：測試中對 TTL 的範圍斷言較窄，且未考慮測試執行時間的影響。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4580 (cache hit 4480) ｜ completion tokens 652 ｜ PR #9</sub>