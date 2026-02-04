# Skills 總覽

**用途**: 為 AI Agent 提供標準化的工作流程和腳本

---

## 📚 可用 Skills

### 1. 古文卦例提取 (Ancient Text Extraction)
**路徑**: `.agent/skills/ancient-text-extraction/SKILL.md`

**功能**:
- 從分頁中提取完整卦例
- 自動標註座標
- 生成標準化 YAML Frontmatter

**適用 Agent**: 所有

**使用方式**:
```
請載入「古文卦例提取」skill,然後處理 pages/page_005.txt
```

---

### 2. 座標驗證 (Coordinate Verification)
**路徑**: `.agent/skills/coordinate-verification/SKILL.md`

**功能**:
- 驗證 YAML 格式
- 檢查座標範圍
- 偵測重疊
- 計算覆蓋率

**配套腳本**: `scripts/verify_coordinates.py`

**使用方式**:
```bash
python scripts/verify_coordinates.py original/inbox/
```

---

## 🎯 Skills 使用流程

```
1. Agent 載入 Skill
   ↓
2. 按照 Skill 指示執行
   ↓
3. 生成標準化輸出
   ↓
4. 執行驗證腳本
   ↓
5. 通過驗證 → 歸檔
```

---

## 📝 給 Agent 的提示範本

```markdown
你即將開始處理《增刪卜易》原文。

請先載入以下 Skills:
1. 古文卦例提取 (.agent/skills/ancient-text-extraction/SKILL.md)
2. 座標驗證 (.agent/skills/coordinate-verification/SKILL.md)

然後處理 pages/page_001.txt

務必嚴格遵守 Skills 中的:
- 輸出格式規範
- 座標計算方法
- 品質檢查清單

你的 Agent ID 是: {AGENT_ID}
```

---

## ✅ 品質保證

使用 Skills 的好處:
- ✅ 所有 Agent 輸出格式一致
- ✅ 減少人工檢查工作
- ✅ 可自動化驗證
- ✅ 易於追蹤問題

---

**維護**: User + Antigravity  
**最後更新**: 2026-02-04
