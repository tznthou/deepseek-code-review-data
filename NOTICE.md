# 第三方資料聲明

這個 repo 的實驗用到兩個公開資料集。**資料集本身沒有放在這裡**，請從原處下載（版本見下）。
這裡放的是我們自己的產出：模型的 review 輸出、標記單、計分結果與腳本。這些產出會引用到資料集裡的
code 片段與 PR 內容。

## Qodo PR-Review-Bench

- 來源：<https://huggingface.co/datasets/Qodo/PR-Review-Bench>（Curated by: Qodo team）
- 版本：revision `a73957c450a70693a743260e5637fffc44625f16`
- 授權：MIT（依資料集卡片的 `license: mit` 宣告；資料集沒有附 LICENSE 檔）
- 資料集裡的 PR 來自多個開源專案（例如 cal.com、firefox-ios、Ghost、dify、tauri、aspnetcore、redis、prefect），
  那些 code 的授權依各專案而定

## openai/codex-plugin-cc 的 adversarial-review prompt

- 來源：<https://github.com/openai/codex-plugin-cc>（`plugins/codex/prompts/adversarial-review.md`）
- 授權：Apache-2.0，全文見 [LICENSE-Apache-2.0.txt](LICENSE-Apache-2.0.txt)
- 用到的檔：`2026-09-21-three-way-review/codex-full.txt`（主體改寫自上述 prompt，我們有修改；檔頭已加註）

## AACR-Bench

- 來源：<https://huggingface.co/datasets/Alibaba-Aone/aacr-bench>
- 版本：`dataset.json`，2026-10-01 下載，sha256 `0804505f0a474765ce2840c832cfeaa6c4f0250dd6ccb169fe73c6758b245a86`
- 授權：Apache-2.0（<https://www.apache.org/licenses/LICENSE-2.0>）
