# 多次取樣／投票的 $0 模擬（2026-09-25）

> 狀態：完成，$0（只用 2026-09-24 confidence loop 已標記的資料，沒有呼叫 API）
> 對照的外部研究見同目錄 `research-notes.md`

## 問的問題

GitHub 上的做法（Cursor Bugbot、mira、paper-lantern、SWR-Bench）會把同一份 diff 跑 N 次，
再投票或取聯集。動手前先用現有資料算：**這招在我們的資料上能改善什麼，改善不了什麼**。

## 資料與方法

- 資料：`../2026-09-24-confidence-loop/rounds/`。現行 rubric（v1.4.0）= v02+v05，每個標的 10 次跑；
  舊 rubric = v00+v04，當複製組（probe 那組是 9 次）
- 「同一個 finding」的判定：
  - **oracle**：用標記時指派的 `item`（依內容分群）→ 投票效益的**上限**
  - **loc**：同 path、行號差 ≤ 2，跨 run 連通分量（production 做得到）
  - **snippet**：`existing_code` 共用至少一行（去空白後 ≥ 8 字元）
- 代表 finding：cluster 內 confidence 最高的那一筆（production 也只會貼一則）
- strict：有爭議算不成立；lenient：有爭議算成立

## 結果

### 1. 信度 baseline（第一次量）

兩兩 run 的 item 集合 Jaccard（現行 rubric）：python 0.76、shell 0.65、probe 0.63。
也就是任兩次跑的 finding 聯集裡，有 24–37% 只出現在其中一次。

### 2. 投票 vs 現有的 confidence 門檻（自動 loc 分群，strict，現行 rubric）

| 標的 | 現況 inline（單次、≥0.7） | 3 次跑、≥2 票且 ≥0.7 才 inline | 3 次聯集的 recall |
|---|---|---|---|
| python | P 0.762／R 0.588 | P 0.803／R 0.617 | 0.625（單次 0.600） |
| shell | P 0.932／R 0.629 | P 0.928／R 0.743 | 0.857（單次 0.700） |
| probe | P 0.833／R 0.267 | P 0.818／R 0.294 | 0.431（單次 0.267） |

- inline 那層的 precision：跟現有 confidence 門檻比，6 格（3 標的 × 2 rubric）是 −0.015～+0.05，**沒有穩定改善**
- 聯集確實拉得動 recall（shell +0.16、probe +0.16），但摘要表會變長、變雜（python 6.4 → 8.0 筆，P 0.766 → 0.667）
- 成本 ×3
- 自動 loc 分群跟 oracle 差不多：混到不同 item 的 cluster 佔 6.6–8.1%，混到對錯兩種說法的佔 3.8–6.1%
- snippet 分群比較差：模型每次抄的行不一樣，同一個問題會被拆開，票數不足就被刷掉（python recall 0.62 → 0.49）

### 3. 一致性當排序訊號（AUC，strict）

| | confidence | 一致性（10 次 LOO） | N=3：一致性優先、再看 confidence |
|---|---|---|---|
| 現行 rubric | 0.876 | 0.891 | **0.904**（同批抽樣的 confidence 0.876 → +0.028） |
| 舊 rubric | 0.825 | 0.922 | 0.910（同批抽樣的 confidence 0.829 → +0.081） |

現行 rubric 下 +0.028，沒有過改 rubric 時用的 +0.05 門檻。

### 4. 持續型誤報（投票消不掉的那種）

- 只算「明確不成立」：現行 rubric 19 筆有 8 筆屬於「≥50% 的跑都會報」的 item，**8 筆全是同一個 `PR-B11`**
  （把操作者設定的 `NOTES_WEBHOOK` 當成外部輸入）；舊 rubric 7 筆 0 筆
- ⚠️ 前一版寫的「46% 是持續型」是 strict 口徑，把有爭議的 `PY-K-classify` 也算進去了，不能當通則
- `PR-B11` 跟真實 PR 的 R09（「lint-command 由 repo 擁有者填」）是**同一型：信任邊界誤判**。這一型要靠給資訊，投票沒用；
  而且多數決會替它背書

### 5. 事後發現（沒有預登記，只能當假說）

`PR-B11` 在舊 rubric 9 次跑出現 1 次，在 v1.4.0 rubric 10 次跑出現 8 次，**其中 5 筆 ≥0.7，會貼成 inline**
（Fisher 單尾 p≈0.005）。但這是在約 50 個 item 裡事後挑出來的，考慮多重比較，不能當結論。
→ 放進「v1.4.0 真實 PR 驗證」的觀察點：信任邊界型的誤報有沒有變多。

## 限制

1. 標的全是合成的，而且三個 diff 都是**整檔新增**（`@@ -0,0 +1,N @@`，沒有 context 行、也沒有刪除行）。
   模型本來就看得到整個檔案 → **這套 harness 量不到「擴充上下文」「錨點檢查」這類做法**
2. oracle 分群是標記者指派的，本身就用了「行號 ±2 + 內容 regex」
3. N=3 是從 10 次跑裡抽樣，不是真的各自獨立跑 3 次

## 重跑

```bash
python3 vote_sim.py          # 頻率表、Jaccard、k-of-N 投票（oracle 分群）
python3 consistency_auc.py   # confidence vs 一致性的 AUC、持續型組成（strict）
python3 auto_cluster_sim.py  # 自動分群（loc／snippet）與分層設計
```

三支都只讀 `../2026-09-24-confidence-loop/`；2026-09-25 從 scratchpad 搬過來後重跑，輸出與 `*.out` 逐位元組一致。
