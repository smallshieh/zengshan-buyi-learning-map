# 多 Agent 文本處理系統 - 系統規格書

**規格編號**: SPEC-001  
**版本**: 1.0.0  
**狀態**: Draft

---

## 1. 系統概述

### 1.1 系統名稱
**多 Agent 文本處理系統** (Multi-Agent Text Processing System, MATPS)

### 1.2 系統描述
一套通用的文本處理框架,透過多個 AI Agent 協作完成大規模文本的提取、分析、翻譯與結構化。系統採用**座標式索引**避免命名衝突,透過 **Skills 框架**標準化工作流程,並建立**三層防護機制**確保輸出品質。

### 1.3 核心價值主張
- **避免混亂**: 座標系統取代主觀命名
- **確保品質**: 三層防護 (Gatekeeper → Skills → Quality Reviewer)
- **優化成本**: 本地與雲端模型混合使用,節省 70-80%
- **可追溯**: 完整的進度與績效記錄
- **可擴展**: 模組化設計,適用多種文本類型

---

## 2. 系統架構

### 2.1 三層架構

```
┌─────────────────────────────────────────────────────────┐
│                    MATPS 系統                            │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐      ┌─────▼─────┐     ┌─────▼─────┐
   │ 規則層  │      │  執行層   │     │  監督層   │
   │(Policy) │      │(Execution)│     │(Monitoring)│
   └────┬────┘      └─────┬─────┘     └─────┬─────┘
        │                  │                  │
  ┌─────┴─────┐      ┌─────┴─────┐     ┌─────┴─────┐
  │PROTOCOL   │      │ Skills    │     │Gatekeeper │
  │AGENTS     │      │ Agents    │     │Quality    │
  │TASK_MATRIX│      │ Scripts   │     │Tracker    │
  └───────────┘      └───────────┘     └───────────┘
```

### 2.2 層級職責

#### 規則層 (Policy Layer)
**職責**: 定義系統行為準則與約束

**組件**:
- `PROTOCOL.md` - 核心協定與流程
- `AGENTS.md` - Agent 能力評估
- `TASK_MATRIX.md` - 任務-Agent 能力矩陣

**輸出**: 規則、標準、限制

---

#### 執行層 (Execution Layer)
**職責**: 實際執行文本處理任務

**組件**:
- **Skills** - 標準化工作流程指示
- **AI Agents** - 13+ 個可用模型
- **Scripts** - 自動化處理腳本

**輸出**: 提取的文本、結構化資料

---

#### 監督層 (Monitoring Layer)
**職責**: 確保品質與合規性

**組件**:
- `agent_gatekeeper.py` - 前置檢查,禁止不合格組合
- `quality_reviewer.py` - 後置驗證,量化評分
- `verify_coordinates.py` - 座標與格式驗證

**輸出**: 品質報告、績效記錄、違規日誌

---

## 3. 核心概念

### 3.1 座標系統 (Coordinate System)

#### 3.1.1 概念定義
**檔名 = 物理地址, 標題 = 語義標籤**

傳統命名:
```
❌ 父外任平安.md
❌ 姤之恒_父外任平安.md
❌ case_057_父外任平安.md
```

座標命名:
```
✅ page_005_120_450.md
   │      │   │   └─ 段落長度 (字數)
   │      │   └───── 起始位置 (字數)
   │      └───────── 頁碼
   └──────────────── 前綴
```

#### 3.1.2 座標格式規範

**格式**: `{prefix}_{page}_{start}_{length}.{ext}`

| 欄位 | 類型 | 說明 | 範例 |
|------|------|------|------|
| prefix | string | 固定前綴 | page, chunk, section |
| page | integer | 頁碼 (3位數,補0) | 001, 023, 145 |
| start | integer | 起始字數 | 0, 120, 500 |
| length | integer | 段落長度 | 50, 450, 1200 |
| ext | string | 副檔名 | md, txt, json |

**範例**:
```
page_001_0_1500.md       # 第1頁,從0開始,長度1500字
page_023_500_300.md      # 第23頁,從500開始,長度300字
section_010_0_5000.md    # 第10節,完整5000字
```

