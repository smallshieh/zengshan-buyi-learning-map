---
name: 古文卦例提取 (Ancient Text Case Extraction)
description: 從《增刪卜易》分頁中提取卦例,並標註精確座標
version: 1.0
---

# 古文卦例提取 Skill

## 📋 目標

從古文分頁中提取完整的卦例內容,並生成符合座標系統的結構化輸出。

---

## 🎯 輸入要求

- **分頁檔案**: `pages/page_XXX.txt`
- **Manifest**: `original/manifest.json` (用於座標驗證)

---

## 📤 輸出格式

每個提取的卦例必須嚴格遵守以下 YAML Frontmatter 格式:

```markdown
---
source_page: "page_005.txt"
local_start: 120          # 該段落在本頁的起始字數
local_length: 450         # 該段落總字數
agent: "{YOUR_AGENT_ID}"  # 例如: Claude-3.5, DeepSeek-R1-32B-Local
extraction_type: "case"
case_number: "057"        # 卦例編號 (如果能識別)
verified: false           # 初次提取設為 false
---

# 卦例內容

[提取的完整卦例文本]

## 元數據

- **時間**: 申月 癸巳日
- **問事**: 父外任平安
- **卦象**: 姤之恒
- **結果**: ...
```

---

## 🔍 提取步驟

### Step 1: 讀取分頁

```python
# 讀取分頁內容
with open(f"pages/{page_file}", 'r', encoding='utf-8') as f:
    content = f.read()
```

### Step 2: 識別卦例邊界

**卦例開始標誌**:
- 包含「占」字的標題 (如「占父近病」)
- 時間標記 (如「申月 癸巳日」)
- 卦象名稱 (如「姤之恒」)

**卦例結束標誌**:
- 結果描述結束
- 下一個卦例開始
- 段落明顯分隔

### Step 3: 計算座標

```python
# 計算起始位置
local_start = content.find(case_start_text)

# 計算長度
local_length = len(extracted_case)

# 驗證座標
assert 0 <= local_start < len(content)
assert local_length > 0
```

### Step 4: 提取元數據

從卦例中提取:
- 時間 (月份、日期)
- 問事 (占卜主題)
- 卦象 (原卦、變卦)
- 結果 (驗證結果)

### Step 5: 生成輸出

按照輸出格式生成 Markdown 檔案。

---

## ✅ 品質檢查清單

在輸出前,確認:

- [ ] YAML Frontmatter 格式正確
- [ ] `local_start` 和 `local_length` 已計算
- [ ] `agent` 欄位已填寫
- [ ] 卦例內容完整 (有開頭和結尾)
- [ ] 元數據已提取 (時間、問事、卦象、結果)
- [ ] 無多餘的空白或格式錯誤

---

## ⚠️ 常見錯誤

### 錯誤 1: 座標計算錯誤

```yaml
# ❌ 錯誤: local_start 超出範圍
local_start: 999999

# ✅ 正確: 在有效範圍內
local_start: 1205
```

### 錯誤 2: 卦例不完整

```markdown
# ❌ 錯誤: 只提取了開頭
占父近病

# ✅ 正確: 提取完整內容
占父近病
- 時間: ...
- 卦象: ...
- 結果: ...
```

### 錯誤 3: YAML 格式錯誤

```yaml
# ❌ 錯誤: 缺少引號
source_page: page_005.txt

# ✅ 正確: 字串需要引號
source_page: "page_005.txt"
```

---

## 🔧 使用範例

### 範例 1: Claude 使用此 Skill

```markdown
你已裝載「古文卦例提取」skill。

請處理 pages/page_005.txt,提取所有卦例。

記住:
- 嚴格遵守 YAML Frontmatter 格式
- 精確計算座標
- 完整提取卦例內容
```

### 範例 2: 本地 Ollama 使用

```python
import requests

skill_prompt = open('.agent/skills/ancient-text-extraction/SKILL.md').read()
page_content = open('pages/page_005.txt').read()

prompt = f"""
{skill_prompt}

請處理以下內容:
{page_content}

agent: "DeepSeek-R1-32B-Local"
"""

response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "huihui_ai/deepseek-r1-abliterated:32b", "prompt": prompt}
)
```

---

## 📊 驗證腳本

```python
def verify_extraction(output_file):
    \"\"\"驗證提取結果\"\"\"
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查 YAML
    if not content.startswith('---'):
        return False, "Missing YAML frontmatter"
    
    # 解析 YAML
    import yaml
    parts = content.split('---')
    if len(parts) < 3:
        return False, "Invalid YAML structure"
    
    metadata = yaml.safe_load(parts[1])
    
    # 驗證必要欄位
    required = ['source_page', 'local_start', 'local_length', 'agent']
    for field in required:
        if field not in metadata:
            return False, f"Missing field: {field}"
    
    # 驗證座標
    if metadata['local_start'] < 0:
        return False, "Invalid local_start"
    
    if metadata['local_length'] <= 0:
        return False, "Invalid local_length"
    
    return True, "All checks passed"
```

---

## 🎓 最佳實踐

1. **一次處理一個卦例**: 不要試圖一次提取整頁的所有卦例
2. **保留原文格式**: 不要修改標點或斷句
3. **標註不確定**: 如果無法確定邊界,使用 `verified: false`
4. **記錄困難**: 遇到難以提取的內容,在備註中說明

---

**維護者**: User  
**最後更新**: 2026-02-04
