<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 dict 的 stored-key API 從全域狀態切換（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式，並移除了 storedHashFunction 和 storedKeyCompare。整體方向合理，能消除脆弱的全域狀態切換。但主要風險在於 hashTypeDelete 的簽名變更：原本的 isSdsField 參數被移除，改為一律假設傳入的是 sds 欄位。然而在 onFieldExpire 中，原本傳入的是 Entry*（isSdsField=0），現在卻直接將 Entry* 當作 sds 使用，這會導致 sdslen 讀取錯誤的記憶體，可能造成當機或錯誤行為。此外，dictSetKeyAtLink 中對 addedKey 的使用可能不一致，以及 validateStoredKeyConversion 函式未被使用，可能觸發編譯警告。建議優先修正 hashTypeDelete 的呼叫點，確保傳入正確的 key 型別。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/t_hash.c:3503` | hashTypeDelete 不再接受 Entry*，但 onFieldExpire 仍傳入 Entry* | 0.95 |
| ⚠️ | Major | `src/dict.c:914` | dictSetKeyAtLink 中搜尋時使用 addedKey 可能不一致 | 0.80 |
| 🔸 | Minor | `src/dict.c:102` | validateStoredKeyConversion 函式未被使用，可能觸發 -Wunused-function 警告 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/t_hash.c:3503</code> hashTypeDelete 不再接受 Entry*，但 onFieldExpire 仍傳入 Entry*</summary>

在 `onFieldExpire` 中，原本呼叫 `hashTypeDelete(expCtx->hashObj, field, 0)`，其中 `field` 是 `Entry*` 型別（`isSdsField=0`）。但此 PR 移除了 `isSdsField` 參數，並將 `hashTypeDelete` 的實作改為一律將 `field` 視為 `sds`（呼叫 `sdslen((sds)field)`）。這會導致對 `Entry*` 指標呼叫 `sdslen`，讀取錯誤的記憶體，可能造成當機或未定義行為。

**失敗情境**：當 hash 欄位過期且需要刪除時，`onFieldExpire` 被呼叫，傳入的 `field` 是 `Entry*`，但 `hashTypeDelete` 會嘗試取得其 sds 長度，導致記憶體存取錯誤。

**建議修法**：在呼叫 `hashTypeDelete` 前，先從 `Entry*` 中取出 sds 欄位，例如使用 `entryGetKey(entry)` 取得 sds 後再傳入。或者保留 `isSdsField` 參數以區分兩種型別。

**判斷依據**：diff 中 `src/t_hash.c` 的變更：`-    serverAssert(hashTypeDelete(expCtx->hashObj, field, 0) == 1);` 改為 `+    serverAssert(hashTypeDelete(expCtx->hashObj, field) == 1);`，且 `hashTypeDelete` 的簽名從 `int hashTypeDelete(robj *o, void *field, int isSdsField)` 改為 `int hashTypeDelete(robj *o, void *field)`，實作中直接呼叫 `sdslen((sds)field)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:914</code> dictSetKeyAtLink 中搜尋時使用 addedKey 可能不一致</summary>

在 `dictSetKeyAtLink` 中，當 `*link == NULL` 時，程式碼改為 `*link = dictFindLink(d, addedKey, NULL);`。但 `addedKey` 是經過 `keyDup` 處理後的 key，而 `dictFindLink` 預期的是 lookup key（即從 stored-key 提取出的 key）。如果 `keyDup` 會複製或轉換 key，則 `addedKey` 可能不是正確的 lookup key，導致找不到對應的 entry。

**失敗情境**：若 `keyDup` 回傳的 key 與原始 stored-key 不同（例如配置了不同的 keyDup），則 `dictFindLink` 可能找不到 entry，進而觸發 assert 或錯誤行為。

**建議修法**：應使用 `dictStoredKey2Key(d, key)` 取得 lookup key 後再呼叫 `dictFindLink`，而不是使用 `addedKey`。

**判斷依據**：diff 中 `src/dict.c` 的變更：`-        *link = dictFindLink(d, key, NULL);` 改為 `+        *link = dictFindLink(d, addedKey, NULL);`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:102</code> validateStoredKeyConversion 函式未被使用，可能觸發 -Wunused-function 警告</summary>

新增的 `validateStoredKeyConversion` 函式在整個 diff 中沒有被呼叫。若編譯器開啟 `-Wunused-function`（且專案使用 `-Werror`），這會導致編譯失敗。

**建議修法**：移除該函式，或將其標記為 `static inline` 並確保有使用，或加上 `__attribute__((unused))`。

**判斷依據**：diff 中新增了 `validateStoredKeyConversion` 函式，但未見任何呼叫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12404 (cache hit 12288) ｜ completion tokens 1362 ｜ PR #1</sub>