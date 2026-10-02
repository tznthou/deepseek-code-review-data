<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在 replica 上會移除欄位過期時間的問題，做法是將複寫指令從 HSET 改為 HSETEX 並加上 KEEPTTL 旗標。主要風險在於複寫指令的建構方式：使用 rewriteClientCommandVector 搭配 shared.fields 與 shared.integers[1]，若 shared.fields 未正確初始化或 shared.integers[1] 非預期值，可能導致複寫錯誤或崩潰。另外，測試中對 f2 的 TTL 斷言為 -1，但複寫指令使用 KEEPTTL，若 f2 原本無 TTL，行為應正確，但需確認 KEEPTTL 對無 TTL 欄位的處理。整體而言，修正方向正確，但需驗證 shared 物件初始化與複寫指令格式。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2571` | 複寫指令使用 shared.fields 與 shared.integers[1]，需確認初始化與值正確 | 0.80 |
| 🔸 | Minor | `src/t_hash.c:2571` | 複寫指令使用 KEEPTTL 但未處理無 TTL 欄位的情況 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> 複寫指令使用 shared.fields 與 shared.integers[1]，需確認初始化與值正確</summary>

在 hincrbyfloatCommand 中，複寫指令改為使用 rewriteClientCommandVector 並傳入 shared.fields 與 shared.integers[1]。shared.fields 已在 createSharedObjects 中初始化，但 shared.integers[1] 的值需確認是否為 1。若 shared.integers[1] 不是 1，複寫的指令將包含錯誤的欄位數量，可能導致 replica 執行錯誤。建議確認 shared.integers 的初始化順序，或改用明確的整數物件。

**判斷依據**：diff 中新增的 rewriteClientCommandVector 呼叫使用了 shared.integers[1] 作為 FIELDS 數量，但未在 diff 中看到 shared.integers 的初始化內容，需確認其值為 1。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/t_hash.c:2571</code> 複寫指令使用 KEEPTTL 但未處理無 TTL 欄位的情況</summary>

複寫指令使用 HSETEX 搭配 KEEPTTL，但若原始欄位沒有 TTL，KEEPTTL 的行為需確認。在測試中，f2 原本無 TTL，複寫後 replica 的 TTL 應為 -1，測試已涵蓋此情境，但需確保 KEEPTTL 對無 TTL 欄位不會設定錯誤的過期時間。

**判斷依據**：測試中對 f2 的 TTL 斷言為 -1，但複寫指令使用 KEEPTTL，需確認 KEEPTTL 對無 TTL 欄位的處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4580 (cache hit 3584) ｜ completion tokens 795 ｜ PR #9</sub>