<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 dict 的 stored-key API 從全域狀態切換（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式進行轉換，並移除了相關的 storedHashFunction 與 storedKeyCompare 欄位。整體設計更乾淨，但存在幾個潛在問題：validateStoredKeyConversion 函式未被使用，可能導致編譯警告；dictSetKeyAtLink 中對 addedKey 的搜尋邏輯可能因 keyDup 而失效；hashTypeDelete 的簽名變更後，部分呼叫點可能傳入錯誤的 key 類型；此外，dict.h 中 __stored_key 巨集定義為空，可能影響程式碼可讀性與型別安全。建議優先修正 dictSetKeyAtLink 的邏輯，並確認所有 hashTypeDelete 呼叫點的正確性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/dict.c:914` | dictSetKeyAtLink 中搜尋 addedKey 可能失敗 | 0.80 |
| ⚠️ | Major | `src/dict.c:102` | validateStoredKeyConversion 函式未被使用 | 0.75 |
| ⚠️ | Major | `src/t_hash.c:3503` | hashTypeDelete 呼叫點可能傳入錯誤的 key 類型 | 0.70 |
| 🔸 | Minor | `src/dict.h:66` | __stored_key 巨集定義為空，降低型別安全 | 0.60 |
| 🔸 | Minor | `src/dict.c:98` | dictStoredKey2Key 可能回傳 NULL，但呼叫者未檢查 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:914</code> dictSetKeyAtLink 中搜尋 addedKey 可能失敗</summary>

在 dictSetKeyAtLink 中，當 link 為 NULL 時，程式碼使用 `dictFindLink(d, addedKey, NULL)` 來尋找現有 entry。然而，`addedKey` 是經過 `keyDup` 處理後的 key，而 `dictFindLink` 內部會使用 `dictStoredKey2Key` 將 stored key 轉換為 lookup key。如果 `keyDup` 回傳的 key 與原始 key 不同（例如複製了 sds），則 `dictStoredKey2Key` 可能無法正確轉換，導致找不到對應的 entry，進而觸發 assert 失敗或錯誤的行為。

建議：在呼叫 `dictFindLink` 前，先將 `addedKey` 轉換為 lookup key，或直接使用原始的 `key` 進行搜尋。

**判斷依據**：diff 中新增的這一行，位於 dictSetKeyAtLink 函式內，且 addedKey 是 keyDup 的結果。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:102</code> validateStoredKeyConversion 函式未被使用</summary>

新增的 `validateStoredKeyConversion` 函式在 dict.c 中定義，但沒有被任何地方呼叫。這可能導致編譯器警告（特別是在 -Werror 下），且該函式目前沒有實際作用。

建議：移除該函式，或將其用於除錯或斷言中。

**判斷依據**：diff 中新增的函式定義，且未在其他地方看到呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:3503</code> hashTypeDelete 呼叫點可能傳入錯誤的 key 類型</summary>

hashTypeDelete 的簽名從 `(robj *o, void *key, int isSdsField)` 改為 `(robj *o, void *key)`，移除了 isSdsField 參數。然而，在 onFieldExpire 函式中，原本的呼叫是 `hashTypeDelete(expCtx->hashObj, field, 0)`，其中 field 是 Entry* 類型（stored key），但現在直接傳入 field，而 hashTypeDelete 內部會假設 key 是 sds 並呼叫 sdslen。這可能導致對 Entry* 指標呼叫 sdslen 而崩潰。

建議：檢查 onFieldExpire 中 field 的實際類型，若為 Entry*，則需先轉換為 sds 再呼叫。

**判斷依據**：diff 中此行的變更，且 onFieldExpire 的 field 參數類型為 eItem，可能不是 sds。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.h:66</code> __stored_key 巨集定義為空，降低型別安全</summary>

`__stored_key` 巨集被定義為空，因此它不會在編譯時期提供任何型別檢查。這使得 stored key 和 lookup key 的區別僅存在於註解中，容易導致誤用。

建議：考慮使用不同的指標型別（例如 typedef）來區分，或至少使用屬性標記（如 `__attribute__((address_space(1)))`）來增加編譯器檢查。

**判斷依據**：diff 中新增的巨集定義。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:98</code> dictStoredKey2Key 可能回傳 NULL，但呼叫者未檢查</summary>

`dictStoredKey2Key` 在 `keyFromStoredKey` 存在時直接呼叫該回呼，但未檢查回傳值是否為 NULL。如果回呼實作可能回傳 NULL（例如錯誤情況），則後續的 hash 或比較操作可能會對 NULL 指標進行操作而導致崩潰。

建議：在 dictStoredKey2Key 中增加 NULL 檢查，或確保所有 keyFromStoredKey 實作不會回傳 NULL。

**判斷依據**：diff 中新增的函式實作。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12404 (cache hit 11904) ｜ completion tokens 1452 ｜ PR #1</sub>