<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 dict 的 stored-key API 從全域狀態切換（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式，並移除了 storedHashFunction/storedKeyCompare。整體方向合理，但存在多個正確性與相容性風險：dictStoredKey2Key 未在 dict.h 中宣告，可能導致隱式宣告或連結錯誤；validateStoredKeyConversion 未使用，可能觸發編譯警告；dictSetKeyAtLink 中新增的 dictFindLink 呼叫可能造成效能回歸；hashTypeDelete 簽名變更未更新所有呼叫點；且缺少測試覆蓋。建議在合併前修正這些問題。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/dict.c:97` | dictStoredKey2Key 未在 dict.h 中宣告，可能導致隱式宣告或連結錯誤 | 0.95 |
| ⚠️ | Major | `src/t_hash.c:1257` | hashTypeDelete 簽名變更未更新所有呼叫點 | 0.90 |
| ⚠️ | Major | `src/dict.c:101` | validateStoredKeyConversion 函式未使用，可能觸發編譯警告 | 0.85 |
| ⚠️ | Major | `src/dict.c:913` | dictSetKeyAtLink 中新增 dictFindLink 呼叫可能造成效能回歸 | 0.80 |
| 🔸 | Minor | `src/dict.h:157` | pauseAutoResize 型別變更可能影響 ABI 相容性 | 0.70 |
| 🔸 | Minor | `src/server.c:321` | 移除 dictCompareKV 可能影響其他使用者 | 0.70 |
| 🔸 | Minor | `src/dict.c:97` | dictStoredKey2Key 應為 static inline 以減少呼叫開銷 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/dict.c:97</code> dictStoredKey2Key 未在 dict.h 中宣告，可能導致隱式宣告或連結錯誤</summary>

函式 `dictStoredKey2Key` 在 dict.c 中定義，但未在 dict.h 中宣告。其他檔案（如 defrag.c）呼叫此函式時，若未包含正確的宣告，將導致隱式宣告（C99 中為錯誤）或連結錯誤。

建議在 dict.h 中新增宣告：
```c
const void *dictStoredKey2Key(dict *d, const void *key __stored_key);
```

**判斷依據**：diff 中新增了此函式，但 dict.h 的修改未包含其宣告。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:1257</code> hashTypeDelete 簽名變更未更新所有呼叫點</summary>

`hashTypeDelete` 的簽名從 `int hashTypeDelete(robj *o, void *key, int isSdsField)` 改為 `int hashTypeDelete(robj *o, void *key)`，但 diff 中仍有呼叫點傳入第三個參數（例如 `hashTypeDelete(o, field, 1)`）。這會導致編譯錯誤。

請搜尋所有呼叫點並移除多餘的參數。

**判斷依據**：diff 中修改了函式定義，但未修改所有呼叫點（例如 module.c 中的呼叫仍傳入 1）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:101</code> validateStoredKeyConversion 函式未使用，可能觸發編譯警告</summary>

新增的靜態函式 `validateStoredKeyConversion` 從未被呼叫。若編譯器開啟 `-Wunused-function`（通常包含在 `-Wall` 中），將產生警告，違反 R04（-Werror 下編譯失敗）。

建議移除該函式，或加入實際使用（例如在 debug 模式中驗證）。

**判斷依據**：diff 中新增此函式，但未見任何呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:913</code> dictSetKeyAtLink 中新增 dictFindLink 呼叫可能造成效能回歸</summary>

在 `dictSetKeyAtLink` 中，當 `*link == NULL` 時，新增了 `dictFindLink(d, addedKey, NULL)` 來尋找連結。這會對每個插入操作增加一次完整的 dict 查找，可能顯著影響效能，特別是在大量插入時。

原本的設計是呼叫者應提供正確的 link，此處的 fallback 可能掩蓋呼叫者的錯誤。建議評估是否必要，或改為 assert 並要求呼叫者提供 link。

**判斷依據**：diff 中新增了 dictFindLink 呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.h:157</code> pauseAutoResize 型別變更可能影響 ABI 相容性</summary>

`pauseAutoResize` 從 bitfield 改為 `int16_t`，這可能改變 struct dict 的記憶體佈局，影響 ABI 相容性。若有用戶端依賴舊佈局（例如透過擴充模組），可能導致問題。

建議確認此變更的必要性，並評估對 ABI 的影響。

**判斷依據**：diff 中將 bitfield 改為 int16_t。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:321</code> 移除 dictCompareKV 可能影響其他使用者</summary>

`dictCompareKV` 被移除，但可能仍有其他程式碼引用它（例如在外部模組中）。若未完全移除所有引用，將導致連結錯誤。

建議搜尋整個程式碼庫，確保沒有殘留引用。

**判斷依據**：diff 中移除了 dictCompareKV，但未確認所有引用已移除。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:97</code> dictStoredKey2Key 應為 static inline 以減少呼叫開銷</summary>

`dictStoredKey2Key` 在多處被呼叫，若未內聯，可能增加函式呼叫開銷。建議宣告為 `static inline` 以允許編譯器最佳化。

**判斷依據**：diff 中定義為 static，但未 inline。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12922 (cache hit 12800) ｜ completion tokens 1749 ｜ PR #1</sub>