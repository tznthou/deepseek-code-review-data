<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 dict 的 stored-key API 從全域狀態切換（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式，以消除脆弱的狀態管理。整體方向合理，但存在一個關鍵的型別安全問題：__stored_key 被定義為空巨集，導致編譯器無法區分 stored-key 與 lookup key，可能造成錯誤傳遞。此外，validateStoredKeyConversion 函式未被使用，且 dictSetKeyAtLink 中對 addedKey 的使用可能引入不一致。建議先修正型別安全問題再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/dict.h:66` | __stored_key 定義為空巨集，無法提供型別安全 | 0.95 |
| ⚠️ | Major | `src/dict.c:102` | validateStoredKeyConversion 函式未被使用 | 0.80 |
| ⚠️ | Major | `src/dict.c:913` | dictSetKeyAtLink 中對 addedKey 的使用可能不一致 | 0.75 |

<details><summary>🛑 <b>Blocker</b> — <code>src/dict.h:66</code> __stored_key 定義為空巨集，無法提供型別安全</summary>

`__stored_key` 被定義為空巨集（`#define __stored_key`），因此所有標記為 `__stored_key` 的參數在編譯器眼中與一般指標無異。這使得 stored-key 與 lookup key 的區分僅存在於文件，無法在編譯時期防止錯誤傳遞。例如，呼叫 `dictAdd` 時若誤傳 lookup key（如 sds）而非 stored-key（如 Entry*），編譯器不會發出警告，可能導致執行時期錯誤。建議將 `__stored_key` 定義為實際型別（例如 `Entry*` 或特定 struct），或使用其他機制（如 wrapper struct）來強制型別安全。

**判斷依據**：diff 中新增的巨集定義為空，且所有使用該標記的函式參數仍為 `void *`，無法提供型別檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:102</code> validateStoredKeyConversion 函式未被使用</summary>

新增的 `validateStoredKeyConversion` 函式在整個 diff 中沒有被呼叫。這可能是為了除錯或驗證而加入，但若未使用，會造成 dead code，且可能隱藏潛在問題。建議移除或實際使用它來驗證 keyFromStoredKey 回呼的正確性。

**判斷依據**：diff 中新增此函式，但未見任何呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:913</code> dictSetKeyAtLink 中對 addedKey 的使用可能不一致</summary>

在 `dictSetKeyAtLink` 中，當 `*link == NULL` 時，使用 `addedKey` 來呼叫 `dictFindLink`，但 `addedKey` 是經過 `keyDup` 處理後的 key，可能與原始 `key` 不同。若 `keyDup` 會改變 key 的內容或型別，可能導致查找失敗或錯誤。建議確認此處應使用原始 `key` 還是 `addedKey`，並確保一致性。

**判斷依據**：diff 中將原本的 `key` 改為 `addedKey`，但 `addedKey` 是 `keyDup` 的結果，可能與原始 key 不同。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11911 (cache hit 11904) ｜ completion tokens 947 ｜ PR #1</sub>