#### 3.1.3 座標優勢
1. **唯一性**: 絕對無衝突
2. **可追溯**: 可定位到原文位置
3. **可排序**: 自然排序即為原文順序
4. **自動化友好**: 易於程式處理

---

### 3.2 三層資料架構

```
L0: 原文層 (Raw Layer)
├── source/book_full.txt          # 完整原文
└── pages/page_*.txt              # 切分頁面

L1: 過渡層 (Transitional Layer)
├── inbox/                        # Agent 產出
│   ├── page_001_0_500_Claude.md
│   └── page_001_500_300_DeepSeek.md
└── review/                       # 人工檢視區

L2: 知識庫層 (Structured Layer)
├── cases/                        # 卦例
├── theory/                       # 理論
├── glossary/                     # 術語
└── manifest.json                 # 座標地圖
```

**層級權限**:
- L0: **唯讀** (Read-only) - Agent 禁止修改
- L1: **讀寫** (Read-Write) - Agent 可寫入,人類可檢視
- L2: **人類主導** (Human-controlled) - 最終知識庫

---

### 3.3 Agent 分類與能力

#### 3.3.1 Agent 分類

**雲端 Agent** (Token 限制):
- Claude Sonnet/Opus 系列
- Gemini 系列
- GPT 系列
- DeepSeek-V3

**本地 Agent** (無限免費):
- DeepSeek-R1-32B (最強)
- DeepSeek-R1-14B
- DeepSeek-R1-Latest

**CLI 工具**:
- Codex CLI
- Gemini CLI

#### 3.3.2 能力評估維度

| 維度 | 說明 | 評分標準 |
|------|------|---------|
| T1 | 座標式提取 | 1-5 星 |
| T2 | 結構理解 | 1-5 星 |
| T3 | 術語定義 | 1-5 星 |
| T4 | 白話翻譯 | 1-5 星 |
| T5 | 結構化輸出 | 1-5 星 |
| T6 | 文字品質 | 1-5 星 |
| T7 | 批次處理 | 1-5 星 |
| T8 | 理論摘要 | 1-5 星 |
| T9 | 交叉驗證 | 1-5 星 |

---

### 3.4 Skills 框架

#### 3.4.1 Skill 定義
**Skill** 是標準化的工作流程指示,包含:
- 詳細步驟 (Step-by-step)
- 輸入/輸出格式
- 品質檢查清單
- 常見錯誤範例

#### 3.4.2 Skill 結構

```markdown
---
skill_name: "example-skill"
version: "1.0"
applies_to: ["text-extraction", "translation"]
---

# Skill 名稱

## 輸入要求
- 欄位 1
- 欄位 2

## 輸出格式
```yaml
---
field1: value
field2: value
---
內容
```

## 執行步驟
1. 步驟 1
2. 步驟 2

## 品質檢查
- [ ] 檢查項 1
- [ ] 檢查項 2

## 範例
[實際範例]
```

---

## 4. 組件規格

### 4.1 agent_gatekeeper.py

#### 功能需求
- FR-GK-001: 檢查 Agent 是否可執行任務
- FR-GK-002: 自動選擇最佳 Agent
- FR-GK-003: 記錄違規嘗試
- FR-GK-004: 支援成本偏好配置

#### 介面規範

```python
class AgentGatekeeper:
    def can_execute(
        agent_id: str, 
        task_type: str
    ) -> Tuple[bool, str]:
        """
        檢查 Agent 能否執行任務
        
        Returns:
            (can_execute, reason)
        """
        pass
    
    def get_best_agent(
        task_type: str,
        prefer_local: bool = True,
        max_cost: str = 'high'
    ) -> str:
        """
        選擇最佳 Agent
        
        Args:
            task_type: 任務類型 (T1-T9)
            prefer_local: 優先本地模型
            max_cost: 成本限制 (low/medium/high)
        
        Returns:
            agent_id
        """
        pass
```

#### 資料格式

