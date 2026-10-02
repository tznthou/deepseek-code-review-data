# 2026-09-25 文件裡的「檔名:行號」引用過期（PR #38）

> 狀態: **已結案** (PR #38 squash merge `50c1e7b`, 2026-09-25 07:14:51 UTC). $0.

## 兩支腳本

- `check-line-refs.py`: 掃 repo 所有 tracked 的 `.md/.py/.yml/.sh`, 抽出 `檔名:數字` 形式的引用, 印出引用處上下文與目標行, 供人工比對 (唯讀)
  - ⚠️ regex 抓不到「第 N 行」這種中文寫法, 要另外 `grep -n '第 ?[0-9]+ ?行'`
  - CHANGELOG 與 README 評估紀錄裡的行號是**當時的狀態**, 命中不代表要改
- `check-anchors.sh`: SETUP-CHECKLIST 改用內容當錨點後, 驗四個錨點在各自的 workflow 裡 `grep -c -F` 都剛好 = 1
  - 若子超決定做成 selftest, 從這支改寫 (09-25 選配待決)

## 結果

- `SETUP-CHECKLIST.md` 6 處行號 4 處指錯: `04:19` ×2 (實為 29)、`01-static-review.yml:48` (實為 50)、`04:31` 的 `# environment: ai-review` (1.0.2 `eff7abf` 就刪了)
- environment 那條照做會被 actionlint 擋: `when a reusable workflow is called with "uses", "environment" is not available` (scratchpad 最小樣本實測)
- 修法: 全部改標那一行的內容, 不寫行號; environment 那條改「整項跳過」並指向 04 開頭的註解
- 同一份文件 `1f3941a` (1.0.0 前) 修過一次行號參照, 修完又漂 → 這次不再改數字
