# 核心管理工具使用指南

## 已創建的工具

### 1. obsidian_folders.py - 資料夾管理工具

#### 功能
- 合併資料夾
- 重命名資料夾
- 分析資料夾結構

#### 使用範例

**合併資料夾**:
```bash
# 預覽
python scripts\obsidian_folders.py merge --source "風水" --target "陰宅" --dry-run

# 執行
python scripts\obsidian_folders.py merge --source "風水" --target "陰宅"
```

**重命名資料夾**:
```bash
python scripts\obsidian_folders.py rename --old "占求財" --new "求財"
```

**分析結構**:
```bash
python scripts\obsidian_folders.py analyze --output "folder_report.md"
```

---

### 2. glossary_manager.py - 術語管理工具

#### 功能
- 檢查缺失術語
- 批次創建術語
- 建立術語索引

#### 使用範例

**檢查缺失術語**:
```bash
python scripts\glossary_manager.py check-missing
```

**創建單個術語**(支持模板):
```bash
# 使用基本模板
python scripts\glossary_manager.py create "五行生克"

# 使用爻的模板
python scripts\glossary_manager.py create "兄弟爻" --template yao

# 使用狀態模板
python scripts\glossary_manager.py create "旬空" --template state
```

**批次創建缺失術語**:
```bash
# 預覽
python scripts\glossary_manager.py batch-create --dry-run

# 執行
python scripts\glossary_manager.py batch-create
```

**建立術語索引**:
```bash
python scripts\glossary_manager.py build-index
```

---

## 配置文件

### config/folder_mappings.yaml
- 記錄所有資料夾合併歷史
- 記錄重命名操作
- 定義八大類分類

### config/glossary_templates.yaml
- 定義術語模板
- 支持 basic, yao, state, relation 四種模板

---

## 當前發現

### 術語缺失情況
- 引用的術語: 166個
- 已存在術語: 60個
- **缺失術語: 108個**

主要缺失類別:
- 六親相關: 兄弟爻、妻財爻、子孫爻、官鬼爻、父母爻
- 狀態相關: 旬空、月破、日破、化空、化墓
- 關係相關: 三合局、六合、六沖、三刑
- 六神相關: 青龍、朱雀、勾陳、騰蛇、白虎、玄武

---

## 建議工作流

### 日常維護
1. 定期檢查缺失術語
2. 使用模板批次創建
3. 維護術語索引

### 資料夾調整
1. 先用 analyze 分析結構
2. 用 dry-run 預覽操作
3. 執行實際操作
4. 配置文件自動記錄歷史

---

## Token 節省效果

**之前**: 每次操作都創建新腳本 → 大量重複代碼  
**現在**: 統一工具 + 配置文件 → 極簡調用

**預估節省**: ~60-70% token

---

### 3. guali_stats.py - 卦例統計分析工具

#### 功能
- 按用神分類統計
- 生成卦例分布報告
- 驗證分類正確性

#### 使用範例

**按用神統計**:
```bash
python scripts\guali_stats.py --by-yongshen
```

**分布分析**:
```bash
python scripts\guali_stats.py --distribution
```

**驗證分類**:
```bash
python scripts\guali_stats.py --validate-classification
```

**執行所有分析**:
```bash
python scripts\guali_stats.py --all
```

---

### 4. case_validator.py - 卦例驗證工具

#### 功能
- 檢查卦例格式
- 驗證必要欄位
- 檢查連結有效性

#### 使用範例

**檢查格式**:
```bash
python scripts\case_validator.py --check-format
```

**檢查欄位**:
```bash
python scripts\case_validator.py --check-fields
```

**檢查連結**:
```bash
python scripts\case_validator.py --check-links
```

**執行所有檢查**:
```bash
python scripts\case_validator.py --all
```

---

## 工具總覽

| 工具 | 功能 | 用途 |
|------|------|------|
| obsidian_folders.py | 資料夾管理 | 合併、重命名、分析 |
| glossary_manager.py | 術語管理 | 檢查、創建、索引 |
| guali_stats.py | 統計分析 | 用神分類、分布報告 |
| case_validator.py | 驗證工具 | 格式、欄位、連結檢查 |

---

## Token 節省效果

**之前**: 每次操作都創建新腳本 → 大量重複代碼  
**現在**: 統一工具 + 配置文件 → 極簡調用

**預估節省**: ~60-70% token
