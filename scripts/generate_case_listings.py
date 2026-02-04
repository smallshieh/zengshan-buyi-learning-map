#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
為學習地圖生成詳細的案例列表
"""
import re
import yaml
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(r"c:\Users\smallshieh\Obsidian筆記")
CASES_DIR = BASE_DIR / "cases"

def extract_frontmatter(file_path):
    """提取檔案的 frontmatter"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            return yaml.safe_load(match.group(1))
    except:
        pass
    return {}

def extract_title_from_content(file_path):
    """從檔案內容提取標題"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('# '):
                    return line.strip('# \r\n')
    except:
        pass
    return None

def generate_case_listings():
    """生成所有類別的案例列表"""
    categories = defaultdict(list)
    
    for category_dir in sorted(CASES_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        
        category_name = category_dir.name
        case_files = sorted(category_dir.glob('case_*.md'))
        
        for case_file in case_files:
            frontmatter = extract_frontmatter(case_file)
            title = extract_title_from_content(case_file)
            question = frontmatter.get('question', '')
            
            # 從檔名提取簡短描述
            filename = case_file.stem
            # case_###_占XXX_描述.md -> 占XXX_描述
            match = re.match(r'case_\d+_(.*)', filename)
            short_desc = match.group(1) if match else filename
            
            # 優先使用 question,其次使用標題,最後使用檔名
            display_name = question or title or short_desc
            
            categories[category_name].append({
                'file': case_file.name,
                'display': display_name,
                'path': f"cases/{category_name}/{case_file.name}"
            })
    
    return categories

def format_category_section(category_name, cases, max_display=10):
    """格式化單個類別的案例列表"""
    lines = []
    
    # 顯示前 N 個案例
    display_cases = cases[:max_display]
    
    for case in display_cases:
        # 格式: - [[path|display_name]]
        lines.append(f"- [[{case['path']}|{case['display']}]]")
    
    # 如果還有更多案例
    if len(cases) > max_display:
        remaining = len(cases) - max_display
        lines.append(f"- *(及其他 {remaining} 個案例)*")
    
    return '\n'.join(lines)

def main():
    """主函數"""
    print("=" * 70)
    print("生成學習地圖案例列表")
    print("=" * 70 + "\n")
    
    categories = generate_case_listings()
    
    # 按類別輸出
    for category_name in sorted(categories.keys()):
        cases = categories[category_name]
        print(f"\n### {category_name} ({len(cases)} 個)")
        print(format_category_section(category_name, cases, max_display=5))
    
    print("\n" + "=" * 70)
    print(f"完成! 共 {sum(len(c) for c in categories.values())} 個案例")
    print("=" * 70)
    
    # 保存到檔案以便複製
    output_file = BASE_DIR / "case_listings_for_map.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        for category_name in sorted(categories.keys()):
            cases = categories[category_name]
            f.write(f"\n### {category_name} ({len(cases)} 個)\n")
            f.write(format_category_section(category_name, cases, max_display=5))
            f.write("\n")
    
    print(f"\n輸出已保存至: {output_file}")

if __name__ == "__main__":
    main()
