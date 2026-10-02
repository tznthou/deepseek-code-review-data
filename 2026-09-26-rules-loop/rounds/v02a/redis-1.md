<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 dict 的 stored-key API 從全域狀態切換（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式，並移除了 storedHashFunction/storedKeyCompare。整體方向合理，可消除全域狀態帶來的潛在問題。但改動涉及 dict 核心，且新增的 validateStoredKeyConversion 函式未被使用，可能導致編譯警告（違反 R04）。此外，部分函式簽章變更（如 hashTypeDelete）需要確認所有呼叫點已同步更新。建議先處理未使用函式與編譯警告，再進行合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/dict.c:102` | [R04] 未使用的靜態函式 validateStoredKeyConversion 可能導致編譯警告 | 0.90 |
| 🔸 | Minor | `src/dict.c:97` | dictStoredKey2Key 函式未宣告為 static，可能違反 R07 | 0.80 |
| 🔸 | Minor | `src/dict.c:97` | dictStoredKey2Key 函式未處理 keyFromStoredKey 回傳 NULL 的情況 | 0.70 |
| 🔸 | Minor | `src/dict.h:157` | pauseAutoResize 型別從 bitfield 改為 int16_t 可能影響結構佈局與 ABI | 0.70 |
| 🔸 | Minor | `src/server.c:316` | kvGetKey 函式未檢查 kvobj 是否為 NULL | 0.70 |
| 🔸 | Minor | `src/dict.c:97` | dictStoredKey2Key 函式名稱與參數標記可能造成混淆 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:102</code> [R04] 未使用的靜態函式 validateStoredKeyConversion 可能導致編譯警告</summary>

新增的靜態函式 `validateStoredKeyConversion` 在整個 diff 中沒有被任何地方呼叫。若專案啟用 `-Werror` 且編譯器會對未使用的靜態函式發出警告（如 `-Wunused-function`），這將導致編譯失敗，違反規範 R04。

建議：移除該函式，或若未來有使用計畫，請加上 `__attribute__((unused))` 或 `UNUSED` 巨集，但更佳做法是直接刪除。

**判斷依據**：diff 中新增了 `validateStoredKeyConversion` 函式，但搜尋整個 diff 未見任何呼叫點。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:97</code> dictStoredKey2Key 函式未宣告為 static，可能違反 R07</summary>

`dictStoredKey2Key` 函式在 `dict.c` 中定義，但未加上 `static` 修飾詞。若此函式僅供 dict.c 內部使用，則應宣告為 `static` 以符合規範 R07（內部輔助函式必須宣告為 static）。

建議：確認此函式是否需要在其他編譯單元中使用，若不需要，請加上 `static`。

**判斷依據**：diff 中新增的 `dictStoredKey2Key` 函式沒有 `static` 關鍵字，且未在標頭檔中宣告。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:97</code> dictStoredKey2Key 函式未處理 keyFromStoredKey 回傳 NULL 的情況</summary>

`dictStoredKey2Key` 直接呼叫 `d->type->keyFromStoredKey(key)` 並回傳其結果，但未檢查回傳值是否為 NULL。若 `keyFromStoredKey` 實作可能回傳 NULL（例如輸入無效），則後續的 hash 或比較操作可能對 NULL 指標進行解參考，導致 crash。

建議：在函式內加入斷言或錯誤處理，確保回傳值非 NULL。

**判斷依據**：diff 中新增的 `dictStoredKey2Key` 函式沒有對 `keyFromStoredKey` 的回傳值做 NULL 檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.h:157</code> pauseAutoResize 型別從 bitfield 改為 int16_t 可能影響結構佈局與 ABI</summary>

原本 `pauseAutoResize` 是 15 位元的 bitfield，現在改為 `int16_t`。這會改變 `struct dict` 的記憶體佈局，可能影響 ABI 相容性，尤其是當外部模組或序列化依賴此結構時。此外，`int16_t` 的範圍為 -32768 到 32767，而原本 bitfield 的範圍為 -16384 到 16383，若程式碼中曾依賴此範圍，可能造成行為差異。

建議：確認此變更的必要性，並檢查是否有外部程式碼依賴此結構佈局。

**判斷依據**：diff 中將 `signed pauseAutoResize: 15;` 改為 `int16_t pauseAutoResize;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:316</code> kvGetKey 函式未檢查 kvobj 是否為 NULL</summary>

`kvGetKey` 直接呼叫 `kvobjGetKey((kvobj *) kv)`，但未檢查 `kv` 是否為 NULL。若呼叫端傳入 NULL，可能導致 crash。

建議：加入 NULL 檢查或斷言。

**判斷依據**：diff 中新增的 `kvGetKey` 函式沒有對 `kv` 做 NULL 檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:97</code> dictStoredKey2Key 函式名稱與參數標記可能造成混淆</summary>

函式名稱 `dictStoredKey2Key` 暗示將 stored key 轉換為 key，但參數標記為 `__stored_key`，且函式內部若 `keyFromStoredKey` 為 NULL 則直接回傳原指標。這可能讓讀者誤解其行為。

建議：在註解中更清楚地說明此函式的用途與回傳值。

**判斷依據**：diff 中新增的函式與其命名和參數標記。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12912 (cache hit 1536) ｜ completion tokens 1662 ｜ PR #1</sub>