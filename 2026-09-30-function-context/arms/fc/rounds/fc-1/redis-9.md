<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在複本上會移除欄位過期時間的問題，改為複寫成 HSETEX KEEPTTL 指令。主要變更包括新增共享物件、修改複寫邏輯、調整函式可見度，並新增測試。風險集中在複寫指令的建構是否正確、KEEPTTL 語意是否與原指令一致，以及測試是否充分涵蓋邊界情境。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2571` | HINCRBYFLOAT 複寫為 HSETEX KEEPTTL 可能遺失欄位 TTL | 0.80 |
| 🔸 | Minor | `src/t_hash.c:2571` | 複寫指令參數順序可能錯誤 | 0.60 |
| 🔸 | Minor | `src/t_hash.c:2571` | 複寫指令未包含 TTL 參數，可能無法保留過期時間 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> HINCRBYFLOAT 複寫為 HSETEX KEEPTTL 可能遺失欄位 TTL</summary>

原程式碼使用 `HASH_SET_KEEP_TTL` 保留欄位 TTL，但複寫指令改為 `HSETEX KEEPTTL`。若 `HSETEX KEEPTTL` 的實作在欄位不存在時不會設定 TTL，則複本上原本沒有 TTL 的欄位將維持無 TTL，但主節點上該欄位可能因 `HINCRBYFLOAT` 而獲得 TTL（例如原本有 TTL 的欄位被更新後，TTL 應保留）。需確認 `HSETEX KEEPTTL` 在欄位不存在時的行為是否與 `HASH_SET_KEEP_TTL` 一致。

**判斷依據**：diff 中 `hashTypeSet` 的 flags 從 `HASH_SET_TAKE_VALUE | HASH_SET_KEEP_TTL` 改為 `HASH_SET_TAKE_VALUE`，且複寫指令改為 `HSETEX KEEPTTL`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/t_hash.c:2571</code> 複寫指令參數順序可能錯誤</summary>

`rewriteClientCommandVector` 的參數順序為 `(c, argc, ...)`，此處傳入 6 個參數，但 `HSETEX` 指令的語法為 `HSETEX key [NX|XX] [KEEPTTL] [EX|PX|EXAT|PXAT] FIELDS num field value [field value ...]`。目前建構的指令為 `HSETEX key KEEPTTL FIELDS 1 field value`，缺少 TTL 選項，可能導致語法錯誤或行為不符預期。

**判斷依據**：diff 中新增的 `rewriteClientCommandVector` 呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/t_hash.c:2571</code> 複寫指令未包含 TTL 參數，可能無法保留過期時間</summary>

`HSETEX` 指令若未指定 TTL 選項，可能預設為不設定過期時間，導致複本上欄位 TTL 遺失。需確認 `HSETEX` 在僅有 `KEEPTTL` 而無 TTL 選項時的行為。

**判斷依據**：diff 中新增的 `rewriteClientCommandVector` 呼叫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13129 (cache hit 1536) ｜ completion tokens 970 ｜ PR #9</sub>