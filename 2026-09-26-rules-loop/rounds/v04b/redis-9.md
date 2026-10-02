<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在 replica 上會移除 field expiration 的問題，做法是將複寫指令從 HSET 改為 HSETEX KEEPTTL FIELDS 1，並新增測試。主要風險在於複寫指令的建構方式與參數順序是否正確，以及測試中對 TTL 的斷言可能因時間誤差而不穩定。整體方向正確，但需確認 HSETEX 語法與 KEEPTTL 行為符合預期。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2571` | 複寫指令參數順序可能錯誤 | 0.80 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1980` | 測試中 TTL 斷言可能因時間誤差而不穩定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> 複寫指令參數順序可能錯誤</summary>

`rewriteClientCommandVector` 的參數順序為 `(c, argc, ...)`，此處傳入 6 個參數，但實際需要的參數數量可能不符。HSETEX 語法為 `HSETEX key [EX seconds|PX milliseconds|EXAT unix-time|PXAT unix-time|KEEPTTL] FIELDS numfields field value [field value ...]`，此處建構的指令為 `HSETEX key KEEPTTL FIELDS 1 field value`，共 7 個 token（含指令本身），但 `argc` 傳入 6，可能導致參數截斷或錯誤。建議確認 `rewriteClientCommandVector` 的 argc 計算方式，並驗證產生的指令是否完整。

**判斷依據**：diff 中新增的 `rewriteClientCommandVector` 呼叫，argc 為 6，但後續傳入 7 個參數（hsetex, key, keepttl, fields, 1, field, value），可能導致指令建構錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1980</code> 測試中 TTL 斷言可能因時間誤差而不穩定</summary>

`assert_range [r httl h1 FIELDS 1 f1] 90 100` 假設 TTL 在 90 到 100 秒之間，但測試執行時間可能超過 10 秒，導致 TTL 低於 90 而失敗。建議放寬範圍或使用 `assert_morethan` 搭配較低門檻。

**判斷依據**：測試中對 TTL 的範圍斷言，若測試執行時間較長，TTL 可能低於 90。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4096 (cache hit 3968) ｜ completion tokens 721 ｜ PR #9</sub>