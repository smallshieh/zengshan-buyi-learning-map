#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知識點自動連結腳本 (Knowledge Linking Script)
根據《知識連結規範 v1.0》實作
⚡ Token 優化：改用 term_index.json 而非掃描目錄

功能：
1. 自動為卦例中的術語建立 [[連結]]
2. 遵循「首次出現」原則
3. 只在指定區塊（斷語、理論要點）中連結
4. 保護 YAML、代碼區塊、既有連結
"""

import os
import re
import json
from pathlib import Path
from typing import List, Set, Dict

# ==================== 配置 ====================
BASE_DIR = Path(r"c:\Users\smallshieh\Obsidian筆記")
GLOSSARY_DIR = BASE_DIR / "glossary"
THEORY_DIR = BASE_DIR / "theory"
CASES_DIR = BASE_DIR / "cases"
TERM_INDEX_FILE = BASE_DIR / "data" / "term_index.json"

# 目標區塊（只在這些區塊內連結）
TARGET_SECTIONS = [
    "## 斷語",
    "## 卦象分析", 
    "## 理論要點",
    "## 重點摘要",
    "## 野鶴評註"
]

# ==================== 術語載入 ====================
def load_terms() -> List[str]:
    """
    載入所有術語（從 glossary 和 theory）
    ⚡ Token 優化：改用 term_index.json 而非掃描目錄
    """
    terms = []
    
    # 優先從 term_index.json 讀取（Token 優化）
    if TERM_INDEX_FILE.exists():
        print("📖 從 term_index.json 讀取術語（Token 優化模式）...")
        try:
            with open(TERM_INDEX_FILE, 'r', encoding='utf-8') as f:
                index = json.load(f)
            
            # 使用快速查詢的名稱列表
            terms = index['term_names']['glossary'] + index['term_names']['theory']
            print(f"   ✅ 從索引檔載入 {len(terms)} 個術語")
        except Exception as e:
            print(f"   ⚠️  讀取 term_index.json 失敗: {e}")
            print("   ℹ️  退回到掃描模式...")
    
    # 若索引檔不存在或讀取失敗，退回掃描模式
    if not terms:
        print("⚠️  使用目錄掃描模式（建議執行 python scripts/build_term_index.py）")
        # 從術語表載入
        if GLOSSARY_DIR.exists():
            for f in GLOSSARY_DIR.glob("*.md"):
                terms.append(f.stem)
        
        # 從理論章節載入
        if THEORY_DIR.exists():
            for f in THEORY_DIR.glob("*.md"):
                # 處理 "01_八卦章.md" -> 加入 "八卦章" 和 "01_八卦章"
                full_name = f.stem
                terms.append(full_name)
                if "_" in full_name:
                    short_name = full_name.split("_", 1)[1]
                    terms.append(short_name)
    
    # 按長度排序（長詞優先，避免被短詞截斷）
    # 例如：「化進神」應該在「進神」之前處理
    terms = sorted(list(set(terms)), key=len, reverse=True)
    
    # 過濾單字術語（避免誤判）
    terms = [t for t in terms if len(t) > 1]
    
    return terms

# ==================== 內容解析 ====================
def split_frontmatter_and_body(content: str) -> tuple:
    """分離 YAML Frontmatter 和正文"""
    parts = re.split(r'^---$', content, maxsplit=2, flags=re.MULTILINE)
    
    if len(parts) >= 3:
        frontmatter = f"---{parts[1]}---"
        body = parts[2]
        return frontmatter, body
    else:
        return "", content

def extract_target_sections(body: str) -> Dict[str, str]:
    """提取目標區塊（斷語、理論要點等）"""
    sections = {}
    
    # 分割所有 ## 標題
    lines = body.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        if line.startswith('## '):
            # 儲存上一個區塊
            if current_section and current_section in TARGET_SECTIONS:
                sections[current_section] = '\n'.join(current_content)
            
            # 開始新區塊
            current_section = line.strip()
            current_content = [line]
        else:
            if current_section:
                current_content.append(line)
    
    # 儲存最後一個區塊
    if current_section and current_section in TARGET_SECTIONS:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

# ==================== 連結邏輯 ====================
def protect_existing_links(text: str) -> tuple:
    """暫時替換既有連結，避免嵌套"""
    placeholders = {}
    links = re.findall(r'\[\[.*?\]\]', text)
    
    for i, link in enumerate(links):
        placeholder = f"__LINK_PLACEHOLDER_{i}__"
        text = text.replace(link, placeholder)
        placeholders[placeholder] = link
    
    return text, placeholders

def restore_links(text: str, placeholders: Dict[str, str]) -> str:
    """還原被保護的連結"""
    for placeholder, original_link in placeholders.items():
        text = text.replace(placeholder, original_link)
    return text

def link_terms_in_section(section_content: str, terms: List[str]) -> str:
    """在區塊中為術語建立連結（首次出現原則）"""
    # 保護既有連結
    protected_text, placeholders = protect_existing_links(section_content)
    
    # 保護代碼區塊
    code_blocks = re.findall(r'```.*?```', protected_text, re.DOTALL)
    for i, block in enumerate(code_blocks):
        code_placeholder = f"__CODE_BLOCK_{i}__"
        protected_text = protected_text.replace(block, code_placeholder)
        placeholders[code_placeholder] = block
    
    # 追蹤已連結的術語
    linked_terms: Set[str] = set()
    
    # 為每個術語建立連結（只連結首次出現）
    for term in terms:
        if term in linked_terms:
            continue
        
        # 檢查術語是否存在（且不在已連結的詞中）
        if term in protected_text and not f"[[{term}]]" in protected_text:
            # 使用正則確保不會連結到詞的一部分
            # 例如：不要將 "用神章" 中的 "用神" 連結（因為整體是 "用神章"）
            pattern = re.compile(f'(?<!\\[\\[){re.escape(term)}(?!\\]\\])')
            
            # 只替換第一次出現
            protected_text = pattern.sub(f'[[{term}]]', protected_text, count=1)
            linked_terms.add(term)
    
    # 還原所有被保護的內容
    result = restore_links(protected_text, placeholders)
    
    return result

# ==================== 檔案處理 ====================
def process_case_file(filepath: Path, terms: List[str], dry_run: bool = False) -> bool:
    """處理單個卦例檔案"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 分離 Frontmatter 和正文
        frontmatter, body = split_frontmatter_and_body(original_content)
        
        # 提取目標區塊
        target_sections = extract_target_sections(body)
        
        if not target_sections:
            # 沒有目標區塊，跳過
            return False
        
        # 處理每個目標區塊
        modified = False
        for section_title, section_content in target_sections.items():
            new_content = link_terms_in_section(section_content, terms)
            if new_content != section_content:
                body = body.replace(section_content, new_content)
                modified = True
        
        if not modified:
            return False
        
        # 重組內容
        new_content = frontmatter + body
        
        # 寫回檔案（除非是 dry run）
        if not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
        
        return True
        
    except Exception as e:
        print(f"❌ 處理 {filepath.name} 時發生錯誤: {e}")
        return False

