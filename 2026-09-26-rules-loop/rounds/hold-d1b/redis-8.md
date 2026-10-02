<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — ✅ 未發現阻斷性問題

本次 PR 修改了 hash 欄位過期在 HINCRBYFLOAT 複寫到 replica 時被移除的問題。主要變更包括：新增 shared.fields 物件、修改 hashTypeGetValue 函式簽名以輸出過期時間、在 hincrbyfloatCommand 中手動傳播 HSET 與 HPEXPIREAT 命令，並新增對應的複寫測試。整體而言，變更範圍明確且測試涵蓋了主要情境。針對 repo 規範的檢查，未發現違反 R01–R08 的情形。

_沒有 inline findings。_

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6046 (cache hit 6016) ｜ completion tokens 148 ｜ PR #8</sub>