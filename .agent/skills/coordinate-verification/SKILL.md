---
name: 座標驗證 (Coordinate Verification)
description: 驗證提取內容的座標正確性和完整性
version: 1.0
---

# 座標驗證 Skill

## 📋 目標

驗證 Agent 提取的內容是否符合座標系統規範,確保:
- YAML Frontmatter 格式正確
- 座標計算準確
- 無重疊或遺漏

---

## 🔍 驗證項目

### 1. YAML 格式檢查

```yaml
# 必須包含的欄位
source_page: "page_XXX.txt"    # 來源分頁
local_start: <整數>             # 起始位置
local_length: <整數>            # 長度
agent: "<Agent ID>"            # Agent 識別碼
extraction_type: "case|theory|glossary"  # 類型
```

### 2. 座標範圍檢查

```python
# 驗證座標在有效範圍內
assert 0 <= local_start < page_length
assert local_length > 0
assert local_start + local_length <= page_length
```

### 3. 重疊檢查

```python
# 檢查是否與其他提取重疊
for other in extractions:
    start1, end1 = local_start, local_start + local_length
    start2, end2 = other.start, other.start + other.length
    
    # 不應該重疊
    assert not (start1 < end2 and start2 < end1)
```

### 4. 覆蓋率檢查

```python
# 計算總覆蓋率
total_chars = sum(e.length for e in extractions)
coverage = total_chars / page_length * 100
print(f"覆蓋率: {coverage:.1f}%")
```

---

## 🔧 驗證腳本

見 `scripts/verify_coordinates.py`

---

## ✅ 通過標準

- [ ] 所有欄位都存在
- [ ] 座標在有效範圍內
- [ ] 無重疊
- [ ] 覆蓋率 > 80%
- [ ] 原文內容匹配

---

**最後更新**: 2026-02-04
