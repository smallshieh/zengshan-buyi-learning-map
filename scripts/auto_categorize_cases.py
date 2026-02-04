#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動分類並重新命名所有未分類的卦例檔案
"""
import os
import re
import shutil
import yaml
from pathlib import Path

BASE_DIR = Path(r"c:\Users\smallshieh\Obsidian筆記")
CASES_DIR = BASE_DIR / "cases"

# 類別映射 (從檔名或標籤推斷)
CATEGORY_MAP = {
    "天時": "天時",
    "陰宅": "風水",
    "風水": "風水",
    "求財": "求財",
    "功名": "功名",
    "疾病": "疾病",
    "六親": "六親",
    "官訟": "官訟",
    "行人": "行人",
    "婚姻": "婚姻",
    "出行": "出行",
    "生產": "生產",
    "壽元": "壽元",
    "趨避": "趨避",
    "家宅": "家宅",
    "學業": "學業",
    "終身財福": "終身財福",
}

def extract_frontmatter(file_path):
    """提取檔案的 frontmatter"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 YAML frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except:
            return {}
    return {}

def infer_category(filename, frontmatter):
    """從檔名和 frontmatter 推斷類別"""
    # 先從檔名推斷
    for key, category in CATEGORY_MAP.items():
        if key in filename:
            return category
    
    # 從標籤推斷
    tags = frontmatter.get('tags', [])
    for tag in tags:
        if isinstance(tag, str):
            for key, category in CATEGORY_MAP.items():
                if key in tag:
                    return category
    
    return "其他"

def generate_new_filename(old_filename, frontmatter):
    """生成新的標準檔名"""
    # 提取案例編號
    match = re.match(r'case_(\d+)_', old_filename)
    if not match:
        return None
    
    case_num = match.group(1)
    
    # 提取問事內容
    question = frontmatter.get('question', '')
    if not question:
        # 從檔名提取
        parts = old_filename.replace('.md', '').split('_')
        if len(parts) > 3:
            question = '_'.join(parts[3:])[:20]  # 限制長度
    
    # 清理問事內容
    question = question.replace('占', '').replace('問', '').strip()
    question = re.sub(r'[^\w\u4e00-\u9fff]+', '_', question)[:15]
    
    return f"case_{case_num}_占{question}.md"

def process_files(dry_run=True):
    """處理所有未分類檔案"""
    uncategorized = list(CASES_DIR.glob("case_*.md"))
    uncategorized = [f for f in uncategorized if f.is_file()]
    
    print(f"找到 {len(uncategorized)} 個未分類檔案\n")
    
    moves = []
    for file_path in sorted(uncategorized):
        frontmatter = extract_frontmatter(file_path)
        category = infer_category(file_path.name, frontmatter)
        new_filename = generate_new_filename(file_path.name, frontmatter)
        
        if not new_filename:
            print(f"⚠️  無法處理: {file_path.name}")
            continue
        
        new_dir = CASES_DIR / category
        new_path = new_dir / new_filename
        
        moves.append({
            'old': file_path,
            'new': new_path,
            'category': category,
            'old_name': file_path.name,
            'new_name': new_filename
        })
    
    # 顯示計劃
    print("=" * 80)
    print("移動計劃:")
    print("=" * 80)
    for move in moves:
        print(f"\n{move['old_name']}")
        print(f"  → {move['category']}/{move['new_name']}")
    
    if dry_run:
        print("\n" + "=" * 80)
        print("這是預覽模式。若要執行,請設定 dry_run=False")
        print("=" * 80)
        return moves
    
    # 執行移動
    print("\n" + "=" * 80)
    print("開始執行移動...")
    print("=" * 80)
    
    for move in moves:
        move['new'].parent.mkdir(exist_ok=True)
        shutil.move(str(move['old']), str(move['new']))
        print(f"✓ {move['new_name']}")
    
    print(f"\n完成! 共處理 {len(moves)} 個檔案")
    return moves

if __name__ == "__main__":
    # 先預覽
    process_files(dry_run=True)
