<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在複本上會移除欄位過期時間的問題，方法是將複寫指令從 HSET 改為 HSETEX 並加上 KEEPTTL 旗標。主要風險在於複寫指令的建構方式：使用 rewriteClientCommandVector 搭配 shared.fields 與 shared.integers[1]，若 shared.fields 未正確初始化或 shared.integers[1] 非預期值，可能導致複寫錯誤或當機。此外，測試涵蓋了基本情境，但未驗證 KEEPTTL 與 FIELDS 參數的組合在其他指令或邊界條件下的行為。整體而言，修正方向正確，但需確認共用物件初始化與複寫向量建構的細節。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2571` | 複寫指令向量可能使用未初始化的 shared.fields 或錯誤的 shared.integers[1] | 0.80 |
| 🔸 | Minor | `src/t_hash.c:2571` | 複寫指令參數順序可能與 HSETEX 語法不符 | 0.60 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1966` | 測試未涵蓋 HINCRBYFLOAT 在欄位不存在時的行為 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> 複寫指令向量可能使用未初始化的 shared.fields 或錯誤的 shared.integers[1]</summary>

在 `rewriteClientCommandVector` 呼叫中，使用了 `shared.fields` 和 `shared.integers[1]`。`shared.fields` 已在 `createSharedObjects` 中初始化，但需確認其值為 "FIELDS"（大寫）。`shared.integers[1]` 是共用整數物件，其值為 1，但若未來共用整數陣列順序變更，可能導致錯誤。建議改用明確的整數物件或直接建立新物件，避免依賴共用物件的索引。

**判斷依據**：diff 中新增的 rewriteClientCommandVector 呼叫使用了 shared.fields 和 shared.integers[1]。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/t_hash.c:2571</code> 複寫指令參數順序可能與 HSETEX 語法不符</summary>

HSETEX 語法為 `HSETEX key [NX|XX] [KEEPTTL] [FIELDS numfields field value ...]`。目前向量順序為 `shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj`，看起來正確，但需確認 `shared.keepttl` 的值為 "KEEPTTL"（大寫）。若大小寫錯誤，複本可能無法正確解析。

**判斷依據**：diff 中新增的 rewriteClientCommandVector 呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1966</code> 測試未涵蓋 HINCRBYFLOAT 在欄位不存在時的行為</summary>

測試僅對已存在的欄位執行 HINCRBYFLOAT，未測試欄位不存在時是否會建立新欄位且不設定過期時間。若實作有誤，可能導致新欄位意外繼承過期時間。建議增加測試案例。

**判斷依據**：diff 中測試僅對已存在的 f1 和 f2 執行 HINCRBYFLOAT。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4096 (cache hit 3584) ｜ completion tokens 954 ｜ PR #9</sub>