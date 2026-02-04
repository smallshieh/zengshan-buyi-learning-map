#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
卦例驗證工具
檢查卦例檔案的格式、欄位和連結完整性
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Set

BASE_DIR = Path(r"c:\Users\smallshieh\Obsidian筆記")
CASES_DIR = BASE_DIR / "cases"

class CaseValidator:
    def __init__(self):
        self.cases_dir = CASES_DIR
        self.errors = []
        self.warnings = []
    
    def check_format(self, case_file: Path) -> Dict:
        """檢查卦例格式"""
        result = {
            'file': case_file.name,
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            content = case_file.read_text(encoding='utf-8')
            
            # 檢查標題
            if not content.startswith('#'):
                result['errors'].append('缺少標題')
                result['valid'] = False
            
            # 檢查基本章節
            required_sections = ['卦象', '分析', '斷語']
            for section in required_sections:
                if f"## {section}" not in content and f"### {section}" not in content:
                    result['warnings'].append(f'建議添加「{section}」章節')
            
        except Exception as e:
            result['errors'].append(f'讀取錯誤: {str(e)}')
            result['valid'] = False
        
        return result
    
    def check_fields(self, case_file: Path) -> Dict:
        """檢查必要欄位"""
        result = {
            'file': case_file.name,
            'valid': True,
            'missing_fields': []
        }
        
        try:
            content = case_file.read_text(encoding='utf-8')
            
            # 檢查是否包含用神相關內容
            if '用神' not in content:
                result['missing_fields'].append('用神')
            
            # 檢查是否有卦象信息
            if '爻' not in content and '卦' not in content:
                result['missing_fields'].append('卦象信息')
            
            if result['missing_fields']:
                result['valid'] = False
        
        except Exception as e:
            result['valid'] = False
            result['missing_fields'].append(f'讀取錯誤: {str(e)}')
        
        return result
    
    def check_links(self, case_file: Path) -> Dict:
        """檢查連結有效性"""
        result = {
            'file': case_file.name,
            'valid': True,
            'broken_links': []
        }
        
        try:
            content = case_file.read_text(encoding='utf-8')
            
            # 找出所有連結
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            
            for link in links:
                # 移除顯示文字 (如 [[link|顯示文字]])
                link_path = link.split('|')[0]
                
                # 檢查連結是否存在
                if link_path.startswith('glossary/'):
                    term_file = BASE_DIR / f"{link_path}.md"
                    if not term_file.exists():
                        result['broken_links'].append(link_path)
                        result['valid'] = False
                
                elif link_path.startswith('theory/'):
                    theory_file = BASE_DIR / f"{link_path}.md"
                    if not theory_file.exists():
                        result['broken_links'].append(link_path)
                        result['valid'] = False
                
                elif link_path.startswith('cases/'):
                    case_ref = BASE_DIR / f"{link_path}.md"
                    if not case_ref.exists():
                        result['broken_links'].append(link_path)
                        result['valid'] = False
        
        except Exception as e:
            result['valid'] = False
            result['broken_links'].append(f'檢查錯誤: {str(e)}')
        
        return result
    
    def validate_all(self, check_type: str = 'all'):
        """驗證所有卦例"""
        print(f"\n🔍 卦例驗證 - {check_type}")
        print("=" * 60)
        
        all_cases = list(self.cases_dir.rglob("case_*.md"))
        print(f"找到 {len(all_cases)} 個卦例檔案\n")
        
        error_count = 0
        warning_count = 0
        
        for case_file in all_cases:
            if check_type in ['all', 'format']:
                result = self.check_format(case_file)
                if result['errors']:
                    error_count += len(result['errors'])
                    print(f"❌ {result['file']}")
                    for error in result['errors']:
                        print(f"   - {error}")
                if result['warnings']:
                    warning_count += len(result['warnings'])
            
            if check_type in ['all', 'fields']:
                result = self.check_fields(case_file)
                if not result['valid']:
                    error_count += 1
                    print(f"⚠️  {result['file']}")
                    print(f"   缺少欄位: {', '.join(result['missing_fields'])}")
            
            if check_type in ['all', 'links']:
                result = self.check_links(case_file)
                if not result['valid']:
                    error_count += 1
                    print(f"🔗 {result['file']}")
                    for link in result['broken_links']:
                        print(f"   - 失效連結: [[{link}]]")
        
        print("\n" + "=" * 60)
        print(f"總計: {len(all_cases)} 個檔案")
        print(f"錯誤: {error_count}")
        print(f"警告: {warning_count}")
        
        if error_count == 0 and warning_count == 0:
            print("✅ 所有檔案驗證通過!")

def main():
    parser = argparse.ArgumentParser(description='卦例驗證工具')
    parser.add_argument('--check-format', action='store_true', help='檢查格式')
    parser.add_argument('--check-fields', action='store_true', help='檢查欄位')
    parser.add_argument('--check-links', action='store_true', help='檢查連結')
    parser.add_argument('--all', action='store_true', help='執行所有檢查')
    
    args = parser.parse_args()
    
    validator = CaseValidator()
    
    if args.all:
        validator.validate_all('all')
    elif args.check_format:
        validator.validate_all('format')
    elif args.check_fields:
        validator.validate_all('fields')
    elif args.check_links:
        validator.validate_all('links')
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
