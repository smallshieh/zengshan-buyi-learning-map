#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品質審查員 (Quality Reviewer)
抽檢 Agent 產出並進行量化評分
"""
import json
import random
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import yaml


class QualityReviewer:
    """品質審查員 - 量化評分 Agent 產出"""
    
    # 評分項目 (1-5 分)
    CRITERIA = {
        'coordinate_accuracy': {
            'name': '座標準確度',
            'weight': 0.25,
            'description': 'local_start 和 local_length 是否正確'
        },
        'yaml_format': {
            'name': 'YAML 格式',
            'weight': 0.15,
            'description': 'Frontmatter 格式是否標準'
        },
        'content_completeness': {
            'name': '內容完整性',
            'weight': 0.25,
            'description': '是否提取完整,無遺漏'
        },
        'text_quality': {
            'name': '文字品質',
            'weight': 0.20,
            'description': '中文表達是否流暢準確'
        },
        'extraction_precision': {
            'name': '提取精確度',
            'weight': 0.15,
            'description': '邊界識別是否準確'
        }
    }
    
    def __init__(self, performance_file: str = "original/.agent_performance.json"):
        """初始化審查員"""
        self.performance_file = Path(performance_file)
        self.performance_data = self._load_performance()
    
    def _load_performance(self) -> Dict:
        """載入歷史績效資料"""
        if self.performance_file.exists():
            with open(self.performance_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                'agents': {},  # Agent 績效記錄
                'reviews': []  # 所有評分記錄
            }
    
    def _save_performance(self):
        """儲存績效資料"""
        with open(self.performance_file, 'w', encoding='utf-8') as f:
            json.dump(self.performance_data, f, ensure_ascii=False, indent=2)
    
    def sample_files(
        self, 
        directory: str, 
        sample_rate: float = 0.2,
        min_samples: int = 5,
        max_samples: int = 20
    ) -> List[Path]:
        """
        隨機抽樣檔案進行審查
        
        Args:
            directory: 要抽樣的目錄
            sample_rate: 抽樣比例 (0.0-1.0)
            min_samples: 最少抽樣數
            max_samples: 最多抽樣數
        
        Returns:
            抽樣的檔案列表
        """
        all_files = list(Path(directory).glob('*.md'))
        
        if not all_files:
            return []
        
        # 計算抽樣數
        sample_size = max(
            min_samples,
            min(max_samples, int(len(all_files) * sample_rate))
        )
        
        # 隨機抽樣
        if len(all_files) <= sample_size:
            return all_files
        else:
            return random.sample(all_files, sample_size)
    
    def review_file(self, file_path: Path) -> Dict:
        """
        審查單個檔案
        
        Returns:
            評分結果字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析 YAML
            if not content.startswith('---'):
                return {
                    'error': 'Missing YAML frontmatter',
                    'scores': {},
                    'total_score': 0
                }
            
            parts = content.split('---')
            if len(parts) < 3:
                return {
                    'error': 'Invalid YAML structure',
                    'scores': {},
                    'total_score': 0
                }
            
            metadata = yaml.safe_load(parts[1])
            agent_id = metadata.get('agent', 'Unknown')
            
            # 初始化評分
            scores = {}
            
            # 自動評分項目
            scores['yaml_format'] = self._score_yaml_format(metadata)
            scores['coordinate_accuracy'] = self._score_coordinates(
                metadata, 
                file_path.parent
            )
            
            # 需要人工評分的項目 (預設 0,需要手動輸入)
            scores['content_completeness'] = 0
            scores['text_quality'] = 0
            scores['extraction_precision'] = 0
            
            return {
                'file': str(file_path),
                'agent': agent_id,
                'scores': scores,
                'total_score': 0,  # 待人工評分完成後計算
                'auto_scored': True,
                'needs_manual_review': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'scores': {},
                'total_score': 0
            }
    
    def _score_yaml_format(self, metadata: Dict) -> int:
        """評分 YAML 格式 (1-5)"""
        score = 5
        
        # 檢查必要欄位
        required = ['source_page', 'local_start', 'local_length', 'agent']
        for field in required:
            if field not in metadata:
                score -= 1
        
        # 檢查時間戳記
        if 'extracted_at' not in metadata:
            score -= 1
        
        return max(1, score)
    
    def _score_coordinates(self, metadata: Dict, directory: Path) -> int:
        """評分座標準確度 (1-5)"""
        try:
            local_start = metadata.get('local_start')
            local_length = metadata.get('local_length')
            
            if local_start is None or local_length is None:
                return 1
            
            # 基本驗證
            if local_start < 0 or local_length <= 0:
                return 1
            
            # 如果有 manifest 可做進一步驗證
            # 暫時給 4 分 (需要更詳細的驗證)
            return 4
            
        except:
            return 1
    
    def interactive_review(self, review_result: Dict) -> Dict:
        """
        互動式人工評分
        
        Args:
            review_result: review_file() 返回的結果
        
        Returns:
            完整評分結果
        """
        print("\n" + "=" * 60)
        print(f"審查檔案: {review_result['file']}")
        print(f"Agent: {review_result['agent']}")
        print("=" * 60)
        
        scores = review_result['scores']
        
        print("\n自動評分結果:")
        print(f"  YAML 格式: {scores['yaml_format']}/5")
        print(f"  座標準確度: {scores['coordinate_accuracy']}/5")
        
        print("\n請進行人工評分 (1-5):")
        
        # 內容完整性
        while True:
            try:
                score = int(input("  內容完整性 (1-5): "))
                if 1 <= score <= 5:
                    scores['content_completeness'] = score
                    break
            except:
                pass
            print("    請輸入 1-5 的整數")
        
        # 文字品質
        while True:
            try:
                score = int(input("  文字品質 (1-5): "))
                if 1 <= score <= 5:
                    scores['text_quality'] = score
                    break
            except:
                pass
            print("    請輸入 1-5 的整數")
        
        # 提取精確度
        while True:
            try:
                score = int(input("  提取精確度 (1-5): "))
                if 1 <= score <= 5:
                    scores['extraction_precision'] = score
                    break
            except:
                pass
            print("    請輸入 1-5 的整數")
        
        # 計算加權總分
        total = 0
        for criterion, weight_info in self.CRITERIA.items():
            total += scores[criterion] * weight_info['weight']
        
        review_result['total_score'] = round(total, 2)
        review_result['needs_manual_review'] = False
        
        print(f"\n總分 (加權): {review_result['total_score']}/5.0")
        
        return review_result
    
    def batch_review(
        self, 
        directory: str, 
        sample_rate: float = 0.2,
        interactive: bool = True
    ) -> List[Dict]:
        """
        批次審查
        
        Args:
            directory: 要審查的目錄
            sample_rate: 抽樣比例
            interactive: 是否進行互動式評分
        
        Returns:
            所有評分結果
        """
        samples = self.sample_files(directory, sample_rate)
        
        print(f"\n[品質審查] 共 {len(list(Path(directory).glob('*.md')))} 個檔案")
        print(f"[品質審查] 抽樣 {len(samples)} 個進行審查 ({sample_rate*100}%)")
        
        results = []
        
        for i, file_path in enumerate(samples, 1):
            print(f"\n進度: {i}/{len(samples)}")
            
            review = self.review_file(file_path)
            
            if interactive and review.get('needs_manual_review'):
                review = self.interactive_review(review)
            
            results.append(review)
            
            # 記錄到績效資料
            self._record_review(review)
        
        # 儲存績效
        self._save_performance()
        
        return results
    
    def _record_review(self, review: Dict):
        """記錄評分到績效資料"""
        agent_id = review.get('agent', 'Unknown')
        
        # 初始化 Agent 記錄
        if agent_id not in self.performance_data['agents']:
            self.performance_data['agents'][agent_id] = {
                'total_reviews': 0,
                'average_score': 0.0,
                'scores_history': [],
                'criteria_averages': {}
            }
        
        agent_data = self.performance_data['agents'][agent_id]
        
        # 更新統計
        if not review.get('error') and review['total_score'] > 0:
            agent_data['total_reviews'] += 1
            agent_data['scores_history'].append(review['total_score'])
            
            # 計算平均分
            agent_data['average_score'] = round(
                sum(agent_data['scores_history']) / len(agent_data['scores_history']),
                2
            )
            
            # 更新各項指標平均
            for criterion in self.CRITERIA:
                if criterion not in agent_data['criteria_averages']:
                    agent_data['criteria_averages'][criterion] = []
                
                agent_data['criteria_averages'][criterion].append(
                    review['scores'].get(criterion, 0)
                )
        
        # 記錄到總列表
        review_record = {
            'timestamp': datetime.now().isoformat(),
            'agent': agent_id,
            'file': review['file'],
            'total_score': review['total_score'],
            'scores': review['scores']
        }
        self.performance_data['reviews'].append(review_record)
    
    def get_agent_performance(self, agent_id: str) -> Dict:
        """獲取 Agent 績效摘要"""
        if agent_id not in self.performance_data['agents']:
            return {
                'error': f'No performance data for {agent_id}'
            }
        
        data = self.performance_data['agents'][agent_id]
        
        # 計算各項指標平均
        criteria_avg = {}
        for criterion, scores in data['criteria_averages'].items():
            if scores:
                criteria_avg[criterion] = round(sum(scores) / len(scores), 2)
        
        return {
            'agent': agent_id,
            'total_reviews': data['total_reviews'],
            'average_score': data['average_score'],
            'criteria_averages': criteria_avg,
            'trend': self._calculate_trend(data['scores_history'])
        }
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """計算分數趨勢"""
        if len(scores) < 3:
            return 'insufficient_data'
        
        # 比較最近 3 次和之前的平均
        recent = sum(scores[-3:]) / 3
        previous = sum(scores[:-3]) / len(scores[:-3]) if len(scores) > 3 else recent
        
        if recent > previous + 0.3:
            return 'improving'
        elif recent < previous - 0.3:
            return 'declining'
        else:
            return 'stable'
    
    def generate_report(self) -> str:
        """生成績效報告"""
        report = []
        report.append("=" * 60)
        report.append("Agent 績效報告")
        report.append("=" * 60)
        report.append("")
        
        if not self.performance_data['agents']:
            report.append("尚無績效資料")
            return "\n".join(report)
        
        # 按平均分排序
        agents = sorted(
            self.performance_data['agents'].items(),
            key=lambda x: x[1]['average_score'],
            reverse=True
        )
        
        for agent_id, data in agents:
            perf = self.get_agent_performance(agent_id)
            
            report.append(f"\n{agent_id}")
            report.append("-" * 40)
            report.append(f"審查次數: {perf['total_reviews']}")
            report.append(f"平均分數: {perf['average_score']}/5.0")
            report.append(f"趨勢: {perf['trend']}")
            report.append("\n各項指標:")
            
            for criterion, avg in perf['criteria_averages'].items():
                name = self.CRITERIA[criterion]['name']
                report.append(f"  {name}: {avg}/5.0")
        
        return "\n".join(report)


def main():
    """測試品質審查系統"""
    reviewer = QualityReviewer()
    
    print("[品質審查系統] 測試模式")
    print("\n功能:")
    print("1. 隨機抽樣檔案")
    print("2. 自動評分 (YAML, 座標)")
    print("3. 互動式人工評分")
    print("4. 記錄 Agent 績效")
    print("5. 生成績效報告")
    
    # 範例:審查 inbox 目錄
    # results = reviewer.batch_review('original/inbox/', sample_rate=0.2)
    
    # 生成報告
    print("\n" + reviewer.generate_report())


if __name__ == "__main__":
    main()
