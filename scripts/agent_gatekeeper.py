#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 守門員 (Agent Gatekeeper)
確保 AI Agent 只執行它能勝任的任務
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class AgentGatekeeper:
    """Agent 守門員 - 強制執行任務能力限制"""
    
    # 任務類型定義
    TASKS = {
        'T1': '座標式卦例提取',
        'T2': '古文結構理解',
        'T3': '術語定義提取',
        'T4': '白話文翻譯',
        'T5': '結構化輸出',
        'T6': '文字品質與表達',
        'T7': '大批次處理',
        'T8': '理論段落摘要',
        'T9': '交叉驗證'
    }
    
    # Agent 能力評分 (從 TASK_MATRIX.md 提取)
    AGENT_SCORES = {
        'Claude-Sonnet-4.5': {
            'T1': 5, 'T2': 5, 'T3': 5, 'T4': 5, 'T5': 5,
            'T6': 5, 'T7': 3, 'T8': 5, 'T9': 5,
            'overall': 9.5
        },
        'Claude-Sonnet-4.5-Thinking': {
            'T1': 5, 'T2': 5, 'T3': 5, 'T4': 5, 'T5': 5,
            'T6': 5, 'T7': 2, 'T8': 5, 'T9': 5,
            'overall': 9.5
        },
        'Claude-Opus-4.5-Thinking': {
            'T1': 5, 'T2': 5, 'T3': 5, 'T4': 5, 'T5': 5,
            'T6': 5, 'T7': 2, 'T8': 5, 'T9': 5,
            'overall': 9.5
        },
        'DeepSeek-R1-32B-Local': {
            'T1': 5, 'T2': 5, 'T3': 5, 'T4': 4, 'T5': 5,
            'T6': 4, 'T7': 5, 'T8': 5, 'T9': 5,
            'overall': 9.0
        },
        'DeepSeek-V3': {
            'T1': 4, 'T2': 4, 'T3': 4, 'T4': 4, 'T5': 5,
            'T6': 4, 'T7': 5, 'T8': 4, 'T9': 4,
            'overall': 8.0
        },
        'DeepSeek-R1-14B-Local': {
            'T1': 4, 'T2': 4, 'T3': 4, 'T4': 3, 'T5': 4,
            'T6': 3, 'T7': 5, 'T8': 4, 'T9': 4,
            'overall': 7.5
        },
        'GPT-4-Turbo': {
            'T1': 4, 'T2': 4, 'T3': 4, 'T4': 4, 'T5': 5,
            'T6': 4, 'T7': 4, 'T8': 4, 'T9': 5,
            'overall': 8.0
        },
        'Gemini-3-Pro-High': {
            'T1': 3, 'T2': 4, 'T3': 3, 'T4': 4, 'T5': 4,
            'T6': 3, 'T7': 5, 'T8': 4, 'T9': 4,
            'overall': 7.0
        },
        'Gemini-3-Flash': {
            'T1': 3, 'T2': 3, 'T3': 3, 'T4': 3, 'T5': 4,
            'T6': 3, 'T7': 5, 'T8': 3, 'T9': 3,
            'overall': 6.0
        },
        'DeepSeek-R1-Latest': {
            'T1': 3, 'T2': 3, 'T3': 3, 'T4': 2, 'T5': 4,
            'T6': 2, 'T7': 5, 'T8': 3, 'T9': 3,
            'overall': 5.5
        }
    }
    
    # 禁止組合 (Agent + 任務)
    FORBIDDEN = {
        'DeepSeek-R1-Latest': ['T4'],  # 禁止翻譯
        'Gemini-3-Flash': ['T3'],      # 禁止術語定義
        'DeepSeek-R1-14B-Local': [],   # 無絕對禁止,但需警告
    }
    
    # 最低品質門檻
    MIN_SCORE = {
        'T1': 4,  # 提取至少需要 4 星
        'T2': 4,  # 理解至少需要 4 星
        'T3': 4,  # 術語至少需要 4 星
        'T4': 4,  # 翻譯至少需要 4 星
        'T5': 4,  # 結構化至少需要 4 星
        'T6': 3,  # 表達至少需要 3 星
        'T7': 3,  # 批次處理至少需要 3 星
        'T8': 4,  # 摘要至少需要 4 星
        'T9': 4,  # 驗證至少需要 4 星
    }
    
    def __init__(self):
        """初始化守門員"""
        self.log_file = Path("original/.gatekeeper_log.json")
        self.violations = []
    
    def can_execute(self, agent_id: str, task_type: str) -> Tuple[bool, str]:
        """
        檢查 Agent 是否可執行任務
        
        Returns:
            (can_execute: bool, reason: str)
        """
        # 檢查 Agent 是否存在
        if agent_id not in self.AGENT_SCORES:
            return False, f"❌ 未知的 Agent: {agent_id}"
        
        # 檢查任務類型是否有效
        if task_type not in self.TASKS:
            return False, f"❌ 未知的任務類型: {task_type}"
        
        # 檢查是否在禁止列表中
        if agent_id in self.FORBIDDEN and task_type in self.FORBIDDEN[agent_id]:
            reason = f"❌ 絕對禁止: {agent_id} 不可執行 {self.TASKS[task_type]}"
            self.log_violation(agent_id, task_type, reason)
            return False, reason
        
        # 檢查能力評分
        score = self.AGENT_SCORES[agent_id].get(task_type, 0)
        min_required = self.MIN_SCORE.get(task_type, 3)
        
        if score < min_required:
            reason = f"⚠️ 能力不足: {agent_id} 在 {self.TASKS[task_type]} 的評分為 {score}/5, 最低要求 {min_required}/5"
            self.log_violation(agent_id, task_type, reason)
            return False, reason
        
        # 警告低分情況
        if score == 3:
            reason = f"⚠️ 需謹慎: {agent_id} 在 {self.TASKS[task_type]} 的評分僅 3/5, 建議仔細檢查輸出"
            return True, reason
        
        return True, f"✅ 允許: {agent_id} 可執行 {self.TASKS[task_type]} (評分: {score}/5)"
    
    def get_best_agent(
        self, 
        task_type: str, 
        prefer_local: bool = True,
        max_cost: str = 'high'
    ) -> str:
        """
        為任務選擇最佳 Agent
        
        Args:
            task_type: 任務類型 (T1-T9)
            prefer_local: 優先選擇本地模型
            max_cost: 最高成本 ('low', 'medium', 'high')
        
        Returns:
            最佳 Agent ID
        """
        # 過濾可用 Agent
        candidates = []
        for agent_id, scores in self.AGENT_SCORES.items():
            can_do, _ = self.can_execute(agent_id, task_type)
            if can_do:
                candidates.append((agent_id, scores[task_type]))
        
        if not candidates:
            raise ValueError(f"沒有 Agent 可執行任務: {self.TASKS[task_type]}")
        
        # 根據成本限制過濾
        if max_cost == 'low':
            # 只選本地模型
            candidates = [(a, s) for a, s in candidates if 'Local' in a]
        elif max_cost == 'medium':
            # 排除最貴的 Opus 和 Thinking
            candidates = [(a, s) for a, s in candidates if 'Opus' not in a and 'Thinking' not in a]
        
        # 優先本地模型
        if prefer_local:
            local_candidates = [(a, s) for a, s in candidates if 'Local' in a]
            if local_candidates:
                candidates = local_candidates
        
        # 選擇評分最高的
        best_agent = max(candidates, key=lambda x: x[1])
        return best_agent[0]
    
    def log_violation(self, agent_id: str, task_type: str, reason: str):
        """記錄違規嘗試"""
        violation = {
            'timestamp': datetime.now().isoformat(),
            'agent': agent_id,
            'task': task_type,
            'reason': reason
        }
        self.violations.append(violation)
        
        # 寫入日誌
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(violation)
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    
    def get_task_recommendations(self, task_type: str) -> Dict:
        """獲取任務的 Agent 推薦"""
        recommendations = {
            'excellent': [],    # 5 星
            'good': [],         # 4 星
            'acceptable': [],   # 3 星
            'not_recommended': [] # < 3 星
        }
        
        for agent_id, scores in self.AGENT_SCORES.items():
            score = scores.get(task_type, 0)
            
            if score == 5:
                recommendations['excellent'].append(agent_id)
            elif score == 4:
                recommendations['good'].append(agent_id)
            elif score == 3:
                recommendations['acceptable'].append(agent_id)
            else:
                recommendations['not_recommended'].append(agent_id)
        
        return recommendations
    
    def generate_report(self) -> str:
        """生成守門員報告"""
        report = []
        report.append("=" * 60)
        report.append("Agent 守門員報告")
        report.append("=" * 60)
        report.append("")
        
        if not self.violations:
            report.append("✅ 無違規記錄")
        else:
            report.append(f"⚠️ 發現 {len(self.violations)} 次違規嘗試:")
            report.append("")
            for v in self.violations:
                report.append(f"時間: {v['timestamp']}")
                report.append(f"Agent: {v['agent']}")
                report.append(f"任務: {v['task']}")
                report.append(f"原因: {v['reason']}")
                report.append("-" * 60)
        
        return "\n".join(report)


