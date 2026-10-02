<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 主要修正 GcsBucket._resolve_path 在 storage_block_id 為 null 時造成的路徑雙重巢狀問題，並調整測試設定與過濾警告。核心改動在 _resolve_path 中加入 bucket_folder 前綴檢查，但該檢查使用子字串比對，可能誤判包含 bucket_folder 字串但非前綴的路徑（例如 bucket_folder='data/' 時，路徑 'metadata/file.txt' 會被錯誤跳過）。此外，_bucket_folder_suffix 中新增的跨欄位驗證使用 field_validator 而非 model_validator，可能無法正確取得 bucket 欄位值，導致驗證失效。其他改動（測試設定、警告過濾、測試檔案格式）風險較低。建議優先修正 _resolve_path 的比對邏輯，並確認跨欄位驗證的實作方式。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734` | 子字串比對可能誤判非前綴路徑 | 0.90 |
| ⚠️ | Major | `src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:710` | 跨欄位驗證使用 field_validator 可能無法取得 bucket 值 | 0.80 |
| 🔸 | Minor | `src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734` | 路徑比對未考慮正規化 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734</code> 子字串比對可能誤判非前綴路徑</summary>

`if self.bucket_folder and self.bucket_folder in path:` 使用子字串比對，而非檢查路徑是否以 bucket_folder 開頭。若 bucket_folder 為 'data/'，而 path 為 'metadata/file.txt'，則 'data/' 存在於 'metadata/' 中，導致錯誤地跳過前綴添加，產生錯誤路徑。建議改為 `path.startswith(self.bucket_folder)` 或使用 `PurePosixPath` 比較前綴。

**判斷依據**：diff 中新增的檢查使用 `in` 運算子，而非 `startswith`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:710</code> 跨欄位驗證使用 field_validator 可能無法取得 bucket 值</summary>

在 `_bucket_folder_suffix` 中使用 `info.data.get("bucket")` 進行跨欄位驗證，但 `field_validator` 的 `info.data` 僅包含已驗證的欄位，且欄位驗證順序不保證 bucket 已先驗證。若 bucket 欄位尚未驗證，`info.data.get("bucket")` 可能回傳 None，導致驗證失效。應改用 `model_validator` 進行跨欄位驗證。

**判斷依據**：diff 中新增的驗證邏輯位於 `field_validator` 內，但註解也提到應使用 `model_validator`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734</code> 路徑比對未考慮正規化</summary>

`self.bucket_folder` 可能包含尾隨斜線，而 `path` 可能未正規化（例如包含多餘斜線或相對路徑）。直接使用 `in` 或 `startswith` 可能無法正確處理。建議先將兩者正規化（例如使用 `PurePosixPath`）再比較。

**判斷依據**：diff 中未對路徑進行正規化處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4278 (cache hit 4224) ｜ completion tokens 941 ｜ PR #5</sub>