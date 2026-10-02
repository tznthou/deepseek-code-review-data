# 三方 code review 對照實驗（2026-09-21）

> ⚠️ **這份資料不可重現**。本工具每次跑的結果都不同（見 repo README §8「已知的不穩定」），
> 重跑拿不到同一份結果。這是三個 reviewer 跑同一份標的的唯一一份原始紀錄。

## 這是什麼

刻意寫一份很髒的 Python（`sandbox/pr_stats.py`，104 行，10 個埋點），
分別給三個 reviewer 審，量召回與誤報。標的的 branch 跑完就刪了，
diff 保留在 `pr.diff`。

**方法論重點：預期表在跑之前就定稿（`expected.md`），跑完不得修改。**
沒有這一步，結果無法解讀——只會得到一句「它報了 N 筆」，不知道該抓的抓了幾成。

## 結果

| | v4-pro | flash | Codex |
|---|---|---|---|
| A 類召回（該報 7 個） | **7/7** | 6/7（漏迴圈內重複 I/O） | 1/7 |
| B 類誤報（不該報 2 個） | 0 | 0 | 0 |
| 雜訊 | 0 | 0 | 0 |
| finding 數 | 9 | 7 | 1 |
| 耗時 | 24.5s | 9.1s | 31s |
| **自報行號正確數** | **0/9** | **0/7** | 1/1 |

### 四個結論

1. **定位層是命脈不是優化**。16 筆 DeepSeek finding，自報行號 **0 筆**指對，
   偏移 2～29 行。沒有 `locate.py`，inline comment 會全部貼錯位置。
   比 memory 記的「16 筆只有 1 筆指對」更糟。
2. **誤報探針 B1 被反殺**。埋的陷阱是「`events[0]` 上面幾行已有 `if not events: return`」，
   賭它會報「空容器沒檢查」。兩個模型都**明確讀懂了那行守衛**（body 原文寫「已處理」），
   改報排序假設與 `KeyError`，兩個都成立。方向與 `annotated-code-review-blindspot` 相反，
   但 N=1 推翻不了那條。
3. **flash 在 Python 標的上的表現跟禁令對不上**。RESUME 的禁令說 flash「4 個技術斷言錯 3 個、
   安全問題只給 0.6 信心」——那是在 **shell 標的**上得到的。這次 Python 標的：7 筆斷言全成立、
   shell injection 給 0.9 blocker。⚠️ 兩個變因同時不同（標的型態＋有無 `python.md`），
   不能下因果結論，只能說「那條禁令不能外推到 Python 標的」。
4. **Codex 的 adversarial frame 找到獨特路徑**。它多說了一句
   「supplying no PR numbers bypasses API fetching and reaches `archive()` directly」——
   `numbers = sys.argv[2:]` 空 list ⇒ 兩個迴圈都不跑 ⇒ 完全繞過所有 API 呼叫直達
   shell injection。DeepSeek 兩個模型都只報「這裡有洞」，沒報「怎麼走到洞」。

### 三個比較上的限制（解讀前必讀）

- **Codex 的 prompt 明文要求收斂**（"Prefer one strong finding over several weak ones"），
  所以 1/7 不是召回率，是遵守指示。拿它比 DeepSeek 的 7/7 是比錯東西。
- **輸入格式不同**：Codex 拿純檔案（行號直接對應），DeepSeek 拿 unified diff（要從 hunk 換算）。
  Codex 行號 1/1 正確不能歸因於模型較強。
- **標的對 DeepSeek 最有利**：Python（有專屬規則檔）＋新增整檔＋缺陷密度 10 個/104 行。
  真實 PR 不長這樣，7/7 不能外推。

## 檔案

| 檔案 | 內容 |
|---|---|
| `expected.md` | **跑之前定稿的預期表**，含 10 個埋點分類與已知變因 |
| `pr.diff` | 標的的 diff（branch 已刪，這是唯一副本） |
| `findings.json` / `review.md` | deepseek-v4-pro 的結果 |
| `findings-flash.json` / `review-flash.md` | deepseek-flash 的結果 |
| `codex-full.txt` | 送給 Codex 的完整 prompt（回應只有 1 筆 Critical + 3/10 評分，見上表） |

## 順帶撈到的兩個真 bug

比埋的那些缺陷更有價值，已在 v1.2.2 修掉：

1. `review-local.sh` 沒傳 `--rules-dir` → 本機與 CI 跑的不是同一套配置，兩邊都不提示
2. `max_tokens` 截斷報成「找不到 JSON 物件」→ 症狀指向格式、真因是長度，費用照算
