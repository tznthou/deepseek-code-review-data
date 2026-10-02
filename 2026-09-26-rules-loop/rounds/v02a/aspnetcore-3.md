<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修改了 Unix 憑證信任流程，使其在 SSL_CERT_DIR 已設定但未包含目標目錄時，能顯示建議訊息並正確回報信任失敗。同時新增了兩個 EventSource 事件，並將 NssDb 類別從 primary constructor 改為傳統建構子以符合命名慣例。整體改動合理，但存在一個潛在的例外處理問題：在解析 SSL_CERT_DIR 中的路徑時，catch 區塊過於寬鬆，可能掩蓋非預期的錯誤。此外，EventSource 事件 114 的訊息格式與事件 110 不一致，可能造成使用者混淆。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:371` | 過度寬鬆的 catch 區塊可能掩蓋非預期的例外 | 0.60 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/CertificateManager.cs:1317` | 事件 114 的訊息格式與事件 110 不一致 | 0.50 |

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:371</code> 過度寬鬆的 catch 區塊可能掩蓋非預期的例外</summary>

在解析 SSL_CERT_DIR 中的每個目錄時，`catch` 區塊捕獲所有例外並回傳 false。這可能掩蓋了非預期的錯誤（例如 `Path.GetFullPath` 因權限不足或路徑格式錯誤以外的原因失敗）。建議僅捕獲預期的例外類型（如 `ArgumentException`、`NotSupportedException`、`PathTooLongException`），或至少記錄例外訊息以便診斷。

**判斷依據**：diff 中新增的 try-catch 區塊，catch 未指定例外類型。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/CertificateManager.cs:1317</code> 事件 114 的訊息格式與事件 110 不一致</summary>

事件 110 的訊息為 `For example, `export {2}="{0}:{1}"`.`，而事件 114 的訊息為 `For example, `export {1}="{0}:${1}"`.`。兩者皆用於建議設定 SSL_CERT_DIR，但格式不同（一個使用 `{1}` 代表現有值，另一個使用 `${1}`）。這可能導致使用者困惑，建議統一格式。

**判斷依據**：diff 中新增的事件 114 定義，與既有事件 110 的訊息格式不同。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5645 (cache hit 1536) ｜ completion tokens 689 ｜ PR #3</sub>