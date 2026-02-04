# Agent 品質追蹤系統使用指南

**版本**: 1.0  
**最後更新**: 2026-02-04

---

## 📊 系統概述

品質追蹤系統用於:
1. **抽檢 Agent 產出** - 隨機抽樣進行品質檢查
2. **量化評分** - 5 個維度的評分 (1-5分)
3. **績效記錄** - 累積各 Agent 的歷史表現
4. **優化分派** - 根據實際表現調整任務分配

---

## 🎯 評分標準

### 5 個評分維度

| 維度 | 權重 | 說明 | 評分方式 |
|------|------|------|---------|
| **座標準確度** | 25% | local_start/length 是否正確 | 自動評分 |
| **YAML 格式** | 15% | Frontmatter 是否標準 | 自動評分 |
| **內容完整性** | 25% | 是否提取完整,無遺漏 | 人工評分 |
| **文字品質** | 20% | 中文表達是否流暢準確 | 人工評分 |
| **提取精確度** | 15% | 邊界識別是否準確 | 人工評分 |

**總分計算**: 加權平均 (最高 5.0 分)

---

## 🔧 使用方法

### 1. 批次審查

```python
from scripts.quality_reviewer import QualityReviewer

reviewer = QualityReviewer()

# 審查 inbox 目錄,抽樣 20%
results = reviewer.batch_review(
    directory='original/inbox/',
    sample_rate=0.2,
    interactive=True  # 互動式人工評分
)
```

### 2. 查看 Agent 績效

```python
# 獲取特定 Agent 的績效
performance = reviewer.get_agent_performance('DeepSeek-R1-32B-Local')

print(f"平均分數: {performance['average_score']}/5.0")
print(f"趨勢: {performance['trend']}")  # improving/stable/declining
print(f"各項指標: {performance['criteria_averages']}")
```

### 3. 生成績效報告

```python
# 查看所有 Agent 的績效排名
report = reviewer.generate_report()
print(report)
```

輸出範例:
```
============================================================
Agent 績效報告
============================================================

Claude-Sonnet-4.5
----------------------------------------
審查次數: 15
平均分數: 4.75/5.0
趨勢: stable

各項指標:
  座標準確度: 4.8/5.0
  YAML 格式: 5.0/5.0
  內容完整性: 4.7/5.0
  文字品質: 5.0/5.0
  提取精確度: 4.6/5.0

DeepSeek-R1-32B-Local
----------------------------------------
審查次數: 25
平均分數: 4.20/5.0
趨勢: improving

各項指標:
  座標準確度: 4.5/5.0
  YAML 格式: 4.8/5.0
  內容完整性: 4.0/5.0
  文字品質: 3.8/5.0
  提取精確度: 4.2/5.0
```

---

## 📋 工作流程

### 每日品質檢查流程

```bash
# Step 1: Agent 處理完成後
# (假設已產生 original/inbox/*.md 檔案)

# Step 2: 執行抽檢 (抽樣 20%)
python scripts/quality_reviewer.py --batch-review \
  --directory original/inbox/ \
  --sample-rate 0.2

# Step 3: 互動式評分
# 系統會逐個檔案提示評分:
#   內容完整性 (1-5): 4
#   文字品質 (1-5): 5
#   提取精確度 (1-5): 4

# Step 4: 查看報告
python scripts/quality_reviewer.py --report

# Step 5: 根據績效調整任務分配
# 查看 original/.agent_performance.json
```

---

## 📈 績效資料格式

### `original/.agent_performance.json`

