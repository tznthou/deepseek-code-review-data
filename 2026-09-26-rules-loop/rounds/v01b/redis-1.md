<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 dict 的 stored-key API 從全域狀態切換（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式，並移除了 storedHashFunction 與 storedKeyCompare。整體方向合理，可消除全域狀態帶來的脆弱性。但改動範圍大，涉及 dict 核心、hash、rdb、kvstore 等多個模組，且新增了 validateStoredKeyConversion 函式但未使用，可能違反 -Werror 規範。此外，hashTypeDelete 的簽名變更可能遺漏某些呼叫點，需確認。建議優先修正未使用的函式與潛在的編譯警告。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/dict.c:102` | [R04] 未使用的靜態函式 validateStoredKeyConversion 可能導致 -Werror 編譯失敗 | 0.90 |
| ⚠️ | Major | `src/dict.c:97` | dictStoredKey2Key 可能對 NULL keyFromStoredKey 回呼處理不當 | 0.85 |
| ⚠️ | Major | `src/dict.c:913` | dictSetKeyAtLink 中對 addedKey 的搜尋可能使用錯誤的 key 格式 | 0.80 |
| 🔸 | Minor | `src/dict.c:647` | dictGenericDelete 中比較 key 時未使用 dictStoredKey2Key 轉換 | 0.70 |
| 🔸 | Minor | `src/dict.c:797` | dictFindLinkInternal 中比較 key 時未使用 dictStoredKey2Key 轉換 | 0.70 |
| 🔸 | Minor | `src/dict.c:972` | dictTwoPhaseUnlinkFind 中比較 key 時未使用 dictStoredKey2Key 轉換 | 0.70 |
| 🔸 | Minor | `src/dict.c:1766` | dictFindLinkForInsert 中比較 key 時未使用 dictStoredKey2Key 轉換 | 0.70 |
| 🔸 | Minor | `src/server.c:316` | kvGetKey 回呼可能對非 kvobj 指標進行錯誤轉型 | 0.60 |
| 🔸 | Minor | `src/t_hash.c:1257` | hashTypeDelete 簽名變更可能遺漏呼叫點 | 0.60 |
| 🔹 | Nit | `src/dict.h:66` | 註解中提及 __stored_key 但未定義其語意 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:102</code> [R04] 未使用的靜態函式 validateStoredKeyConversion 可能導致 -Werror 編譯失敗</summary>

新增的靜態函式 `validateStoredKeyConversion` 在整個 diff 中沒有被任何地方呼叫。若專案以 `-Werror` 編譯，且編譯器啟用 `-Wunused-function`（GCC/Clang 預設對 static 函式會警告），將導致編譯失敗。

建議：移除該函式，或若未來有使用計畫，請加上 `__attribute__((unused))` 或實際使用它。

**判斷依據**：diff 中新增了此函式，但搜尋整個 diff 未見任何呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:97</code> dictStoredKey2Key 可能對 NULL keyFromStoredKey 回呼處理不當</summary>

`dictStoredKey2Key` 在 `d->type->keyFromStoredKey` 為 NULL 時直接回傳原始 key，但若 key 本身為 NULL，則回傳 NULL。呼叫端（如 `dictAddRaw`）會將此結果傳給 `dictFindLinkForInsert`，後者會對 key 進行 hash 與比較，可能導致對 NULL 指標解參考。

雖然目前所有 dictType 都設定了 keyFromStoredKey，但未來新增 dictType 時若遺漏，將造成崩潰。建議在函式中加入 assert 或明確處理 NULL key。

**判斷依據**：函式直接回傳 key，未檢查 NULL。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:913</code> dictSetKeyAtLink 中對 addedKey 的搜尋可能使用錯誤的 key 格式</summary>

在 `dictSetKeyAtLink` 中，當 `*link == NULL` 時，程式碼使用 `addedKey` 呼叫 `dictFindLink`。但 `addedKey` 是經過 `keyDup` 處理後的 key，若 `keyDup` 回傳的 key 與原始 key 不同（例如複製了 sds），則 `dictFindLink` 會以複製後的 key 進行查找，可能找不到原本的 entry。

建議：應使用原始 key（或 `dictStoredKey2Key(d, key)`）進行查找，而非 `addedKey`。

**判斷依據**：diff 中此處將原本的 `key` 改為 `addedKey`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:647</code> dictGenericDelete 中比較 key 時未使用 dictStoredKey2Key 轉換</summary>

在 `dictGenericDelete` 中，比較時使用 `he_key = dictStoredKey2Key(d, dictGetKey(he))`，但 `key` 參數是 lookup key，未經轉換。若 lookup key 與 stored key 格式不同，比較可能失敗。

目前所有呼叫端都傳入正確的 lookup key，但為求一致與安全，建議也對 `key` 進行轉換（或確保呼叫端已傳入正確格式）。

**判斷依據**：此處僅轉換了 stored key，未轉換 lookup key。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:797</code> dictFindLinkInternal 中比較 key 時未使用 dictStoredKey2Key 轉換</summary>

與 `dictGenericDelete` 類似，`dictFindLinkInternal` 中比較時使用 `visitedKey = dictStoredKey2Key(d, dictGetKey(*link))`，但 `key` 參數未轉換。若 lookup key 與 stored key 格式不同，可能導致查找失敗。

建議對 `key` 也進行轉換，或確保所有呼叫端都傳入正確格式。

**判斷依據**：此處僅轉換了 stored key，未轉換 lookup key。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:972</code> dictTwoPhaseUnlinkFind 中比較 key 時未使用 dictStoredKey2Key 轉換</summary>

與前述類似，`dictTwoPhaseUnlinkFind` 中比較時使用 `de_key = dictStoredKey2Key(d, dictGetKey(*ref))`，但 `key` 參數未轉換。若 lookup key 與 stored key 格式不同，可能導致查找失敗。

建議對 `key` 也進行轉換，或確保所有呼叫端都傳入正確格式。

**判斷依據**：此處僅轉換了 stored key，未轉換 lookup key。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:1766</code> dictFindLinkForInsert 中比較 key 時未使用 dictStoredKey2Key 轉換</summary>

與前述類似，`dictFindLinkForInsert` 中比較時使用 `he_key = dictStoredKey2Key(d, dictGetKey(he))`，但 `key` 參數未轉換。若 lookup key 與 stored key 格式不同，可能導致查找失敗。

建議對 `key` 也進行轉換，或確保所有呼叫端都傳入正確格式。

**判斷依據**：此處僅轉換了 stored key，未轉換 lookup key。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:316</code> kvGetKey 回呼可能對非 kvobj 指標進行錯誤轉型</summary>

`kvGetKey` 直接將 `kv` 轉型為 `kvobj *` 並呼叫 `kvobjGetKey`。若 dict 中儲存的不是 kvobj（例如誤用），將導致未定義行為。雖然目前使用此 dictType 的 dict 都儲存 kvobj，但建議加入 assert 或型別檢查。

**判斷依據**：直接轉型，無任何檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/t_hash.c:1257</code> hashTypeDelete 簽名變更可能遺漏呼叫點</summary>

`hashTypeDelete` 移除了 `isSdsField` 參數，但 diff 中僅更新了部分呼叫點。若其他檔案（未在此 diff 中）仍以舊簽名呼叫，將導致編譯錯誤。建議全域搜尋確認所有呼叫點均已更新。

**判斷依據**：diff 中更新了多處呼叫，但無法確認是否涵蓋所有檔案。

</details>

<details><summary>🔹 <b>Nit</b> — <code>src/dict.h:66</code> 註解中提及 __stored_key 但未定義其語意</summary>

新增的 `__stored_key` 巨集僅作為標記，但註解未清楚說明其用途與限制。建議補充說明此巨集僅用於靜態分析或文件，不影響編譯。

**判斷依據**：巨集定義為空，但未在註解中明確說明。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12912 (cache hit 12800) ｜ completion tokens 2511 ｜ PR #1</sub>