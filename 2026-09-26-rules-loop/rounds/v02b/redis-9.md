<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在 replica 上會移除欄位過期時間的問題，方法是將複寫指令從 HSET 改為 HSETEX 並加上 KEEPTTL 旗標。主要風險在於複寫指令的建構方式：使用 rewriteClientCommandVector 搭配 shared.integers[1] 作為 FIELDS 數量，若未來欄位數不為 1 會產生錯誤；此外，移除 HASH_SET_KEEP_TTL 旗標可能影響其他呼叫 hashTypeSet 的指令，需確認無回歸。測試涵蓋了 replica 情境，但未驗證 AOF 重寫路徑。整體而言，修正方向正確，但需確認上述風險。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2571` | 複寫指令使用 shared.integers[1] 作為 FIELDS 數量，可能導致未來欄位數不為 1 時複寫錯誤 | 0.80 |
| ⚠️ | Major | `src/t_hash.c:2559` | 移除 HASH_SET_KEEP_TTL 旗標可能影響其他呼叫 hashTypeSet 的指令 | 0.70 |
| 🔸 | Minor | `src/t_hash.c:2571` | 複寫指令使用 shared.integers[1] 可能造成共享物件生命週期問題 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> 複寫指令使用 shared.integers[1] 作為 FIELDS 數量，可能導致未來欄位數不為 1 時複寫錯誤</summary>

在 hincrbyfloatCommand 中，複寫指令改為 HSETEX，並使用 shared.integers[1] 作為 FIELDS 的數量。目前 HINCRBYFLOAT 只操作單一欄位，因此數量為 1 是正確的。但若未來指令支援多欄位，此處會產生錯誤的複寫指令。建議改用明確的整數物件或從參數中取得數量，避免依賴 shared.integers[1]。

**判斷依據**：diff 中新增的 rewriteClientCommandVector 呼叫，其中 shared.integers[1] 被用作 FIELDS 數量。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2559</code> 移除 HASH_SET_KEEP_TTL 旗標可能影響其他呼叫 hashTypeSet 的指令</summary>

原本 hashTypeSet 呼叫帶有 HASH_SET_KEEP_TTL 旗標，以保留欄位 TTL。移除後，HINCRBYFLOAT 在執行時會移除欄位的 TTL，但複寫指令會使用 KEEPTTL 來保留。這在 master 上會導致欄位 TTL 被移除，而 replica 上保留，造成不一致。需確認此行為是否符合預期，或是否應保留旗標並在複寫時使用 KEEPTTL。

**判斷依據**：diff 中 hashTypeSet 呼叫移除了 HASH_SET_KEEP_TTL 旗標。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/t_hash.c:2571</code> 複寫指令使用 shared.integers[1] 可能造成共享物件生命週期問題</summary>

shared.integers[1] 是共享整數物件，在 rewriteClientCommandVector 中使用後，其引用計數可能被修改。需確認 rewriteClientCommandVector 是否會增加引用計數，否則可能導致共享物件被意外釋放。

**判斷依據**：diff 中使用了 shared.integers[1] 作為參數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4604 (cache hit 4480) ｜ completion tokens 931 ｜ PR #9</sub>