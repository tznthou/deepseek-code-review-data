> **minor**：新增一個 opt-in 的 input（`repo-rules-path`），介面只加不減。沒設的 caller 不用改任何東西，
> 行為也不變（`tools/fixtures/` 的 golden 由 v1.4.1 產生，逐字比對）。引用 `@v1` 的 repo 會自動拿到新版；
> 要用新功能，在 `reusable-ai-review-post.yml` 的 caller 加上 `repo-rules-path`（說明見 USAGE「客製」一節）。

### Added

- **repo 規範檔另外用一次呼叫（opt-in）**：`reusable-ai-review-post.yml` 新增 `repo-rules-path`。
  設了之後每個 PR 多一次 DeepSeek 呼叫：一般 review 完全不動，另外一次把規範接在 diff 後面，
  只留標了規範編號（`[R03]`）的 finding，跟一般 review 合併貼出。沒設的 caller 行為不變。
  - 依據：2026-09-26 在 Qodo PR-Review-Bench 上量過（[實測紀錄](https://github.com/tznthou/deepseek-code-review/blob/main/experiments/2026-09-26-rules-loop.md)）。
    整份規範放進同一次呼叫，功能缺陷的 recall 會掉；分開呼叫、程式只留標了編號的，規則類多抓、
    功能缺陷不變。那組違規是刻意注入的，真實 repo 的違規少很多，那個準度帶不走。
  - 規範區塊的呈現逐字沿用那次實驗量過的版本：Qodo 8 個 repo 的規範寫成下面的格式後，送出去的
    區塊跟實驗逐字相同。
  - 格式：第 0 欄的 `- `（或 `* `）各算一條，在 `## ` 節裡的帶節標題當分組；沒有條目的 `## ` 節
    整節算一條；其他散文不送。0 條或超過 99 條就跳過並印 warning。
  - ⚠️ 規範檔的條目會送給 DeepSeek，同樣在禁用詞掃描的範圍內。檔案取自 default branch，
    不是 PR 的 head。
  - 規範那次失敗不擋一般 review，摘要會註明。它的最壞耗時壓在約 6 分鐘內：用預設參數，
    最壞要 20 分鐘，會吃光 job 的額度，連一般 review 都貼不出來。
  - 規範那次的 finding 落在一般 finding 的同檔 ±3 行內，兩則併成一則留言；只有過得了行內門檻的
    才會貼或併，其餘列在摘要。
  - 已知語意：冪等照舊只看 `(path, line)`。第二次 push 時，規範 finding 若落在上一輪留過言的那一行，
    只會出現在摘要。

### Changed

- `tools/selftest.py` 從 18 組 100 項增加到 **21 組 162 項**。新增的三組涵蓋規範檔的切條目與逐字渲染、
  規範編號過濾，以及 post 的兩件事：沒設規範檔時輸出逐字不變（`tools/fixtures/` 的 golden 是用改動前的
  v1.4.1 產生的），有設時的合併與摘要。

### Docs

- `post_review.py` 貼摘要那段的註解還寫著「冪等：編輯自己上一則」。#40 只修了開頭的 docstring，
  這裡跟著改：摘要每次執行都新建一則 review，冪等只做在 inline comment。
- USAGE「這套不會幫你做的事」補一條：collect 的 `paths-ignore` 只決定跑不跑。PR 裡只要有一個檔案
  不在忽略清單內，整個 PR 照樣觸發，送出去的也是整份 diff（被忽略的檔案也在裡面）；目前沒有
  「送出前排除某些路徑」的設定。這條是實際導入一個外部 repo 時記下的：那次為了「純文件 PR 不要跑」
  加了 `paths-ignore`，混合 PR 的文件部分照樣會送出去，USAGE 卻沒有講。
- 1.4.0 那句「看不到改善就改回來」結案：**保留 v1.4.0**。這句照字面做不到——要在真實 PR 上分出
  合成標的量到的差距，新舊兩版各要約 190 筆不成立的 finding，而舊版在正式環境不會再跑。
  改在 Qodo PR-Review-Bench 的 100 個修改型 PR 上，把 v1.4.0 跟前一版 rubric 各跑兩輪、
  混在同一批盲標。改回的條件跑前寫死，兩條都沒成立：行內留言那層（信心 ≥ 0.7）前一版只多抓
  8 則功能缺陷（門檻 10 則）；位置命中第一輪前一版高、第二輪打平，不是兩輪都贏。
  信心 ≥ 0.6 那層兩版一樣多，v1.4.0 的差別是把一部分真問題改列在摘要表。
  真實 PR 上的誤報沒有量到。
  - 新增一頁 `experiments/2026-09-28-v140-exit.md`，索引加一列。
  - README §4.7 那句「真實 PR 上的效果還在量」改成指向這頁。
- 新增 `experiments/`：實測紀錄的公開索引。實驗的原始資料一直放在不進 repo 的私有目錄，
  README §9 說這個 repo 值得看的是實測紀錄，但 09-25 起方法最硬的兩組只有我們自己看得到。
  索引列了 13 組實驗：已經寫在 README／CHANGELOG 的只寫結論、連過去，數字不重抄；另外寫了
  兩頁新的——修改型 PR 的 recall 基準線（Qodo PR-Review-Bench），以及把 repo 規範放進 prompt 的得失。
- README 開頭「這個 kit 對自己做過的兩件事」改成「實測紀錄」，補上上面那兩組，數字都帶分母與條件；
  §1 檔案總覽加上 `experiments/`。
- README §2 步驟 5 補一條：整份規範檔放進同一次呼叫，功能缺陷的 recall 會掉（盲標量過），
  只挑幾條的代價沒量過。
- USAGE「第 2 步」與 README §7 的「強制 action 釘 SHA 的 repo 目前不能用」改寫成 `v1.4.1` 起可以用。
  2026-09-26 在測試 repo 開著這個政策實測：collect、code-review、post 都跑到最後；同一個設定下，
  還停在 `v1.4.0` 的 caller 照樣被擋。沒實測到的也寫明了：測試 repo 沒有依賴清單，dependency review
  那個 job 是跳過的，而跳過的 job 不會被這個政策檢查。AI agent 安裝程序的前提檢查同步放寬
  （`sha_pinning_required` 是 `true` 也可以）。
- README 開頭「它在什麼標的上有用」的 ⛔ 那列標錯了標的。「Markdown／文件（27 檔）」底下的
  「16 筆只有 1 筆成立、註解密度 51.7%」出自一個 TypeScript／React PR（27 檔裡 14 個 TS/TSX、
  9 個文件），§4.7 寫的也是「TypeScript + React 專案的 PR」，51.7% 是排除文件後算的。
  這列改掛回「TypeScript／React，註解密度高」；markdown 那列換成真正的純文件 PR（§8 的 PR #1、
  §4.8 的 #24）。§9 那句「markdown 標的上 16 筆只有 1 筆成立」同步改。
- 同一段開頭那句「命中率由標的型態決定，不是由模型決定」改成「模型用 `deepseek-v4-pro` 的前提下，
  命中率主要看標的：型態，以及作者有沒有把決策理由寫在 code 旁邊」。改標之後表上有兩列
  TS/React、結論相反，原句跟表格對不上；而且那 16 筆裡有 10 筆是 flash 報的（0 筆成立），
  同一列本身就混了兩個模型。
- 標題下那句「便宜的先跑，貴的才跑」改寫：`01` 與 `03` 都在 PR 開啟／更新時直接觸發、同時跑，
  `04` 只看 `03` 的結果，AI review 不會等 linter，也不看它過沒過。實際的分工是 linter/SAST
  當合併關卡（§2 步驟 6），AI review 只給意見（§6）。
