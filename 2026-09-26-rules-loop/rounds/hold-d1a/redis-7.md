<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 aof-load-broken 與 aof-load-broken-max-size 設定，讓 Redis 在啟動時若 AOF 檔案中間有格式錯誤，可以自動截斷損壞部分並繼續載入。主要風險在於自動截斷可能造成資料遺失，且實作中對檔案截斷的處理與錯誤路徑需要謹慎。最需要先確認的是 server.h 的 include guard 變更是否符合專案規範，以及新增的設定是否有完整的文件與測試。

### Findings（1 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `src/server.h:15` | [R03] 變更 include guard 命名，可能違反專案規範 | 0.90 |

<details><summary>🔸 <b>Minor</b> — <code>src/server.h:15</code> [R03] 變更 include guard 命名，可能違反專案規範</summary>

此 PR 將 `__REDIS_H` 改為 `_REDIS_H`，但專案規範 R03 要求使用雙底線開頭與結尾的 include guard（例如 `__REDIS_H`）。此變更可能導致不符合規範，且若其他檔案依賴原本的 guard 名稱，可能造成重複 include 問題。建議保留原本的 `__REDIS_H`，或確認此變更是否有其他原因。

**判斷依據**：diff 中顯示原本為 `#ifndef __REDIS_H` 與 `#define __REDIS_H`，被改為 `_REDIS_H`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7395 (cache hit 7296) ｜ completion tokens 367 ｜ PR #7</sub>