<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 dict 的 stored-key API 從全域開關（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式自動轉換，並移除了 storedHashFunction/storedKeyCompare。整體方向合理，可簡化呼叫端並減少錯誤。但改動範圍大，涉及 dict 核心、hash、rdb、kvstore 等多個模組，需特別注意正確性與相容性。主要風險在於 keyFromStoredKey 回呼的實作與使用是否一致，以及 hashTypeDelete 簽名變更後所有呼叫點是否正確更新。建議合併前仔細驗證 hash 欄位刪除、RDB 載入、rehash 等路徑。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/dict.c:102` | validateStoredKeyConversion 函式未使用且邏輯可能錯誤 | 0.80 |
| ⚠️ | Major | `src/dict.c:342` | rehash 時使用 dictStoredKey2Key 轉換 storedKey 可能導致 hash 不一致 | 0.75 |
| ⚠️ | Major | `src/dict.c:913` | dictSetKeyAtLink 中新增的 dictFindLink 呼叫可能使用錯誤的 key | 0.70 |
| ⚠️ | Major | `src/server.c:316` | kvGetKey 回呼可能回傳 NULL 或非預期指標 | 0.70 |
| ⚠️ | Major | `src/t_hash.c:1257` | hashTypeDelete 簽名變更後，呼叫點可能傳入錯誤的 key 類型 | 0.70 |
| 🔸 | Minor | `src/dict.h:157` | pauseAutoResize 型別從 bitfield 改為 int16_t 可能影響 ABI 或行為 | 0.60 |
| 🔸 | Minor | `src/dict.h:66` | 新增 __stored_key 巨集但未用於所有相關參數 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:102</code> validateStoredKeyConversion 函式未使用且邏輯可能錯誤</summary>

新增的 `validateStoredKeyConversion` 函式在整個 diff 中沒有被呼叫，且其邏輯有問題：當 `keyFromStoredKey` 存在時，它只檢查回傳值是否為 NULL，但 NULL 可能是合法的 key 值（例如空字串指標？），且未驗證轉換後 key 的正確性。建議移除此函式，或若需驗證，應在 dict 初始化或除錯模式中呼叫，並修正判斷邏輯。

**判斷依據**：diff 中新增此函式，但未見任何呼叫點。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:342</code> rehash 時使用 dictStoredKey2Key 轉換 storedKey 可能導致 hash 不一致</summary>

在 `rehashEntriesInBucketAtIndex` 中，原本直接使用 storedKey 計算 hash（透過 storedHashFunction），現在改為先呼叫 `dictStoredKey2Key` 取得 key 再計算 hash。若 `keyFromStoredKey` 回呼有副作用或依賴 dict 狀態，可能導致 rehash 時 hash 值與插入時不同，造成 key 遺失或重複。需確認所有 dictType 的 `keyFromStoredKey` 實作是純函式且與插入時使用的 hashFunction 一致。

**判斷依據**：diff 中此處由原本的 `dictHashKey(d, key, 1)` 改為先轉換再 hash。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:913</code> dictSetKeyAtLink 中新增的 dictFindLink 呼叫可能使用錯誤的 key</summary>

在 `dictSetKeyAtLink` 中，當 `*link == NULL` 時，原本使用 `key` 呼叫 `dictFindLink`，現在改為使用 `addedKey`。但 `addedKey` 是經過 `keyDup` 處理後的 key，可能與原始 key 不同（例如 keyDup 會複製或轉換）。若 `keyDup` 不是簡單複製，可能導致找不到正確的 link。需確認所有 dictType 的 keyDup 行為。

**判斷依據**：diff 中此處由 `dictFindLink(d, key, NULL)` 改為 `dictFindLink(d, addedKey, NULL)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:316</code> kvGetKey 回呼可能回傳 NULL 或非預期指標</summary>

`kvGetKey` 直接呼叫 `kvobjGetKey` 並回傳其結果。若 `kvobjGetKey` 可能回傳 NULL（例如某些特殊 kvobj 類型），則 `dictStoredKey2Key` 會回傳 NULL，後續 hash 或比較可能崩潰。需確認所有使用此 dictType 的 kvobj 都保證有有效的 key。

**判斷依據**：diff 中新增此函式作為 keyFromStoredKey。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:1257</code> hashTypeDelete 簽名變更後，呼叫點可能傳入錯誤的 key 類型</summary>

`hashTypeDelete` 移除了 `isSdsField` 參數，現在假設傳入的 `field` 一定是 sds。但原本有些呼叫點傳入的是 `Entry*`（例如 `onFieldExpire` 中 `hashTypeDelete(expCtx->hashObj, field, 0)`），現在改為 `hashTypeDelete(expCtx->hashObj, field)`，但 `field` 的型別是 `eItem`，可能不是 sds。需檢查所有呼叫點，確保傳入的是 sds 字串。

**判斷依據**：diff 中函式簽名由 `int hashTypeDelete(robj *o, void *key, int isSdsField)` 改為 `int hashTypeDelete(robj *o, void *key)`，且呼叫點 `onFieldExpire` 原本傳入 `0` 表示非 sds，現在直接傳入 `field`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.h:157</code> pauseAutoResize 型別從 bitfield 改為 int16_t 可能影響 ABI 或行為</summary>

原本 `pauseAutoResize` 是 15-bit signed bitfield，現在改為 `int16_t`。雖然大小相同，但 bitfield 的符號性和溢位行為可能不同。若程式碼依賴其溢位行為（例如遞增到最大值後變負數），可能產生差異。需確認沒有此類依賴。

**判斷依據**：diff 中此處由 `signed pauseAutoResize: 15;` 改為 `int16_t pauseAutoResize;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.h:66</code> 新增 __stored_key 巨集但未用於所有相關參數</summary>

新增了 `#define __stored_key` 作為標記，但並非所有 stored-key 參數都加上此標記（例如 `dictFindLink` 的 key 參數沒有）。這可能導致標記不一致，降低可讀性。建議全面套用或移除。

**判斷依據**：diff 中新增此巨集，但僅部分函式參數使用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12888 (cache hit 12800) ｜ completion tokens 1949 ｜ PR #1</sub>