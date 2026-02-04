#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移動並重新命名未分類的卦例檔案
"""
import os
import re
import shutil
from pathlib import Path

BASE_DIR = Path(r"c:\Users\smallshieh\Obsidian筆記")
CASES_DIR = BASE_DIR / "cases"

# 定義重新命名規則
RENAME_MAP = {
    # 天時類
    "case_057_天時_case_new_tianshi_fu_wairen_pingan_gou_zhi_heng.md": 
        ("天時", "case_057_占父外任平安.md"),
    "case_061_天時_case_tianshi_chen_ri_gui_si_ri_zhan_jia_wu_ri_yu_fou.md":
        ("天時", "case_061_占甲午日雨否.md"),
    
    # 陰宅類 → 風水
    "case_153_陰宅_case_yinzhai_suiguanfu_shangren_bizhi_jing.md":
        ("風水", "case_153_占隨官上任.md"),
}

def get_all_uncategorized_files():
    """取得所有未分類的檔案"""
    uncategorized = []
    for file in CASES_DIR.glob("case_*.md"):
        if file.is_file():
            uncategorized.append(file.name)
    return uncategorized

def move_and_rename_file(old_name, category, new_name):
    """移動並重新命名檔案"""
    old_path = CASES_DIR / old_name
    new_dir = CASES_DIR / category
    new_path = new_dir / new_name
    
    # 確保目標目錄存在
    new_dir.mkdir(exist_ok=True)
    
    # 移動並重新命名
    if old_path.exists():
        print(f"移動: {old_name}")
        print(f"  → {category}/{new_name}")
        shutil.move(str(old_path), str(new_path))
        return True
    else:
        print(f"警告: 找不到檔案 {old_name}")
        return False

def main():
    print("=" * 60)
    print("開始處理未分類檔案...")
    print("=" * 60)
    
    # 先列出所有未分類檔案
    uncategorized = get_all_uncategorized_files()
    print(f"\n找到 {len(uncategorized)} 個未分類檔案:\n")
    for f in sorted(uncategorized):
        print(f"  - {f}")
    
    print("\n" + "=" * 60)
    print("開始移動和重新命名...")
    print("=" * 60 + "\n")
    
    # 執行移動和重新命名
    moved_count = 0
    for old_name, (category, new_name) in RENAME_MAP.items():
        if move_and_rename_file(old_name, category, new_name):
            moved_count += 1
    
    print("\n" + "=" * 60)
    print(f"完成! 共處理 {moved_count} 個檔案")
    print("=" * 60)
    
    # 檢查是否還有未處理的檔案
    remaining = get_all_uncategorized_files()
    if remaining:
        print(f"\n警告: 還有 {len(remaining)} 個檔案未處理:")
        for f in sorted(remaining):
            print(f"  - {f}")

if __name__ == "__main__":
    main()
