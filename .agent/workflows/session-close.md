---
description: 儲存工作進度、執行連結檢查並同步至 GitHub。
---

這個 workflow 會引導你完成 session 關閉前的標準作業程序 (SOP)，確保所有筆記變更都被妥善記錄與同步。

### 1. 確認工作區狀態
執行 `git status` 檢查是否有未追蹤或未提交的檔案。

// turbo
### 2. 暫存並提交變更
將所有變更加入 Git 暫存區並提交。
```powershell
git add .
git commit -m "歸檔今日進度 (自動產生)"
```

// turbo
### 3. 同步至 GitHub
執行 `git push` 確保遠端儲存庫也是最新狀態。

### 4. 產生今日成果總結 (可選)
為了讓下次開工更順利，請確認 `.gemini/antigravity/brain/walkthrough.md` 已經更新，內容應包含：
- 今日修正的連結數量。
- 已完成的術語更正。
- 下次開工的建議位置（例如：第 31 章）。

### 5. 結束作業
完成上述步驟後，即可放心地關閉編輯器。
