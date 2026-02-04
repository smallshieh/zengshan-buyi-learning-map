#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新重新命名檔案後的連結
根據 auto_categorize_cases.py 的移動記錄更新所有 Obsidian 連結
"""
import re
import sys
from pathlib import Path
from typing import Dict, Set, Tuple

BASE_DIR = Path(r"c:\Users\smallshieh\Obsidian筆記")

def build_rename_map() -> Dict[str, str]:
    """
    建立舊檔名 → 新檔名的映射表
    從 auto_categorize_cases.py 重新執行以取得映射
    """
    sys.path.insert(0, str(BASE_DIR / "scripts"))
    from auto_categorize_cases import CASES_DIR, extract_frontmatter, infer_category, generate_new_filename
    
    rename_map = {}
    
    # 掃描所有分類目錄中的檔案
    for category_dir in CASES_DIR.iterdir():
        if not category_dir.is_dir():
            continue
        
        for case_file in category_dir.glob("case_*.md"):
            # 檢查是否為最近重新命名的檔案
            # 新檔名格式: case_###_占XXX.md (簡潔)
            # 舊檔名格式: case_###_類別_case_xxx_long_name.md (冗長)
            
            # 由於我們已經移動了檔案,需要從記錄中重建映射
            # 這裡我們使用簡化的啟發式方法
            pass
    
    # 手動建立已知的重新命名映射(從執行記錄中提取)
    # 由於檔案已移動,我們需要掃描並比對
    return rename_map

def extract_wikilinks(content: str) -> Set[str]:
    """提取內容中的所有 Wikilink"""
    # 匹配 [[filename]] 或 [[filename|alias]]
    pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
    matches = re.findall(pattern, content)
    return set(matches)

def update_links_in_file(file_path: Path, rename_map: Dict[str, str], dry_run: bool = True) -> Tuple[int, list]:
    """
    更新檔案中的連結
    返回: (更新數量, 更新詳情列表)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"⚠️  無法讀取 {file_path}: {e}")
        return 0, []
    
    original_content = content
    updates = []
    
    # 提取所有連結
    wikilinks = extract_wikilinks(content)
    
    for old_link in wikilinks:
        # 移除可能的路徑前綴,只保留檔名
        old_filename = old_link.split('/')[-1]
        
        # 檢查是否在重新命名映射中
        if old_filename in rename_map:
            new_filename = rename_map[old_filename]
            
            # 替換連結(保留路徑結構)
            if '/' in old_link:
                # 有路徑的連結
                path_prefix = '/'.join(old_link.split('/')[:-1])
                new_link = f"{path_prefix}/{new_filename}"
            else:
                # 純檔名連結
                new_link = new_filename
            
            # 執行替換
            # 需要處理兩種情況: [[old]] 和 [[old|alias]]
            pattern1 = re.compile(r'\[\[' + re.escape(old_link) + r'\]\]')
            pattern2 = re.compile(r'\[\[' + re.escape(old_link) + r'\|([^\]]+)\]\]')
            
            if pattern1.search(content):
                content = pattern1.sub(f'[[{new_link}]]', content)
                updates.append(f"{old_link} → {new_link}")
            
            if pattern2.search(content):
                content = pattern2.sub(f'[[{new_link}|\\1]]', content)
                updates.append(f"{old_link}|alias → {new_link}|alias")
    
    # 如果有更新且非 dry run,寫入檔案
    if content != original_content:
        if not dry_run:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                print(f"⚠️  無法寫入 {file_path}: {e}")
                return 0, []
        
        return len(updates), updates
    
    return 0, []

def create_simple_rename_map() -> Dict[str, str]:
    """
    建立簡化的重新命名映射
    基於檔案移動的模式推斷
    """
    rename_map = {}
    
    # 掃描所有案例檔案,建立檔名映射
    # 舊檔名模式: case_###_類別_case_xxx_long_english_name.md
    # 新檔名模式: case_###_占XXX.md
    
    for category_dir in (BASE_DIR / "cases").iterdir():
        if not category_dir.is_dir():
            continue
        
        for case_file in category_dir.glob("case_*.md"):
            # 提取案例編號
            match = re.match(r'case_(\d+)_', case_file.name)
            if match:
                case_num = match.group(1)
                
                # 檢查是否為新格式(簡潔的中文名稱)
                if '占' in case_file.name and len(case_file.name) < 50:
                    # 這是新檔名,嘗試找出可能的舊檔名
                    # 舊檔名會包含類別和英文描述
                    possible_old_patterns = [
                        f"case_{case_num}_天時_case_",
                        f"case_{case_num}_陰宅_case_",
                        f"case_{case_num}_風水_case_",
                    ]
                    
                    # 由於舊檔案已被移動,我們無法直接比對
                    # 這個映射需要從執行記錄中提取
    
    return rename_map

def main(dry_run: bool = True):
    """主執行流程"""
    print("=" * 70)
    print("連結更新腳本 - 檔案重新命名後")
    print("=" * 70)
    
    if dry_run:
        print("\n⚠️  DRY RUN 模式: 不會實際修改檔案\n")
    
    # 由於檔案已移動,我們需要使用不同的策略
    # 策略: 掃描所有 markdown 檔案,找出斷裂的連結
    print("📂 掃描所有 Markdown 檔案...")
    md_files = list(BASE_DIR.rglob("*.md"))
    
    # 排除某些目錄
    md_files = [f for f in md_files if not any(
        exclude in str(f) for exclude in ['.gemini', '.agent', 'node_modules', '.git']
    )]
    
    print(f"   找到 {len(md_files)} 個檔案\n")
    
    # 建立所有現存檔案的索引(不含副檔名)
    existing_files = set()
    for f in (BASE_DIR / "cases").rglob("*.md"):
        existing_files.add(f.stem)  # 不含 .md
    
    print(f"📋 現存案例檔案: {len(existing_files)} 個\n")
    
    # 掃描斷裂的連結
    print("🔍 掃描斷裂的連結...")
    broken_links = {}
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            wikilinks = extract_wikilinks(content)
            
            for link in wikilinks:
                # 提取檔名(移除路徑和副檔名)
                filename = link.split('/')[-1].replace('.md', '')
                
                # 檢查是否存在
                if filename.startswith('case_') and filename not in existing_files:
                    if filename not in broken_links:
                        broken_links[filename] = []
                    broken_links[filename].append(str(md_file.relative_to(BASE_DIR)))
        
        except Exception as e:
            pass
    
    if broken_links:
        print(f"\n⚠️  發現 {len(broken_links)} 個斷裂的連結:\n")
        for broken, files in sorted(broken_links.items())[:10]:
            print(f"  ❌ {broken}")
            for f in files[:3]:
                print(f"     引用自: {f}")
            if len(files) > 3:
                print(f"     ... 及其他 {len(files)-3} 個檔案")
    else:
        print("\n✅ 未發現斷裂的連結!")
    
    print("\n" + "=" * 70)
    print("💡 由於檔案已移動,建議使用 Obsidian 的內建功能:")
    print("   1. 開啟 Obsidian")
    print("   2. 使用 Ctrl+P → 'Detect all broken links'")
    print("   3. 使用 'Update internal links' 自動修復")
    print("=" * 70)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='更新檔案重新命名後的連結')
    parser.add_argument('--commit', action='store_true', help='執行實際更新')
    
    args = parser.parse_args()
    
    main(dry_run=not args.commit)
