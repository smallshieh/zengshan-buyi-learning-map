#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
術語索引建立工具 (Term Index Builder)
用途：掃描 glossary/ 和 theory/ 目錄，生成 term_index.json
目標：避免 AI Agent 重複掃描目錄，節省 Token 消耗
"""

import json
from pathlib import Path
from typing import List, Dict

# 路徑設定
BASE_DIR = Path(__file__).resolve().parent.parent
GLOSSARY_DIR = BASE_DIR / "glossary"
THEORY_DIR = BASE_DIR / "theory"
OUTPUT_FILE = BASE_DIR / "data" / "term_index.json"


def scan_directory(directory: Path, category: str) -> List[Dict[str, str]]:
    """
    掃描指定目錄，提取所有 .md 檔案的術語資訊
    
    Args:
        directory: 要掃描的目錄
        category: 類別名稱（glossary 或 theory）
    
    Returns:
        術語列表，每個術語包含 name, category, file_path
    """
    terms = []
    
    if not directory.exists():
        print(f"⚠️  目錄不存在: {directory}")
        return terms
    
    for md_file in sorted(directory.glob("*.md")):
        # 跳過 README
        if md_file.name.upper() == "README.MD":
            continue
        
        term_name = md_file.stem
        
        # 讀取第一行作為描述（選用）
        try:
            first_line = md_file.read_text(encoding='utf-8').split('\n')[0]
            description = first_line.replace('#', '').strip()
        except Exception as e:
            description = term_name
            print(f"⚠️  無法讀取 {md_file.name}: {e}")
        
        terms.append({
            "name": term_name,
            "category": category,
            "file_path": str(md_file.relative_to(BASE_DIR)),
            "description": description
        })
    
    return terms


def build_index() -> Dict:
    """
    建立完整的術語索引
    
    Returns:
        包含所有術語的索引字典
    """
    print("🔍 開始建立術語索引...\n")
    
    # 掃描 glossary
    print(f"📚 掃描 glossary/ ...")
    glossary_terms = scan_directory(GLOSSARY_DIR, "glossary")
    print(f"   ✅ 找到 {len(glossary_terms)} 個術語\n")
    
    # 掃描 theory
    print(f"📖 掃描 theory/ ...")
    theory_terms = scan_directory(THEORY_DIR, "theory")
    print(f"   ✅ 找到 {len(theory_terms)} 個理論主題\n")
    
    # 建立索引結構
    index = {
        "metadata": {
            "total_terms": len(glossary_terms) + len(theory_terms),
            "glossary_count": len(glossary_terms),
            "theory_count": len(theory_terms),
            "generated_by": "build_term_index.py"
        },
        "glossary": glossary_terms,
        "theory": theory_terms,
        # 提供快速查詢的名稱列表
        "term_names": {
            "glossary": [t["name"] for t in glossary_terms],
            "theory": [t["name"] for t in theory_terms]
        }
    }
    
    return index


def save_index(index: Dict):
    """
    儲存索引到 JSON 檔案
    
    Args:
        index: 術語索引字典
    """
    # 確保 data 目錄存在
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 索引已儲存: {OUTPUT_FILE}")
    print(f"   總術語數: {index['metadata']['total_terms']}")
    print(f"   - glossary: {index['metadata']['glossary_count']}")
    print(f"   - theory: {index['metadata']['theory_count']}")


def main():
    """主執行流程"""
    print("=" * 60)
    print("術語索引建立工具")
    print("=" * 60)
    print()
    
    # 建立索引
    index = build_index()
    
    # 儲存檔案
    save_index(index)
    
    print("\n" + "=" * 60)
    print("✅ 完成！")
    print("=" * 60)
    print("\n💡 使用說明：")
    print("   AI Agent 現在可以讀取 data/term_index.json")
    print("   而不需要掃描 glossary/ 和 theory/ 目錄")
    print("   這將大幅減少 Token 消耗")


if __name__ == "__main__":
    main()