# ==================== 主程式 ====================
def main(dry_run: bool = False, test_mode: bool = False):
    """主執行流程"""
    print("=" * 60)
    print("知識點自動連結腳本 v1.1 (Token 優化版)")
    print("遵循《知識連結規範》階段一標準")
    print("=" * 60)
    
    # 載入術語
    print("\n📚 正在載入術語...")
    terms = load_terms()
    print(f"✅ 載入了 {len(terms)} 個術語")
    print(f"   範例：{', '.join(terms[:10])}")
    
    # 收集所有卦例檔案
    case_files = list(CASES_DIR.rglob("*.md"))
    print(f"\n📂 找到 {len(case_files)} 個卦例檔案")
    
    # 測試模式：只處理前 5 個
    if test_mode:
        case_files = case_files[:5]
        print(f"⚠️  測試模式：只處理前 {len(case_files)} 個檔案")
    
    # 處理檔案
    print(f"\n🔗 開始建立連結...")
    if dry_run:
        print("⚠️  DRY RUN 模式：不會實際修改檔案\n")
    
    modified_count = 0
    for i, filepath in enumerate(case_files, 1):
        if process_case_file(filepath, terms, dry_run):
            modified_count += 1
            print(f"  [{i}/{len(case_files)}] ✅ {filepath.name}")
        else:
            print(f"  [{i}/{len(case_files)}] ⏭️  {filepath.name} (無需修改)")
    
    # 統計報告
    print("\n" + "=" * 60)
    print("✅ 執行完成")
    print(f"   修改檔案數：{modified_count}/{len(case_files)}")
    print(f"   未修改：{len(case_files) - modified_count}")
    
    if dry_run:
        print("\n💡 這是 DRY RUN，實際檔案未被修改")
        print("   若要執行實際修改，請使用：python link_knowledge.py --commit")
    else:
        print("\n💾 已儲存所有變更")
        print("   建議執行：git diff 查看變更")
    print("=" * 60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='知識點自動連結 (Token優化版)')
    parser.add_argument('--dry-run', action='store_true', help='模擬執行，不實際修改檔案')
    parser.add_argument('--test', action='store_true', help='測試模式，只處理前5個檔案')
    parser.add_argument('--commit', action='store_true', help='執行實際修改')
    
    args = parser.parse_args()
    
    # 預設為 dry run（安全起見）
    if args.commit:
        main(dry_run=False, test_mode=args.test)
    else:
        main(dry_run=True, test_mode=args.test)
