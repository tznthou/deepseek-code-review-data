<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在複本上會移除欄位過期時間的問題，方法是將複寫指令從 HSET 改為 HSETEX 並加上 KEEPTTL 旗標。主要風險在於複寫指令的參數順序與長度是否正確，以及測試中對 TTL 範圍的斷言可能過於嚴格。整體方向正確，但需確認複寫格式與測試穩定性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2571` | 複寫指令參數順序可能錯誤 | 0.80 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1988` | TTL 範圍斷言可能過於嚴格 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> 複寫指令參數順序可能錯誤</summary>

`rewriteClientCommandVector` 的參數順序為 `(c, argc, ...)`，但此處傳入的參數順序為 `shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj`。根據 HSETEX 語法，正確順序應為 `HSETEX key [KEEPTTL] FIELDS num field value`，因此 `shared.keepttl` 應在 `shared.fields` 之前，但此處 `shared.keepttl` 在 `shared.fields` 之後，可能導致複寫指令格式錯誤。

失敗情境：當主節點執行 HINCRBYFLOAT 時，複本會收到錯誤格式的 HSETEX 指令，導致複寫中斷或資料不一致。

建議修正：調整參數順序為 `shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj`。

**判斷依據**：diff 中新增的 `rewriteClientCommandVector` 呼叫，參數順序與 HSETEX 命令語法不符。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1988</code> TTL 範圍斷言可能過於嚴格</summary>

測試中 `assert_range [r httl h1 FIELDS 1 f1] 90 100` 假設 TTL 在 90 到 100 秒之間，但實際 TTL 可能因測試執行時間而低於 90 秒，導致測試不穩定。

失敗情境：若測試執行較慢，TTL 可能降至 90 以下，造成斷言失敗。

建議修正：放寬範圍或使用相對誤差，例如 `assert_range [r httl h1 FIELDS 1 f1] 80 100`。

**判斷依據**：測試中新增的斷言，TTL 範圍固定為 90-100，未考慮時間流逝。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3603 (cache hit 3584) ｜ completion tokens 787 ｜ PR #9</sub>