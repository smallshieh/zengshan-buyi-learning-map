#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
連結有效性驗證腳本
檢查卦例中的連結是否指向存在的檔案
"""

import re
from pathlib import Path
from typing import List, Dict, Set

# ==================== 配置 ====================
BASE_DIR = Path(r"c:\Users\smallshieh\Obsidian筆記")
GLOSSARY_DIR = BASE_DIR / "glossary"
THEORY_DIR = BASE_DIR / "theory"
CASES_DIR = BASE_DIR / "cases"

# ==================== 連結提取 ====================
def extract_links(content: str) -> List[str]:
    """提取所有 [[連結]] 格式的連結"""
    # 匹配 [[連結]] 或 [[連結|顯示文字]]
    pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
    links = re.findall(pattern, content)
    return links

def resolve_link_path(link: str) -> Path:
    """解析連結路徑"""
    # 移除可能的路徑前綴
    link = link.strip()
    
    # 處理相對路徑連結
    if link.startswith('glossary/'):
        return GLOSSARY_DIR / f"{link.split('/', 1)[1]}.md"
    elif link.startswith('theory/'):
        return THEORY_DIR / f"{link.split('/', 1)[1]}.md"
    elif link.startswith('reference/'):
        return BASE_DIR / "reference" / f"{link.split('/', 1)[1]}.md"
    else:
        # 嘗試在 glossary 和 theory 中尋找
        glossary_path = GLOSSARY_DIR / f"{link}.md"
        theory_path = THEORY_DIR / f"{link}.md"
        
        if glossary_path.exists():
            return glossary_path
        elif theory_path.exists():
            return theory_path
        else:
            return BASE_DIR / f"{link}.md"

# ==================== 驗證邏輯 ====================
def verify_case_file(filepath: Path) -> Dict:
    """驗證單個卦例檔案的連結"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        links = extract_links(content)
        
        results = {
            'file': filepath.name,
            'total_links': len(links),
            'valid_links': [],
            'broken_links': [],
            'duplicate_links': []
        }
        
        # 檢查連結有效性
        seen_links = set()
        for link in links:
            target_path = resolve_link_path(link)
            
            if link in seen_links:
                results['duplicate_links'].append(link)
            else:
                seen_links.add(link)
            
            if target_path.exists():
                results['valid_links'].append(link)
            else:
                results['broken_links'].append({
                    'link': link,
                    'expected_path': str(target_path)
                })
        
        return results
        
    except Exception as e:
        return {
            'file': filepath.name,
            'error': str(e)
        }

# ==================== 主程式 ====================
def main(sample_size: int = 10):
    """主執行流程"""
    print("=" * 60)
    print("連結有效性驗證腳本")
    print("=" * 60)
    
    # 收集所有卦例檔案
    case_files = list(CASES_DIR.rglob("*.md"))
    
    # 隨機抽樣
    import random
    if len(case_files) > sample_size:
        case_files = random.sample(case_files, sample_size)
    
    print(f"\n📂 抽取 {len(case_files)} 個卦例檔案進行驗證\n")
    
    # 統計數據
    total_links = 0
    total_valid = 0
    total_broken = 0
    total_duplicates = 0
    broken_details = []
    
    # 驗證每個檔案
    for i, filepath in enumerate(case_files, 1):
        result = verify_case_file(filepath)
        
        if 'error' in result:
            print(f"  [{i}/{len(case_files)}] ❌ {result['file']} - 錯誤: {result['error']}")
            continue
        
        total_links += result['total_links']
        total_valid += len(result['valid_links'])
        total_broken += len(result['broken_links'])
        total_duplicates += len(result['duplicate_links'])
        
        status = "✅" if len(result['broken_links']) == 0 else "⚠️"
        print(f"  [{i}/{len(case_files)}] {status} {result['file']}")
        print(f"      連結總數: {result['total_links']} | 有效: {len(result['valid_links'])} | 失效: {len(result['broken_links'])}")
        
        if result['broken_links']:
            broken_details.append({
                'file': result['file'],
                'broken': result['broken_links']
            })
        
        if result['duplicate_links']:
            print(f"      ⚠️ 重複連結: {', '.join(result['duplicate_links'])}")
    
    # 生成報告
    print("\n" + "=" * 60)
    print("📊 驗證報告")
    print("=" * 60)
    print(f"抽樣檔案數: {len(case_files)}")
    print(f"連結總數: {total_links}")
    print(f"有效連結: {total_valid} ({total_valid/total_links*100:.1f}%)" if total_links > 0 else "有效連結: 0")
    print(f"失效連結: {total_broken} ({total_broken/total_links*100:.1f}%)" if total_links > 0 else "失效連結: 0")
    print(f"重複連結: {total_duplicates}")
    
    if broken_details:
        print("\n❌ 失效連結詳情:")
        for item in broken_details:
            print(f"\n  檔案: {item['file']}")
            for broken in item['broken']:
                print(f"    - [[{broken['link']}]]")
                print(f"      預期路徑: {broken['expected_path']}")
    
    print("\n" + "=" * 60)
    
    # 儲存報告
    report_path = BASE_DIR / "link_verification_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("連結有效性驗證報告\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"抽樣檔案數: {len(case_files)}\n")
        f.write(f"連結總數: {total_links}\n")
        f.write(f"有效連結: {total_valid} ({total_valid/total_links*100:.1f}%)\n" if total_links > 0 else "有效連結: 0\n")
        f.write(f"失效連結: {total_broken} ({total_broken/total_links*100:.1f}%)\n" if total_links > 0 else "失效連結: 0\n")
        f.write(f"重複連結: {total_duplicates}\n")
        
        if broken_details:
            f.write("\n失效連結詳情:\n")
            for item in broken_details:
                f.write(f"\n檔案: {item['file']}\n")
                for broken in item['broken']:
                    f.write(f"  - [[{broken['link']}]]\n")
                    f.write(f"    預期路徑: {broken['expected_path']}\n")
    
    print(f"\n💾 報告已儲存至: {report_path}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='驗證連結有效性')
    parser.add_argument('--sample', type=int, default=10, help='抽樣檔案數量')
    parser.add_argument('--all', action='store_true', help='驗證所有檔案')
    
    args = parser.parse_args()
    
    if args.all:
        main(sample_size=999999)
    else:
        main(sample_size=args.sample)