**違規日誌**: `.gatekeeper_log.json`
```json
[
  {
    "timestamp": "2026-02-04T19:00:00+08:00",
    "agent": "DeepSeek-R1-Latest",
    "task": "T4",
    "reason": "絕對禁止: 不可執行白話文翻譯"
  }
]
```

---

### 4.2 quality_reviewer.py

#### 功能需求
- FR-QR-001: 隨機抽樣檔案
- FR-QR-002: 自動評分 (YAML, 座標)
- FR-QR-003: 互動式人工評分
- FR-QR-004: 累積績效記錄
- FR-QR-005: 趨勢分析

#### 評分維度

| 維度 | 權重 | 評分方式 | 範圍 |
|------|------|---------|------|
| 座標準確度 | 25% | 自動 | 1-5 |
| YAML 格式 | 15% | 自動 | 1-5 |
| 內容完整性 | 25% | 人工 | 1-5 |
| 文字品質 | 20% | 人工 | 1-5 |
| 提取精確度 | 15% | 人工 | 1-5 |

#### 績效資料格式

`.agent_performance.json`
```json
{
  "agents": {
    "Claude-Sonnet-4.5": {
      "total_reviews": 15,
      "average_score": 4.75,
      "scores_history": [4.8, 4.7, 4.75],
      "criteria_averages": {
        "coordinate_accuracy": [5, 5, 4],
        "yaml_format": [5, 5, 5],
        "content_completeness": [5, 4, 5],
        "text_quality": [5, 5, 5],
        "extraction_precision": [5, 4, 5]
      }
    }
  }
}
```

---

### 4.3 Skills 組件

#### 必要 Skills

**extraction-skill** (提取技能):
- 適用: 文本提取任務
- 輸出: YAML Frontmatter + Markdown 內容
- 時間戳記: ISO 8601 格式

**verification-skill** (驗證技能):
- 適用: 品質驗證任務
- 檢查: YAML格式、座標範圍、重疊偵測

**translation-skill** (翻譯技能):
- 適用: 語言轉換任務
- 輸出: 保持原文結構的譯文

---

## 5. 工作流程規格

### 5.1 標準處理流程

```
1. 準備階段
   ├── 取得原文
   ├── 清理格式
   └── 切分頁面 (split_pages.py)

2. 索引階段
   ├── 生成 manifest.json (build_manifest.py)
   └── 定義座標範圍

3. 提取階段
   ├── Gatekeeper 選擇 Agent
   ├── 載入 Skill 指示
   ├── Agent 執行提取
   └── 輸出到 inbox/

4. 驗證階段
   ├── 自動驗證 (verify_coordinates.py)
   ├── 品質抽檢 (quality_reviewer.py)
   └── 人工檢視 (optional)

5. 歸檔階段
   ├── 通過驗證的檔案
   ├── 移動到 knowledge/
   └── 更新 manifest
```

### 5.2 中斷恢復流程

```
1. 檢測中斷
   ├── Token 用盡
   ├── 網路中斷
   └── 手動停止

2. 記錄狀態
   ├── progress_tracker.save()
   └── 記錄最後處理位置

3. 切換 Agent
   ├── Gatekeeper 推薦替代 Agent
   └── 載入相同 Skill

4. 繼續處理
   ├── 從中斷點恢復
   └── 完成剩餘任務
```

---

## 6. 品質保證規格

### 6.1 品質門檻

| 任務類型 | 最低平均分 | 抽檢比例 |
|---------|-----------|---------|
| 核心內容提取 | 4.0/5.0 | 30% |
| 一般內容提取 | 3.5/5.0 | 20% |
| 術語定義 | 4.5/5.0 | 40% |
| 白話翻譯 | 4.0/5.0 | 20% |

### 6.2 績效趨勢

- **improving**: 最近3次 > 之前平均 + 0.3
- **stable**: 在 ±0.3 範圍內
- **declining**: 最近3次 < 之前平均 - 0.3

### 6.3 決策矩陣

