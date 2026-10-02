<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 dict 的 stored-key API 從全域狀態切換（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式，並移除了 storedHashFunction 和 storedKeyCompare。整體方向合理，可消除全域狀態帶來的脆弱性。但改動涉及核心資料結構，需特別注意正確性與相容性。主要風險在於 hashTypeDelete 的參數語意變更、dictStoredKey2Key 在無回呼時的回傳型別，以及移除快取比較邏輯可能造成的效能影響。建議先修正 hashTypeDelete 的呼叫點與 dictStoredKey2Key 的型別問題，並確認效能測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/t_hash.c:3503` | hashTypeDelete 參數語意變更導致傳入 Entry* 而非 sds | 0.95 |
| ⚠️ | Major | `src/dict.c:97` | dictStoredKey2Key 在無 keyFromStoredKey 時回傳型別不符 | 0.85 |
| ⚠️ | Major | `src/server.c:321` | 移除 dictCompareKV 可能導致效能回歸 | 0.80 |
| 🔸 | Minor | `src/dict.h:157` | pauseAutoResize 型別變更可能影響 ABI 相容性 | 0.70 |
| 🔸 | Minor | `src/dict.c:102` | validateStoredKeyConversion 函式未使用且邏輯可能錯誤 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/t_hash.c:3503</code> hashTypeDelete 參數語意變更導致傳入 Entry* 而非 sds</summary>

hashTypeDelete 的簽章從 `int hashTypeDelete(robj *o, void *key, int isSdsField)` 改為 `int hashTypeDelete(robj *o, void *key)`，且註解說明 `field` 應為 sds。但在 `onFieldExpire` 中，原本呼叫 `hashTypeDelete(expCtx->hashObj, field, 0)`，其中 `field` 是 `eItem` 結構中的 `field` 成員，型別為 `Entry*`（或類似結構），並非 sds。修改後呼叫 `hashTypeDelete(expCtx->hashObj, field)`，會將 Entry* 當作 sds 使用，導致 `sdslen((sds)field)` 讀取錯誤記憶體，可能造成 crash 或未定義行為。

**失敗情境**：當 hash 欄位過期時，`onFieldExpire` 被呼叫，傳入的 `field` 是 Entry 指標，但函式內會對其呼叫 `sdslen`，讀取 Entry 結構的前幾個位元組當作 sds header，可能得到錯誤長度或越界存取。

**建議**：在 `onFieldExpire` 中，先從 Entry 取得 sds 欄位名稱（例如使用 `entryGetKey(entry)` 或類似函式），再傳入 `hashTypeDelete`。或者保留 `isSdsField` 參數以區分輸入型別。

**判斷依據**：diff 中 `onFieldExpire` 的呼叫從 `hashTypeDelete(expCtx->hashObj, field, 0)` 改為 `hashTypeDelete(expCtx->hashObj, field)`，且 `hashTypeDelete` 的實作中直接使用 `sdslen((sds)field)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:97</code> dictStoredKey2Key 在無 keyFromStoredKey 時回傳型別不符</summary>

`dictStoredKey2Key` 的實作：
```c
static const void *dictStoredKey2Key(dict *d, const void *key __stored_key) {
    return (d->type->keyFromStoredKey) ? d->type->keyFromStoredKey(key) : key;
}
```
當 `keyFromStoredKey` 為 NULL 時，回傳 `key`，但 `key` 的型別是 `const void *`，而函式回傳型別也是 `const void *`，看似正確。然而，在呼叫端，例如 `dictAddRaw` 中：
```c
void *position = dictFindLinkForInsert(d, dictStoredKey2Key(d, key), existing);
```
`dictFindLinkForInsert` 的參數型別是 `const void *key`，所以沒有型別問題。但若 `keyFromStoredKey` 為 NULL，則 `dictStoredKey2Key` 回傳的指標與原始 `key` 相同，這在語意上是對的。真正的問題在於 `validateStoredKeyConversion` 函式：
```c
static int validateStoredKeyConversion(dict *d, const void *key __stored_key) {
    const void *extracted = dictStoredKey2Key(d, key);
    if (d->type->keyFromStoredKey) {
        return extracted != NULL;
    }
    return extracted == key;
}
```
此函式未被使用，且其邏輯可能不正確：當 `keyFromStoredKey` 存在時，僅檢查 `extracted != NULL`，但未驗證 extracted 是否為有效 key。不過此函式目前未被呼叫，影響有限。

**建議**：移除未使用的 `validateStoredKeyConversion`，或修正其邏輯並在適當處呼叫。

**判斷依據**：diff 中新增的 `dictStoredKey2Key` 和 `validateStoredKeyConversion` 函式。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.c:321</code> 移除 dictCompareKV 可能導致效能回歸</summary>

原本 `dictCompareKV` 使用快取機制（`cache->useCache`）來避免在比較時重複取得 key 和長度。現在改為 `dictSdsCompareKV`，直接比較兩個 sds，但移除了快取邏輯。在 dict 查找過程中，比較函式會被多次呼叫，若每次都要計算 `sdslen` 和 `memcmp`，可能增加 CPU 負擔，尤其在 hash 衝突較多時。

**失敗情境**：在高負載下，大量 key 比較可能導致效能下降。

**建議**：評估是否需要在新的比較函式中加入類似的快取機制，或確認效能影響可接受。

**判斷依據**：diff 中刪除了 `dictCompareKV` 函式，並修改 `dictSdsCompareKV` 的實作。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.h:157</code> pauseAutoResize 型別變更可能影響 ABI 相容性</summary>

`pauseAutoResize` 從 bitfield `signed pauseAutoResize: 15;` 改為 `int16_t pauseAutoResize;`。雖然大小可能相同（皆為 2 bytes），但 bitfield 的符號性和位元排列可能與 `int16_t` 不同，若 dict 結構被外部模組直接存取，可能造成 ABI 不相容。Redis 的 dict 結構通常不視為公開 API，但模組可能透過指標操作。

**建議**：確認此變更不會影響外部模組，或保留 bitfield 宣告。

**判斷依據**：diff 中 struct dict 的欄位變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:102</code> validateStoredKeyConversion 函式未使用且邏輯可能錯誤</summary>

新增的 `validateStoredKeyConversion` 函式目前沒有被任何地方呼叫，且其邏輯僅檢查 extracted 是否為 NULL 或是否等於原始 key，並未真正驗證轉換的正確性。這可能是開發中的殘留程式碼。

**建議**：移除或實作完整的驗證邏輯並在適當處呼叫。

**判斷依據**：diff 中新增的函式，且未見呼叫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12912 (cache hit 12800) ｜ completion tokens 2236 ｜ PR #1</sub>