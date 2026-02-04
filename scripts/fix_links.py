#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
連結自動修復工具 (Link Auto-Fixer)
自動修復損壞的 Obsidian 連結
"""

import os
import re
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(r"c:\Users\smallshieh\Obsidian筆記")

def build_file_index() -> Dict[str, Path]:
    """建立檔案索引：檔名 -> 完整路徑"""
    index = {}
    
    for pattern in ['cases/**/*.md', 'glossary/*.md', 'theory/*.md']:
        for filepath in BASE_DIR.glob(pattern):
            # 使用檔名（不含副檔名）作為 key
            basename = filepath.stem
            index[basename] = filepath
    
    return index

def fix_links_in_file(filepath: Path, file_index: Dict[str, Path], dry_run: bool = True) -> int:
    """修復單個檔案中的連結"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes_count = 0
        
        # 找到所有連結
        def replace_link(match):
            nonlocal fixes_count
            full_match = match.group(0)
            link_text = match.group(1)
            alias = match.group(2) if match.group(2) else None
            
            # 移除可能的 .md
            link_text = link_text.replace('.md', '')
            
            # 提取檔名（路徑的最後一部分）
            if '/' in link_text or '\\' in link_text:
                link_basename = Path(link_text.replace('\\', '/')).name
            else:
                link_basename = link_text
            
            # 在索引中查找
            if link_basename in file_index:
                target_path = file_index[link_basename]
                # 計算相對路徑
                try:
                    rel_path = target_path.relative_to(BASE_DIR)
                    # 移除 .md 副檔名
                    rel_path_str = str(rel_path).replace('\\', '/').replace('.md', '')
                    
                    # 構建新連結
                    if alias:
                        new_link = f"[[{rel_path_str}|{alias}]]"
                    else:
                        new_link = f"[[{rel_path_str}]]"
                    
                    if new_link != full_match:
                        fixes_count += 1
                        return new_link
                except ValueError:
                    pass
            
            return full_match
        
        # 替換所有連結
        pattern = r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]'
        content = re.sub(pattern, replace_link, content)
        
        # 如果有變更且不是 dry run，寫回檔案
        if content != original_content and not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return fixes_count
        
    except Exception as e:
        print(f"❌ 處理 {filepath} 時發生錯誤: {e}")
        return 0

def main(dry_run: bool = True, target_dir: str = None):
    """主執行流程"""
    print("=" * 70)
    print("🔧 Obsidian 連結自動修復工具")
    print("=" * 70)
    
    if dry_run:
        print("\n⚠️  DRY RUN 模式：只顯示會修復的內容，不實際修改檔案\n")
    
    # 建立檔案索引
    print("📚 正在建立檔案索引...")
    file_index = build_file_index()
    print(f"✅ 索引了 {len(file_index)} 個檔案\n")
    
    # 收集要處理的檔案
    if target_dir:
        target_path = BASE_DIR / target_dir
        files_to_process = list(target_path.glob("*.md"))
        print(f"🎯 目標目錄：{target_dir}")
    else:
        files_to_process = []
        for pattern in ['glossary/*.md', 'theory/*.md']:
            files_to_process.extend(BASE_DIR.glob(pattern))
        print(f"🎯 處理所有術語表和理論章節")
    
    print(f"📂 找到 {len(files_to_process)} 個檔案\n")
    
    # 處理檔案
    print("🔗 開始修復連結...\n")
    
    total_fixes = 0
    files_modified = 0
    
    for i, filepath in enumerate(files_to_process, 1):
        fixes = fix_links_in_file(filepath, file_index, dry_run)
        if fixes > 0:
            total_fixes += fixes
            files_modified += 1
            status = "會修復" if dry_run else "已修復"
            print(f"  [{i}/{len(files_to_process)}] ✅ {filepath.name}: {status} {fixes} 個連結")
        else:
            print(f"  [{i}/{len(files_to_process)}] ⏭️  {filepath.name}: 無需修復")
    
    # 結果報告
    print("\n" + "=" * 70)
    print("📊 修復結果摘要")
    print("=" * 70)
    print(f"處理檔案數：{len(files_to_process)}")
    print(f"修改檔案數：{files_modified}")
    print(f"修復連結數：{total_fixes}")
    
    if dry_run and total_fixes > 0:
        print("\n💡 這是 DRY RUN，實際檔案未被修改")
        print("   若要執行實際修復，請使用：python fix_links.py --commit")
    elif not dry_run:
        print("\n✅ 所有連結已修復！")
        print("   建議執行：git diff 查看變更")
    
    print("=" * 70)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='自動修復 Obsidian 連結')
    parser.add_argument('--dry-run', action='store_true', default=True, help='模擬執行（預設）')
    parser.add_argument('--commit', action='store_true', help='執行實際修復')
    parser.add_argument('--dir', type=str, help='只處理指定目錄（例如：glossary）')
    
    args = parser.parse_args()
    
    main(dry_run=not args.commit, target_dir=args.dir)