| 平均分 | 趨勢 | 建議動作 |
|--------|------|---------|
| ≥ 4.5 | any | 增加工作量 |
| 4.0-4.5 | improving | 維持分配 |
| 4.0-4.5 | declining | 密集抽檢 |
| < 4.0 | any | 調整任務或更換 Agent |

---

## 7. 部署指南

### 7.1 環境需求

**必要**:
- Python 3.8+
- Git
- YAML parser
- JSON handler

**可選**:
- Ollama (本地模型)
- Antigravity CLI
- 雲端 API keys

### 7.2 目錄結構規範

```
project/
├── specs/                    # 規格書 (本目錄)
├── source/                   # L0: 原文
│   ├── book_full.txt
│   └── pages/
├── processing/               # L1: 過渡區
│   ├── inbox/
│   └── review/
├── knowledge/                # L2: 知識庫
├── .agent/
│   └── skills/
├── scripts/
│   ├── agent_gatekeeper.py
│   ├── quality_reviewer.py
│   ├── verify_coordinates.py
│   └── progress_tracker.py
├── PROTOCOL.md
├── AGENTS.md
└── TASK_MATRIX.md
```

---

## 8. 擴展指南

### 8.1 適配新文本類型

#### 步驟 1: 定義文本特性
```yaml
text_type: "technical_manual"
structure:
  - chapters
  - sections
  - code_snippets
  - diagrams
language: "en"
special_requirements:
  - preserve_code_formatting
  - extract_api_references
```

#### 步驟 2: 創建專用 Skill
```markdown
# technical-manual-extraction Skill

## 輸入要求
- 技術文檔頁面
- 包含程式碼區塊

## 輸出格式
```yaml
---
source_page: "page_010.txt"
local_start: 0
local_length: 500
content_type: "code_snippet"
language: "python"
---
```

#### 步驟 3: 更新 TASK_MATRIX
新增任務類型:
- T10: 程式碼提取
- T11: API 文檔生成

#### 步驟 4: 訓練 Agent
提供範例讓 Gatekeeper 評估各 Agent 能力

---

### 8.2 新增 Agent

#### 步驟 1: 註冊 Agent
在 `AGENTS.md` 新增:
```markdown
### NewAgent-1.0
- **類型**: 雲端
- **Token 限制**: 100K/day
- **優勢**: 擅長技術文檔
- **弱點**: 古文理解弱
```

#### 步驟 2: 能力評估
在 `TASK_MATRIX.md` 新增評分:
```
| NewAgent-1.0 | T1:⭐⭐⭐ | T2:⭐⭐⭐⭐ | ... |
```

#### 步驟 3: 整合 Gatekeeper
更新 `agent_gatekeeper.py`:
```python
AGENT_SCORES['NewAgent-1.0'] = {
    'T1': 3, 'T2': 4, ...
}
```

---

## 9. 成功指標

### 9.1 系統層面
- ✅ 處理速度: > 100 頁/小時
- ✅ 成本效益: 節省 > 70%
- ✅ 可用性: 系統正常運行 > 95%

### 9.2 品質層面
- ✅ 平均分數: > 4.0/5.0
- ✅ 座標準確率: > 98%
- ✅ 人工修正率: < 10%

### 9.3 維護層面
- ✅ 文檔完整性: 100%
- ✅ 程式碼覆蓋率: > 80%
- ✅ 更新週期: 每月檢視

---

## 10. 附錄

### 10.1 術語表

| 術語 | 定義 |
|------|------|
| 座標 | 文本的物理位置 (頁碼+起始+長度) |
| L0/L1/L2 | 三層資料架構 |
| Skill | 標準化工作流程指示 |
| Gatekeeper | 前置檢查機制 |
| Quality Reviewer | 後置驗證機制 |

### 10.2 參考資料
- [PROTOCOL.md](../original/PROTOCOL.md)
- [AGENTS.md](../original/AGENTS.md)
- [TASK_MATRIX.md](../original/TASK_MATRIX.md)

---

**規格維護者**: User  
**審核者**: To be assigned  
**批准者**: To be assigned
