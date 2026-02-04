#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
卦例統計分析工具
分析知識庫中的卦例分布和分類情況
"""

import argparse
import yaml
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

BASE_DIR = Path(r"c:\Users\smallshieh\Obsidian筆記")
CASES_DIR = BASE_DIR / "cases"
CONFIG_DIR = BASE_DIR / "config"

class GualiStats:
    def __init__(self):
        self.cases_dir = CASES_DIR
        self.config_file = CONFIG_DIR / "folder_mappings.yaml"
        self.classifications = self.load_classifications()
    
    def load_classifications(self) -> Dict:
        """載入八大類分類"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('classifications', {})
        return {}
    
    def by_yongshen(self):
        """按用神分類統計"""
        # 用神對照表
        yongshen_map = {
            '天時': '試驗驗證(五行生剋)',
            '終身財福': '世爻',
            '終身功名': '世爻',
            '趨避': '世爻',
            '六親': '六親爻',
            '功名': '官鬼爻+父母爻',
            '求財': '妻財爻+子孫爻',
            '婚姻': '財爻/官爻+子孫爻',
            '出行': '世爻+子孫爻',
            '官訟': '世應+官鬼爻',
            '疾病': '世爻/用神',
            '家宅': '父母爻',
            '陰宅': '父母爻',
            '失物': '雜占',
            '其他': '雜占'
        }
        
        print("\n📊 按用神分類統計")
        print("=" * 70)
        print(f"{'資料夾':<15} {'卦例數':>8} {'用神':>20}")
        print("-" * 70)
        
        stats = {}
        total_cases = 0
        
        for folder in sorted(self.cases_dir.iterdir()):
            if not folder.is_dir():
                continue
            
            case_files = list(folder.glob("case_*.md"))
            count = len(case_files)
            total_cases += count
            
            yongshen = yongshen_map.get(folder.name, '未知')
            stats[folder.name] = {
                'count': count,
                'yongshen': yongshen
            }
            
            print(f"{folder.name:<15} {count:>8} {yongshen:>20}")
        
        print("-" * 70)
        print(f"{'總計':<15} {total_cases:>8}")
        print("=" * 70)
        
        return stats
    
    def distribution(self):
        """生成卦例分布報告"""
        print("\n📈 卦例分布分析")
        print("=" * 60)
        
        # 按八大類分組統計
        category_stats = defaultdict(list)
        for category, folders in self.classifications.items():
            for folder_name in folders:
                folder = self.cases_dir / folder_name
                if folder.exists():
                    count = len(list(folder.glob("case_*.md")))
                    category_stats[category].append({
                        'folder': folder_name,
                        'count': count
                    })
        
        total_by_category = {}
        for category, folders in category_stats.items():
            total = sum(f['count'] for f in folders)
            total_by_category[category] = total
            
            print(f"\n### {category} (共 {total} 個)")
            for folder in sorted(folders, key=lambda x: x['count'], reverse=True):
                print(f"  - {folder['folder']}: {folder['count']} 個")
        
        # 總計
        grand_total = sum(total_by_category.values())
        print(f"\n{'=' * 60}")
        print(f"總計: {grand_total} 個卦例")
        
        # 比例分析
        print(f"\n### 比例分析")
        for category, total in sorted(total_by_category.items(), key=lambda x: x[1], reverse=True):
            percentage = (total / grand_total * 100) if grand_total > 0 else 0
            print(f"{category}: {percentage:.1f}%")
        
        return category_stats
    
    def validate_classification(self):
        """驗證分類是否符合《增刪卜易》"""
        print("\n✅ 分類驗證")
        print("=" * 60)
        
        # 檢查每個資料夾是否在八大類中
        all_classified = set()
        for folders in self.classifications.values():
            all_classified.update(folders)
        
        existing_folders = set()
        for folder in self.cases_dir.iterdir():
            if folder.is_dir():
                existing_folders.add(folder.name)
        
        # 未分類的資料夾
        unclassified = existing_folders - all_classified
        
        if unclassified:
            print(f"\n⚠️  未納入八大類的資料夾:")
            for folder in sorted(unclassified):
                print(f"  - {folder}")
        else:
            print(f"\n✅ 所有資料夾都已納入八大類分類")
        
        # 配置中存在但實際不存在的資料夾
        missing = all_classified - existing_folders
        if missing:
            print(f"\n⚠️  配置中存在但實際不存在的資料夾:")
            for folder in sorted(missing):
                print(f"  - {folder}")
        
        # 八大類檢查
        print(f"\n### 八大類完整性檢查")
        for category, folders in self.classifications.items():
            existing_count = sum(1 for f in folders if (self.cases_dir / f).exists())
            print(f"{category}: {existing_count}/{len(folders)} 個資料夾存在")
        
        return {
            'unclassified': unclassified,
            'missing': missing
        }

def main():
    parser = argparse.ArgumentParser(description='卦例統計分析工具')
    parser.add_argument('--by-yongshen', action='store_true', help='按用神分類統計')
    parser.add_argument('--distribution', action='store_true', help='生成分布報告')
    parser.add_argument('--validate-classification', action='store_true', help='驗證分類')
    parser.add_argument('--all', action='store_true', help='執行所有分析')
    
    args = parser.parse_args()
    
    stats = GualiStats()
    
    if args.all or args.by_yongshen:
        stats.by_yongshen()
    
    if args.all or args.distribution:
        stats.distribution()
    
    if args.all or args.validate_classification:
        stats.validate_classification()
    
    if not any([args.by_yongshen, args.distribution, args.validate_classification, args.all]):
        parser.print_help()

if __name__ == "__main__":
    main()