```json
{
  "agents": {
    "Claude-Sonnet-4.5": {
      "total_reviews": 15,
      "average_score": 4.75,
      "scores_history": [4.8, 4.7, 4.75, ...],
      "criteria_averages": {
        "coordinate_accuracy": [5, 5, 4, ...],
        "yaml_format": [5, 5, 5, ...],
        "content_completeness": [5, 4, 5, ...],
        "text_quality": [5, 5, 5, ...],
        "extraction_precision": [5, 4, 5, ...]
      }
    }
  },
  "reviews": [
    {
      "timestamp": "2026-02-04T19:00:00+08:00",
      "agent": "Claude-Sonnet-4.5",
      "file": "original/inbox/page_001_Claude.md",
      "total_score": 4.75,
      "scores": {
        "coordinate_accuracy": 5,
        "yaml_format": 5,
        "content_completeness": 5,
        "text_quality": 5,
        "extraction_precision": 4
      }
    }
  ]
}
```

---

## 🎯 決策建議

### 根據績效調整任務分配

#### 情況 1: Agent 表現優異 (平均 ≥ 4.5)
```python
if performance['average_score'] >= 4.5:
    print(f"✅ {agent_id} 表現優異,可增加工作量")
    # 可處理更多複雜任務
```

#### 情況 2: Agent 表現良好 (平均 4.0-4.5)
```python
elif performance['average_score'] >= 4.0:
    print(f"👍 {agent_id} 表現良好,維持現有分配")
    # 繼續當前任務類型
```

#### 情況 3: Agent 表現不佳 (平均 < 4.0)
```python
else:
    print(f"⚠️ {agent_id} 表現需改進")
    
    # 檢查哪個維度最弱
    weak_criteria = min(
        performance['criteria_averages'].items(),
        key=lambda x: x[1]
    )
    
    print(f"   最弱項: {weak_criteria[0]} ({weak_criteria[1]}/5)")
    
    # 建議:
    # - 減少該類型任務
    # - 加強 Skill 指示
    # - 或更換 Agent
```

#### 情況 4: 趨勢下降
```python
if performance['trend'] == 'declining':
    print(f"📉 {agent_id} 表現下降,需要檢查")
    # 可能原因:
    # - Agent 版本更新
    # - 任務難度提升
    # - Skill 指示不明確
```

---

## 🔄 整合守門員系統

```python
from scripts.agent_gatekeeper import AgentGatekeeper
from scripts.quality_reviewer import QualityReviewer

gatekeeper = AgentGatekeeper()
reviewer = QualityReviewer()

def select_agent_with_performance(task_type, prefer_local=True):
    """結合能力和績效選擇 Agent"""
    
    # 1. 守門員篩選可用 Agent
    recommendations = gatekeeper.get_task_recommendations(task_type)
    candidates = recommendations['excellent'] + recommendations['good']
    
    # 2. 根據實際績效排序
    agent_scores = []
    for agent_id in candidates:
        perf = reviewer.get_agent_performance(agent_id)
        if 'error' not in perf:
            agent_scores.append((agent_id, perf['average_score']))
    
    # 3. 選擇績效最佳的
    if agent_scores:
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 優先本地模型
        if prefer_local:
            local_agents = [(a, s) for a, s in agent_scores if 'Local' in a]
            if local_agents:
                return local_agents[0][0]
        
        return agent_scores[0][0]
    
    # 4. 無績效資料,使用守門員推薦
    return gatekeeper.get_best_agent(task_type, prefer_local)

# 使用範例
best_agent = select_agent_with_performance('T4', prefer_local=True)
print(f"推薦 Agent: {best_agent}")
```

---

## 📝 注意事項

1. **抽樣率建議**: 
   - 初期: 30-40% (建立基線)
   - 穩定期: 15-20% (維持監控)
   - 問題期: 50%+ (密集審查)

2. **評分一致性**:
   - 建立評分標準範例
   - 同一人評分維持一致性
   - 定期校準評分標準

3. **績效趨勢**:
   - 至少 5 次評分後才看趨勢
   - 注意環境變化 (Agent 更新、任務難度)

4. **資料隱私**:
   - `.agent_performance.json` 包含敏感資訊
   - 已在 `.gitignore` 中排除

---

**維護者**: User  
**技術支援**: Antigravity AI
