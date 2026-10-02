<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 dict 的 stored-key API 從全域開關（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式，使程式碼更明確且不易誤用。主要風險在於回呼函式的正確性與效能，以及部分呼叫點可能傳入錯誤的 key 型別。整體方向合理，但需確認所有 dictType 均已正確定義 keyFromStoredKey，且效能影響可接受。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/dict.c:102` | validateStoredKeyConversion 函式未使用 | 0.80 |
| ⚠️ | Major | `src/dict.c:542` | dictInsertKeyAtLink 未使用 dictStoredKey2Key 轉換 key | 0.70 |
| ⚠️ | Major | `src/dict.c:913` | dictSetKeyAtLink 中 dictFindLink 使用 addedKey 而非原始 key | 0.70 |
| 🔸 | Minor | `src/dict.c:1807` | dictGetHash 註解宣稱編譯器會 inline，但未使用 inline 關鍵字 | 0.60 |
| 🔸 | Minor | `src/dict.h:157` | pauseAutoResize 型別從 bitfield 改為 int16_t，可能影響 ABI 相容性 | 0.60 |
| 🔸 | Minor | `src/server.c:316` | kvGetKey 回傳 sds，但 keyFromStoredKey 預期回傳 const void* | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:102</code> validateStoredKeyConversion 函式未使用</summary>

新增的 validateStoredKeyConversion 函式從未被呼叫，可能遺漏了驗證邏輯。若此函式旨在確保 keyFromStoredKey 回呼的正確性，應在適當位置（如 dictInit 或 dictAddRaw）呼叫，否則應移除。

**判斷依據**：diff 中新增此函式，但未見任何呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:542</code> dictInsertKeyAtLink 未使用 dictStoredKey2Key 轉換 key</summary>

dictInsertKeyAtLink 接受 stored key，但在內部使用 key 進行 hash 和比較時，未先轉換為 lookup key。若 dictType 有定義 keyFromStoredKey，可能導致 hash 或比較錯誤。建議在函式開頭將 key 轉換為 lookup key，或確保呼叫者傳入的是 lookup key。

**判斷依據**：函式簽名標記 key 為 __stored_key，但函式內未呼叫 dictStoredKey2Key。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:913</code> dictSetKeyAtLink 中 dictFindLink 使用 addedKey 而非原始 key</summary>

在 dictSetKeyAtLink 中，當 *link 為 NULL 時，使用 addedKey 呼叫 dictFindLink。addedKey 是 keyDup 的結果，可能與原始 key 不同（例如 keyDup 複製了 key）。若 keyDup 有實作，addedKey 可能不是預期的 lookup key，導致找不到正確的 link。建議使用原始 key 或轉換後的 lookup key。

**判斷依據**：addedKey 來自 keyDup，可能與原始 key 不同。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:1807</code> dictGetHash 註解宣稱編譯器會 inline，但未使用 inline 關鍵字</summary>

註解寫「Compiler inlines this for internal calls within dict.c (verified with -O3)」，但函式定義未加上 inline 關鍵字。雖然編譯器可能自動 inline，但依賴最佳化行為可能導致不同編譯設定下效能不一致。建議明確加上 inline 或移除註解。

**判斷依據**：函式定義未使用 inline 關鍵字。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.h:157</code> pauseAutoResize 型別從 bitfield 改為 int16_t，可能影響 ABI 相容性</summary>

struct dict 中 pauseAutoResize 從 bitfield 改為 int16_t，可能改變結構體佈局，影響與外部模組的 ABI 相容性。若 Redis 作為動態連結庫使用，可能導致崩潰。建議確認此變更的必要性，或保留 bitfield 以維持 ABI。

**判斷依據**：型別變更可能影響結構體大小與對齊。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:316</code> kvGetKey 回傳 sds，但 keyFromStoredKey 預期回傳 const void*</summary>

kvGetKey 回傳 sds（即 char*），但 dictType.keyFromStoredKey 的簽名為 const void *(*)(const void *)。雖然隱式轉換可行，但可能遺失型別安全性。建議明確轉型為 const void*。

**判斷依據**：回傳型別為 sds，與函式簽名不完全匹配。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11875 (cache hit 11776) ｜ completion tokens 1436 ｜ PR #1</sub>