---
description: 儲存工作進度、執行驗證並同步至 GitHub (支援多分支與座標系統)
---

這個 workflow 會引導你完成 session 關閉前的標準作業程序 (SOP),確保所有變更都被妥善記錄、驗證與同步。

### 1. 儲存進度追蹤 (如果有使用)
如果本次 session 使用了 progress_tracker,請儲存進度:
```python
# 確認進度已保存
tracker.save()
print(tracker.get_summary())
```

// turbo
### 2. 執行座標驗證 (如果有新提取)
如果本次處理了原文提取,執行驗證:
```powershell
python scripts/verify_coordinates.py original/inbox/
```

// turbo
### 3. 確認工作區狀態
檢查當前分支和未提交的檔案:
```powershell
git status
git branch --show-current
```

### 4. 暫存並提交變更
依據變更類型選擇適當的 commit message 格式:

**功能新增**:
```powershell
git add .
git commit -m "feat: 簡短描述

詳細說明:
- 變更項目 1
- 變更項目 2"
```

**Bug 修復**:
```powershell
git commit -m "fix: 修正問題描述"
```

**文檔更新**:
```powershell
git commit -m "docs: 文檔更新說明"
```

**重構**:
```powershell
git commit -m "refactor: 重構說明"
```

// turbo
### 5. 同步至 GitHub
推送到當前分支:
```powershell
git push origin $(git branch --show-current)
```

### 6. 更新工作記錄 (重要!)
確認 walkthrough.md 已更新,包含:
- ✅ 本次完成的主要工作
- ✅ 使用的 Agent 和 tokens
- ✅ 遇到的問題和解決方案
- ✅ 下次繼續的位置

### 7. 清理臨時檔案 (可選)
```powershell
# 清理測試腳本
Remove-Item test_*.py -ErrorAction SilentlyContinue

# 清理 Agent 暫存
Remove-Item .gemini/cache/* -Recurse -ErrorAction SilentlyContinue
```

### 8. 結束檢查清單
- [ ] Progress tracker 已儲存
- [ ] 座標驗證通過 (如適用)
- [ ] Git commit message 清晰
- [ ] 已推送到正確分支
- [ ] Walkthrough 已更新
- [ ] 臨時檔案已清理

### 9. 結束作業
完成上述步驟後,即可放心地關閉編輯器。

---

**提示**: 如果在多個分支間切換,記得在提交前確認當前分支!
