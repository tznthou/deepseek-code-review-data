<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 dict 的 stored-key API 從全域開關（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式，使程式碼更不易誤用。主要風險在於回呼函式的正確性與效能，以及部分呼叫點未正確轉換 key 格式。建議先修正 dictSetKeyAtLink 中可能使用未轉換 key 進行查找的問題，並確認所有 dictType 的 keyFromStoredKey 回呼均正確。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/dict.c:914` | dictSetKeyAtLink 使用未轉換的 key 進行查找 | 0.90 |
| ⚠️ | Major | `src/dict.c:102` | validateStoredKeyConversion 函式未使用 | 0.80 |
| ⚠️ | Major | `src/dict.c:98` | dictStoredKey2Key 可能回傳 NULL 導致後續錯誤 | 0.75 |
| ⚠️ | Major | `src/dict.c:342` | rehash 時使用 dictGetHash 可能與既有 hash 不一致 | 0.70 |
| ⚠️ | Major | `src/dict.c:890` | dictSetKeyAtLink 中 keyDup 可能重複轉換 key | 0.70 |
| 🔸 | Minor | `src/dict.c:97` | dictStoredKey2Key 名稱可能造成混淆 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>src/dict.c:914</code> dictSetKeyAtLink 使用未轉換的 key 進行查找</summary>

在 dictSetKeyAtLink 中，當 *link 為 NULL 時，程式碼使用 `dictFindLink(d, addedKey, NULL)` 來查找現有 entry。然而，`addedKey` 是經過 keyDup 處理後的 stored-key，而 `dictFindLink` 預期的是 lookup key。若 dictType 有設定 keyFromStoredKey，則此處應先將 addedKey 轉換為 lookup key，否則可能找不到正確的 entry，導致資料不一致或錯誤。

失敗情境：當 dict 使用 keyFromStoredKey（例如 dbDictType），且呼叫 dictSetKeyAtLink 更新現有 entry 的 key 時，若 stored-key 與 lookup key 不同，dictFindLink 會使用錯誤的 key 進行比較，可能找不到 entry 或找到錯誤的 entry。

建議修正：將 `dictFindLink(d, addedKey, NULL)` 改為 `dictFindLink(d, dictStoredKey2Key(d, addedKey), NULL)`。

**判斷依據**：diff 中第 912 行：`*link = dictFindLink(d, addedKey, NULL);`，而 addedKey 是 stored-key，但 dictFindLink 需要 lookup key。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:102</code> validateStoredKeyConversion 函式未使用</summary>

新增的 `validateStoredKeyConversion` 函式在整個 diff 中沒有被呼叫。這可能是開發中的除錯程式碼，若無用途應移除，以免造成混淆。

**判斷依據**：diff 中新增了此函式，但搜尋整個 diff 未見任何呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:98</code> dictStoredKey2Key 可能回傳 NULL 導致後續錯誤</summary>

`dictStoredKey2Key` 直接呼叫 `d->type->keyFromStoredKey(key)`，若該回呼實作可能回傳 NULL（例如錯誤處理），則後續的 hash 或比較函式可能收到 NULL 指標而導致 crash。雖然目前提供的回呼（kvGetKey）不會回傳 NULL，但 API 設計上應考慮防禦。

**判斷依據**：diff 中新增的 dictStoredKey2Key 函式，未檢查回呼回傳值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:342</code> rehash 時使用 dictGetHash 可能與既有 hash 不一致</summary>

在 `rehashEntriesInBucketAtIndex` 中，原本使用 `dictHashKey(d, key, 1)` 來計算 stored-key 的 hash，現在改為先取得 lookup key 再呼叫 `dictGetHash`。若 dictType 的 hashFunction 與 storedHashFunction 不同（例如舊版 API 中兩者可能不同），則新舊 hash 可能不一致，導致 rehash 後 key 被放到錯誤的 bucket。

失敗情境：若某 dictType 的 storedHashFunction 與 hashFunction 實作不同，且 keyFromStoredKey 轉換後得到的 key 與原本 stored-key 的 hash 不同，則 rehash 後 key 可能無法被找到。

建議：確認所有使用此 dict 的 dictType 中，hashFunction 與 storedHashFunction 的關係，或確保 keyFromStoredKey 轉換後的 key 與 stored-key 的 hash 一致。

**判斷依據**：diff 中 rehashEntriesInBucketAtIndex 的修改，從 dictHashKey(d, key, 1) 改為 dictGetHash(d, key)。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:890</code> dictSetKeyAtLink 中 keyDup 可能重複轉換 key</summary>

在 `dictSetKeyAtLink` 中，`addedKey` 是透過 `d->type->keyDup(d, key)` 產生的。若 keyDup 實作假設輸入是 lookup key，但此處傳入的是 stored-key，可能導致錯誤。需要確認所有 keyDup 實作是否相容於 stored-key。

**判斷依據**：diff 中 dictSetKeyAtLink 的修改，keyDup 的輸入參數 key 被標記為 __stored_key，但 keyDup 的實作可能未預期 stored-key。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:97</code> dictStoredKey2Key 名稱可能造成混淆</summary>

函式名稱 `dictStoredKey2Key` 中的 '2' 可能被誤解為 'to'，但實際上它是轉換函式。建議使用更明確的名稱，如 `dictGetKeyFromStoredKey`。

**判斷依據**：diff 中新增的函式名稱。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11875 (cache hit 1408) ｜ completion tokens 1652 ｜ PR #1</sub>