def main():
    """測試守門員"""
    import sys
    
    gatekeeper = AgentGatekeeper()
    
    print("[守門員] Agent Gatekeeper 測試")
    print("=" * 60)
    
    # 測試案例
    test_cases = [
        ("Claude-Sonnet-4.5", "T4", "[OK] 應該允許"),
        ("DeepSeek-R1-Latest", "T4", "[X] 應該禁止 (翻譯品質差)"),
        ("DeepSeek-R1-32B-Local", "T4", "[OK] 應該允許"),
        ("Gemini-3-Flash", "T3", "[X] 應該禁止 (術語理解淺)"),
    ]
    
    for agent, task, expected in test_cases:
        can_do, reason = gatekeeper.can_execute(agent, task)
        status = "[OK]" if can_do else "[X]"
        print(f"\n{expected}")
        print(f"{status} {agent} -> {gatekeeper.TASKS[task]}")
        print(f"   {reason}")
    
    print("\n" + "=" * 60)
    print("\n[推薦] 為「白話文翻譯」選擇最佳 Agent:")
    
    # 測試 Agent 選擇
    print("\n1. 成本優先 (prefer_local=True):")
    best = gatekeeper.get_best_agent('T4', prefer_local=True)
    print(f"   推薦: {best}")
    
    print("\n2. 品質優先 (prefer_local=False):")
    best = gatekeeper.get_best_agent('T4', prefer_local=False)
    print(f"   推薦: {best}")
    
    print("\n3. 低成本限制 (max_cost='low'):")
    best = gatekeeper.get_best_agent('T4', max_cost='low')
    print(f"   推薦: {best}")
    
    # 生成報告
    print("\n" + "=" * 60)
    print(gatekeeper.generate_report())


if __name__ == "__main__":
    main()
