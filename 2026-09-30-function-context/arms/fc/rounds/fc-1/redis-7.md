<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 `aof-load-broken` 與 `aof-load-broken-max-size` 設定，讓 Redis 在啟動時若 AOF 檔尾有格式錯誤且損壞部分小於指定大小，可自動截斷並繼續載入。整體設計合理，但實作中有幾個關鍵問題：`valid_up_to` 未初始化為 -1 可能導致錯誤截斷；`fmterr` 處理中若 `aof_load_broken` 啟用但損壞大小超過限制，會遺失原始錯誤訊息；`loadAppendOnlyFiles` 中對 `AOF_BROKEN_RECOVERED` 的處理不一致，可能導致非最後一個檔案被錯誤接受。建議優先修正 `valid_up_to` 初始化與錯誤處理邏輯。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/aof.c:1488` | valid_up_to 未初始化為 -1，可能導致錯誤截斷 | 0.90 |
| ⚠️ | Major | `src/aof.c:1746` | fmterr 處理中若損壞大小超過限制，遺失原始錯誤訊息 | 0.80 |
| ⚠️ | Major | `src/aof.c:1841` | loadAppendOnlyFiles 中對 AOF_BROKEN_RECOVERED 的處理不一致 | 0.75 |
| 🔸 | Minor | `src/aof.c:1728` | fmterr 處理中未檢查 truncate 失敗後的檔案描述符狀態 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/aof.c:1488</code> valid_up_to 未初始化為 -1，可能導致錯誤截斷</summary>

`valid_up_to` 在函式開頭宣告為 `off_t valid_up_to = 0;`，但在 `fmterr` 處理中，若 `aof_load_broken` 啟用且 `valid_up_to` 仍為 0（例如第一個命令就格式錯誤），則會執行 `truncate(aof_filepath, valid_up_to)`，將檔案截斷為 0 位元組，造成資料完全遺失。

建議將 `valid_up_to` 初始化為 -1，並在 `fmterr` 中檢查 `valid_up_to == -1` 時不進行截斷，改為記錄錯誤並回傳 `AOF_FAILED`。

**判斷依據**：diff 中 `off_t valid_up_to = 0;` 未變更，但新增的 `fmterr` 處理使用 `valid_up_to` 進行截斷，若為 0 會截斷整個檔案。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1746</code> fmterr 處理中若損壞大小超過限制，遺失原始錯誤訊息</summary>

在 `fmterr` 標籤中，當 `aof_load_broken` 啟用但損壞大小超過 `aof_load_broken_max_size` 時，僅記錄「AOF was not loaded because the size of the corrupted portion exceeds the configured limit」，但未包含原始格式錯誤的詳細資訊（如檔案名稱、錯誤位置）。這會讓使用者難以判斷損壞的具體原因。

建議在該分支中保留原有的「Bad file format reading the append only file」訊息，或至少包含檔案名稱與錯誤類型。

**判斷依據**：diff 中新增的 `else` 分支僅記錄大小超限，未包含原始錯誤訊息。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1841</code> loadAppendOnlyFiles 中對 AOF_BROKEN_RECOVERED 的處理不一致</summary>

在 `loadAppendOnlyFiles` 中，當 `ret == AOF_BROKEN_RECOVERED` 且 `last_file` 為 false 時，程式碼會將 `ret` 設為 `AOF_FAILED` 並記錄錯誤，但之後的 `if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED)` 條件中又包含了 `AOF_BROKEN_RECOVERED`，這可能導致非最後一個檔案被錯誤接受。

建議移除該條件中的 `ret == AOF_BROKEN_RECOVERED`，或明確處理此情況。

**判斷依據**：diff 中新增了 `ret == AOF_BROKEN_RECOVERED` 到條件中，但前一行已將非最後一個檔案的 `AOF_BROKEN_RECOVERED` 轉為 `AOF_FAILED`，此條件可能造成邏輯矛盾。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/aof.c:1728</code> fmterr 處理中未檢查 truncate 失敗後的檔案描述符狀態</summary>

在 `fmterr` 處理中，若 `truncate` 失敗，程式碼僅記錄錯誤，但未處理 `server.aof_fd` 的狀態。若 `server.aof_fd` 不為 -1，且 `truncate` 失敗，後續的 AOF 寫入可能會使用錯誤的檔案偏移。

建議在 `truncate` 失敗時，也確保 `server.aof_fd` 被正確處理（例如關閉或重置）。

**判斷依據**：diff 中新增的 `truncate` 失敗分支未處理 `server.aof_fd`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 39276 (cache hit 1536) ｜ completion tokens 1482 ｜ PR #7</sub>