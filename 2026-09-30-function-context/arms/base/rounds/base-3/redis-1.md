<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 dict 的 stored-key API 從全域狀態切換（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式，使程式碼更不易出錯。主要風險在於所有 dictType 是否正確實作 keyFromStoredKey，以及 hashTypeDelete 簽名變更後所有呼叫點是否已更新。整體設計合理，但需確認記憶體管理與回呼函式的正確性。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/dict.c:102` | validateStoredKeyConversion 函式未使用，可能遺漏驗證 | 0.80 |
| ⚠️ | Major | `src/dict.c:97` | keyFromStoredKey 回呼可能回傳 NULL，導致後續解參考崩潰 | 0.70 |
| ⚠️ | Major | `src/dict.c:542` | dictInsertKeyAtLink 未將 stored key 轉換為 lookup key 進行比較 | 0.70 |
| ⚠️ | Major | `src/dict.c:913` | dictSetKeyAtLink 中新增鍵時未使用轉換後的 key 進行查找 | 0.70 |
| 🔸 | Minor | `src/dict.h:157` | pauseAutoResize 型別從 bitfield 改為 int16_t，可能影響 ABI 或行為 | 0.60 |
| 🔸 | Minor | `src/server.c:316` | kvGetKey 回呼直接回傳 sds，未處理可能的 NULL | 0.60 |
| 🔸 | Minor | `src/t_hash.c:1257` | hashTypeDelete 移除 isSdsField 參數後，呼叫者需確保傳入正確型別 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:102</code> validateStoredKeyConversion 函式未使用，可能遺漏驗證</summary>

新增的 `validateStoredKeyConversion` 函式在整個 diff 中沒有被呼叫。如果此函式是為了驗證 keyFromStoredKey 回呼的正確性，應在 dict 初始化或插入時呼叫；否則應移除，避免死碼。

**判斷依據**：diff 中新增此函式，但搜尋整個 diff 未見任何呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:97</code> keyFromStoredKey 回呼可能回傳 NULL，導致後續解參考崩潰</summary>

`dictStoredKey2Key` 直接呼叫 `d->type->keyFromStoredKey(key)` 並回傳其結果，未檢查 NULL。若回呼實作錯誤或輸入異常，可能回傳 NULL，後續 `dictGetHash` 或比較函式會對 NULL 解參考，造成 crash。建議在回呼後檢查 NULL 並處理錯誤。

**判斷依據**：diff 中新增此函式，未見 NULL 檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:542</code> dictInsertKeyAtLink 未將 stored key 轉換為 lookup key 進行比較</summary>

在 `dictInsertKeyAtLink` 中，插入時直接使用傳入的 `key`（stored key）進行 hash 和比較，但未先呼叫 `dictStoredKey2Key` 轉換。若 dict 使用 keyFromStoredKey，可能導致 hash 值錯誤或比較失敗，造成重複鍵或查找錯誤。

**判斷依據**：diff 中此函式簽名加入 __stored_key，但函式內未見轉換呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:913</code> dictSetKeyAtLink 中新增鍵時未使用轉換後的 key 進行查找</summary>

在 `dictSetKeyAtLink` 中，當 `newItem` 為真且需要重新查找 bucket 時，使用 `dictStoredKey2Key(d, key)` 轉換，但後續 `dictFindLink(d, addedKey, NULL)` 使用 `addedKey`（可能已複製的 stored key），未轉換為 lookup key。若 keyDup 回傳 stored key 格式，可能導致查找失敗。

**判斷依據**：diff 中此處使用 addedKey，未見轉換。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.h:157</code> pauseAutoResize 型別從 bitfield 改為 int16_t，可能影響 ABI 或行為</summary>

原本 `pauseAutoResize` 是 15 位元的 bitfield，現在改為 `int16_t`。這可能改變 struct 佈局或在不同平台上行為不一致，且失去原本的符號性檢查（負值表示錯誤）。需確認此變更的必要性與影響。

**判斷依據**：diff 中 struct dict 的欄位型別變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:316</code> kvGetKey 回呼直接回傳 sds，未處理可能的 NULL</summary>

`kvGetKey` 直接呼叫 `kvobjGetKey` 並回傳其結果，未檢查 NULL。若 kvobj 結構異常，可能回傳 NULL，導致後續 hash 或比較 crash。

**判斷依據**：diff 中新增此函式，未見 NULL 檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/t_hash.c:1257</code> hashTypeDelete 移除 isSdsField 參數後，呼叫者需確保傳入正確型別</summary>

`hashTypeDelete` 現在假設傳入的 `field` 一定是 sds。但原本有些呼叫點傳入 `Entry*`（如 `onFieldExpire` 中 `field` 可能是 entry）。需確認所有呼叫點都已更新為傳入 sds，否則可能導致型別錯誤。

**判斷依據**：diff 中函式簽名變更，且呼叫點 `onFieldExpire` 原本傳入 `field`（可能為 entry），現改為直接傳入，需確認型別。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11911 (cache hit 11904) ｜ completion tokens 1605 ｜ PR #1</sub>