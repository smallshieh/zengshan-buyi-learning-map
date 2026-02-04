import os
import json
import re
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
CHAPTERS_DIR = BASE_DIR / "reference" / "chapters"
REF_DIR = BASE_DIR / "reference"
REGISTRY_FILE = REF_DIR / "chapter_registry.json"
INDEX_FILE = REF_DIR / "keyword_index.json"

# Taxonomy for Indexing
KEYWORDS = {
    # Categories
    "求財": ["求財", "財運", "生意", "開店", "借貸", "博戲"],
    "婚姻": ["婚姻", "嫁娶", "男占女", "女占男", "納寵", "白頭", "媒妁", "聘禮", "婚期"],
    "疾病": ["疾病", "病源", "醫藥", "延醫", "痘疹", "瘡瘍", "痘疹"],
    "功名": ["功名", "升遷", "考試", "童試", "鄉試", "會試", "仕途", "發案"],
    "官訟": ["官訟", "詞訟", "爭競", "避訟", "牢獄", "受刑", "官府"],
    "出行": ["出行", "舟行", "行路", "遠行", "中途"],
    "行人": ["行人", "音信", "歸期", "客居"],
    "家宅": ["家宅", "陽宅", "修造", "遷居", "入火", "蓋造", "置宅", "起蓋"],
    "陰宅": ["陰宅", "墳墓", "風水", "尋地", "點穴", "修墳", "造葬", "山頭"],
    "胎孕": ["胎孕", "生產", "產期", "求子", "墮胎"],
    "失物": ["失物", "盜賊", "逃亡", "捕盜", "失脫", "緝捕"],
    "天時": ["天時", "晴雨", "禱雨", "祈晴", "占風", "占雷", "陰晴"],
    "田產": ["田產", "買田", "置產", "田地", "契業", "地產", "買地", "尋地", "置宅"],
    
    # Technical Terms
    "用神": ["用神"],
    "元神": ["元神", "原神"],
    "忌神": ["忌神"],
    "仇神": ["仇神"],
    "世應": ["世應", "世爻", "應爻"],
    "動變": ["動爻", "變爻", "動化"],
    "進神": ["進神", "化進"],
    "退神": ["退神", "化退"],
    "飛伏": ["飛神", "伏神", "飛伏"],
    "月破": ["月破"],
    "日破": ["日破"],
    "暗動": ["暗動"],
    "旬空": ["旬空", "空亡"],
    "反吟": ["反吟"],
    "伏吟": ["伏吟"],
    "六合": ["六合"],
    "六沖": ["六沖"],
    "三刑": ["三刑"],
    "三合": ["三合"],
    "長生": ["長生", "帝旺", "墓絕", "十二宮"]
}

def load_chapters():
    chapters = []
    if not CHAPTERS_DIR.exists():
        print(f"Directory not found: {CHAPTERS_DIR}")
        return chapters
        
    for f in CHAPTERS_DIR.glob("*.txt"):
        try:
            with open(f, "r", encoding="utf-8") as file:
                content = file.read()
                chapters.append({
                    "filename": f.name,
                    "content": content,
                    "size": len(content)
                })
        except Exception as e:
            print(f"Error reading {f.name}: {e}")
    return chapters

def build_registry(chapters):
    registry = {}
    for chap in chapters:
        # Extract title from filename: chap_085_婚姻章.txt -> 婚姻章
        match = re.match(r"chap_\d+_(.+)\.txt", chap["filename"])
        title = match.group(1) if match else chap["filename"]
        
        # Simple heuristic summary (first 50 chars)
        summary = chap["content"][:100].replace("\n", " ").strip() + "..."
        
        registry[chap["filename"]] = {
            "title": title,
            "size": chap["size"],
            "preview": summary
        }
    return registry

def build_index(chapters):
    index = {k: [] for k in KEYWORDS.keys()}
    
    for chap in chapters:
        content_lower = chap["content"].lower()
        title_lower = chap["filename"].lower()
        
        for main_key, sub_terms in KEYWORDS.items():
            # Check if any sub-term exists in title (high weight) or content (lower weight)
            # For simplicity: boolean match.
            
            # Title match?
            is_match = False
            for term in sub_terms:
                if term in title_lower:
                    is_match = True
                    break
            
            # Content match? (Threshold: appear at least once? Or specialized logic?)
            # Let's say if appear in content, we add it. 
            if not is_match:
                for term in sub_terms:
                    if term in content_lower:
                        is_match = True
                        break
            
            if is_match:
                index[main_key].append(chap["filename"])
    
    # Sort file lists
    for k in index:
        index[k].sort()
        
    return index

def main():
    print("Building Knowledge Index...")
    chapters = load_chapters()
    print(f"Loaded {len(chapters)} chapters.")
    
    # 1. Registry
    registry = build_registry(chapters)
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    print(f"Registry saved to {REGISTRY_FILE} ({len(registry)} entries)")
    
    # 2. Inverted Index
    index = build_index(chapters)
    # Remove empty keys
    index = {k: v for k, v in index.items() if v}
    
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"Index saved to {INDEX_FILE} ({len(index)} terms)")

if __name__ == "__main__":
    main()
