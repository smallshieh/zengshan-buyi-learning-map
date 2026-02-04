# 實作路線圖

**版本**: 1.0.0  
**最後更新**: 2026-02-04

---

## 當前狀態

### ✅ 已完成 (v1.0 - 2026-02-04)

基於《增刪卜易》專案,已完成:

**核心文檔** (100%):
- [x] PROTOCOL.md
- [x] AGENTS.md  
- [x] TASK_MATRIX.md
- [x] CLI_TOOLS.md
- [x] QUALITY_TRACKING_GUIDE.md

**Skills 系統** (40%):
- [x] ancient-text-extraction
- [x] coordinate-verification
- [ ] translation-skill (待實作)
- [ ] summarization-skill (待實作)
- [ ] api-doc-generation-skill (待實作)

**自動化腳本** (80%):
- [x] agent_gatekeeper.py
- [x] quality_reviewer.py
- [x] verify_coordinates.py
- [x] progress_tracker.py
- [ ] split_pages.py (待實作)
- [ ] build_manifest.py (待實作)
- [ ] process_drafts.py (待實作)

**規格文檔** (100%):
- [x] SYSTEM_SPEC.md
- [x] CHANGE_MANAGEMENT.md
- [x] ROADMAP.md (本檔案)

---

## 短期目標 (v1.1 - 2026-02 ~ 2026-03)

### 1. 補完核心腳本

**優先級**: High  
**預估工時**: 6-8 小時

#### split_pages.py
```python
# 功能: 切分原文為分頁
# 輸入: source/book_full.txt
# 輸出: source/pages/page_*.txt
# 規則:
# - 每頁約 2000-3000 字
# - 保留完整段落,不切斷句子
# - 生成頁碼索引
```

#### build_manifest.py
```python
# 功能: 生成座標地圖
# 輸入: source/pages/
# 輸出: manifest.json
# 格式:
{
  "book_title": "...",
  "total_pages": 100,
  "total_chars": 250000,
  "pages": [
    {
      "filename": "page_001.txt",
      "start": 0,
      "length": 2500,
      "checksum": "md5..."
    }
  ]
}
```

#### process_drafts.py
```python
# 功能: 自動歸檔通過驗證的檔案
# 輸入: processing/review/
# 輸出: knowledge/{category}/
# 邏輯:
# - 讀取 YAML metadata
# - 根據 extraction_type 分類
# - 移動到對應目錄
# - 更新 manifest
```

---

### 2. 新增 Skills

**優先級**: Medium  
**預估工時**: 4-6 小時

#### translation-skill
- 古文轉白話文
- 保持結構清晰
- 標註難字解釋

#### summarization-skill
- 理論段落摘要
- 提取關鍵概念
- 生成思維導圖素材

---

### 3. 增強品質追蹤

**優先級**: Medium  
**預估工時**: 3-4 小時

- [ ] 自動生成週報 (每週 Agent 表現總結)
- [ ] 視覺化趨勢圖表
- [ ] 異常檢測 (分數突然下降)

---

## 中期目標 (v1.5 - 2026-03 ~ 2026-06)

### 1. Web UI 介面

**優先級**: Medium  
**預估工時**: 20-30 小時

**功能**:
- Dashboard 顯示進度
- 品質審查介面 (取代 CLI)
- Agent 績效視覺化
- 座標瀏覽器

**技術棧**:
- Backend: FastAPI
- Frontend: React + Tailwind
- Database: SQLite

---

### 2. 多書籍支援

**優先級**: High  
**預估工時**: 10-15 小時

**變更**:
- 專案模板系統
- 書籍配置檔 (book_config.yaml)
- 多專案管理工具

**範例配置**:
```yaml
book:
  title: "易經"
  author: "周文王"
  language: "古文"
  structure:
    - type: "hexagram"
      count: 64
    - type: "commentary"
      count: 10
  
skills:
  - hexagram-extraction
  - commentary-analysis
  
agents:
  preferred:
    - Claude-Sonnet-4.5
    - DeepSeek-R1-32B-Local
```

---

### 3. CI/CD 整合

**優先級**: Low  
**預估工時**: 6-8 小時

- GitHub Actions 自動測試
- 規格一致性檢查
- 自動生成 changelog
- Release 自動化

---

## 長期目標 (v2.0 - 2026-06 ~ 2026-12)

### 1. LLM 微調支援

**動機**: 提升專用領域表現

**計劃**:
- 收集《增刪卜易》提取資料作為訓練集
- 微調 DeepSeek-R1-32B
- 建立評估基準
- 整合到 AGENTS.md

---

### 2. 協作功能

**多人協作**:
- 任務分配系統
- 人工審查工作流程
- 評分一致性校準工具

---

### 3. 插件系統

**擴展性**:
- 自訂 Skill 格式
- 第三方 Agent 整合  
- 自訂驗證規則

---

## 技術債務

### 需要重構的部分

1. **progress_tracker.py** (優先級: Medium)
   - 改用 SQLite 取代 JSON
   - 支援多專案

2. **agent_gatekeeper.py** (優先級: Low)
   - 抽象化能力評分載入
   - 支援動態 Agent 註冊

3. **quality_reviewer.py** (優先級: Low)
   - 介面優化 (目前 CLI 不夠友善)
   - 支援批次評分匯入

---

## 測試策略

### 單元測試 (v1.1)
```
scripts/tests/
├── test_gatekeeper.py
├── test_quality_reviewer.py
├── test_verify_coordinates.py
└── test_progress_tracker.py
```

### 整合測試 (v1.5)
```
tests/integration/
├── test_end_to_end_workflow.py
└── test_multi_agent_coordination.py
```

### 壓力測試 (v2.0)
- 處理 1000+ 頁文本
- 10+ Agent 並行

---

## 社群貢獻

### 期待的貢獻方向

1. **新 Skills**:
   - 現代書籍提取
   - 學術論文分析
   - 法律文件處理

2. **新 Agent 整合**:
   - Llama 系列
   - Qwen 系列
   - Yi 系列

3. **工具改進**:
   - 更好的視覺化
   - 更友善的 CLI
   - 效能優化

---

## 里程碑

| 版本 | 預計日期 | 核心功能 |
|------|---------|---------|
| v1.0 | 2026-02-04 ✅ | 基礎系統 + 規格 |
| v1.1 | 2026-03-01 | 補完核心腳本 |
| v1.5 | 2026-06-01 | Web UI + 多書籍 |
| v2.0 | 2026-12-01 | LLM 微調 + 協作 |

---

**維護者**: User  
**最後更新**: 2026-02-04
